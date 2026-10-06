---
name: manage-codex-agents
description: Set up Project Management's packaged Codex agents and guide native hook review, installation, upgrades and verification.
---

Requires local Codex custom agents, Python 3.11+ and the bundled
`project-management-agents` MCP server. Manual setup works before hooks are
trusted; automatic checks require the user's native hook approval.

This skill is the plugin's declared onboarding entrypoint. Use the plugin's
Setup action when available or invoke this skill in the current chat. Keep
hook review, role installation and upgrades in this one guided workflow;
structured settings are for persistent preferences, not a second installer.

Keep the explanation brief: "Project Management adds five agents and
automatic setup checks. Review its three hooks in Codex, then install the
agents if needed." Installing the plugin registers its bundled hooks; do not
copy them into user or project configuration.

Guide the user through Codex's native **Review hooks** dialog (the hook button
in the Desktop composer when review is pending), or `/hooks` in the CLI.
Briefly explain the three handlers:

- Check available agents when the chat starts or resumes.
- Check whether agent installation or an upgrade is needed; writes still
  require the separate installation form.
- Record which packaged agent was selected, in local state without transcripts.

The user chooses **Allow all** or selects individual hooks in Codex. The
onboarding extension launches this skill; it does not expose a hook-approval
action. Do not substitute an MCP form checkbox, edit trust settings, simulate
approval, or bypass hook review. If the current client offers a supported way
to open native review, use it; otherwise give the short navigation above.
Inspect native hook status when the client exposes it. If unavailable, report
approval as unverified. If the user defers review, continue manual setup when
requested and report automatic checks as pending; do not repeatedly prompt.

Use the bundled `codex_agents_status` tool with the current working directory
and session id to distinguish installation state from native role selection
observed in this session. Never infer usability from copied files alone.

Inspect the current spawn tool's schema before claiming that custom roles are
selectable. If it exposes a role/type selector, use the registered `pm_*` name
when a task actually benefits from that role. The parent retains the task's permission
and delegation boundaries. Do not spawn costly probes solely for onboarding.
The role's `sandbox_mode` is a default: the parent's live permission settings
can override it. Dependency maintenance, documentation and release preparation may edit assigned
local files; governance and merge readiness are read-only. The parent owns
policy decisions, GitHub writes, merges and releases.
Give each write task a bounded objective, file ownership and a success condition;
preserve concurrent work and return unresolved decisions to the parent.
Inspect native child runtime permissions before claiming a
separate read-only sandbox; distinguish read-only work from write enforcement.
The bundled `SubagentStart` hook records actual native role selection; report
which roles have been observed and which remain unverified.

When installation is missing or outdated, call `codex_agents_onboard` with the
current directory and session id. It previews owned files, scope and version,
then requests consent using Codex's rich MCP form when available. A declined,
cancelled or unavailable form leaves role files unchanged. Never replace this
consent with a tool argument, shell command or assumed default. If the startup
MCP hook ran before the server connected, call this tool once the connection is
ready. Do not repeatedly prompt after a decline in the same session.
If Codex displays an unsupported-form card, report rendering as failed and
verify that roles are unchanged. Diagnose request-format compatibility before
another attempt; do not start a restart loop or assume another form was accepted.

The installer generates roles in shared `$CODEX_HOME/agents/` (normally
`~/.codex/agents/`) or the selected repository's `.codex/agents/`. The plugin
remains the authored source. Preserve existing role names, project overrides,
trust settings and unrelated configuration. Report ownership/drift conflicts
for resolution; never remove them to make installation succeed.

After installation or upgrade changes role files, use the returned restart
instructions. Do not request another restart when files and role discovery
are already current. This extension cannot reload the desktop app's active
configuration through its
MCP connection. Ask the user to restart Codex and resume the chat, or use a
client-supported reload only when its effect on custom role discovery is
verified. Compaction and rerunning `SessionStart` do not prove a reload.
For CLI, exit and relaunch Codex in the repository. Recheck the spawn schema
and status afterward; report session verification pending until there is
native role-selection evidence. If the client still lacks a role selector,
report that limitation and guide the user to a client with custom-agent support.

After a native plugin upgrade, the startup tool compares bundled asset digests
and offers an upgrade for the existing installation scope. It preserves local
edits, rejects downgrades and rechecks the plan after the form. Review and trust
any new or changed hook definition in Codex when prompted; unchanged trusted
definitions do not need another approval. This flow upgrades generated
roles; it does not update marketplace refs or install upstream skill dependencies.
Cloud/ChatGPT Work discovery is a separate qualification and remains pending.
