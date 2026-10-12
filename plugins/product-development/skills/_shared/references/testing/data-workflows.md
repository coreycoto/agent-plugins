# Data and distributed-workflow verification

This is an explicit modern adaptation of the feedback, observation, preservation
and delivery principles in the [source map](sources.md), not a claim that the
books specify a cloud platform's recovery protocol. Read current consumer and
provider contracts before choosing assertions. Do not import a generic retry
policy into a system with stricter uncertain-outcome rules.

## Define the operation and its authority

Identify the logical input, source revision, transform/configuration versions,
owner/attempt, durable state, artifact identity and publication condition. Trace
the actual serialized handoff through producer and consumer. Separate acceptance,
execution, progress, completion and publication; one status is not proof of all.
Name which system is authoritative for each fact and how a reader verifies it.

Distinguish raw observations from normalized facts, inferred/enriched values and
serving projections. Preserve relevant provenance. A schema-valid value can still
be semantically wrong. A digest confirms equality to an expected digest only;
when both are generated from the same untrusted replacement, internal consistency
does not establish authority.

## Choose failure windows, not just final statuses

| Boundary | Cases to consider | Evidence to inspect |
| --- | --- | --- |
| Admission/dispatch | Rejection, accepted-but-ack-lost, concurrent duplicate | Durable intent/claim and actual external effect count |
| Progress/checkpoint | Before commit, after commit before ack, stale or changed replay | Committed progress and identity-bound receipt |
| Artifact handoff | Truncated bytes, wrong scope/version, missing partition, conflicting write | Trusted manifest, actual readback and consumer acceptance |
| Completion | Duplicate, out-of-order or wrong-owner callback | Monotonic terminal state and unchanged forbidden effects |
| Recovery | Fresh process, stale lease/owner, partial scratch loss | Durable reconstruction and the claimed resume boundary |
| Publication/cleanup | Incomplete proof, late completion, referenced data removal | Visibility gate and preservation of required evidence |

Select relevant cases; do not manufacture a cross-product of every status for
every function. Use real producer/consumer code for envelope compatibility and
native tests for provider semantics. Fakes can deterministically inject failures
but must not bypass the boundary being claimed.

## Verify result semantics and resource behavior

Use independently derived examples for joins, deduplication, normalization and
aggregation. Include missing versus zero, conflicting revisions, tie-breaking,
time zones, invalid geometry or encodings only where the operation needs them.
Conservation checks require an explicit accounting model for rejected, retained,
duplicated and transformed records; a matching row count alone can hide swaps.

Property or metamorphic tests can vary partition size, order and interruption.
First justify the relation: not every operation is commutative, floating-point
aggregation may need a justified tolerance, and historical reference data may
change a replay. Pin reference/model outputs when exact replay requires them.
Retain a reproducible seed, minimized failing input and meaningful diagnostics.
Passing generated examples does not prove every possible input.

Compare interrupted/resumed execution with uninterrupted execution at the
accepted semantic boundary. Extra audit records may be valid; duplicated business
effects may not. Verify completed work is reused as required, not merely that the
final output looks right after full reprocessing.

Resource tests preserve the real threshold and workload characteristic: payload
size, compressed expansion, range length, buffering or concurrency. A reduced
fixture that no longer crosses the original limit cannot replace that regression.
Separate instrumentation overhead from production constraints and report the
actual measured boundary.

## Model outputs and external enrichment

When a pipeline uses a model, define task-level quality examples separately from
shape/transport validation. Record relevant input, prompt/model/tool configuration,
output, validation decisions and accepted nondeterminism. An LLM judge is not an
independent truth source merely because it is another model invocation. Keep
trusted labels or reference checks and assess judge errors where it is used.
These evaluation methods are adaptations, not techniques attributed to the books.

Finish with the operation's safety and progress obligations, tested windows,
source/artifact identity, recovery scope and remaining hosted/semantic gaps.
Tests do not authorize replay of ambiguous external mutations or data publication.
