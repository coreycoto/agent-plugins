# Project Management

Portable guidance for planning work, reviewing project state, and carrying
changes through delivery. The skills use the consumer repository's own rules
for project identity, fields and options, ranking, hierarchy, labels, actors, and
delivery stages.

## Skills

| Skill | Use it to |
| --- | --- |
| `intake` | Turn research or planning material into a decision brief and backlog proposal. |
| `backlog-planning` | Assess, select, sequence, or reprioritize work. |
| `relationship-management` | Review dependencies and parent-child or other item relationships. |
| `quarter-planning` | Prepare time-bound commitments using consumer conventions. |
| `review-closeout` | Assess review findings, blockers, and follow-up. |
| `publish-change` | Prepare a reviewed change for the repository's delivery or release process. |
| `delivery-lifecycle` | Carry selected work through verified delivery stages. |
| `project-governance` | Compare project practices and records with documented consumer rules. |

## GitHub work

Use the `gh-steward` plugin when a task needs a composed plan across GitHub
issues, project fields, relationships, labels, milestones, or governance rules.
That plugin owns executable composition and validation. For ordinary reads or
updates to a single issue or pull request, use the consumer's existing GitHub
connector or native `gh` CLI according to repository policy. This plugin does
not bundle or configure a connector, app, MCP server, hook, or authentication.

## Shared execution agents

When Product Development is installed and delegation is authorized, use its
purpose-specific agents with these skills. The [routing guide](skills/_shared/references/codex-agent-routing.md)
maps dependency, documentation, governance, merge and release helpers to the
current skill names. Reuse the role and provide a bounded task contract; keep
project policy, permission profiles, hosted CI trust and publication authority
with the consumer. This is optional integration, not automatic installation.

## Skill name migration

The focused skills replace the earlier, narrower names. Update consumer
references using this mapping:

| Previous skill | Current skill |
| --- | --- |
| `dependency-remediation` | `delivery-lifecycle` |
| `docs-taxonomy` | `project-governance` |
| `ensure-quarter-milestones` | `quarter-planning` |
| `github-backlog-mutate` | `backlog-planning` |
| `implement-reconciled-item` | `delivery-lifecycle` |
| `intake` | `intake` |
| `intake-and-implement` | `intake` |
| `intake-preview` | `intake` |
| `label-palette-design` | `project-governance` |
| `merge-on-green` | `delivery-lifecycle` |
| `next-item` | `backlog-planning` |
| `plan-quarter-apply` | `quarter-planning` |
| `plan-quarter-preview` | `quarter-planning` |
| `plan-to-backlog-preview` | `backlog-planning` |
| `publish-change` | `publish-change` |
| `rebalance-backlog-apply` | `backlog-planning` |
| `rebalance-backlog-preview` | `backlog-planning` |
| `reconcile-relationships-apply` | `relationship-management` |
| `reconcile-relationships-preview` | `relationship-management` |
| `release-publish` | `publish-change` |
| `research-issue` | `intake` |
| `review-closeout-audit-apply` | `review-closeout` |
| `review-closeout-audit-preview` | `review-closeout` |
| `review-to-backlog-apply` | `review-closeout` |
| `review-to-backlog-preview` | `review-closeout` |
| `work-issue` | `delivery-lifecycle` |
