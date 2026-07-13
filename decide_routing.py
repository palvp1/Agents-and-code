# TOOL NAME: decide_routing              (used by: handoff_agent)
# Paste as a Python code tool named exactly decide_routing.

from typing import Dict, Any


def decide_routing() -> Dict[str, Any]:
  """
  Decides the routing destination for this call and produces the handoff
  summary. Call this exactly once when the bot portion of the call is ending.

  No arguments are needed - the decision uses the verified context already
  stored in this conversation (auth status, caller type, captured intent,
  policy). The routing matrix is applied deterministically in code.

  Returns:
    A dictionary with destination (the skill id to transfer to) and
    handoff_summary (the context line for logs - never speak it aloud).
  """
  s = context.state
  auth_status = s.get("auth_status")
  caller_type = s.get("caller_type")
  intent = s.get("captured_intent")
  language = s.get("caller_language")

  # Routing matrix - first match wins, top-down (BRD order).
  if language == "spanish":
      destination = "cxone_spanish_ivr"
  elif caller_type == "provider":
      destination = "provider_screener_skill"
  elif auth_status == "unauthenticated_transfer":
      destination = "member_screener_skill"
  elif intent == "new_policy":
      destination = "sales_skill"
  elif intent in ("premium_payments", "id_cards"):
      destination = "ivr_self_service"
  elif intent == "claim_status":
      destination = "claims_skill"
  elif intent in ("eligibility", "benefits_prescriptions", "network_preauth"):
      destination = "benefits_skill"
  elif intent == "policy_updates":
      destination = "policy_service_skill"
  else:
      destination = "member_screener_skill"

  policy = s.get("selected_policy") or s.get("policy_number")
  summary = (f"HANDOFF: destination={destination}"
             f" | authStatus={auth_status}"
             f" | callerType={caller_type}"
             f" | memberId={s.get('member_id')}"
             f" | policy={policy}"
             f" | intent={intent}"
             f" | confidence={s.get('intent_confidence')}"
             f" | session={context.session_id}")

  s["destination"] = destination
  s["handoff_summary"] = summary
  print(f"[decide_routing] {summary}")

  return {"destination": destination, "handoff_summary": summary}
