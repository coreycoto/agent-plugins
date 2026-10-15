# Make repeated work and decisive checks rerunnable

Use when a repeated transformation or diagnostic step, or a consequential
comparison, earns a reusable command. Prefer an existing tool or saved query.
A couple of clear edits may be cheaper to perform and check directly; a
nontrivial task does not automatically require a new script or framework.

For a mechanical sweep, inspect a representative unit and its legitimate
exception before automating. Define the transformation and do-not-touch scope.
Run a codemod or script on isolated examples and compare its result with the
accepted manual result, including unchanged and already-converted inputs.
Check rerun behavior and interruption where they matter. Inventory unmatched
or ambiguous cases; return semantic choices instead of guessing a rewrite.

For diagnosis, preserve the query or command that distinguishes the hypotheses,
with inputs, units and observation window. A script should expose missing data
and errors rather than silently turn them into zero. For verification, compare
against an independent expected value; automating a circular check adds no proof.

Use deterministic tools for work with an explicit recipe before considering
agents to repeat it by hand. Keep judgment with the responsible engineer. When
delegation is authorized and useful, provide the accepted recipe, owned files,
exceptions and check through the existing role contract; a tool does not expand
the write boundary or grant access to external systems.

Keep a script or query when a reviewer or later run needs to replay it, using the
consumer's convention. Otherwise retain the exact command and useful result in
the task evidence; do not add a permanent artifact merely to cite a principle.
Keep credentials, raw private traces and operational configuration out of public
source. This [pstack adaptation](sources.md) concerns the work at hand;
[recurrence prevention](../recurrence-prevention.md) owns durable guards for
demonstrated recurring mistakes.
