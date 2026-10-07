---
name: product-requirements
description: Translate a supported product direction into observable outcomes, user-centered requirements, and dependency-aware learning or delivery slices.
---

# Product Requirements

Establish the chosen direction, users, rationale, constraints and unresolved
product decisions. Use `product-discovery` or `product-prioritization` when the
problem or choice is unsettled. A useful provisional draft can expose gaps
without pretending the decision is accepted.

Before requirements turn a contested idea into a delivery commitment, read
[decision pressure-testing](../_shared/references/decision-pressure-testing.md).
Keep requirements provisional where a consequential assumption remains open.

Use the domain's existing terminology consistently. Inspect factual inputs and
current behavior before questioning the user. Ask only where a product choice
changes intended behavior or scope; technical ownership and ordinary drafting
choices do not become mandatory questionnaires.

Define outcomes as user or business change, separately from shipped features.
For each measure, identify what is measured, for whom, its source, time window
and relevant guardrails. Use a baseline or target only when supplied or
supported. Otherwise label it unknown and describe how to establish it. Intent
to improve a metric is not evidence that an idea will do so.

Write requirements around concrete user situations and observable behavior,
including meaningful failure or edge cases. Preserve needs separately from
proposed solutions. State scope, non-goals, constraints, dependencies and open
questions. Acceptance examples should distinguish satisfactory behavior without
prescribing an unchosen technical implementation.

Sequence small slices that each deliver an observable outcome or test a
consequential assumption. State dependency and learning gates. A roadmap can
express relative order and confidence; use dates, staffing and delivery promises
only when supported. Technical owners assess feasibility and implementation;
Project Management owns authorized execution and tracker representation.
Use `product-experiments` when observation is needed before commitment.

Return a product brief containing the decision and evidence limits, users and
measures, requirements and acceptance examples, scope and unresolved choices,
and sequencing rationale. Completion means a technical owner can evaluate the
behavior and dependencies while the decision owner can see what remains open.
The draft does not authorize publishing a roadmap, changing a tracker,
contacting customers or operating providers.
