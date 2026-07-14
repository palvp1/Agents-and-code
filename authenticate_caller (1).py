from typing import Optional, Dict, Any 

 

 

def authenticate_caller(phone: Optional[str] = None, 

                        dob: Optional[str] = None, 

                        member_id: Optional[str] = None, 

                        zip_code: Optional[str] = None) -> Dict[str, Any]: 

  """ 

  Verifies the caller's identity against the member system. Call this whenever 

  the caller has provided credentials to verify. 

 

  Primary path: phone + dob. Alternate path: phone + member_id + zip_code 

  (the alternate path also works when the phone is unknown to the system). 

 

  A hard limit of 3 verification attempts is enforced per conversation. 

  Interpret the response as follows: 

  - authenticated true: the caller is verified. 

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

    A dictionary with authenticated, reason, attempts_used, attempts_remaining, 

    attempts_exhausted, and on success caller_type, member_id, name, 

    policy_number, policies and multi_policy. 

  """ 

  from datetime import datetime 

 

  personas = { 

      "5551110001": {"dob": "1980-01-01", "member_id": "M-1001", "zip": "33601", 

                     "name": "Alice Test", "caller_type": "member", 

                     "policies": [{"id": "P1001", "planType": "Short Term", "status": "Active"}]}, 

      "5551110002": {"dob": "1975-05-05", "member_id": "M-2002", "zip": "33602", 

                     "name": "Bob Provider", "caller_type": "provider", 

                     "policies": [{"id": "P2002", "planType": "Provider", "status": "Active"}]}, 

      "5551110003": {"dob": "1990-09-09", "member_id": "M-3003", "zip": "33603", 

                     "name": "Carol MultiPolicy", "caller_type": "member", 

                     "policies": [{"id": "P3001", "planType": "Dental", "status": "Active"}, 

                                  {"id": "P3002", "planType": "Accident", "status": "Active"}, 

                                  {"id": "P3003", "planType": "Short Term", "status": "Lapsed"}]}, 

      "5551110004": {"dob": "1965-12-12", "member_id": "M-4004", "zip": "33604", 

                     "name": "Dan AltAuth", "caller_type": "member", 

                     "policies": [{"id": "P4004", "planType": "Dental", "status": "Active"}]}, 

  } 

  max_attempts = 3 

 

  # ---- 1. Hard attempt limit, enforced in code ------------------------------- 

  used = int(context.state.get("auth_attempts", 0)) 

  if used >= max_attempts: 

      context.state["auth_status"] = "unauthenticated_transfer" 

      return {"authenticated": False, "reason": "attempts_exhausted", 

              "attempts_used": used, "attempts_remaining": 0, 

              "attempts_exhausted": True} 

 

  # ---- 2. Validate and normalize inputs (no regex, plain Python only) --------- 

  n_phone = None 

  if phone: 

      digits = "".join([ch for ch in phone if ch.isdigit()]) 

      if len(digits) == 11 and digits.startswith("1"): 

          digits = digits[1:] 

      if len(digits) != 10: 

          return {"authenticated": False, "reason": "invalid_input", 

                  "invalid_field": "phone", "attempts_used": used, 

                  "attempts_remaining": max_attempts - used, 

                  "attempts_exhausted": False} 

      n_phone = digits 

 

  n_dob = None 

  if dob: 

      formats = ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%d %B %Y", "%B %d %Y", "%B %d, %Y"] 

      for fmt in formats: 

          try: 

              parsed = datetime.strptime(dob.strip(), fmt) 

              if 1900 <= parsed.year <= datetime.now().year: 

                  n_dob = parsed.strftime("%Y-%m-%d") 

              break 

          except ValueError: 

              continue 

      if not n_dob: 

          return {"authenticated": False, "reason": "invalid_input", 

                  "invalid_field": "dob", "attempts_used": used, 

                  "attempts_remaining": max_attempts - used, 

                  "attempts_exhausted": False} 

 

  n_member_id = None 

  if member_id: 

      cleaned = member_id.strip().upper().replace(" ", "-") 

      if cleaned.isdigit(): 

          cleaned = "M-" + cleaned 

      tail = cleaned[2:] 

      valid = cleaned.startswith("M-") and len(tail) == 4 and tail.isdigit() 

      if not valid: 

          return {"authenticated": False, "reason": "invalid_input", 

                  "invalid_field": "member_id", "attempts_used": used, 

                  "attempts_remaining": max_attempts - used, 

                  "attempts_exhausted": False} 

      n_member_id = cleaned 

 

  n_zip = None 

  if zip_code: 

      z = "".join([ch for ch in zip_code if ch.isdigit()])[:5] 

      if len(z) == 5: 

          n_zip = z 

 

  # ---- 3. Real credential check: count the attempt ------------------------------ 

  used += 1 

  context.state["auth_attempts"] = used 

  print("authenticate_caller attempt " + str(used) + " of " + str(max_attempts)) 

 

  # ---- 4. Credential logic ------------------------------------------------------- 

  match = None 

  persona = personas.get(n_phone) if n_phone else None 

  if persona: 

      if n_dob and n_dob == persona["dob"]: 

          match = persona 

      elif n_member_id == persona["member_id"] and n_zip == persona["zip"]: 

          match = persona 

  else: 

      for p in personas.values(): 

          if n_member_id and n_member_id == p["member_id"] and n_zip == p["zip"]: 

              match = p 

              break 

 

  if match: 

      pols = match["policies"] 

      context.state["auth_status"] = "success" 

      context.state["caller_type"] = match["caller_type"] 

      context.state["member_id"] = match["member_id"] 

      context.state["policy_number"] = pols[0]["id"] if pols else None 

      context.state["policies"] = pols 

      context.state["multi_policy"] = len(pols) > 1 

      print("authenticate_caller verified " + match["member_id"]) 

      return {"authenticated": True, 

              "caller_type": match["caller_type"], 

              "member_id": match["member_id"], 

              "name": match["name"], 

              "policy_number": pols[0]["id"] if pols else None, 

              "policies": pols, 

              "multi_policy": len(pols) > 1, 

              "attempts_used": used, 

              "attempts_remaining": max_attempts - used, 

              "attempts_exhausted": False} 

 

  exhausted = used >= max_attempts 

  if exhausted: 

      context.state["auth_status"] = "unauthenticated_transfer" 

  reason = "no_match" if not persona else "credentials_mismatch" 

  return {"authenticated": False, 

          "reason": reason, 

          "attempts_used": used, 

          "attempts_remaining": max_attempts - used, 

          "attempts_exhausted": exhausted} 