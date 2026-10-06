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

The initial catalog release is prepared at **0.7.0**; Product Development and Project Management's
Codex role extensions are prepared at **0.8.0**. Plugin release versions
are separate from the Agent Plugins 1.0.0 manifest specification. Packages are
independently selectable; adding the catalog does not install every plugin.

For Codex, add the `agent-plugins` marketplace from a reviewed revision and select a package.
The catalog pins independently versioned npm packages. CI builds those packages;
generated distributions are never committed. Registry releases must exist before
that catalog revision can install them. For local authoring, build once and add
the generated `dist/plugin-packages/codex` marketplace instead. Other clients use
the complete portable bundles under `dist/plugin-packages/portable/plugins/<name>`.
Vercel Skills CLI can install individual skills. Optional upstream skills use
the CLI's native `skills-lock.json` format and are restored into the consumer's
`.agents/skills/`. Each package README gives the initialization and verification
commands. First-party skills stay in the plugin; upstream skill trees are not
bundled or copied back into it.

Project Management uses [gh-steward](https://github.com/coreycoto/gh-steward) for
qualified GitHub composition and durable execution. Ordinary GitHub operations
use native `gh` or the client connector. Tool installation, authentication and
task authorization remain separate checks. This catalog distributes skills,
client metadata and author checks. Plugins with custom agents bundle a
local Python Codex onboarding adapter; GitHub workflow execution stays in gh-steward.

Product Development's bundled `SessionStart` hook announces six purpose-specific
Luna, Sol 6.1 and Astra roles and checks installation/upgrade state. Its native
MCP form offers shared-user or project installation with ownership checks.
Generated files and live session usability are reported separately. See the
[Codex role extension](plugins/product-development/README.md#codex-role-extension)
for requirements, consent, upgrade behavior and restart verification.

Each plugin owns its specialized agents. Product Development owns six engineering
roles; Project Management owns five dependency, documentation, governance,
merge-review and release-preparation roles. Agents are not borrowed across
plugins. The [Project Management routing guide](plugins/project-management/skills/_shared/references/codex-agent-routing.md)
maps legacy helper IDs to its own roles. Repositories retain product policy,
permission profiles and operational/release gates. Agent Development and its
specialized autoresearch agents are owned by a separate private publisher.

The author source in `adapters/codex_agents/` supplies shared installer code,
not shared agent definitions. `scripts/build_codex_package.py` generates the
complete portable/Codex packages and reproducible npm archives into ignored
`dist/plugin-packages/`, and checks their bytes against the source. Codex 0.160's
portable-hook workaround exists only in the built Codex artifact. Plugin catalogs,
namespaces, hooks, consent summaries, install directories
and upgrade state remain independent. A change to one plugin cannot replace
another plugin's owned roles.

Codex owns package acquisition through its native npm source; install scripts are
disabled. Refresh the marketplace to discover new exact package versions, then
use native install/update and Setup. CI and operational automation use immutable
qualified pins. Updating files does not prove that an
already running chat has reloaded them; changed hook definitions require native
client trust review.

Product facts, provider access, project policy and permissions belong in the
task or consumer repository. Installation grants no external mutation authority.
First-party content is MIT licensed. Optional upstream dependencies retain their
authors' attribution and license notices. See [CONTRIBUTING.md](CONTRIBUTING.md)
for offline author checks and native dependency restoration.
