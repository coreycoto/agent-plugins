# Contributing

Use Python 3.13+, uv and Node.js for catalog author checks:

```sh
uv sync --locked --group dev
uv run --locked python scripts/validate_agent_plugins.py
uv run --locked python scripts/build_codex_package.py --check
uv run --locked python scripts/verify_skill_dependencies.py
uv run --locked ruff check scripts tests plugins/product-development/com.openai/codex_agents
uv run --locked pytest
```

Product Development's Codex install package is generated beneath its `com.openai/`
extension. Edit only the authored portable package, then run
`uv run --locked python scripts/build_codex_package.py`. Codex 0.160.0 skips
portable-package hooks, so the Codex catalog selects the generated compatibility
layout. Its bytes must match the source before publication. Other clients can
acquire the portable package directly at `plugins/product-development`.

With Codex installed, run `uv run --locked python scripts/smoke_codex_agents.py`
for an optional native check. It uses temporary homes and repositories, tests
hook discovery and rich-form decline/accept/upgrade in both scopes, and makes
zero inference requests. It does not qualify desktop rendering or live role
selection; those remain separate checks after reviewed consumer activation.

For committed CI/cloud role projections, use the offline
`scripts/render_codex_agents.py` author helper from the exact clean source pin.
It reads project overlays, preserves shared model routing, and supports legacy
role aliases without duplicating authored role definitions. Render into an empty
review directory; `--check` verifies already committed outputs. See
[agent adoption](plugins/product-development/com.openai/agents/ADOPTION.md).

These checks validate portable manifests, skill frontmatter, package containment
and native Vercel dependency locks. Python helpers live in `scripts/author_checks`
and are used only by authors; they are not an installable workflow SDK or CLI.

The network-dependent restore check uses isolated consumer projects and Skills
CLI 1.7.0. It compares restored paths, source revisions and content hashes against
the declared native lock:

```sh
uv run --locked python scripts/smoke_skill_dependencies.py
```

Keep upstream pins and notices intact. Preserve independent plugin selection and
portable client boundaries. Put GitHub execution contracts and their tests in
gh-steward, and keep consumer policy out of this catalog. A release requires a
clean reviewed revision, matching package versions and fresh acquisition proof.
