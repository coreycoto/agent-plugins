---
name: project-governance
description: Use this skill to review a project's working rules and identify evidence-backed governance drift or decisions for the consumer to resolve.
---

# Project Governance

Use this skill to assess whether the consumer's project practices and records
agree with its own documented rules. Read the current policy and inspect only
the records relevant to the requested review. Describe the rule, observed state,
and evidence for each material gap.

The consumer owns project identity, field definitions and options, ranking,
hierarchy, label vocabulary, actors, and delivery stages. Compare the live or
checked-in state with those consumer-owned choices; do not introduce new
defaults or treat a convention from another repository as policy. When the
policy is missing or inconsistent, report the decision needed rather than
normalizing state by assumption.

Use `gh-steward` to compose and validate coordinated GitHub governance changes
across project fields, labels, relationships, or multiple records. An ordinary
read or single-record update may use the consumer's existing connector or
native `gh`, following repository policy. Show a reviewable delta before an
authorized apply and verify the resulting state afterward.

See the [decision rubric](../_shared/references/agent-decision-rubric.md) for
consumer policy and authorization boundaries.
