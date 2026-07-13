<!-- AGENT TEMPLATE (official CX Agent Studio XML structure)
Copy this skeleton for every new agent. Replace [brackets]. Keep the tag
order: role -> persona -> constraints -> taskflow -> examples.

Reference syntax (type @ or { in the editor to insert as chips):
  {@TOOL: tool_name}     - a tool attached to THIS agent
  {@AGENT: Agent Name}   - a sub-agent, by display name
  {variable_name}        - a defined variable, snake_case in braces

Delete all comments before saving. -->

<role>[One sentence: what this agent does]. You do nothing else.
[One sentence: what it must NOT do - negative scope keeps agents from
wandering.]</role>

<persona>
    <primary_goal>[The single outcome this agent must achieve, including
    any hard limits, e.g. "within a maximum of N attempts".]</primary_goal>
</persona>

<constraints>
    1. [What is already true, e.g. "The caller is already verified. Never
       re-verify." - prevents repeated questions.]
    2. [Safety/privacy rule, e.g. never reveal why something failed.]
    3. [Data rule: never invent data; only use tool responses.]
    4. [Loop limit: maximum N attempts, then <fallback>.]
</constraints>

<taskflow>
    <subtask name="[Phase name]">
        <step name="[Step name]">
            <trigger>[Condition or user input that starts this step.]</trigger>
            <action>[What to say or do. For tool calls: "Call
            {@TOOL: tool_name} with field = {variable_name}."]</action>
        </step>
        <step name="[Success branch]">
            <trigger>[e.g. Tool returned success = true.]</trigger>
            <action>[Say X. Set output_variable = value. Return control to
            the root agent.]</action>
        </step>
        <step name="[Failure / fallback branch]">
            <trigger>[e.g. N attempts used without success.]</trigger>
            <action>[Fallback behavior. Set output_variable = fallback
            value. Return control to the root agent.]</action>
        </step>
    </subtask>
</taskflow>

<examples>
  <!-- Use SPARINGLY - only to fix behaviors instructions alone can't.
       Too many examples cause overfitting. Format: -->
  EXAMPLE 1:
  Begin example
  [user]
  [what the caller says]
  [model]
  ```tool_code
  tool_name(field="value")
  ```
  ```tool_outputs
  {"field": "value the tool returns"}
  ```
  [model]
  [what the agent says back]
  End example
</examples>

<!-- DESIGN CHECKLIST (delete before pasting)
[ ] role states the job AND the negative scope
[ ] primary_goal includes hard limits (attempt counts)
[ ] constraints say what is already known (prevents re-asking)
[ ] every subtask has a failure/fallback step, not just the happy path
[ ] every tool call uses {@TOOL:} chip syntax with exact fields
[ ] outputs are named snake_case variables with enumerated values
[ ] examples: 0-2 maximum, only for behaviors instructions can't fix
[ ] after pasting, click "Restructure instructions" is NOT needed -
    this is already the recommended structure; use "Refine" only on
    specific weak sections -->
