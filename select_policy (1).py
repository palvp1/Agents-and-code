from typing import Optional, Dict, Any


def select_policy(choice: Optional[str] = None) -> Dict[str, Any]:
  """
  Records which policy this call is about. Call this exactly once after the
  caller answers the policy question, or after they fail to answer twice.

  Pass the caller's choice as the plan type they named, for example "Dental"
  or "Short Term", or the policy id if they said it. Pass nothing when the
  caller did not choose, named several, or said all of them - the lowest
  policy id is then selected automatically per business rules.

  Args:
    choice: The plan type or policy id the caller named. Omit for the
      automatic default.

  Returns:
    A dictionary with selected_policy (the policy id), selected_plan_type,
    and selection_method ("caller_choice" or "default_lowest_id").
  """
  policies = context.state.get("policies", [])

  default_policy = context.state.get("default_policy")
  if not default_policy and policies:
      default_policy = min([p["id"] for p in policies])

  selected = None
  method = "default_lowest_id"

  if choice and choice.strip().lower() not in ("", "default", "all"):
      wanted = choice.strip().lower()
      for p in policies:
          plan_type = p.get("planType", "").lower()
          if wanted == p["id"].lower() or wanted == plan_type:
              selected = p
              method = "caller_choice"
              break

  if selected is None:
      method = "default_lowest_id"
      for p in policies:
          if p["id"] == default_policy:
              selected = p
              break

  selected_id = selected["id"] if selected else None
  selected_plan = selected.get("planType") if selected else None

  context.state["selected_policy"] = selected_id
  context.state["selected_plan_type"] = selected_plan
  context.state["selection_method"] = method
  print("select_policy -> " + str(selected_id) + " (" + method + ")")

  return {"selected_policy": selected_id,
          "selected_plan_type": selected_plan,
          "selection_method": method}
