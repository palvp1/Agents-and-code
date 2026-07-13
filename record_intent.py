# TOOL NAME: record_intent               (used by: intent_capture_agent)
# Paste as a Python code tool named exactly record_intent.

from typing import Optional, Dict, Any

ALLOWED_INTENTS = {
    "premium_payments", "claim_status", "eligibility",
    "benefits_prescriptions", "network_preauth", "id_cards",
    "new_policy", "policy_updates", "other",
}


def record_intent(intent: str,
                  confidence: str = "high",
                  notes: Optional[str] = None) -> Dict[str, Any]:
  """
  Records the classified reason for the caller's call. Call this exactly once,
  after you have classified the caller's request into one intent.

  The intent MUST be one of: premium_payments, claim_status, eligibility,
  benefits_prescriptions, network_preauth, id_cards, new_policy,
  policy_updates, other. Anything else is stored as "other" with low
  confidence.

  Args:
    intent: One intent id from the allowed list.
    confidence: "high" when the classification was clear, "low" when you
      defaulted or guessed after unclear answers.
    notes: Optional single short sentence of the caller's own words,
      including any second topic they mentioned.

  Returns:
    A dictionary with the recorded captured_intent, intent_confidence and
    intent_notes.
  """
  intent = (intent or "").strip().lower()
  confidence = (confidence or "high").strip().lower()

  if intent not in ALLOWED_INTENTS:
      print(f"[record_intent] '{intent}' not in allowed list -> other/low")
      intent = "other"
      confidence = "low"
  if confidence not in ("high", "low"):
      confidence = "low"

  context.state["captured_intent"] = intent
  context.state["intent_confidence"] = confidence
  context.state["intent_notes"] = (notes or "").strip()[:200]
  print(f"[record_intent] intent={intent} confidence={confidence}")

  return {"captured_intent": intent, "intent_confidence": confidence,
          "intent_notes": context.state["intent_notes"]}
