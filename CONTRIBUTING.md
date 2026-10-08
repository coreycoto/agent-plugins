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
GitHub Packages publication is a separate promotion gate, including repository
permissions, package-version availability and observed package visibility. Build and test never publish packages.

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

## GitHub Packages release

GitHub Packages (`https://npm.pkg.github.com`) is the sole package registry.
The `npm` source type and archive format do not imply an npmjs.org account or
publication. The builder rejects every other publishing destination.

After exact-source main CI succeeds, explicitly dispatch `Publish Agent Plugins` with
the full reviewed main SHA and new coordinated version. The workflow qualifies
committed inputs and reproducible archives before a separate job receives
`packages: write`. It publishes each package once using `GITHUB_TOKEN`, then
preserves publication, metadata and fresh acquisition receipts. Do not rerun a
failed publication or dispatch the same version again: inspect each package's
actual registry state and retained receipts before a separately reviewed recovery.

Inspect each package's actual repository association and visibility; do not infer
visibility from repository access or the publish command. If a public plugin was
created as private, use its GitHub package settings to make it public. This visibility change is irreversible. Keep
Agent Development private in its separate publisher. A successful publish or
acquisition alone does not qualify public visibility.

GitHub requires authenticated registry reads even for public packages. Native
Codex uses the npm client's registry configuration. For local acquisition, use
an existing GitHub credential authorized for package reads through a private,
registry-scoped temporary npm configuration or the user's existing credential
setup. Never print tokens, put credentials in marketplace URLs or source files,
or request an npmjs.org login. Actions consumers use `GITHUB_TOKEN` when their
repository has package access. See GitHub's
[registry authentication documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-npm-registry).

Retain the exact source SHA, package version, archive digest, observed visibility,
repository association and fresh download verification in the release receipt.
Verify native materialization and fresh-session discovery separately from
publication; a running desktop chat still requires a supported reload.

The reviewed 0.9.1 qualification failure in run `37705082572` has one bounded
recovery path: a fresh dispatch may name that exact run only after the workflow
verifies its failed CI lookup, skipped build and never-started publication job.
It also requires unchanged package inputs from that run's source. Any additional
same-version dispatch or attempted publication restores the normal hold. This
exception cannot authorize retries of an upload or ambiguous publication.
