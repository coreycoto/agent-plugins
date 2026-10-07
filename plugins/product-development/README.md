# Product Development

Independently maintained engineering procedures, packaged for direct use without
restoring upstream skills. Consumer repositories retain product policy,
implementation contracts, verification commands and durable project knowledge.
The procedures are informed by retained, revision-pinned upstream research;
`THIRD_PARTY_NOTICES.md` records attribution and licenses. Packaged lineage is
provenance, not an installation manifest.

## Skills

| Skill | Use it to |
| --- | --- |
| `engineering-workflow` | Select the smallest sufficient procedure and continue to the authorized endpoint. |
| `understand-codebase` | Explain a bounded path and distinguish current mechanics from historical rationale. |
| `diagnose-problem` | Reproduce a symptom and discriminate causes with decisive probes. |
| `design-change` | Resolve technical alternatives, contracts, impact and validation. |
| `implement-change` | Complete accepted intent in behaviorally useful slices. |
| `review-code` | Assess an exact candidate for supported defects and missing evidence. |
| `test-behavior` | Add independent regression evidence at an appropriate public seam. |
| `verify-product` | Exercise the actual user path and retain observable results or prerequisite gaps. |
| `maintain-verification` | Create, qualify or refresh runnable consumer verification instructions. |
| `prototype-decision` | Answer one uncertainty through a bounded disposable experiment. |
| `improve-performance` | Identify the limiter and measure equivalent work with correctness preserved. |
| `model-domain` | Clarify vocabulary, identity, state, invariants and boundary contracts. |
| `capture-solution` | Retain verified reasoning whose loss would cause recurrence or major rediscovery. |
| `refresh-solutions` | Reconcile selected records while preserving policy, history and unknowns. |
| `phased-refactor` | Change substantial structure in bounded phases with contract and parity evidence. |
| `manage-codex-agents` | Preserve the existing consent-based native role setup workflow. |

A small understood task can go directly to `implement-change`. The router is
not a mandatory chain and no skill automatically ships a local result. Shared
references are read only for relevant techniques; they add no discoverable skills
or mandatory specialist agents. Procedures remain usable in the parent without
delegation. Use actual available tools rather than client-specific commands.

Verification distinguishes executed user behavior from liveness and synthetic
checks. Knowledge uses existing consumer conventions, deduplicates first and
captures selectively; it does not set up a database, mine transcripts or update
global memory or root instructions automatically. Project Management owns
delivery tracking, Product Management owns product decisions and Communication
owns substantial prose when those packages are available.

The repository's `docs/owned-workflows.md` documents legacy-name migration.
Existing consumer-restored upstream copies are outside this package's ownership;
removing them requires a separately scoped inventory and migration.

## Codex role extension

The local Codex client extension keeps role definitions in
`com.openai/agents/`; `extensions.com.openai` references the bundled hooks and
onboarding skill. Root `mcp.json` declares the local onboarding adapter. Other
clients can use the ordinary skills; this adapter manages only local Codex roles.

Codex CLI 0.160.0 skips portable-package hooks in the observed local loader.
The built Codex artifact therefore contains `.codex-plugin/plugin.json` and
`.mcp.json`. Marketplace acquisition and release publication are separate from local source
preparation; a local catalog change is not a released package.
Complete Codex and portable packages are built into ignored
`dist/plugin-packages/`, never committed or edited independently. For local
testing, use the built Codex marketplace. A client
version with qualified native portable-hook support can retire this projection.

| Role | Model and effort | Use |
| --- | --- | --- |
| `pd_explorer` | GPT-6 Luna, high | Focused exploration and evidence gathering |
| `pd_reviewer` | GPT-6.1 Sol, high | Correctness, regressions and missing test coverage |
| `pd_implementer` | GPT-6.1 Sol, high | Assigned implementation from an accepted plan |
| `pd_diagnostician` | GPT-6.1 Sol, high | Root cause and the smallest decisive next experiment |
| `pd_transformer` | GPT-6 Luna, high | Explicit mechanical edits with deterministic validation |
| `pd_architecture_adviser` | GPT-6 Astra, medium | Explicit escalation for difficult architecture decisions |

Explorer, reviewer and architecture adviser declare `sandbox_mode = "read-only"`.
Implementer, diagnostician and transformer declare `sandbox_mode = "workspace-write"`.
Implementation and transformation edit only assigned files. Diagnosis does not
edit product source; its write default permits temporary diagnostic evidence.
These are purpose-specific defaults. Codex reapplies the parent's live permission settings when it
spawns a child, so those settings can override the role's sandbox default.
Verify the effective runtime permissions before claiming a separate read-only
sandbox. Repository guidance, permissions and delegation authority remain with
the task. Model routing belongs to each purpose-specific
agent, not a parent-session profile. Installing the plugin does not opt into
automatic delegation, grant provider access, or change the parent model.

For existing repository roles and committed CI/cloud configuration, use the
[pinned adoption guide](com.openai/agents/ADOPTION.md). The offline author
renderer keeps shared models and behavior in this source while preserving
consumer aliases, task constraints and named permission profiles. It is
separate from the consent-gated local installer.

Requirements: local Codex custom-agent support (qualified against CLI 0.160.0),
Python 3.11+ and an enabled bundled MCP server. Manual setup works before hook
approval; automatic checks require reviewed/trusted hooks. Cloud and ChatGPT
Work discovery are not qualified by this local pilot.

Start with the plugin's **Setup** action, or `$product-development:manage-codex-agents` in the current
chat. The declared onboarding skill guides the user through one setup workflow:

1. Review the three bundled hooks in Codex's **Review hooks** dialog (Desktop
   composer hook button), or `/hooks` in the CLI. They announce available agents,
   check installation/upgrades, and record local native agent selection.
2. Install or update agents through the existing form, only when needed.
3. Restart after role files change, then verify discovery. Already current
   agents do not need another installation or restart.

Installing the plugin registers its hooks, but does not approve them. The
onboarding extension launches a skill; it does not provide an action to open or
approve native hook review. The user approves the exact definitions in Codex;
an installer form cannot grant hook trust. Manual setup remains available if
review is deferred, with automatic checks reported as pending. An upgrade that
introduces or changes a hook requires another native review; unchanged trusted
definitions do not. No second hook installer or settings screen is needed.

At `SessionStart`, the command hook announces roles/routing and disk state.
The MCP hook checks for an install or upgrade and prompts if needed. Setup
also uses the declared plugin-onboarding skill; it is the same installer, not
a separate settings workflow. It prefers the documented
**`openai/elicitation/create`** method when `openai/elicitation.form` is negotiated,
otherwise uses standard MCP `elicitation/create` when advertised. The deprecated
`openai/form` method is not supported. Without either supported form capability,
setup reports `form_unavailable` and leaves role files unchanged.
A missing MCP connection during startup does not block the
session; invoke `$product-development:manage-codex-agents` once the server connects. Decline/cancel
never installs, and a declined choice is not prompted again by that server
in the same session. There are no command-line consent bypasses.

The form previews the package version, models, target paths and writes. It
offers shared user scope (recommended for personal reuse), the current
repository, or later with titled choices and unchecked approval. Decline/cancel
does not trigger another form dialect or an installation. An unsupported-form
card is a failed rendering check, not consent; diagnose it before requesting
another attempt. Structured settings are reserved for future persistent plugin
preferences and are not another role-installation path. It generates roles beneath:

- `$CODEX_HOME/agents/product-development/`, normally `~/.codex/agents/…`;
- `<repository>/.codex/agents/product-development/` for project scope.

These are generated projections, with a local `.gitignore` and ownership marker,
not additional authored sources to maintain in each repo. The native loader
discovers the TOMLs. No `config.toml`, project trust or unrelated roles are
modified. Project installation requires an explicit trusted entry for the
repository root in shared Codex configuration; the installer never grants trust.
Existing explicit
registrations, duplicate scopes, symlinks and locally edited owned files stop
the installer for resolution. The plan is rechecked after the form and under
an installation lock. Upgrades retain private backups outside the agents
discovery tree in the selected scope's `agent-plugin-state/product-development/`.

Native plugin upgrades supply the new assets. Startup compares their version
and digest with the owned projection, then offers an upgrade through the same
form. Older package versions cannot overwrite newer projections. There is no
automatic marketplace-ref update. An interrupted/failed write requires inspection
of the target, lock and retained backup before a retry; unknown outcomes are
never automatically replayed. To uninstall generated roles, first inspect the
ownership marker and local edits, then explicitly request their removal;
disabling the plugin alone does not remove generated role files.

After install/upgrade, **restart Codex and resume the chat**; for CLI, exit and
relaunch in the repository. This adapter cannot reload the desktop app's active
configuration through its MCP connection. Use a client reload only when its
custom-agent discovery is verified. Compaction or a repeated startup hook is
not proof. Inspect the active spawn tool for a role/type selector; if the client
does not expose it, report that limitation instead of claiming readiness.
The `SubagentStart` hook records actual native role selection per parent session
in private shared Codex state, with role ids and digests, never transcripts.
Status lists observed selections separately from unverified roles. A restarted
Desktop chat retains its session id, so native selections can be recorded when
resuming the installation chat. Installation alone leaves verification pending.
These receipts confirm selection, not the model or permission policy loaded
by the child.
Avoid costly verification-only subagents: confirm selection when delegation is
authorized and useful to the task.

Live CLI delegation needs a persistent parent session in qualified Codex 0.160.0;
an ephemeral parent has no rollout to fork. A useful read-only installer review
verified `pd_explorer` selection with GPT-6 Luna, high reasoning and read-only
permissions through native child-session metadata. Desktop accepted the current
rich-form extension and installed the shared roles. After restart, a useful
installer review selected `pd_reviewer` with GPT-6.1 Sol and high reasoning.
Its native runtime inherited the parent's workspace-write permissions; it
performed read-only work. Hook trust and hook-produced selection receipts remain
separate checks. Reviewer selection does not qualify the other roles or prove
an independently enforced read-only sandbox.

The expanded six-role catalog additionally passed isolated native form decline,
installation and three-to-six-role upgrades in both scopes, without inference
requests. Live selection and effective permissions for the new implementer,
diagnostician and transformer still require useful authorized work after the
reviewed upgrade and reload. Earlier selection receipts do not verify a newer
catalog digest.

References: [portable plugin packaging](https://developers.openai.com/plugins/build/plugins),
[native hooks and their trust/connection semantics](https://learn.chatgpt.com/docs/hooks),
[custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
the [plugin onboarding extension](https://github.com/openai/mcp-extensions/blob/main/docs/spec.md#plugin-onboarding),
the [current form extension](https://github.com/openai/mcp-extensions/blob/main/docs/spec.md#openai-form-elicitation),
and [Codex's rich form client implementation](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/rmcp-client/src/elicitation_client_service.rs).
