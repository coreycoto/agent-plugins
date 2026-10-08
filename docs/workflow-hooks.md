# Evidence-based Codex workflow hooks

This guide describes the optional workflow record and advisory routes bundled
with the Product Development and Project Management Codex plugins. Hooks can
capture deterministic facts and nominate a skill or role. They do not load a
skill, spawn an agent, authorize an action, or replace the parent agent's
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
| `paths` | Nonempty repository-relative source scope. |
| `checks` | An array of exact Bash command records, each with `id`, `command`, `checker`, and `environment`; it may be empty. |
| `review_requested` | Whether the task explicitly requests a review nomination. |
| `continuation_limit` | `0` or `1`; bounds a Stop-triggered continuation for this task. |

For example, the parent can record a local implementation task as follows (the
`cwd` and `session_id` are supplied from the current Codex session):

```json
{
  "id": "issue-15",
  "issue": "#15 Add evidence-based Codex hook routing to owned skills and agents",
  "delivery_stage": "local implementation",
  "status": "active",
  "paths": ["src", "tests"],
  "checks": [
    {
      "id": "focused-tests",
      "command": "uv run pytest tests/test_target.py",
      "checker": "pytest",
      "environment": "project virtual environment"
    }
  ],
  "review_requested": true,
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

The candidate fingerprint covers the Git HEAD, configured scope, index entries,
and contents of scoped tracked and staged files plus nonignored untracked files.
Deleted files and file modes are accounted for. If the candidate cannot be
read consistently, it is `candidate_unknown`; evidence and routes tied to an
older candidate are not current. Evidence references supplied explicitly must
identify an existing bounded regular file inside the repository. Hook-generated
check receipts are kept in private Codex state; command output is not copied
there. Recorded references retain file identity and metadata so ordinary edits,
replacement, deletion or symlink changes invalidate their evidence. This is a
freshness check, not a cryptographic assertion about evidence contents; those
contents are neither inspected nor stored by the workflow adapter.

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

A route is a nomination with supporting evidence references and a candidate
fingerprint. It is emitted once for a task, scope, condition, candidate, and
route-catalog version. Changes to the candidate, task contract (including check
environment and review request), supporting evidence, or route assets make an
older route stale. Lifecycle status and continuation-limit updates preserve
the task's existing continuation count. A route in status `nominated` has not been assigned or
completed.

For manual evidence, call `codex_workflow_evidence` with `observation_id`,
`candidate`, `condition` (`check_failed`, `check_passed`, or
`governance_mismatch`), and `reference`. Check evidence also requires the
configured `check_id` and a bounded `signature`; governance evidence must omit
those check fields. The evidence tool records the reference and typed fields,
not the file contents. Use a fresh observation id for each distinct fact and
the candidate currently returned by `codex_workflow_status`.

## Parent-managed skill and agent handoff

Use `codex_workflow_status` to read the task, candidate, current evidence, route
freshness, and continuation count. It creates no task state. When a route is
nominated, the parent should:

1. Check that its candidate, scope, evidence and route freshness still match
   the current task and user instructions.
2. Load and follow the named skill in the current chat. If useful, assign the
   named role only when the current spawn interface exposes it and the parent
   can give it a bounded assignment and appropriate evidence.
3. Record `assigned` with `codex_workflow_route` only after the parent actually
   makes that assignment. `agent_id` is optional and records the assigned
   agent's identifier when available.
4. Record `completed` only after the work has returned, with outcome
   `passed`, `findings`, or `unknown` and an existing bounded repository file
   that supports the outcome. Record a child result and its validation pointer;
   a child-start or child-stop event alone is not a completed outcome.

The route tool records these parent-managed events. It does not call the skill,
spawn the role, grant its default sandbox, or authorize provider, credential,
merge, release, publication, or deployment actions. Roles inherit the active
parent permissions. A nominated role may be unavailable in the current client;
the parent can use the skill in the current chat and record that route without
an `agent_id`.

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
- **PreToolUse / PostToolUse:** Pair only a matching configured Bash invocation
  with its typed exit code and unchanged candidate. Other commands are ignored.
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
