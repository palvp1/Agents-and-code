from typing import Dict, Any


def decide_routing() -> Dict[str, Any]:
  """
  Decides the routing destination for this call and produces the handoff
  summary. Call this exactly once when the bot portion of the call is ending.

  No arguments are needed. The decision uses the verified context already
  stored in this conversation: authentication status, caller type, captured
  intent, policy, and language. The routing matrix is applied deterministically
  in code.

  Returns:
    A dictionary with destination (the skill id to transfer to) and
    handoff_summary (the context line for logs - never speak it aloud).
  """
  auth_status = context.state.get("auth_status")
  caller_type = context.state.get("caller_type")
  intent = context.state.get("captured_intent")
  language = context.state.get("caller_language")

  # Routing matrix - first match wins, top-down.
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

  policy = context.state.get("selected_policy") or context.state.get("policy_number")

  summary = ("HANDOFF: destination=" + str(destination)
             + " | auth_status=" + str(auth_status)
             + " | caller_type=" + str(caller_type)
             + " | member_id=" + str(context.state.get("member_id"))
             + " | policy=" + str(policy)
             + " | intent=" + str(intent)
             + " | confidence=" + str(context.state.get("intent_confidence")))

  context.state["destination"] = destination
  context.state["handoff_summary"] = summary
  print(summary)

  return {"destination": destination, "handoff_summary": summary}
