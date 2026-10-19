# Runtimes and dependencies

Identify the selected executable, project version declaration, package manager,
lockfile and CI lane before changing an installation. A compatibility range,
minimum version and exact pin are different contracts. Read project instructions
and local overlays; a global default does not supersede a project selector.

## Runtime ownership

When the consumer uses mise, inspect selection from the project directory:

```sh
mise ls
mise which python
mise which node
```

Read `mise.toml`, idiomatic version files and relevant settings. A version file
only participates if its discovery mechanism is enabled. `command -v` may show a
shim; the manager's resolution identifies the actual installation. Inspect
project configuration before using `mise exec`, which can load environment
settings and wrappers. `mise use` writes configuration. Installing a missing pin,
reshimming and upgrading a global default are separate setup actions.

Use the consumer's chosen owner for Node, Python, Rust and Bun. Mise can own all
four, but another environment may provision them directly. Rust managed through
mise can use rustup with manager-specific Cargo/Rustup homes; compare that state
before invoking standalone rustup. Avoid creating duplicate installations to
repair a PATH or selector mismatch. Preserve offline and no-auto-install settings
for inspection rather than silently substituting a missing version.

## Python and uv

Read `pyproject.toml`, `uv.lock`, Python selectors, workspace membership and uv
configuration. Determine whether the consumer permits uv-managed Python or uses
an externally managed interpreter. Preserve that choice instead of imposing
a personal download policy. For an authorized setup using an existing Python:

```sh
uv sync --locked --python /path/to/selected/python --no-python-downloads
```

Use the verified executable path. Sync changes the environment, can remove
undeclared packages and may run build steps. Select the intended groups and
extras. `--locked` refuses a stale lock; `--frozen` uses the lock without checking
its freshness. Ordinary `uv run` can lock and sync. `uv run --no-sync COMMAND`
avoids syncing an already prepared environment, but does not establish that the
environment matches current requirements. Existing environments can retain an
older interpreter until deliberately rebuilt.

Use uv's add/remove/lock operations for intended dependency changes and review
manifest and lockfile together. Environment-level `uv pip` work does not maintain
the project dependency contract. Avoid system or user-site installs as a repair
for an isolated environment.

## Bun and JavaScript tools

Read `packageManager`, engines, runtime selectors, `bunfig.toml`, the lockfile and
CI. Use Bun where the project selects it; a Bun runtime does not automatically
satisfy a Node requirement. Upgrade a managed binary through its owner.

For authorized dependency setup in a Bun-managed project:

```sh
bun install --frozen-lockfile
```

The frozen install rejects manifest/lock disagreement, but still writes
dependencies and can execute permitted lifecycle scripts. Use add/remove only
for intended dependency changes. Prefer project scripts and local CLIs to global
fallbacks. `bunx` and similar package runners can acquire missing packages; they
are not availability checks. Global CLI requests and their update schedules
belong to consumer setup, not portable workflow instructions.

Verify executable resolution separately from application compatibility, then
run the relevant project checks. Keep a bounded dependency repair from becoming
an unrelated machine-wide upgrade.

Sources: [mise tools](https://mise.jdx.dev/dev-tools/),
[mise configuration](https://mise.jdx.dev/configuration.html),
[uv sync](https://docs.astral.sh/uv/concepts/projects/sync/),
[uv configuration](https://docs.astral.sh/uv/concepts/configuration-files/),
[Bun installation](https://bun.com/docs/pm/cli/install),
[bunx](https://bun.com/docs/pm/bunx).
