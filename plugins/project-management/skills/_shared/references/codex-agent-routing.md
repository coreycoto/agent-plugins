# Codex agent routing

Project Management owns planning, governance and delivery workflows. Product
Development owns reusable execution roles. When both plugins are available,
use these roles with the current skill and a task-specific assignment rather
than authoring another model-pinned agent for each skill. Neither installation
nor a skill reference authorizes delegation or publication.

| Previous helper | Current skill | Bounded delegation when authorized |
| --- | --- | --- |
| `dependency_patcher` | `delivery-lifecycle` | `pd_implementer` for an accepted dependency change; `pd_transformer` only for a fully specified mechanical update. |
| `docs_taxonomist` | `project-governance` | `pd_explorer` to map drift; `pd_implementer` for accepted documentation edits. Return taxonomy decisions to the parent. |
| `governance_auditor` | `project-governance` | `pd_reviewer` for policy-versus-evidence findings. The parent owns coordinated GitHub plans and applies. |
| `merge_gatekeeper` | `delivery-lifecycle` | `pd_reviewer` for exact-candidate review and merge readiness. The parent owns authorized merges. |
| `release_publisher` | `publish-change` | `pd_reviewer` for release evidence, or `pd_implementer` for bounded local preparation. The parent owns publication. |

The assigned task must name its objective, owned files or read-only scope,
applicable skills, validation, and delivery stage. Do not grant a helper a
credential, provider operation, or publication capability by choosing a role.
Return unresolved policy and authorization decisions to the parent. Use
gh-steward for composed GitHub plans and the existing connector or native gh
for ordinary actions under repository policy.

If Product Development or its custom roles are unavailable, perform the
authorized workflow in the parent. Do not silently install a dependency or
fall back to an unrestricted agent. Inspect the current spawn selector and
actual permissions; the role's sandbox default does not override the parent's
live permission profile.

Keep consumer policy, permission profiles, required local skills and trusted
CI snapshots in the repository. CI/cloud tasks do not inherit a developer's
shared installation. Until native discovery is verified, commit generated,
revision-pinned role projections from the same authored source, and update
workflow role references and projections together.
