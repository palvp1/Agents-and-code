# TOOL NAME: select_policy               (used by: policy_selection_agent)
# Paste as a Python code tool named exactly select_policy.

from typing import Optional, Dict, Any


def select_policy(choice: Optional[str] = None) -> Dict[str, Any]:
  """
  Records which policy this call is about. Call this exactly once after the
  caller answers the policy question (or fails to answer twice).

  Pass the caller's choice as the plan type they named (for example "Dental"
  or "Short Term") or the policy id if they said it. Pass nothing (or
  "default") when the caller did not choose, named several, or said all of
  them - the lowest policy id is then selected automatically per business
  rules.

  Args:
    choice: The plan type or policy id the caller named, or omit for the
      automatic default.

  Returns:
    A dictionary with selected_policy (the policy id), selected_plan_type,
    and selection_method ("caller_choice" or "default_lowest_id").
  """
  policies = context.state.get("policies", [])
  default = context.state.get("default_policy") or min(
      (p["id"] for p in policies), default=None)

  selected = None
  method = "default_lowest_id"

  if choice and choice.strip().lower() not in ("", "default", "all"):
      wanted = choice.strip().lower()
      for p in policies:
          if wanted == p["id"].lower() or wanted == p.get("planType", "").lower():
              selected = p
              method = "caller_choice"
              break

  if selected is None:
      selected = next((p for p in policies if p["id"] == default), None)
      method = "default_lowest_id"

  sel_id = selected["id"] if selected else None
  sel_plan = selected.get("planType") if selected else None

  context.state["selected_policy"] = sel_id
  context.state["selected_plan_type"] = sel_plan
  context.state["selection_method"] = method
  print(f"[select_policy] choice={choice!r} -> {sel_id} ({method})")

  return {"selected_policy": sel_id, "selected_plan_type": sel_plan,
          "selection_method": method}
