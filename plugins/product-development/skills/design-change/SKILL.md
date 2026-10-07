---
name: design-change
description: Resolve technical options, interfaces, impact, migration, and validation for a requested change before implementation commitments.
---

# Design Change

Establish accepted behavior, constraints, consumer architecture rules and open
technical decisions. Inspect current contracts and relevant callers. Ask only
about product or architecture choices not answered by available evidence.
Use [understand-codebase](../understand-codebase/SKILL.md) for a missing path;
do not repeat an explanation already supported by the task.

Choose design depth proportional to coupling and uncertainty. A local routine
change may need only an explicit decision. For a consequential boundary,
compare materially different approaches, including retaining the current
structure where useful. Evaluate caller complexity, locality of rules,
observability, failure modes, compatibility and implementation cost supported
by evidence. Avoid speculative abstractions that merely relocate complexity.

Describe interface behavior beyond signatures: identity, state, ordering,
errors, configuration and resource ownership. Use
[model-domain](../model-domain/SKILL.md) when ambiguous vocabulary or invalid
states drive the design. Read the
[impact guide](../_shared/references/change-impact.md) for cross-component,
serialization, persistence or migration changes.

Identify the assumption on which safety depends and how to check it. If a
small experiment can settle a key uncertainty, use
[prototype-decision](../prototype-decision/SKILL.md). A prototype result does
not establish rollout readiness.

For demonstrated recurring corrections or fragile invariants, use the
[prevention guide](../_shared/references/recurrence-prevention.md) to compare a
structural, type, API, lint or behavioral guard with a local repair. Qualify the
known mistake and legitimate near miss; do not invent a new architecture rule.

Produce the smallest coherent design: chosen approach and rationale, rejected
alternatives, contracts and affected consumers, compatibility or migration,
dependency-ready slices and validation. Mark unresolved choices instead of
inventing estimates or acceptance policy.

For authorized difficult architecture escalation, use `pd_architecture_adviser`
with the competing options and decisive question. Routine design remains in the
parent; role selection does not change authority.

Complete when an implementer can act on accepted intent and a reviewer can
assess tradeoffs and success conditions. Continue already authorized implementation
through [implement-change](../implement-change/SKILL.md); a design artifact does
not independently authorize data migration, deployment or access changes.
