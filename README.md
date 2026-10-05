# Agent Plugins

Select the Agent Plugins you need. Each package has a portable root `plugin.json`
and immediate skill directories under `skills/`. Optional OpenAI client settings
live under `extensions.com.openai` and files under `com.openai/`.

| Plugin | Purpose |
| --- | --- |
| Project Management | Planning, backlog, publishing and delivery |
| Product Development | Implementation, testing, review, debugging and phased refactoring |
| Product Management | Discovery, prioritization and product requirements |
| Communication | Agent collaboration, explanatory prose and editing |

The initial catalog release is prepared at **0.7.0**; Product Development's
Codex role extension is prepared at **0.8.0**. Plugin release versions
are separate from the Agent Plugins 1.0.0 manifest specification. Packages are
independently selectable; adding the catalog does not install every plugin.

For Codex, add the `agent-plugins` marketplace from a reviewed revision and select a package.
The Product Development entry selects its generated Codex compatibility package
because CLI 0.160.0 skips portable-package hooks. Other clients can acquire the
authored portable package directly from `plugins/product-development`.
Vercel Skills CLI can install individual skills. Optional upstream skills use
the CLI's native `skills-lock.json` format and are restored into the consumer's
`.agents/skills/`. Each package README gives the initialization and verification
commands. First-party skills stay in the plugin; upstream skill trees are not
bundled or copied back into it.

Project Management uses [gh-steward](https://github.com/coreycoto/gh-steward) for
qualified GitHub composition and durable execution. Ordinary GitHub operations
use native `gh` or the client connector. Tool installation, authentication and
task authorization remain separate checks. This catalog distributes skills,
client metadata and author checks. Product Development additionally bundles a
local Python Codex onboarding adapter; GitHub workflow execution stays in gh-steward.

Product Development's bundled `SessionStart` hook announces purpose-specific
Luna, Sol 6.1 and Astra roles and checks installation/upgrade state. Its native
MCP form offers shared-user or project installation with ownership checks.
Generated files and live session usability are reported separately. See the
[Codex role extension](plugins/product-development/README.md#codex-role-extension)
for requirements, consent, upgrade behavior and restart verification.

Local clients may track the latest stable release through a qualified update
adapter. Resolve each release to an exact commit, preserve package selection and
enablement, validate before switching, and retain rollback. CI and operational
automation use immutable qualified pins. Updating files does not prove that an
already running chat has reloaded them; changed hook definitions require native
client trust review.

Product facts, provider access, project policy and permissions belong in the
task or consumer repository. Installation grants no external mutation authority.
First-party content is MIT licensed. Optional upstream dependencies retain their
authors' attribution and license notices. See [CONTRIBUTING.md](CONTRIBUTING.md)
for offline author checks and native dependency restoration.
