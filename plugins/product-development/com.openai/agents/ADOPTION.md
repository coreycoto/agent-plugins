# Pinned project adoption

The plugin owns its agents. Project policy, skill contracts, permission profiles
and hosted trust stay in the consumer. Native local installation uses the
plugin's consent-gated Setup workflow; this offline author tool prepares a
reviewed source change for CI/cloud and never installs shared configuration.

Create a project descriptor with `schemaVersion: 1`, `plugin`, an exact
`sourceRevision`, and `roles`. Each consumer role names a `sourceRole` from
that plugin's catalog. It can preserve its role ID and filename, append local
instructions, supply a description, tighten writes to `read-only`, or use an
existing named permission profile. Models and effort remain plugin-owned.
Read-only source roles require an explicitly declared `readOnlyProfiles` entry
when substituting a named profile. That declaration is intent; the consumer
must verify actual runtime permissions.

From the clean publisher checkout at that exact revision:

```sh
python scripts/render_codex_agents.py --project /path/to/agents.project.json --output /empty/review-directory
python scripts/render_codex_agents.py --project /path/to/agents.project.json --output /path/to/consumer/.codex/agents --check
```

Review and commit the generated roles and plugin-qualified projection receipt in a companion
PR. The tool refuses a nonempty render target and rejects unsafe aliases,
filenames and unsupported permission/model overrides. It preserves unrelated
files during comparison. Keep already-qualified consumer skill references
until a separate runtime migration establishes their replacement.

Byte parity proves the committed projection matches its pinned source. It does
not prove cloud discovery, native role selection, hook trust, authentication or
authority for operations. Verify each surface in its actual client.

Each plugin has a distinct receipt filename, so multiple owning-plugin
projections can be checked in the same consumer agents directory.
