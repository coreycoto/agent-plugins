---
name: relationship-management
description: Inspect and repair or propose work-item relationships when dependencies, hierarchy, or ownership affect delivery.
---

# Relationship Management

Read the consumer's relationship and hierarchy policy, then inspect current
records and relevant neighboring items. Distinguish observed relationships
from proposed edges. Explain how each change affects sequencing, ownership or
completion conditions.

Use established relationship types and direction. Do not assume every tracker
has epics, parent issues or the same blocking semantics. Call out cycles,
orphaned work, ambiguous parents, duplicated scope and contradictory records.
Confirm a dependency represents a real prerequisite rather than merely similar
topics. Distinguish hierarchy for scope from dependencies for execution order.

For substantial work, propose a coherent graph of dependency-ready vertical
slices with observable results and explicit prerequisites. Preserve technical
ownership and the consumer's taxonomy; do not create new record types or
reorganize unrelated work to suit a preferred workflow. Keep unsupported
relationships and policy choices open for the decision owner.

Return affected items, current and proposed relationships, rationale and any
completion or ordering impact. Include removals as well as additions so a
reviewer can assess the complete graph.

Use `gh-steward` to compose and validate coordinated GitHub deltas. Ordinary
single-record work may use the existing connector or native `gh` under
repository policy. Recheck the affected graph before an authorized apply and
verify the resulting relationships afterward. Keep failed or partial updates
explicit; do not claim a graph is reconciled from a successful request alone.
Preserve existing authorization through routine continuation within scope.

Complete with a supported relationship proposal or verified authorized graph
and remaining ambiguities. Follow the
[decision rubric](../_shared/references/agent-decision-rubric.md).
