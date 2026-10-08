# Project Workflow Decision Rubric

Use the consumer repository's instructions, configuration, and current records
as the authority for project decisions. Do not supply defaults for:

- project identity, fields, or field options
- ranking, hierarchy, or relationship rules
- labels, milestones, or status vocabulary
- responsible actors or delivery stages

Separate observed facts from assumptions. If a decision depends on missing
consumer policy or product intent, present the gap and ask before choosing a
policy. Keep proposed changes small, explain their rationale, and make the
affected records clear.

## Delivery authority

Resolve the requested endpoint from the task and existing authorization. Continue
routine repairs, relevant checks and read-only diagnosis within that scope.
Do not create another approval gate merely because a workflow changes phase.

Before an uncovered promotion, prepare the concrete candidate and identify the
actions, repositories or recipients, environments, exact artifacts and any
attempt limit. One user decision can cover several ready steps when each is
explicitly included and consumer policy permits it. Keep their review records
and provider receipts distinct. A plan that does not yet exist, a future artifact
or an excluded stage cannot inherit exact-candidate approval.

Request a new decision for changed scope, a violated candidate restriction,
consumed one-shot authority or an uncovered consequential action. Reconcile
failed or ambiguous writes before proposing another attempt. If a client rejects
an authorized action, report its stated reason and use its supported approval
path; skill instructions cannot override the denial.

## GitHub Work

Use the `gh-steward` plugin when a request requires composing or validating a
coordinated GitHub plan across issues, project fields, relationships, labels,
milestones, or governance rules. The Project Management plugin provides the
workflow guidance; `gh-steward` owns the executable composition, validation,
and receipt contract. If that plugin is unavailable, limit work to research or
a reviewable proposal until the required capability is available.

For ordinary GitHub CRUD on a single issue or pull request, use the consumer's
existing GitHub connector or native `gh` CLI according to repository policy.
This plugin does not configure a connector, install an app, add an MCP server,
or establish authentication.

## Preview And Apply

Keep planning separate from applying. Before a coordinated change, show the
target, current state, proposed delta, rationale, and material impact. Apply
only when the user has requested that live change and the consumer's current
policy permits it. Recheck relevant state before acting and verify the result
afterward. A preview, plan, or tool suggestion is not approval.
