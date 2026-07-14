<subtask name="Policy Requests">

    <step name="Policy Related Request">

        <trigger>

        The caller asks to:

        • choose a policy
        • switch policies
        • identify which policy to use
        • says they have multiple policies
        • refers to "my policy" but no policy has been selected

        </trigger>

        <action>

        Transfer control to the Policy Selection Agent.

        Wait until the Policy Selection Agent completes.

        Continue orchestration.

        </action>

    </step>

</subtask>