---
name: backlog-planning
description: Use this skill to assess a backlog, compare candidate work, and prepare a prioritized plan or reviewable backlog delta.
---

# Backlog Planning

Use this skill when the work is to clarify, sequence, select, or reprioritize
backlog items. First read the consumer's project contract and inspect the
current records that the decision depends on. State which candidates were
considered and distinguish observed constraints from judgment.

Apply the consumer's ranking fields, option values, hierarchy, and eligibility
rules as written. Do not introduce a priority scale, queue convention,
initiative type, or definition of “next” from another repository. If the
consumer has no rule for a material choice, return that choice for review
instead of presenting a guessed ranking as deterministic.

For a coordinated plan across GitHub issues or project fields, use
`gh-steward` to compose and validate the proposed delta. Present the expected
effects and any tradeoffs before applying it. For ordinary reads or a simple
single-issue update, use the existing connector or native `gh` under repository
policy. Keep preview and apply distinct, and verify live changes afterward.

See the [decision rubric](../_shared/references/agent-decision-rubric.md) for
consumer policy and authorization boundaries.
