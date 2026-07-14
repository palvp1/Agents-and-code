from typing import Optional, Dict, Any


def lookup_policies(member_id: Optional[str] = None) -> Dict[str, Any]:
  """
  Retrieves all policies for the verified member so you can ask which policy
  the call is about. Call this when the caller has more than one policy and
  the policy list is not yet known.

  If member_id is not provided, the verified member from this conversation is
  used automatically.

  Args:
    member_id: Optional member ID, e.g. "M-3003". Omit to use the verified
      member from this conversation.

  Returns:
    A dictionary with policies (a list of id, planType and status),
    multi_policy (true when more than one), and default_policy (the lowest
    policy id - use it when the caller does not choose).
  """
  all_policies = [
      {"id": "P1001", "planType": "Short Term", "status": "Active", "member_id": "M-1001"},
      {"id": "P2002", "planType": "Provider", "status": "Active", "member_id": "M-2002"},
      {"id": "P3001", "planType": "Dental", "status": "Active", "member_id": "M-3003"},
      {"id": "P3002", "planType": "Accident", "status": "Active", "member_id": "M-3003"},
      {"id": "P3003", "planType": "Short Term", "status": "Lapsed", "member_id": "M-3003"},
      {"id": "P4004", "planType": "Dental", "status": "Active", "member_id": "M-4004"},
  ]

  mid = member_id or context.state.get("member_id")
  pols = [p for p in all_policies if p["member_id"] == mid]

  default_policy = None
  if pols:
      default_policy = min([p["id"] for p in pols])

  context.state["policies"] = pols
  context.state["multi_policy"] = len(pols) > 1
  context.state["default_policy"] = default_policy
  print("lookup_policies member=" + str(mid) + " count=" + str(len(pols)))

  return {"member_id": mid,
          "policies": pols,
          "multi_policy": len(pols) > 1,
          "default_policy": default_policy}
