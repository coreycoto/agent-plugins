---
name: relationship-management
description: Use this skill to inspect and propose changes to dependency, parent-child, or other relationships in a consumer's work system.
---

# Relationship Management

Use this skill when work depends on how items relate to one another. Read the
consumer's relationship and hierarchy policy first, then inspect the relevant
records and their surrounding context. Represent observed relationships
separately from proposed ones, and explain how each proposed edge or hierarchy
change affects sequencing, ownership, or completion.

Do not assume that every tracker uses epics, initiatives, parent issues, or a
particular dependency direction. Use only relationship types and constraints
that the consumer has established. Call out cycles, orphaned work, ambiguous
parents, or conflicting records without resolving them by inventing a rule.

When composing changes across multiple GitHub issues or project records, use
`gh-steward` to prepare and validate the delta. Review the affected relationships
before any apply. Use the existing connector or native `gh` for ordinary
single-record CRUD under repository policy. Verify the resulting graph after an
authorized update.

See the [decision rubric](../_shared/references/agent-decision-rubric.md) for
consumer policy and authorization boundaries.
