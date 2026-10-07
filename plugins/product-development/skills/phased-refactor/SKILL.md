---
name: phased-refactor
description: Refactor a substantial code or test cluster in evidence-backed phases while preserving caller contracts, behavioral confidence, and relevant runtime outputs.
---

# Phased Refactor

Turn a selected structural problem into a bounded refactor. Repository-health
reports identify candidates; actual source, caller and behavior evidence decide
whether to change them. Read consumer ownership, permissions and delivery rules.
Use [design-change](../design-change/SKILL.md) when technical choices remain open.

Record the checkout, branch, baseline revision, existing edits and relevant tool
versions. Give selected findings a disposition: implement, consolidate, defer,
accept or reject with reason. Inspect generated files, migrations and framework
conventions before treating repetition as waste. Agree behavior to preserve,
intentional changes, scope, validation and requested endpoint; quotas are not
universal requirements.

Map exports, callers, data envelopes, generated outputs and discovery or release
inventories. Read the [impact guide](../_shared/references/change-impact.md) when
contracts cross components or persistence. Run a relevant fixed baseline and
retain failures separately from regressions. Comparison artifacts belong in
consumer-approved evidence storage, not raw public source.

Sequence coherent phases around real responsibilities. Separate mechanical
movement from semantic change where useful, preserving interfaces and runtime
outputs. Move actual consumers before retiring legacy contracts. Give authorized
workers independent owned files and success conditions; preserve concurrent
work. Do not change shared candidate state while a harness reads it.

Organize validation around behavior. Use
[test-behavior](../test-behavior/SKILL.md) for independent oracles and meaningful
regression cases. Factor repeated setup only when failures remain specific and
helpers cannot bypass the contract. Inventory coverage targets independently
of coverage output; missing or malformed evidence is not a pass. Show retained
tests catch a removed case's regression before calling it redundant.

At each checkpoint, compare unchanged contracts to the fixed baseline and run
affected tests plus required broader checks. Add failure, interruption and
recovery evidence for stateful changes. Measure suite or runtime cost only under
comparable conditions; use the
[benchmarking guide](../_shared/references/benchmarking.md) for performance claims.
Fix attributable regressions while retaining environment limitations.

Review a substantial final candidate through
[review-code](../review-code/SKILL.md) when needed. Stop repeating passed broad
checks without a new change or uncertainty. Complete only the authorized
endpoint; a refactor grants no provider or promotion authority.

Finish with scope and revisions, intentional behavior changes, caller and parity
evidence, retained test confidence, measured results and remaining failures.
Rerun selected health analysis only when useful; advisory scores do not override
verified behavior. Use available `project-management:handoff-work` for continuation.
