---
name: backlog-planning
description: Compare, select, sequence, or reprioritize existing work using the consumer's backlog policy and current evidence.
---

# Backlog Planning

Read the consumer's project contract and current candidate records. Establish
the decision being made: next eligible work, sequencing, scope reduction or a
broader reprioritization. State which candidates and period were considered.

Apply established ranking fields, hierarchy and eligibility rules. Do not import
a priority scale, queue convention or definition of “next.” Where policy leaves
a material choice open, describe the tradeoff for the decision owner. A
qualitative recommendation can remain conditional when evidence is incomplete.

Compare outcome, dependency readiness, effort evidence, risk and capacity only
as relevant to that decision. Keep estimates and assumptions distinguishable
from verified constraints. Identify cycles, blocked prerequisites and work that
cannot meet its acceptance conditions. Small vertical slices can expose progress
and learning sooner; preserve their technical owner's feasibility decisions.
Do not create tracker records solely to fit a preferred decomposition.

Return a reviewable plan showing selected and deferred work, rationale,
dependency order, open decisions and expected effects on affected records.
Selecting an item does not authorize implementation or a project update; when
that work is already authorized, continue through `delivery-lifecycle`.

Use `gh-steward` to compose and validate coordinated GitHub deltas. For ordinary
reads or a single-record update, use the existing connector or native `gh`
under repository policy. Recheck relevant live state before an authorized
apply, then verify ranking and relationships afterward. Planning and applying
have separate evidence; already granted authorization need not be requested
again for an unchanged delta and scope.

Follow the [decision rubric](../_shared/references/agent-decision-rubric.md).
Complete with a supported ordering or an explicit unresolved decision, not a
fabricated deterministic score.
