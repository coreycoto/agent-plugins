# Conditional review lenses

Select only concerns the candidate introduces or materially changes. Read the
relevant section and investigate concrete triggers. Existing consumer standards
and accepted behavior govern findings; this guide supplies questions, not a
mandatory all-task audit or preferred architecture.

## Security and privacy

For changed trust boundaries, trace input to authorization and effect. Check
identity/tenant scope, permission checks, parsing and escaping, sensitive output
and credential handling. Distinguish authentication from authorization. Test a
specific unauthorized or malformed case without accessing new credentials or
performing live attack actions. A dependency name alone is not a vulnerability.

## Data and durability

For storage or state changes, inspect uniqueness, identity, transactions,
partial completion, concurrent writers, retries and recovery. Verify the actual
producer and consumer envelopes. Retain original failed receipts; fast retries
or successful requests do not establish final state. Check migration compatibility
and rollback limits when persisted data changes.

## API and compatibility

Inspect callers, wire format, status/errors, defaults, ordering and version
coexistence. Type signatures can stay stable while behavior changes. Check
external or generated clients and discovery paths where relevant. Confirm the
contract from accepted policy or independent evidence rather than the candidate
alone.

## Performance and resources

Check realistic work size, repeated I/O, unbounded collections, contention,
resource lifetime and end-to-end contribution. Support performance claims with
comparable measurements rather than inferring speed from code shape. Treat
configuration differences and fast errors as potential measurement confounds.

## Lifecycle and concurrency

Trace ownership, cancellation, teardown, stale responses and state transitions.
Use a scenario that makes the proposed race possible; theoretical interleavings
without a reachable trigger remain hypotheses. Include failure and interruption
when a durable workflow or shared state changes.

Retained findings explain trigger, consequence, location and resolving evidence.
A stylistic preference or unsupported broad possibility is not a defect.
