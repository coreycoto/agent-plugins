# Contributing

Use Python 3.13+, uv and Node.js for catalog author checks:

```sh
uv sync --locked --group dev
uv run --locked python scripts/validate_agent_plugins.py
uv run --locked python scripts/verify_skill_dependencies.py
uv run --locked ruff check scripts tests
uv run --locked pytest
```

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
