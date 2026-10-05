# Project Management Skills

The eight skills provide portable project-planning and delivery guidance.
Consumer repositories own project identity, fields and options, ranking,
hierarchy, labels, actors, and delivery stages; the skills read and follow those
rules rather than imposing a shared project configuration.

For GitHub composition across multiple records or project state, use the
`gh-steward` plugin. Ordinary issue or pull-request CRUD may use the consumer's
existing connector or native `gh` under its policy. Skill metadata does not
require a GitHub connector.

<!-- BEGIN CANONICAL RUNTIME CLASSIFICATIONS -->
| Skill | Runtime classification |
| --- | --- |
| `backlog-planning` | `github_optional` |
| `delivery-lifecycle` | `github_optional` |
| `intake` | `local_first` |
| `project-governance` | `github_optional` |
| `publish-change` | `github_optional` |
| `quarter-planning` | `github_optional` |
| `relationship-management` | `github_optional` |
| `review-closeout` | `github_optional` |
<!-- END CANONICAL RUNTIME CLASSIFICATIONS -->

`local_first` means the default workflow can produce useful work without a live
GitHub interaction. `github_optional` means local analysis or preview is useful
on its own, while live GitHub state may be needed for the requested outcome.
Neither classification selects a connector or authorizes a write.
