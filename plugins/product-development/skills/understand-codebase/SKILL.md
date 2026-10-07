---
name: understand-codebase
description: Explain a bounded code path, component, or architectural decision from current source and relevant history without changing product behavior.
---

# Understand Codebase

Identify the question and bound the path or component to explain. Read consumer
guidance, relevant domain terms and supplied artifacts. Inspect entry points,
public contracts and callers before expanding into implementation details.
Search relevant existing solution records when a prior decision could explain
the shape; use the [retrieval guide](../_shared/references/project-knowledge.md).

Trace a representative input through control flow, state or data changes,
external boundaries and observable result. Include the conditions that alter
behavior: configuration, identity, failure, ordering or serialization as
applicable. Follow real references rather than inferring callers from names.
Use the [impact guide](../_shared/references/change-impact.md) when the question
crosses packages, storage or API boundaries.

For “why,” distinguish current mechanics from documented rationale. Read
relevant decisions or focused Git history; cite evidence for intentional
tradeoffs. History can explain when a change occurred but does not prove its
author's motive. If no rationale survives, label a plausible explanation as
inference. Source behavior may conflict with accepted product policy.

Explain in the reader's domain vocabulary, with a concrete example and current
file references. A small diagram can clarify relationships or lifecycle when
prose would obscure them. Identify unknown runtime or provider facts instead
of substituting liveness for product behavior.

For authorized exploration delegation, use `pd_explorer` with a focused question
and read-only scope. The explanation remains useful without delegation.

Complete with how the path works, the evidence for any design rationale,
important failure or boundary conditions, and unanswered questions. Exploration
does not imply a refactor, configuration change or provider access. Route to
[design-change](../design-change/SKILL.md) only when a technical change is requested.
