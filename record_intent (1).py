from typing import Optional, Dict, Any


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
    notes: Optional short sentence of the caller's own words, including any
      second topic they mentioned.

  Returns:
    A dictionary with the recorded captured_intent, intent_confidence and
    intent_notes.
  """
  allowed = ["premium_payments", "claim_status", "eligibility",
             "benefits_prescriptions", "network_preauth", "id_cards",
             "new_policy", "policy_updates", "other"]

  clean_intent = (intent or "").strip().lower()
  clean_confidence = (confidence or "high").strip().lower()

  if clean_intent not in allowed:
      print("record_intent unknown intent '" + clean_intent + "' -> other")
      clean_intent = "other"
      clean_confidence = "low"

  if clean_confidence not in ("high", "low"):
      clean_confidence = "low"

  clean_notes = (notes or "").strip()[:200]

  context.state["captured_intent"] = clean_intent
  context.state["intent_confidence"] = clean_confidence
  context.state["intent_notes"] = clean_notes
  print("record_intent intent=" + clean_intent + " confidence=" + clean_confidence)

  return {"captured_intent": clean_intent,
          "intent_confidence": clean_confidence,
          "intent_notes": clean_notes}
