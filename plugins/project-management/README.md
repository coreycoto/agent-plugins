# Project Management

Independently maintained procedures for planning work, reviewing project state,
and carrying changes through the requested delivery endpoint. Workflows run
from the packaged instructions without invoking upstream skills. Consumer
repositories own project identity, fields and options, ranking, hierarchy,
labels, actors and delivery stages.

## Skills

| Skill | Use it to |
| --- | --- |
| `intake` | Turn research or planning material into a decision brief and backlog proposal. |
| `backlog-planning` | Assess, select, sequence, or reprioritize work. |
| `relationship-management` | Review dependencies and parent-child or other item relationships. |
| `quarter-planning` | Prepare time-bound commitments using consumer conventions. |
| `review-closeout` | Assess review findings, blockers, and follow-up. |
| `publish-change` | Prepare a reviewed change for the repository's delivery or release process. |
| `delivery-lifecycle` | Carry selected work through dependency-ready slices and verified delivery stages. |
| `handoff-work` | Pause, transfer or resume work with checkout, evidence and authorization preserved. |
| `project-governance` | Compare project practices and records with documented consumer rules. |

## Working through delivery

Start with `intake` for unclear source material or `backlog-planning` for a
selection decision. Carry accepted work through `delivery-lifecycle`, giving
technical ownership to Product Development or the parent under repository
guidance. Use `review-closeout` to assess the requested endpoint and
`publish-change` for an authorized publication step. Routine checks and repairs
preserve existing authorization; changing scope or promotion stage needs its
own task authority.

A local result, reviewable candidate, merged source, published artifact and
verified live behavior have different evidence. `handoff-work` makes incomplete
work resumable with exact state and a next action. Durable solution capture is
selective: `review-closeout` can use available
`product-development:capture-solution` when retention is requested. Neither
closeout nor handoff requires a memory, skill or tracker write.

## GitHub work

Use the `gh-steward` plugin when a task needs a composed plan across GitHub
issues, project fields, relationships, labels, milestones, or governance rules.
That plugin owns executable composition and validation. For ordinary reads or
updates to a single issue or pull request, use the consumer's existing GitHub
connector or native `gh` CLI according to repository policy. This plugin does
not bundle or configure a GitHub connector, app, or authentication. Its local
Codex MCP server manages only its own agent installation.

## Codex agents

Project Management owns five specialized agents; it does not depend on
Product Development's agents. Use **Setup** or
`$project-management:manage-codex-agents`, review its three native hook handlers,
and install the agents in shared-user or trusted project scope through the
native consent form. Restart Codex after changed role files, then inspect the
current spawn selector and native selection receipts. Installation alone does
not reload an active chat. Cloud discovery remains unverified.

| Agent | Model / effort | Task |
| --- | --- | --- |
| `pm_dependency_maintainer` | GPT-6.1 Sol / high | Accepted manifest and lockfile changes with compatibility evidence |
| `pm_documentation_steward` | GPT-6 Luna / high | Accepted taxonomy, documentation and link maintenance |
| `pm_governance_auditor` | GPT-6.1 Sol / high | Read-only policy and record audit |
| `pm_merge_reviewer` | GPT-6.1 Sol / high | Read-only exact-candidate merge readiness |
| `pm_release_preparer` | GPT-6.1 Sol / high | Assigned local release preparation and artifact evidence |

The parent owns policy decisions, GitHub writes, merges and publication.
Write roles edit only assigned local files. All roles inherit live chat
permissions; their sandbox defaults grant no authority. See the
[routing guide](skills/_shared/references/codex-agent-routing.md) for skill
assignments and legacy helper migration, and the
[pinned projection guide](com.openai/agents/ADOPTION.md) for CI/cloud consumers.

Its authored extension lives in `com.openai/`. Complete portable and Codex
distributions are built into ignored `dist/plugin-packages/`; no runtime copies
or distribution trees are committed. The catalog pins an exact npm package,
with publication and acquisition qualified separately. Codex 0.160 uses the
built compatibility package because that version skips portable hooks.
The same authored installer in `adapters/codex_agents/` is generated into each
bundle; its ownership marker, target directory and private upgrade state are
specific to this plugin. Native forms recheck the exact plan, preserve local
conflicts and unrelated configuration, reject downgrades and keep private
backups. Decline, cancellation and unavailable forms leave roles unchanged.

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
