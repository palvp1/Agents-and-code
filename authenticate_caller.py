# TOOL NAME: authenticate_caller        (used by: authentication_agent)
# Paste this whole file as a Python code tool named exactly authenticate_caller.
# The global `context` object is provided by the runtime - do not import it.

import re
from datetime import datetime
from typing import Optional, Dict, Any

# ---- Mock IDP data (POC only - replace with ces_requests call to the real
# ---- IDP API later; only this block changes) --------------------------------
PERSONAS = {
    "5551110001": {"dob": "1980-01-01", "memberId": "M-1001", "zip": "33601",
                   "name": "Alice Test", "callerType": "member",
                   "policies": [{"id": "P1001", "planType": "Short Term", "status": "Active"}]},
    "5551110002": {"dob": "1975-05-05", "memberId": "M-2002", "zip": "33602",
                   "name": "Bob Provider", "callerType": "provider",
                   "policies": [{"id": "P2002", "planType": "Provider", "status": "Active"}]},
    "5551110003": {"dob": "1990-09-09", "memberId": "M-3003", "zip": "33603",
                   "name": "Carol MultiPolicy", "callerType": "member",
                   "policies": [{"id": "P3001", "planType": "Dental", "status": "Active"},
                                 {"id": "P3002", "planType": "Accident", "status": "Active"},
                                 {"id": "P3003", "planType": "Short Term", "status": "Lapsed"}]},
    "5551110004": {"dob": "1965-12-12", "memberId": "M-4004", "zip": "33604",
                   "name": "Dan AltAuth", "callerType": "member",
                   "policies": [{"id": "P4004", "planType": "Dental", "status": "Active"}]},
}

MAX_ATTEMPTS = 3


def _digits(raw):
    return re.sub(r"\D+", "", raw or "")


def _norm_phone(raw):
    d = _digits(raw)
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    return d if len(d) == 10 else None


def _norm_dob(raw):
    if not raw:
        return None
    raw = raw.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%d %B %Y", "%B %d %Y", "%B %d, %Y"):
        try:
            dt = datetime.strptime(raw, fmt)
            if 1900 <= dt.year <= datetime.now().year:
                return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _norm_member_id(raw):
    if not raw:
        return None
    c = raw.strip().upper().replace(" ", "-")
    if c.isdigit():
        c = "M-" + c
    return c if re.match(r"^M-\d{4}$", c) else None


def _norm_zip(raw):
    d = _digits(raw)[:5]
    return d if len(d) == 5 else None


def authenticate_caller(phone: Optional[str] = None,
                        dob: Optional[str] = None,
                        member_id: Optional[str] = None,
                        zip_code: Optional[str] = None) -> Dict[str, Any]:
  """
  Verifies the caller's identity against the member system. Call this whenever
  the caller has provided credentials to verify.

  Primary path: phone + dob. Alternate path: phone + member_id + zip_code
  (also works when the phone is unknown to the system).

  A hard limit of 3 verification attempts is enforced per conversation.
  Interpret the response as follows:
  - authenticated true: the caller is verified; auth_status, caller_type,
    member_id, policy_number and multi_policy are now set.
  - reason "invalid_input": the input was malformed and did NOT use an
    attempt. Re-ask the caller for the invalid_field in a clearer way.
  - attempts_exhausted true: STOP trying. Tell the caller you could not
    verify them and hand off for transfer.

  Args:
    phone: Caller phone number in any spoken format, e.g. "555-111-0001".
    dob: Date of birth, e.g. "1980-01-01" or "January 1 1980".
    member_id: Member ID for alternate verification, e.g. "M-1001".
    zip_code: 5-digit ZIP code for alternate verification.

  Returns:
    A dictionary with authenticated, reason, attempts_used,
    attempts_remaining, attempts_exhausted, and on success the caller's
    caller_type, member_id, name, policy_number, policies and multi_policy.
  """
  # ---- 1. Hard attempt limit, enforced in code via session state ----------
  used = int(context.state.get("auth_attempts", 0))
  if used >= MAX_ATTEMPTS:
      context.state["auth_status"] = "unauthenticated_transfer"
      return {"authenticated": False, "reason": "attempts_exhausted",
              "attempts_used": used, "attempts_remaining": 0,
              "attempts_exhausted": True}

  # ---- 2. Validate & normalize (bad input does NOT burn an attempt) --------
  n_phone = _norm_phone(phone)
  if phone and not n_phone:
      return {"authenticated": False, "reason": "invalid_input",
              "invalid_field": "phone", "attempts_used": used,
              "attempts_remaining": MAX_ATTEMPTS - used,
              "attempts_exhausted": False}
  n_dob = _norm_dob(dob)
  if dob and not n_dob:
      return {"authenticated": False, "reason": "invalid_input",
              "invalid_field": "dob", "attempts_used": used,
              "attempts_remaining": MAX_ATTEMPTS - used,
              "attempts_exhausted": False}
  n_mid = _norm_member_id(member_id)
  if member_id and not n_mid:
      return {"authenticated": False, "reason": "invalid_input",
              "invalid_field": "member_id", "attempts_used": used,
              "attempts_remaining": MAX_ATTEMPTS - used,
              "attempts_exhausted": False}
  n_zip = _norm_zip(zip_code)

  # ---- 3. Real credential check: count the attempt --------------------------
  used += 1
  context.state["auth_attempts"] = used
  print(f"[authenticate_caller] attempt {used}/{MAX_ATTEMPTS} session={context.session_id}")

  # ---- 4. Credential logic (BRD rules) ---------------------------------------
  persona = PERSONAS.get(n_phone or "")
  match = None
  if persona:
      if n_dob and n_dob == persona["dob"]:
          match = persona
      elif n_mid == persona["memberId"] and n_zip == persona["zip"]:
          match = persona
  else:
      for p in PERSONAS.values():
          if n_mid and n_mid == p["memberId"] and n_zip == p["zip"]:
              match = p
              break

  if match:
      pols = match["policies"]
      # Write verified identity to session state so other agents/tools can
      # read it via {variables} - models cannot set state themselves.
      context.state["auth_status"] = "success"
      context.state["caller_type"] = match["callerType"]
      context.state["member_id"] = match["memberId"]
      context.state["policy_number"] = pols[0]["id"] if pols else None
      context.state["policies"] = pols
      context.state["multi_policy"] = len(pols) > 1
      return {"authenticated": True, "caller_type": match["callerType"],
              "member_id": match["memberId"], "name": match["name"],
              "policy_number": context.state["policy_number"],
              "policies": pols, "multi_policy": len(pols) > 1,
              "attempts_used": used,
              "attempts_remaining": MAX_ATTEMPTS - used,
              "attempts_exhausted": False}

  exhausted = used >= MAX_ATTEMPTS
  if exhausted:
      context.state["auth_status"] = "unauthenticated_transfer"
  return {"authenticated": False,
          "reason": "no_match" if not persona else "credentials_mismatch",
          "attempts_used": used, "attempts_remaining": MAX_ATTEMPTS - used,
          "attempts_exhausted": exhausted}
