# Adopt shared Codex agents

Use the plugin's Setup action for local shared-user or project installation.
That path requires the supported native form and produces owned, ignored files;
it does not replace a consumer's tracked role definitions.

For CI/cloud configuration, keep one authored role source in this plugin and
commit generated projections alongside a small project overlay. Local global
installation does not establish discovery in hosted runs. The author helper
`scripts/render_codex_agents.py` is an offline renderer/checker, not a runtime
installer or a substitute for native form consent.

## Choose a role and preserve the task contract

| Existing purpose | Shared source |
| --- | --- |
| Exploration/scouting | `pd_explorer` |
| Correctness, behavior or contract review | `pd_reviewer` |
| Accepted implementation | `pd_implementer` |
| Root-cause investigation | `pd_diagnostician` |
| Deterministic mechanical edits | `pd_transformer` |
| Difficult architecture escalation | `pd_architecture_adviser` |

Use the owning workflow's current skills. Project Management maintains the
[maintenance routing](https://github.com/coreycoto/agent-plugins/tree/main/plugins/project-management#shared-execution-agents) in its own package; consumers
must not retain obsolete skill names merely to preserve an old helper label.
For consumers still pinned to a qualified legacy workflow runtime, preserve
that working runtime and its valid skill references until its own migration
is qualified. Adopting role projections does not replace an executable runtime
or install the current Project Management plugin into a hosted job.
Aliases can keep existing native role IDs stable while their authored source
and models change. An optional `file` preserves an existing TOML basename when
it differs from the role ID; paths and duplicate filenames are rejected.
Product-specific instructions, required local skills,
permission profiles, experiment constraints, and release/operational gates
remain with the consumer. Organization-owned contracts keep their own adoption
path; do not create a competing public policy catalog.

## Pin, render, and review

Put an overlay in the consumer's `.codex/agent-plugin-project.json`, with the
actual reviewed publisher commit as `sourceRevision`. For example:

```json
{
  "schemaVersion": 1,
  "sourceRevision": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "roles": {
    "dependency_patcher": {
      "sourceRole": "pd_implementer",
      "appendInstructions": "Use $project-management:delivery-lifecycle for the accepted dependency change."
    },
    "pr-review-guard": {
      "sourceRole": "pd_reviewer",
      "appendInstructions": "Return findings to the parent; do not run project checks or edit files."
    }
  }
}
```

Run from the clean publisher checkout at that exact commit:

```sh
uv run --locked python scripts/render_codex_agents.py \
  --project /path/to/consumer/.codex/agent-plugin-project.json \
  --output /path/to/empty-review-directory
```

Review the generated diff before replacing the corresponding tracked role
files and committing the `.agent-plugin-projection.json` receipt. The renderer
refuses to overwrite a nonempty destination. It never edits config registrations,
trust, permission definitions, or user configuration. Change the overlay and
regenerate instead of hand-editing generated model pins or instructions.

To preserve a named permission profile, set `default_permissions` on that role.
For a read-only source role, declare the profile in `readOnlyProfiles` too.
Alternatively, a write-capable source role can be tightened with
`"sandbox_mode": "read-only"`. These declarations express project intent;
they do not create profiles, grant authority, or prove an enforced child sandbox.
Models and effort remain controlled by the pinned shared source.

Verify committed projections in CI from the same publisher revision:

```sh
uv run --locked python scripts/render_codex_agents.py \
  --project /path/to/consumer/.codex/agent-plugin-project.json \
  --output /path/to/consumer/.codex/agents --check
```

Keep permission/config registrations, prompt role references and overlays
consistent. Preserve trusted-base snapshots before checking out untrusted PR
code. A source pin or generated receipt is provenance, not authorization.
Native role selection, effective runtime permissions, and hosted discovery
remain separate checks. Remove obsolete aliases only in a reviewed consumer
change that updates all callers together.
