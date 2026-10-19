# Development tools and environment

Use this reference when repository exploration, setup, checks or product
verification needs a tool choice. Load only the relevant topic:

| Need | Reference |
| --- | --- |
| Search contents, discover paths or select candidates | [Search and navigation](search.md) |
| Resolve runtimes, package managers or locked environments | [Runtimes and dependencies](runtimes.md) |
| Scan secrets, validate shell scripts or retrieve LFS content | [Repository checks](checks.md) |
| Inspect a browser, monorepo graph, deployment or database branch | [Browser and service tools](services.md) |

Read the consumer's scripts, manifests, lockfiles and environment setup first.
Prefer its project-pinned executable and existing workflow. An installed global
tool is a useful fallback when compatible; it does not replace the project's
version contract. Discover actual executable selection before adding another
installation. Inspect available connectors and their required skills before
choosing a CLI for a provider operation.

Apply these choices in local development, CI and cloud development environments.
Inspect the actual OS, client version, writable paths, network/proxy rules,
installed tools and credential mechanism. A cloud VM running a compatible Codex
runtime can support capabilities that a different managed service cannot.
Determine support for plugin discovery, bundled processes and lifecycle hooks
from that host and a bounded runtime check; do not infer support or failure from
the word "cloud" or from a desktop-only label on another installation surface.

Tool availability, package acquisition, enablement, authentication, hook trust,
session discovery and successful execution are separate observations. A declared
marketplace or dependency is not proof that the current agent loaded it. Preserve
host-managed configuration and report unavailable prerequisites. Do not work
around a read-only plugin home or an executable denial through another transport.

Keep personal paths, account defaults, global version requests and update
schedules in consumer configuration. Preserve useful selection policy across
hosts: project pins first, explicit global fallback, locked dependency setup,
and separate installation from inspection. Version/help commands can trigger
shim installation, updates or authentication; inspect the owner and use its
documented offline/no-install mode when the task is read-only.

Cloud environments may inject proxy, CA and destination-scoped credentials.
Keep those bindings scoped to their intended commands and services; do not print
or persist secrets in source. Check child-process environment filtering when a
tool works directly but fails under a task runner. Preserve certificate
verification and network policy instead of globally relaxing either to obtain
a passing check. Startup, build and test tasks can have side effects; inspect
their scripts before treating them as verification.
