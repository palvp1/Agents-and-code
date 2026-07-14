from typing import Dict, Any


def set_caller_language(language: str) -> Dict[str, Any]:
  """
  Records the language the caller is speaking. Call this ONLY when the caller
  speaks a language other than English, normally Spanish.

  Spanish-speaking callers are transferred rather than handled by this bot, so
  after calling this you should hand off immediately.

  Args:
    language: The detected language in lowercase, for example "spanish".

  Returns:
    A dictionary with caller_language and transfer_required (true when the
    caller must be transferred rather than served by this bot).
  """
  supported = ["spanish", "english"]

  lang = (language or "").strip().lower()
  if lang not in supported:
      lang = "english"

  transfer_required = lang != "english"

  context.state["caller_language"] = lang
  print("set_caller_language language=" + lang + " transfer=" + str(transfer_required))

  return {"caller_language": lang, "transfer_required": transfer_required}
