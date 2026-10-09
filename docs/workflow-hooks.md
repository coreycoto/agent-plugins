# Evidence-based Codex workflow hooks

This guide describes the optional workflow record and advisory skill routes
bundled with all four public plugins. Product Development and Project
Management also have selected routes that may nominate their own specialist
roles. Hooks capture deterministic facts and nominate a route. They do not load
a skill, spawn an agent, authorize an action, or replace the parent agent's
judgment. The parent loads the named skill, decides whether delegation helps,
assigns bounded work, and records the result.

## Opt in with an explicit task

Without a task record, workflow hooks do nothing. Initialize one through the
owning plugin's `codex_workflow_task` MCP tool. The task object requires:

| Field | Meaning |
| --- | --- |
| `id` | Stable task identifier. Reusing the same id updates the record; a new id starts a fresh task record and continuation budget. |
| `issue` | Current issue or task reference. |
| `delivery_stage` | The requested local, review, or later delivery stage as a record; it grants no authority. |
| `status` | `active`, `paused`, `blocked`, `waiting_for_approval`, or `complete`. Only active tasks receive nominations or a Stop continuation. |
| `paths` | Nonempty repository-relative input scope used for the current candidate fingerprint. |
| `checks` | An array of exact Bash command records, each with `id`, `command`, `checker`, and `environment`; optional `capture_mode` is `hook` (default) or `parent`. It may be empty. |
| `review_requested` | Whether the task explicitly requests a review nomination. |
| `continuation_limit` | `0` or `1`; bounds a Stop-triggered continuation for this task. |

For example, the parent can record a local documentation trial as follows (the
`cwd` and `session_id` are supplied from the current Codex session):

```json
{
  "id": "example-task",
  "issue": "Example issue for workflow routing",
  "delivery_stage": "local documentation trial",
  "status": "active",
  "paths": ["docs"],
  "checks": [],
  "review_requested": false,
  "continuation_limit": 1
}
```

Keep the task scope and checks accurate. The workflow adapter never executes a
check command. It watches for an exact configured Bash command in the current
working directory and records only a typed integer `exit_code`, candidate
fingerprint, check identity and private receipt reference. It does not retain
the command output or transcript. If the tool response lacks a typed exit code,
the work directory differs, or the candidate changes between pre- and
post-tool hooks, the result stays unknown and cannot trigger a failure route.

### Native shell status and explicit evidence

Codex's [hook contract](https://learn.chatgpt.com/docs/hooks) describes
`tool_response` as tool-specific JSON; it does not guarantee a shell exit code.
In the qualified Codex CLI 0.160.0 implementation,
[`ExecCommandToolOutput::post_tool_use_response`](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/core/src/tools/context.rs)
sends completed unified-exec command output as a string. Its structured
tool-caller result carries the exit code separately. A quiet success and quiet
failure can therefore produce the same hook response. A running command does
not yet have a completed hook response; a later `write_stdin` poll can deliver
the original command's completion. CLI qualification does not establish the
version of a separate desktop runtime.

For a correctly paired current check without a typed hook exit status, the hook
records an unknown reason and emits an advisory checkpoint. The parent reads
`codex_workflow_status`, checks the actual tool-caller result for a completed
integer exit code, saves a bounded repository artifact describing the observed
command and result, and records explicit evidence with `codex_workflow_evidence`.
Use `check_passed` for exit code zero, `check_failed` otherwise, and
`signature: "exit:<code>"`. Keep the configured check identity, current candidate
and a fresh observation id. This is parent-recorded evidence, not an automatic
native hook receipt.

If the caller result is incomplete or untyped, or the candidate or task contract
changed during the command, leave the result unknown. Never infer success from
an empty output, parse status-looking output text, or rerun a command merely to
manufacture evidence. Current unknown check summaries in workflow status explain
which checks still need evidence. A subsequent valid observation resolves that
status; an unknown still breaks the consecutive failure streak. The checkpoint
does not execute a check, grant permission, or request a Stop continuation.

On a client without typed native hook status, configure future checks with
`capture_mode: "parent"`. This explicitly disables native observation for those
checks; the parent records each actual tool-caller result through the evidence
tool. Otherwise every untyped native completion breaks the failure streak, even
when the parent later records its result. Selecting parent capture changes the
task contract, so earlier evidence is stale and must not be carried across that
change. Other checks can keep the default hook capture mode.

Parent capture requires a complete observed check history. Wait for a running
command to finish when appropriate. If completion cannot be established, record
`check_unknown`, with the configured `check_id`, an explanatory bounded
`signature` such as `unknown:completion_unavailable`, and a real artifact of
that observation. Unknown evidence never nominates a failure route and breaks
the streak, including when its artifact later becomes unavailable. Do not claim
consecutive failures across an incomplete or ambiguous result. Parent capture
does not execute a command or relax the caller's permissions.

The candidate fingerprint covers the Git HEAD, configured input scope, index
entries, and contents of scoped tracked and staged files plus nonignored
untracked files.
Deleted files and file modes are accounted for. If the candidate cannot be
read consistently, it is `candidate_unknown`; evidence and routes tied to an
older candidate are not current. Evidence references supplied explicitly must
identify an existing bounded regular file inside the repository. Hook-generated
check receipts are kept in private Codex state; command output is not copied
there. Recorded references retain file identity and metadata so ordinary edits,
replacement, deletion or symlink changes invalidate their evidence. This is a
freshness check, not a cryptographic assertion about evidence contents; the
reference check compares metadata without reading or hashing the referenced
file. A referenced file inside the configured input scope also contributes to
the candidate fingerprint. File contents are never stored in workflow records.

## Conditions nominate routes

Each plugin packages only routes it owns. Product Development defines:

| Condition | Route | When it is nominated |
| --- | --- | --- |
| `repeated_check_failure` | `product-development:diagnose-problem`; optionally `pd_diagnostician` | The same configured check has at least two consecutive equivalent failures for the current candidate and task contract. A pass, changed signature, unknown result, or stale observation breaks its streak. |
| `review_needed` | `product-development:review-code`; optionally `pd_reviewer` | The explicit task record has `review_requested: true`. |

Project Management defines:

| Condition | Route | When it is nominated |
| --- | --- | --- |
| `governance_mismatch` | `project-management:project-governance`; optionally `pm_governance_auditor` | Current-candidate evidence explicitly records a governance mismatch. |

Communication and Product Management add skill-only routes:

| Evidence condition | Route | Required details and trigger |
| --- | --- | --- |
| `prose_review_requested` | `communication:edit-prose` | `kind: "prose"`; the task requests editing supplied prose. |
| `communication_report_requested` | `communication:agent-communication` | Both `verified_refs` and `unfinished` are required in `details`; at least one list is nonempty. The task requests a progress report or handoff. |
| `document_draft_requested` | `communication:write-prose` | `audience` and `purpose`; the task requests a draft. |
| `customer_evidence_recorded` | `product-management:product-discovery` | `change: "new"` or `"conflicting"`; new or conflicting customer evidence is recorded. |
| `product_comparison_requested` | `product-management:product-prioritization` | `options` (2–16 unique items) and `constraints` (1–32 items); the task requests a comparison of supplied options under supplied constraints. |
| `requirements_handoff_requested` | `product-management:product-requirements` | `direction` and `outcome`; an accepted direction or outcome is handed to requirements work. |
| `experiment_criteria_recorded` | No route | This is a checkpoint required before experiment results can be recorded; criteria alone do not nominate a skill. |
| `experiment_results_recorded` | `product-management:product-experiments` | `experiment_id` and `criteria_observation_id`; results are linked to a prior criteria record for that experiment and task contract. |

These conditions are typed records, not semantic classification. Detail text
is nonblank, bounded to 512 characters, and contains no control characters;
experiment and observation identifiers are bounded safe IDs. The parent
records the request or evidence in the workflow record; the hook does not infer intent
from prose or inspect artifact contents. Skill-only routes have no nominated
agent role and require no agent installation or setup. Criteria evidence is
accepted only by a plugin that also configures the corresponding experiment
results route.

A route is a nomination with supporting evidence references and a candidate
fingerprint. It is emitted once for a task, scope, condition, candidate, and
route-catalog version. Changes to the candidate, task contract (including check
environment and review request), supporting evidence, or route assets make an
older route stale. The task contract includes its id, issue, delivery stage,
input paths, check definitions, and review request. Status and continuation
limit are excluded from the task fingerprint; status still controls whether
hooks can nominate. Referenced evidence files are checked by file identity and
metadata; the reference check does not hash or read their contents. Lifecycle
status and continuation-limit updates preserve the task's existing continuation
count. A stale route remains historical and
cannot be completed as evidence for the current candidate; the parent must
record fresh evidence or a new request if work is still needed. Paths should
name the task's input files. A drafted result can be saved as a separate
repository artifact and referenced without adding it to the input scope. If an
edit changes an input candidate, the old nomination is stale; hooks do not
invent a new request or restart a writing loop. A route in status `nominated`
has not been assigned or completed. The route tool supports a parent-managed
assignment without `agent_id`, including when the parent loads and follows a
skill in the current chat.

For manual evidence, call `codex_workflow_evidence` with `observation_id`,
`candidate`, `condition` (`check_failed`, `check_passed`, `check_unknown`, or
`governance_mismatch`, or one of the skill-route conditions above), and
`reference`. Check evidence also requires the configured `check_id` and a
bounded `signature`; governance and skill-route evidence must omit those check
fields. Skill-route evidence also supplies its condition-specific `details`
exactly as listed above. All explicit evidence uses a current candidate and an
existing bounded repository file reference. Communication `verified_refs`
and experiment criteria references are also bound to file metadata and checked
for freshness. The tool records references and typed fields, not file contents.
Use a fresh observation id for each
distinct fact and the candidate currently returned by
`codex_workflow_status`.

For example, record a request to edit an existing document with
`condition: "prose_review_requested"`, `details: {"kind": "prose"}`, and a
reference to that document. The `paths` scope names the input document; a
revised draft can be saved separately and referenced as the route outcome.
The parent then loads
`communication:edit-prose`, assigns that work in the current chat or through
an available role it owns, and records the assignment and completed outcome.

Experiment evidence uses an explicit two-record checkpoint:

1. Record `experiment_criteria_recorded` with an `experiment_id` and a
   repository reference to the agreed criteria artifact.
2. After the parent has actually observed and recorded results, record
   `experiment_results_recorded` with the same `experiment_id`, the prior
   `criteria_observation_id`, the results reference, and the current candidate.

The local adapter checks that the criteria record came first, names the same
experiment and task contract, and its referenced file metadata is still
unchanged. Criteria may belong to an earlier source candidate; results must
belong to the current candidate. This verifies local record order and reference
freshness only. It does not establish that the real experiment observation
occurred after criteria were set; the parent owns that factual judgment. Recording a
customer evidence change likewise records only a parent-supplied typed
assertion and file pointer; it does not establish that a provider or customer
check was performed. Criteria alone do not nominate Product Experiments.

## Parent-managed skill and agent handoff

Use `codex_workflow_status` to read the task, candidate, current evidence,
unresolved unknown checks, route freshness, and continuation count. It creates
no task state. When a route is
nominated, the parent should:

1. Check that its candidate, scope, evidence and route freshness still match
   the current task and user instructions.
2. Load and follow the named skill in the current chat. For routes that name a
   role, delegate only when the current spawn interface exposes that role and
   the parent can give it a bounded assignment and appropriate evidence.
3. Record `assigned` with `codex_workflow_route` only after the parent actually
   makes that assignment. `agent_id` is optional and records the assigned
   agent's identifier when available.
4. Record `completed` only after the work has returned, with outcome
   `passed`, `findings`, or `unknown` and an existing bounded repository file
   that supports the outcome. Record a child result and its validation pointer;
   a child-start or child-stop event alone is not a completed outcome.

Completion requires a real evidence file. Do not create a placeholder receipt
for a chat-only result. If the work has no suitable artifact, keep the route
assigned and summarize the outcome in the normal task response.

The route tool records these parent-managed events. It does not call the skill,
spawn a role, grant a role's default sandbox, or authorize provider, credential,
merge, release, publication, or deployment actions. Roles inherit the active
parent permissions. A nominated role may be unavailable in the current client;
the parent can use the skill in the current chat and record that route without
an `agent_id`. Communication and Product Management routes are skill-only.

The MCP tools are `codex_workflow_task`, `codex_workflow_status`,
`codex_workflow_evidence`, and `codex_workflow_route`. Each call includes the
current absolute `cwd` and `session_id`. The extension stores private records
per plugin, repository and session; they are not shared as policy or consumer
project records. The task's delivery stage remains descriptive. Repository
policy and permission boundaries stay in the consuming repository.

## Hook lifecycle

- **SessionStart:** If a task exists, restore its id, issue, status, stage,
  scope and current candidate. On compact restore, historical task instructions
  remain subordinate to the latest user and session instructions. Read the
  status tool for current evidence and route state.
- **PreToolUse / PostToolUse:** For checks in hook capture mode, pair only a matching configured Bash invocation
  with its typed exit code and unchanged candidate. A paired current command
  without typed status prompts the parent to record supported explicit evidence;
  checks in parent capture mode and other commands are ignored.
- **Stop:** With an active task, `continuation_limit: 1` permits at most one
  continuation when a new route is nominated and `stop_hook_active` is not
  already true. Set the limit to `0` to disable this. The hook does not repeat
  a nomination or loop on an active Stop hook.
- **Interrupt:** Store a small task id and status checkpoint with the candidate
  marked unverified, without scanning the worktree. This
  is a pointer for later recovery, not an independent source of instructions.

Hook state only exists for an explicitly initialized task. Inactive task
statuses do not nominate routes or request a Stop continuation. Hook failures
or unsupported/untyped events do not establish evidence. Do not treat missing
records as proof that work or review did not happen.

## Local source, activation and release

These files describe local source behavior. Editing them does not update an
installed plugin or reload an active Codex session. A local trial uses the
repository's normal build and candidate installation procedure. Changed native
hook definitions require Codex's hook trust review; installation and trust do
not establish that the active session exposes the named custom roles. Verify
the current MCP tools, active task behavior, and spawn selector separately.
Cloud discovery remains unverified.

Source preparation or a local trial does not publish the package. A release
requires the repository's separate release process and authorization. The
workflow records and route nominations themselves confer no promotion or
provider-operation authority.
