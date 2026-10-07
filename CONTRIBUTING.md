# Contributing

Use Python 3.13+, uv and Node.js for catalog author checks:

```sh
uv sync --locked --group dev
uv run --locked python scripts/validate_agent_plugins.py
uv run --locked python scripts/build_codex_package.py
uv run --locked python scripts/build_codex_package.py --check
uv run --locked python scripts/verify_skill_dependencies.py
uv run --locked ruff check adapters scripts tests evals/owned-workflows plugins/product-development/skills/maintain-verification/scripts
uv run --locked pytest
```

Edit the shared runtime in `adapters/codex_agents/` and each plugin's authored
roles, skills and manifests in `plugins/<name>/`. The builder creates complete
portable and Codex marketplaces plus npm archives in ignored
`dist/plugin-packages/`. It never writes runtime copies or distributions into
plugin source. CI verifies the builds and retains candidate artifacts.
Codex 0.160.0's compatibility manifest is confined to the built Codex artifact.
For local testing, add `dist/plugin-packages/codex` with the native marketplace
command; the Git catalog uses exact npm versions after an authorized release.
Public registry publication is a separate promotion gate, including account/scope
ownership and package-version availability. Build and test never publish packages.

Use the [installation diagnostic and local trial recipe](docs/owned-workflows.md#read-only-installation-diagnostic)
to compare explicit candidate/cache and discovery roots without installing or
changing client configuration. Run it with `python -B`; file matches and native
inventory alone do not prove active-session discovery or reload.

With Codex installed, run `uv run --locked python scripts/smoke_codex_agents.py`
for an optional native check. It uses temporary homes and repositories, tests
hook discovery and rich-form decline/accept/upgrade in both scopes, and makes
zero inference requests. It does not qualify desktop rendering or live role
selection; those remain separate checks after reviewed consumer activation.

`uv run --locked python scripts/smoke_npm_plugin.py --archive <built-npm-tgz>`
qualifies Codex's native npm materialization and role setup in both scopes using
an isolated local registry fixture. It does not test registry access or change
the actual user's configuration. Real `npm pack --ignore-scripts` is also tested
for hidden manifest and complete asset preservation. See
[the native source contract](https://developers.openai.com/plugins/build/plugins#marketplace-metadata).

For committed CI/cloud role projections, use the offline
`scripts/render_codex_agents.py` author helper from the exact clean source pin.
It reads project overlays, preserves shared model routing, and supports legacy
role aliases without duplicating authored role definitions. Render into an empty
review directory; `--check` verifies already committed outputs. See
[agent adoption](plugins/product-development/com.openai/agents/ADOPTION.md).

These checks validate portable manifests, skill frontmatter, package containment
local reference integrity, source lineage and optional legacy dependency locks. Python helpers live in `scripts/author_checks`
and are used only by authors; they are not an installable workflow SDK or CLI.

Current packages have no upstream runtime skill dependencies. The smoke command
is offline by default. For an explicitly selected historical package that still
declares a lock, `--restore` opts into Skills CLI 1.7.0 network restoration and
compares source revisions, paths and content hashes:

```sh
uv run --locked python scripts/smoke_skill_dependencies.py --restore
```

Keep packaged source lineage pins and notices intact. Preserve independent plugin selection and
portable client boundaries. Put GitHub execution contracts and their tests in
gh-steward, and keep consumer policy out of this catalog. A release requires a
clean reviewed revision, matching package versions and fresh acquisition proof.
