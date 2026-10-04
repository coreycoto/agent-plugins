---
name: delivery-lifecycle
description: Use this skill to carry selected work from planning through implementation, verification, review, and delivery-state handoff.
---

# Delivery Lifecycle

Use this skill when a task spans work selection, implementation, review, and
completion tracking. Confirm the requested scope and use the consumer's rules
for choosing work, representing ownership, and defining delivery stages. Keep
the work item's state aligned with verified progress; do not mark work complete
because code was written or a pull request was opened.

Follow the repository's implementation and verification guidance. Before
changing a stage or linked record, identify the target and expected effect. For
coordinated GitHub project or issue updates, use `gh-steward` to compose and
validate the change. Use the available connector or native `gh` for ordinary
pull-request and issue operations under consumer policy.

Keep code delivery, hosted review, and project-state handoff as distinct gates.
After each authorized action, verify the resulting state and report blockers
with the smallest next step. Do not merge or apply project changes unless the
user has requested that step and current policy permits it.

See the [decision rubric](../_shared/references/agent-decision-rubric.md) for
consumer policy and authorization boundaries.
