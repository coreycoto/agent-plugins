---
name: manage-codex-agents
description: Install, upgrade or verify Product Development's packaged roles in a local Codex client when startup reports missing or outdated agents, or the user asks to manage these roles.
---

Requires local Codex custom agents, trusted plugin hooks, Python 3.11+ and the
bundled `product-development-agents` MCP server.

Use the bundled `codex_agents_status` tool with the current working directory
and session id to distinguish installation state from native role selection
observed in this session. Never infer usability from copied files alone.

Inspect the current spawn tool's schema before claiming that custom roles are
selectable. If it exposes a role/type selector, use the registered `pd_*` name
when a task actually benefits from that role. Explicitly select Astra only for
a difficult architecture question. The parent retains the task's permission
and delegation boundaries. Do not spawn costly probes solely for onboarding.
The bundled `SubagentStart` hook records actual native role selection; report
which roles have been observed and which remain unverified.

When installation is missing or outdated, call `codex_agents_onboard` with the
current directory and session id. It previews owned files, scope and version,
then requests consent using Codex's rich MCP form when available. A declined,
cancelled or unavailable form leaves role files unchanged. Never replace this
consent with a tool argument, shell command or assumed default. If the startup
MCP hook ran before the server connected, call this tool once the connection is
ready. Do not repeatedly prompt after a decline in the same session.

The installer generates roles in shared `$CODEX_HOME/agents/` (normally
`~/.codex/agents/`) or the selected repository's `.codex/agents/`. The plugin
remains the authored source. Preserve existing role names, project overrides,
trust settings and unrelated configuration. Report ownership/drift conflicts
for resolution; never remove them to make installation succeed.

After installation or upgrade, use the returned restart instructions. This
extension cannot reload the desktop app's active configuration through its
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
the new hook definition in Codex when prompted. This flow upgrades generated
roles; it does not update marketplace refs or install upstream skill dependencies.
Cloud/ChatGPT Work discovery is a separate qualification and remains pending.
