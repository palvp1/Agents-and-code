"""
test_tools.py — runs the Python code tools locally by faking the CX Agent
Studio runtime's global `context` object (one context = one conversation).

Run: python test_tools.py
"""

from pathlib import Path


class FakeContext:
    """Mimics the runtime ToolContext: .state dict + .session_id."""
    def __init__(self, session_id="local-test"):
        self.state = {}
        self.session_id = session_id


def load_tools(ctx):
    """Exec each tool file with the fake context injected as a global,
    exactly how the runtime provides it. Returns {func_name: func}."""
    tools = {}
    for f in ["authenticate_caller.py", "lookup_policies.py",
              "select_policy.py", "record_intent.py", "decide_routing.py"]:
        ns = {"context": ctx, "print": lambda *a, **k: None}  # silence prints
        exec(Path(f).read_text(), ns)
        name = f[:-3]
        tools[name] = ns[name]
    return tools


results = []
def check(label, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL':6} | {label}" + (f"  ({detail})" if not ok else ""))


def main():
    # ---------- Scenario 1: happy path end-to-end -----------------------------
    ctx = FakeContext("s1")
    t = load_tools(ctx)
    r = t["authenticate_caller"](phone="(555) 111-0001", dob="01/01/1980")
    check("01 Messy formats normalized, authenticated", r["authenticated"] is True)
    check("02 State written: auth_status/member_id",
          ctx.state.get("auth_status") == "success" and ctx.state.get("member_id") == "M-1001")
    t["record_intent"](intent="claim_status", confidence="high")
    r = t["decide_routing"]()
    check("03 Routing: claim_status -> claims_skill", r["destination"] == "claims_skill")
    check("04 Handoff summary contains member and policy",
          "M-1001" in r["handoff_summary"] and "P1001" in r["handoff_summary"])

    # ---------- Scenario 2: attempt limit ---------------------------------------
    ctx = FakeContext("s2")
    t = load_tools(ctx)
    r = t["authenticate_caller"](phone="banana phone", dob="1980-01-01")
    check("05 Invalid phone -> invalid_input, no attempt burned",
          r["reason"] == "invalid_input" and r["attempts_used"] == 0)
    for _ in range(3):
        r = t["authenticate_caller"](phone="1112223333", dob="1980-01-01")
    check("06 3rd failure -> attempts_exhausted", r["attempts_exhausted"] is True)
    check("07 State flipped to unauthenticated_transfer",
          ctx.state.get("auth_status") == "unauthenticated_transfer")
    r = t["authenticate_caller"](phone="5551110001", dob="1980-01-01")
    check("08 4th attempt REFUSED even with correct credentials",
          r["authenticated"] is False and r["reason"] == "attempts_exhausted")
    r = t["decide_routing"]()
    check("09 Unauthenticated routes to screener", r["destination"] == "member_screener_skill")

    # ---------- Scenario 3: alternate auth on unknown ANI -------------------------
    ctx = FakeContext("s3")
    t = load_tools(ctx)
    r = t["authenticate_caller"](phone="9998887777", member_id="m 4004", zip_code="33604")
    check("10 Alt-auth + memberId normalization ('m 4004')", r["authenticated"] is True)

    # ---------- Scenario 4: multi-policy with default selection --------------------
    ctx = FakeContext("s4")
    t = load_tools(ctx)
    t["authenticate_caller"](phone="5551110003", dob="1990-09-09")
    check("11 Multi-policy flag set", ctx.state.get("multi_policy") is True)
    r = t["lookup_policies"]()
    check("12 lookup_policies uses member_id from state, default=P3001",
          r["member_id"] == "M-3003" and r["default_policy"] == "P3001")
    r = t["select_policy"]()  # caller didn't choose
    check("13 No choice -> default lowest id",
          r["selected_policy"] == "P3001" and r["selection_method"] == "default_lowest_id")
    r = t["select_policy"](choice="Accident")
    check("14 Plan-type choice -> caller_choice",
          r["selected_policy"] == "P3002" and r["selection_method"] == "caller_choice")
    t["record_intent"](intent="eligibility")
    r = t["decide_routing"]()
    check("15 Selected policy appears in handoff", "P3002" in r["handoff_summary"])
    check("16 eligibility -> benefits_skill", r["destination"] == "benefits_skill")

    # ---------- Scenario 5: provider outranks intent ---------------------------------
    ctx = FakeContext("s5")
    t = load_tools(ctx)
    t["authenticate_caller"](phone="5551110002", dob="1975-05-05")
    t["record_intent"](intent="claim_status")
    r = t["decide_routing"]()
    check("17 Provider outranks intent", r["destination"] == "provider_screener_skill")

    # ---------- Scenario 6: intent validation ------------------------------------------
    ctx = FakeContext("s6")
    t = load_tools(ctx)
    r = t["record_intent"](intent="win_the_lottery", confidence="high")
    check("18 Unknown intent coerced to other/low",
          r["captured_intent"] == "other" and r["intent_confidence"] == "low")

    # ---------- Scenario 7: Spanish outranks everything ----------------------------------
    ctx = FakeContext("s7")
    t = load_tools(ctx)
    t["authenticate_caller"](phone="5551110001", dob="1980-01-01")
    ctx.state["caller_language"] = "spanish"  # set by root agent path via a tool/callback
    t["record_intent"](intent="claim_status")
    r = t["decide_routing"]()
    check("19 Spanish outranks everything", r["destination"] == "cxone_spanish_ivr")

    print("-" * 64)
    print(f"{sum(results)}/{len(results)} passed\n")


if __name__ == "__main__":
    main()
