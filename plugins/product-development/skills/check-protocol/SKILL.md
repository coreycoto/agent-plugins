---
name: check-protocol
description: Check a stateful coordination protocol with an executable model of competing actors, interruption, and recovery; report bounded safety evidence, progress assumptions, and counterexamples.
---

# Check Protocol

Use for a consequential ordering or recovery question, not ordinary value
validation. `model-domain` clarifies meanings; this procedure explores permitted
executions; `test-behavior` checks implementation. Read the requested contract,
actual callers and persistence boundaries. Preserve the task's delivery scope.

Name actors, identities, durable and volatile state, initial conditions and
external observations. Separate acceptance from completion and unknown outcomes
from known failure. Identify which events can be delayed, duplicated, reordered
or lost. State storage atomicity, clock and crash assumptions; do not assume
exactly-once delivery or cancellation from a timeout.

Specify safety invariants and any requested progress properties separately.
Make invalid states, terminal states and enabled actions explicit. For eventual
progress, record environmental and fairness assumptions rather than assume
cooperative scheduling. Use the [modeling guide](references/modeling.md) for
state-space limits, vacuity, temporal checking and implementation correspondence.

Build the smallest faithful executable model using existing consumer tools.
A finite state explorer can suffice; TLA+ is optional, not a required framework.
Keep production code unchanged unless repair is assigned. Retain model source,
checker version, configuration, enabled properties and exploration bounds.
Model atomic actions no larger than the actual indivisible boundary.

Execute the selected checks and verify that interesting states and competing
paths are reachable. Separate exhaustive exploration of a finite model from a
depth-limited search, random simulation or incomplete run. Confirm a meaningful
bad transition violates the intended property in isolated scratch; a syntax
error or dead model is not a successful sensitivity check. Preserve the unchanged
candidate while another check reads it.

For a counterexample, replay the event sequence, explain the violated contract,
and map it to real operations. When authorized, retain a regression through
[test-behavior](../test-behavior/SKILL.md). Do not weaken an invariant merely to
make the model pass. For a clean run, identify remaining unmodeled behavior.

Complete with the question, model/configuration identity, actual command and
result, enabled properties, reached-state evidence, assumptions, bounds,
sensitivity result and implementation mapping. State progress as unverified
when the checker or assumptions do not establish it. A passing model is not
proof of production correctness; unavailable tools leave an unexecuted model,
not a verification claim. No provider fault injection or rollout follows.
