# Change impact and compatibility

Use this for shared contracts, stateful behavior, persistence or a broad change.
Bound the affected surface rather than enumerating hypothetical risks.

Trace public callers and exports, then follow what symbol search misses:
serialized envelopes, generated clients, configuration, discovery inventories,
commands, feature flags, background jobs, stored data and another language's
consumer. Inspect exact library versions or local patches when semantics depend
on them. Identify a representative input, altered output or state and downstream
consequence for each material change.

For failures, inspect ordering and ownership: who starts work, commits state,
retries, cancels or cleans resources? Consider interruption and partial completion
when the change actually introduces those conditions. Distinguish safe retries
from ambiguous external operations whose prior result must be inspected.

For a migration, state old and new contracts, concurrent version compatibility,
reader/writer sequence, identity preservation, data transformation and rollback
limits. Move or adapt actual callers before retiring their old contract. A
compatibility shim should have a reason and observable retirement condition;
a source refactor does not authorize running a data migration.

Find the assumption on which safety depends. Support it with the real code and,
where practical, an executable case that would fail if it were false. For
example, preserving a parser signature is insufficient when a downstream
consumer depends on the error envelope or stable ordering. Source reasoning,
contract tests and live observation support different strengths of claim.

Return affected contracts and callers, verified safety assumptions, intentional
changes, unknown consumers and focused validation. Do not claim an absent search
match proves there is no dynamic or external caller.
