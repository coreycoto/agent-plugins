# Independent behavioral evidence

Choose a public seam that observes the intended contract: exported operation,
request, command, storage interface or user flow. “Public” is relative to the
component being specified; not every behavior requires a browser test. State
what the chosen seam catches and what it leaves unexercised. A concurrency bug
may need multiple callers; a pipeline bug may need the actual envelope chain.

Derive expected behavior independently. A worked example from accepted rules,
known-good fixture or invariant can disagree with the implementation. Calling
the same production transformation to produce expected values cannot catch its
mistake. Full-output snapshots need meaningful review and should not freeze
incidental details. Coverage indicates execution, not correctness of the oracle.

For a regression, observe the original symptom before repair. Ensure a failing
assertion proves behavior rather than setup, import or unavailable dependency.
Then observe the fix and rerun the original broader scenario. A minimized test
can miss the interaction that first caused the failure.

Use fixtures and boundary fakes that retain the contract being examined. Control
clock, random seed or filesystem where these obscure the result. Keep provider
accounts out of deterministic tests; mark synthetic coverage separately from
real upstream observation. Do not mock internal calls simply to assert their
sequence unless that sequence is itself an accepted public contract.

When pruning or consolidating, retain independently specified cases and failure
messages. Demonstrate sensitivity using the old bug, representative bad cases or
a bounded mutation in isolated scratch when meaningful. Do not alter the shared
candidate during another validation run. An arbitrary percentage reduction or
coverage target does not justify removing useful regression evidence.
