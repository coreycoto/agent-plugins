# Browser, monorepo and service tools

Prefer the consumer's project-pinned tools, available native integrations and
installed specialist workflows. A compatible global CLI can supply a missing
capability. Resolve its executable and runtime first; preserve the consumer's
version requests, install owner and update preferences. These choices also apply
inside a cloud development VM; do not assume a developer's home paths exist.

## Browser evidence

Use browser automation for rendered UI or interaction evidence. Honor the user's
selected browser surface and read its required workflow. When agent-browser is
the chosen available tool, inspect its matching packaged skill and commands:

```sh
agent-browser skills get core
agent-browser snapshot -i
```

Use references from the latest snapshot and refresh after navigation or DOM
changes. Opening a page can make authenticated requests. Form submissions,
messages and purchases require their corresponding task scope. Keep private
profiles, cookies, downloads and captures out of source and public reports.
Package installation does not prove a matching browser is installed; browser
downloads are a separate setup action. In a hosted environment, verify browser
availability, sandbox support, proxy routing and certificate trust without
disabling TLS checks or silently switching to a different account.

## Turbo task selection

Inspect project scripts and `turbo.json`, then use the project's Turbo version:

```sh
turbo run build --dry=json
turbo run test --filter=PACKAGE --dry=json
```

Replace the package placeholder with an inspected package identity. A dry run
explains the graph, not whether tests pass. Review filters and dependency
expansion. Tasks can generate outputs, contact providers or deploy according to
their scripts. A cache hit reuses an earlier result; check declared inputs,
environment and revision before presenting it as current qualification. Do not
reflexively force execution or enable remote caching to repair a local failure.
If direct commands work but child tasks fail, inspect environment filtering;
use a scoped consumer-supported correction instead of changing global defaults.

## Vercel

Prefer a matching connector and deployment workflow. Use the CLI for a concrete
capability gap or needed diagnostic evidence, for example inspecting a known
deployment with `vercel inspect DEPLOYMENT_URL`. Check the installed version's
help before relying on flags from newer documentation.

Verify team, project, source revision, deployment identity and Preview versus
Production. Inspection does not prove rendered browser behavior. `vercel link`
writes project state; pull operations write configuration and can retrieve
secrets. Deployment and promotion need the corresponding authorized delivery
stage. Keep `.vercel`, downloaded environment files and login tokens out of Git.
Use the host's documented credential/proxy mechanism and retain destination
scoping; a configured CLI is not evidence of provider access.

## Neon

Prefer an available connector for supported operations. Otherwise verify the
installed CLI identity, runtime requirements and help. The current npm CLI uses
the `neon` package/command; older `neonctl` names may remain in package managers.
Use the consumer's actual install owner rather than adding a second global copy.

Specify project and branch identifiers from current evidence before choosing a
database. Commands can open a browser login; authentication is explicit setup.
Connection strings can contain credentials, so keep them in the credential owner
and out of logs, shell history and reports. Branch creation/deletion, resets,
migrations and SQL writes need the corresponding database scope. A listing or
successful login does not qualify an application's database behavior.

Sources: [agent-browser](https://agent-browser.dev),
[Turbo run](https://turborepo.com/docs/reference/run),
[Vercel CLI](https://vercel.com/docs/cli), [Neon CLI](https://neon.com/docs/cli),
[Neon source](https://github.com/neondatabase/neon-pkgs).
