# Python Code Tools for CX Agent Studio (paste-in, no Cloud Run needed)

These are inline Python code tools per the official docs
(docs.cloud.google.com/gemini-enterprise-cx/cx-agent-studio/tool/python).
All state lives in the runtime's `context.state`, so the attempt counter is
enforced in code, per conversation, with ZERO external infrastructure.

Tested locally with a fake runtime context: **19/19 scenarios pass**
(`python test_tools.py`).

## Tool -> Agent mapping

| Tool (file)            | Function / tool name  | Attach to agent        | What it does |
|------------------------|-----------------------|------------------------|--------------|
| authenticate_caller.py | `authenticate_caller` | authentication_agent   | Validation + normalization, credential check, HARD 3-attempt limit in `context.state`, writes auth_status / caller_type / member_id / policy_number / multi_policy |
| lookup_policies.py     | `lookup_policies`     | policy_selection_agent | Fetches policies (member_id auto-read from state), writes policies / default_policy |
| select_policy.py       | `select_policy`       | policy_selection_agent | Records the chosen policy; deterministic default-to-lowest-ID |
| record_intent.py       | `record_intent`       | intent_capture_agent   | Validates intent against the 9 allowed ids, writes captured_intent / confidence / notes |
| decide_routing.py      | `decide_routing`      | handoff_agent          | Applies the routing matrix in code, no args (reads state), writes destination / handoff_summary |

root_agent: still no tools.

## How to create each tool in the console

1. Add tool -> Python code tool.
2. Tool name = the function name EXACTLY (snake_case), e.g. `authenticate_caller`.
3. Paste the file contents (delete the top comment lines starting with `# TOOL NAME`).
4. Attach the tool to its agent only (least privilege).

The docstrings ARE the tool description the model reads - they were written
as prompting (when to call, how to interpret results). Don't trim them.

## Required instruction edits (agents-v2 files)

The tool names changed to snake_case and sessionId is no longer needed
(the runtime's own session state does the counting). Update:

1. **authentication_agent**: `{@TOOL: authenticateCaller}` -> `{@TOOL: authenticate_caller}`.
   REMOVE all mentions of sessionId / {session_id} (constraint 3 and the
   taskflow actions) - the tool needs no session argument. Argument names
   are now snake_case: phone, dob, member_id, zip_code. Update the two
   few-shot examples accordingly.
2. **policy_selection_agent**: `{@TOOL: lookupPolicies}` -> `{@TOOL: lookup_policies}`.
   ADD: after the caller answers (or fails to answer twice), call
   `{@TOOL: select_policy}` with the caller's choice, or with no argument
   for the default. (Models cannot set state directly - selection must go
   through this tool.)
3. **intent_capture_agent**: ADD a final step - after classifying, call
   `{@TOOL: record_intent}` with intent, confidence, and notes. Attach the
   tool to this agent.
4. **handoff_agent**: `{@TOOL: decideRouting}` -> `{@TOOL: decide_routing}`,
   and remove the argument list from the action - the tool takes no
   arguments (it reads everything from state).
5. Re-insert every changed chip by typing `@` in the editor so it resolves.

## Why this beats the Cloud Run version for the POC

- No deploy, no gcloud, no corporate-network issues: paste and test.
- Attempt counting is per-conversation automatically (context.state is
  session-scoped) - no in-memory-dict caveat, no /reset tool needed. Each
  new simulator conversation starts clean.
- print() output appears in the console's tracing details - live debugging
  during the demo.

## Migration path to the real IDP later

Only the data blocks change: replace the PERSONAS / POLICIES dicts with a
`ces_requests.post(...)` call to the real API (the runtime provides
ces_requests for external HTTP). Function signatures, docstrings, state
writes, and agent instructions all stay identical.
