# Product Development

This independently selectable plugin provides the first-party `phased-refactor`
skill for evidence-led refactoring. Eighteen curated engineering skills are
optional native Vercel dependencies, declared in `skills-lock.json`. Their
source files are not bundled in this plugin. Initialize the selected dependencies
in the consumer project's `.agents/skills/`, where supported clients can discover
them directly. Our own plugin skill remains in the portable `skills/` directory.

`THIRD_PARTY_NOTICES.md` identifies upstream authors and retained license copies.

## Codex role extension

Version 0.8.0 includes a local Codex client extension. Role definitions live in
`com.openai/agents/`; `extensions.com.openai` references the bundled hooks and
onboarding skill. Root `mcp.json` declares the local onboarding adapter. Other
clients can use the ordinary skills; this adapter manages only local Codex roles.

Codex CLI 0.160.0 loads portable skills and MCP servers but intentionally skips
portable-package hooks in its local loader. The Codex catalog therefore selects
the generated, contained compatibility package in `com.openai/codex-package/`,
with `.codex-plugin/plugin.json` and `.mcp.json`. Its definitions and skills are
generated from this authored package, checked for byte equality in CI and never
edited independently. This changes the install layout, not the plugin identity.
The authored portable package remains available to other clients. A client
version with qualified native portable-hook support can retire this projection.

| Role | Model and effort | Use |
| --- | --- | --- |
| `pd_explorer` | GPT-6 Luna, high | Focused exploration and evidence gathering |
| `pd_reviewer` | GPT-6.1 Sol, high | Correctness, regressions and missing test coverage |
| `pd_architecture_adviser` | GPT-6 Astra, medium | Explicit escalation for difficult architecture decisions |

All three roles are for read-only work and declare `sandbox_mode = "read-only"`
as a default. Codex reapplies the parent's live permission settings when it
spawns a child, so those settings can override the role's sandbox default.
Verify the effective runtime permissions before claiming a separate read-only
sandbox. Repository guidance, permissions and delegation authority remain with
the task. Model routing belongs to each purpose-specific
agent, not a parent-session profile. Installing the plugin does not opt into
automatic delegation, grant provider access, or change the parent model.

Requirements: local Codex custom-agent support (qualified against CLI 0.160.0),
Python 3.11+, an enabled bundled MCP server and reviewed/trusted hooks. Installing
a plugin does not automatically trust its hook definition. Review it in Codex;
repeat review when an upgrade changes the definition. Cloud and ChatGPT Work
discovery are not qualified by this local pilot.

At `SessionStart`, the command hook announces roles/routing and disk state.
The MCP hook checks for an install or upgrade and prompts if needed. Setup
also uses the declared plugin-onboarding skill; it is the same installer, not
a separate settings workflow. It prefers the documented
**`openai/elicitation/create`** method when `openai/elicitation.form` is negotiated,
otherwise uses standard MCP `elicitation/create` when advertised. The deprecated
`openai/form` method is not supported. Without either supported form capability,
setup reports `form_unavailable` and leaves role files unchanged.
A missing MCP connection during startup does not block the
session; invoke `$manage-codex-agents` once the server connects. Decline/cancel
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

References: [portable plugin packaging](https://developers.openai.com/plugins/build/plugins),
[native hooks and their trust/connection semantics](https://learn.chatgpt.com/docs/hooks),
[custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
the [plugin onboarding extension](https://github.com/openai/mcp-extensions/blob/main/docs/spec.md#plugin-onboarding),
the [current form extension](https://github.com/openai/mcp-extensions/blob/main/docs/spec.md#openai-form-elicitation),
and [Codex's rich form client implementation](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/rmcp-client/src/elicitation_client_service.rs).

## Initialize upstream skills in a consumer project

The native `skills-lock.json` declares optional upstream skills using Vercel
Skills CLI 1.7.0's version-1 format: `source`, `sourceType`, immutable `ref`,
`skillPath` and `computedHash`. It contains only upstream dependencies, not our
first-party plugin skills. No custom ledger or client hook is required.

An agent should read this lock when asked to adopt or initialize these skills:

1. Use the **consumer project root** as the working directory. Installing the
   plugin does not install these project dependencies. Read the task's local
   guidance and review which locked skills are wanted.
2. Inspect the consumer's existing `skills-lock.json`. Preserve unrelated
   entries. If a selected name already has a different source/ref/hash, resolve
   that choice before replacing it.
3. Group the selected entries by `source` and `ref`. For each group, run the
   official CLI with exactly those names and the locked commit:

   ```sh
   npx --yes skills@1.7.0 add "<source>#<ref>" \
     --skill <selected-names-from-that-source> --agent codex --yes --copy
   ```

   Replace the placeholders from this package's lock; do not use a moving branch,
   `--global` or `--all`. The CLI writes native entries into the consumer lock
   while retaining unrelated entries and installs the selected skills into that
   consumer's `.agents/skills/`. No copy back into plugin `skills/` is needed.
4. Compare the resulting consumer entries and files with this package's original
   lock. Check source/ref/path and content hash, not only the command exit code:
   native restore can log a failure while exiting zero and recalculates hashes.
   In a publisher checkout, the read-only checker is:

   ```sh
   uv run --frozen python scripts/verify_skill_dependencies.py \
     --plugin-root <chosen-plugin-root> \
     --installed-root <consumer-project>/.agents/skills \
     --consumer-lock <consumer-project>/skills-lock.json
   ```

   This uses Node's native hash ordering and the original declared hash. It does
   not install anything. Stop on missing skills, pin drift or changed content.
5. Confirm discovery in the chosen client. For Codex, upstream skills have their
   ordinary names (for example `$code-review`), not a plugin-qualified name.
   Refresh the task's skill catalog when needed; installed files alone do not
   prove that an existing chat has loaded them. Repository policy and the
   current task's authority remain in force.

For a **new consumer project** whose own `skills-lock.json` already contains the
reviewed dependency entries, `npx --yes skills@1.7.0 experimental_install`
restores them into that project's `.agents/skills/`. The command reads only its
working directory's lock; running it in this plugin directory would restore to
the wrong project. It does not accept an alternate lock or destination path.

Maintainers update the declaration with the official CLI in an isolated project
at reviewed immutable refs, inspect the generated native lock and changed
skills, then commit only the reviewed `skills-lock.json` and notices here.
Do not commit the restored `.agents/skills/` tree into a plugin.

Format and behavior were checked against [Vercel Skills 1.7.0](https://github.com/vercel-labs/skills/tree/18f96ea131dab3b0fcc9b27cf7c6f6cbb6174680),
including its [native lock](https://github.com/vercel-labs/skills/blob/18f96ea131dab3b0fcc9b27cf7c6f6cbb6174680/src/local-lock.ts)
and [restore implementation](https://github.com/vercel-labs/skills/blob/18f96ea131dab3b0fcc9b27cf7c6f6cbb6174680/src/install.ts).
