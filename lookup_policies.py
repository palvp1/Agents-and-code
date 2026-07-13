# TOOL NAME: lookup_policies             (used by: policy_selection_agent)
# Paste as a Python code tool named exactly lookup_policies.

from typing import Optional, Dict, Any

# Mock policy data (POC only - replace with ces_requests call later)
POLICIES = [
    {"id": "P1001", "planType": "Short Term", "status": "Active",  "memberId": "M-1001"},
    {"id": "P2002", "planType": "Provider",   "status": "Active",  "memberId": "M-2002"},
    {"id": "P3001", "planType": "Dental",     "status": "Active",  "memberId": "M-3003"},
    {"id": "P3002", "planType": "Accident",   "status": "Active",  "memberId": "M-3003"},
    {"id": "P3003", "planType": "Short Term", "status": "Lapsed",  "memberId": "M-3003"},
    {"id": "P4004", "planType": "Dental",     "status": "Active",  "memberId": "M-4004"},
]


def lookup_policies(member_id: Optional[str] = None) -> Dict[str, Any]:
  """
  Retrieves all policies for the verified member so you can ask which policy
  the call is about. Call this when the caller has more than one policy and
  the policy list is not yet known.

  If member_id is not provided, the verified member from this conversation
  is used automatically.

  Returns:
    A dictionary with policies (list of id, planType, status), multi_policy
    (true if more than one), and default_policy (the lowest policy id - use
    it when the caller does not choose).
  """
  mid = member_id or context.state.get("member_id")
  pols = [p for p in POLICIES if p["memberId"] == mid]
  default = min((p["id"] for p in pols), default=None)

  context.state["policies"] = pols
  context.state["multi_policy"] = len(pols) > 1
  context.state["default_policy"] = default
  print(f"[lookup_policies] member={mid} count={len(pols)} default={default}")

  return {"member_id": mid, "policies": pols,
          "multi_policy": len(pols) > 1, "default_policy": default}
