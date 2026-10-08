---
name: delivery-lifecycle
description: Carry selected work from its task source through implementation, verification, review, and the user's requested delivery endpoint.
---

# Delivery Lifecycle

Use this skill for a selected work item whose completion spans implementation
and delivery. Start from the current issue, accepted local plan, or other work
source allowed by the consumer. Read its acceptance conditions, repository
contracts, exact checkout and existing edits. Establish the requested endpoint:
local result, reviewable candidate, merged source, release, or verified live
behavior. Keep these states distinguishable in evidence and tracking.

Make the work dependency-ready before execution. Identify prerequisites and
split substantial work into small vertical slices that demonstrate an observable
result through the relevant layers. Give each slice an acceptance example,
validation, dependencies and technical owner. Preserve consumer taxonomy;
a slice is not automatically a new issue or project commitment.

Technical implementation belongs to the available Product Development workflow
or the parent following repository guidance. For authorized delegation, assign
bounded scope, owned files and a success condition. Use
`pm_dependency_maintainer` for accepted dependency maintenance and
`pm_merge_reviewer` for review of an exact candidate; consult the
[agent routing guide](../_shared/references/codex-agent-routing.md).

For an opted-in task with available `codex_workflow_*` tools, keep its source,
delivery stage, status and scoped candidate inputs current. Record a governance
mismatch only with concrete evidence from the consumer's rules and records.
Read a nominated installed skill before optionally assigning its owned role;
record assignment and completion separately with candidate-bound evidence.
Paused, blocked, completed and approval-waiting records suppress automatic
continuation. A record or nomination cannot grant authority or override the
latest user instructions.

Use native Git worktree isolation when required by the consumer or concurrent
work. Inspect the starting ref and existing edits; reuse a suitable checkout
when possible. Preserve unrelated work. Creating isolation does not authorize
later cleanup or deleting branches.

Continue ordinary repairs, relevant checks and review responses within the
existing scope and authorized stage. A CI failure or comment is evidence to
assess, not permission for unrelated changes. Reproduce material failures and
fix causes attributable to this work; report unrelated failures or decisions.
Read the [delivery evidence guide](references/delivery-evidence.md) when hosted
checks, merge, release or live verification are part of the requested endpoint.

Use `gh-steward` for composed project updates and the existing GitHub connector
or native `gh` for ordinary operations under consumer policy. Verify each
result before updating completion state. Retain authorization across routine
continuation; request a decision only for an uncovered action or changed scope.

Finish with the achieved endpoint, exact candidate, evidence, remaining gates
and next action. Use `handoff-work` if execution pauses or transfers. Follow the
[decision rubric](../_shared/references/agent-decision-rubric.md).
