# Bounded maintainability assessment

Use only for a requested architecture or maintainability assessment. Agree the
subsystem, question and relevant evidence window; a broad invitation to inspect
code is not permission to repair every finding. Existing project policy and
product priorities govern the recommendation.

Map the selected user behavior to responsibilities, public callers, shared
invariants, data ownership and dependency direction. Identify where changes must
cross boundaries or repeat a rule. Inspect relevant tests, incidents, current
solution notes and focused history when they explain actual maintenance friction.
Churn, file size, a health score or an unfamiliar abstraction is a lead, not proof
of a structural defect. Distinguish accidental coupling from required product,
compatibility, generated-code or framework constraints.

For material friction, retain a concrete example: the change or failure, affected
callers, the rule that was hard to preserve, its current owner and practical
consequence. Compare alternatives that concentrate the rule at its owning
boundary, a local repair, and leaving the structure unchanged. Consider migration
cost, caller burden, preserved behavior, verification and the consumer's existing
work; do not invent effort estimates or universal architecture rules. A clear
local implementation can be the best outcome.

Finish with the bounded responsibility map, supported friction, options and
recommendation, unresolved semantic decisions and the smallest useful next scope.
Keep hypotheses separate from findings. Route an accepted technical change to
[design-change](../../design-change/SKILL.md), or an accepted substantial structural
change to [phased-refactor](../../phased-refactor/SKILL.md). Carry the agreed caller
contracts and validation with that handoff. Assessment alone does not edit source,
create tracker work, change priorities or grant implementation authority.
