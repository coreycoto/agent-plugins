# Release writing and safeguards investigation

Implementation issue: [#43](https://github.com/coreycoto/agent-plugins/issues/43).
Local source preparation only. No release mutation, policy installation, hook
trust or activation is part of this change.

## Shipped instructions and assets

Communication owns audience selection in
[public release writing](../plugins/communication/skills/_shared/references/public-release-writing.md).
Its existing writing and editing skills load that reference for public notes.
Project Management's [publish-change](../plugins/project-management/skills/publish-change/SKILL.md)
applies the editorial check and the
[release lifecycle](../plugins/project-management/skills/publish-change/references/release-lifecycle.md).
It can perform the editorial check without installing Communication.

Public notes retain consumer capabilities, compatibility, migration and material
limitations. Internal authority and qualification receipts belong in handoffs.
The examples are synthetic; no other repository's notes are changed. Existing
historical changelog entries remain historical. The new unreleased entry is
consumer-facing; this investigation holds the implementation evidence.

The namespaced [rule template](../plugins/project-management/com.openai/release-policy/review-release.rules)
ships as inert bytes. It prompts for ordinary `gh release` mutation prefixes;
it supplies no allow and cannot distinguish draft from published. It is not
referenced by a hook or onboarding handler. A plugin-local `rules/` directory
is **not** assumed to load automatically. Prefix rules apply to supported
outside-sandbox command approval, not every possible execution surface.

## Distribution assessment

Versioned templates can travel in the existing package without a new plugin or
skill. Installation needs a separately reviewed extension of Project Management's
existing Setup workflow. The current `codex_agents_onboard` tool only installs
roles; do not pass a rules plan to it or imply it now supports policies.
Communication needs no policy installer.

Reuse the role installer's lifecycle principles, not its target-directory swap:
roles own a directory, while native rules should use a flat, namespaced `.rules`
file in a loaded config layer. Do not place ownership records or backups in the
loaded `rules/` tree. Do not copy a whole rules directory over consumer policy.

Proposed onboarding contract:

1. Preview the exact template bytes/diff, package version, owner, content digest,
   destination, existing policy combination and supported/unsupported paths.
   Explain that a prompt template is command review, not published-release
   protection. Test the combined policy before offering installation.
2. Offer rules separately from role installation, through explicit native form
   consent. Decline/cancel/unavailable forms write nothing. A checked role-install
   form never authorizes policies or hook trust. Existing executable denials
   remain unchanged; an installer cannot silently retire or weaken them.
3. Offer one scope: `$CODEX_HOME/rules/` for user scope or the trusted repository's
   `.codex/rules/` for project scope. Read shared project trust, preserve config
   comments and all unrelated files, and reject duplicate scopes or unmanaged
   destination files. Keep a namespaced owner/schema/version/digest record in
   `agent-plugin-state/`, outside discovery. Do not adopt an unmarked file even
   when its contents happen to match.
4. Bind consent to the full plan fingerprint and recheck after the form and
   before replacement. Detect altered markers, edited/missing owned files,
   symlinked paths, changed templates, downgrade attempts and same-version
   changed bytes. Preserve conflicts for resolution. Update only the existing
   owned scope, keeping private backups and recovery receipts outside discovery.
5. A production implementation also needs an installation lock, staged writes,
   interrupted-write recovery and protection against filesystem races. The
   offline installer model tests single-process lifecycle semantics only;
   **it is not ready to register as an installer**. Removal would need its own
   exact owned-file/digest check and authorization; deleting an allow may tighten
   policy while deleting a deny may weaken it.
6. Report file installation separately from native hook trust, supported reload,
   rule loading and observed runtime behavior. Restart after changed rules.
   Recheck effective combined rules and representative allowed/denied paths in
   the new runtime. `execpolicy check` against explicit files does not prove the
   running chat loaded them. Compaction and SessionStart replay do not reload
   policy. Changed hook definitions need native review; never edit trust records.

The offline model uses temporary homes and tests preservation, drift, duplicate
scope, consent, upgrade backup and stale-plan behavior. Existing role-installer
tests remain the reference for native form negotiation, shared trust and locking.
Those passing tests do not qualify a new rules form or real policy installation.

## State-aware operation assessment

A dedicated state-aware release operation is preferable to parsing arbitrary
shell text. Its trusted boundary must resolve host, stable repository and release
IDs, tag commit, artifacts and final body; obtain authenticated fresh state;
check independent action authority; and own the exact write. User/model arguments
such as `approved=true` or `isDraft=true` cannot establish either fact. Bind
publication approval to the actual body and artifact digests, and recheck policy
at apply time. Re-read state before effects and verify the result afterward.

Draft body edits and explicitly approved draft publication are eligible under
the workflow. Published stable and prerelease changes are refused. Missing,
inaccessible, malformed or ambiguous observations refuse; a 404 can mean no
draft visibility. Changed identity or payload invalidates the reviewed plan.
After a timeout, inspect the existing release by ID before any retry; publication
does not authorize a later metadata/asset correction.

The pure decision model and fake operation have no network or provider adapter.
They support only draft body edit and draft publication, not asset upload,
delete, tag writes, recreation or release creation. They demonstrate eligibility,
not executable permission. The fake authority input stands for a future trusted
authority store, not a deployed form or permission token.

Two reads detect publication between observations. The race fixture also
publishes **after the final read**, then shows that an unconditional fake write
still edits a published target. Thus neither one nor two reads establish atomic
protection. The documented GitHub update endpoint does not advertise an atomic
`only-if-draft` precondition. Do not invent an `If-Match` guarantee from an ETag
or `updated_at`. Verify provider conditional-write semantics before relying on
them. A client-side lock coordinates only participating clients; it cannot lock
the GitHub UI or other publishers. Where atomic protection is required, leave
the write blocked until the provider or a controlled writer boundary can uphold
that invariant for all relevant actors.

## Trusted PreToolUse hook assessment

| Surface | Proposed handling | Limit or qualification still needed |
| --- | --- | --- |
| Simple `gh release edit/upload/delete/create` | Command review plus a schema-aware operation that owns supported writes | Prefix matching has no draft state; no direct-write blanket allow |
| `gh --repo … release edit`, aliases, absolute paths, wrappers, scripts | Treat as unresolved until canonicalized by a qualified adapter | Reordered flags do not match the shipped prefix; arbitrary shell parsing is unsupported |
| `gh api`, curl, GraphQL/REST clients, Python/Node scripts | Inspect a known structured operation or refuse release writes in the guarded channel | Prefixes on `gh release` do not cover these transports |
| Git tag moves/deletes and release asset endpoints | Protect as separate release effects with identity/action checks | Body-only operation does not cover these effects |
| Local MCP release mutation tools | Match exact observed tool names and validate exact schemas | No release-specific GitHub connector tool is exposed in this task; native delivery remains unverified |
| Hosted connectors, browser/UI actions, tools inside orchestration wrappers | Require host-specific policy coverage and observed nested-call delivery | Local MCP hooks do not prove coverage; no adapter implemented here |
| `write_stdin` into an already approved interactive shell | No fresh PreToolUse is guaranteed | Disable/avoid such mutation channels under a claimed guard |

Registering a catch-all local hook would require explicit native trust and tests
of actual event envelopes. An exact name matcher that misses a renamed connector
is a gap. Unknown schemas, unknown release state and adapter errors should
produce a supported explicit denial on the covered mutation path, never an
allow. Do not request secrets through a model-visible payload.

The candidate denial envelope is
`hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny",
permissionDecisionReason: "…"}`. No such hook is installed by this change.
Official documentation warns that missing servers/tools, callback errors,
timeouts and malformed responses can fail a hook without blocking the action.
Other local hooks run concurrently; one cannot prevent another's side effects.
Disabled/untrusted hooks, unsupported hosted/specialized tool paths and hook
infrastructure failures prevent a fail-closed enforcement claim. A preflight
hook also leaves a read-before-write race even when it successfully denies known
published targets. A trusted hook is an additional guardrail, not complete
provider-side enforcement. Keep current denials binding across transports.

## Evidence and separate delivery stages

The deterministic suite is `tests/test_release_safeguards.py`; prototypes and
synthetic examples live in `evals/release-safeguards/`. Native policy tests require
an explicitly selected existing binary through `CODEX_TEST_BINARY`, avoiding a
package-manager shim that might auto-update. `codex execpolicy check` evaluates
argv against explicit temporary/source rule files and never runs the checked
release commands. CI without that binary skips native-only cases visibly.

Tests compare forbidden + prompt + a synthetic allow in both file orders;
forbidden remains binding. Reordered flags and raw HTTP paths deliberately
produce no matching template rule. The synthetic broad allow is a negative
fixture only; it is never shipped or installed. Public-note fixtures encode
reviewed retention/rejection examples; they do not measure model writing quality.

| Stage | Result for this task |
| --- | --- |
| Source | Instructions, inert template, offline models and tests; local commit only |
| Package release | Candidate versions prepared; no registry/tag/release publication |
| Installation | No plugin update or rule installation; temporary model homes only |
| Hook trust | No trust/configuration change; proposed hook remains unregistered |
| Reload | No client restart or reload performed |
| Runtime | Explicit-file CLI policy evaluation only; no new active guard or real release mutation verified |

## Sources

Verified on 2026-10-16:

- [OpenAI rules](https://developers.openai.com/codex/rules): active-layer discovery,
  startup/restart, most restrictive decision and explicit-file policy checks.
- [OpenAI hooks](https://developers.openai.com/codex/hooks): trust, local tool
  coverage, explicit denial and nonblocking infrastructure failures.
- [GitHub release API](https://docs.github.com/en/rest/releases/releases#update-a-release):
  stable release IDs and distinct draft/prerelease fields; no documented atomic
  draft-only update condition established by this investigation.
- Local `adapters/codex_agents/manager.py`, `server.py` and
  `tests/test_codex_agents.py`: existing role onboarding and ownership contracts.
