# Executable product verification

Use the consumer's established instructions and available tools. Create or
refresh these only when that is the assigned task. A useful instruction record
contains:

- Source revision or artifact and environment; distinguish local from deployed.
- Prerequisites and a safe way to check readiness, instance identity and access.
- Exact launch and interaction commands or stable UI handles, grounded in source.
- User entry point, expected visible outcome and relevant persisted effects.
- Evidence location, redaction needs, owned resources and bounded cleanup.

Prefer documented commands and existing harnesses. Name missing prerequisites
without guessing credentials or creating configuration. If startup is broken,
record that result; do not teach a fabricated successful setup. An authorized
scaffold must be labeled and must not substitute for an unavailable dependency.

Drive the actual user path with stable selectors, commands or requests. Shared
UI state has one driver at a time. Verify the active instance after surprising
behavior; a healthy process can still have wedged UI state. Reset only state
owned by the run or use a fresh isolated session within scope.

Capture the action and observable result, not merely a final screenshot. Inspect
relevant saved state, files or consumer effects when acceptance depends on them.
Health, import or synthetic response checks cannot prove a provider lookup or
end-to-end user outcome. “Dry run” needs its side effects checked, not trusted
from its name. Provider mutations remain task-authorized actions.

Preserve useful evidence before teardown, including failures. Stop only processes
or sessions the run created and remove only authorized owned scratch. Confirm
artifacts survive cleanup. Ambiguous operations are not replayed to improve a
receipt. Report each selected path as passed, failed or unverified with reason.

For maintenance, distinguish instruction drift and harness gaps from product
regressions. Current source describes mechanics; accepted policy can still expose
a bug. Execute changed steps before calling instructions qualified. Record
coverage limits instead of treating a partial map as full verification.
