---
name: engineering-workflow
description: Choose the smallest sufficient engineering procedure for a requested codebase task and continue to its authorized endpoint.
---

# Engineering Workflow

Resolve the intended outcome, work source, exact checkout, existing edits and
requested delivery stage from the task and consumer guidance. Use the actual
host tools. This router chooses a primary procedure; it is not a checklist to
run every skill. A tiny understood change can go directly to implementation
and focused validation without a design document or new tests.

Choose by the unresolved task:

- Explain a code path or assess requested maintainability: [understand-codebase](../understand-codebase/SKILL.md).
- Investigate a failure: [diagnose-problem](../diagnose-problem/SKILL.md).
- Settle technical contracts: [design-change](../design-change/SKILL.md).
- Execute accepted intent: [implement-change](../implement-change/SKILL.md).
- Assess a candidate: [review-code](../review-code/SKILL.md).
- Strengthen regression evidence: [test-behavior](../test-behavior/SKILL.md).
- Exercise user behavior: [verify-product](../verify-product/SKILL.md).

Use specialist procedures only when they answer the task: domain modeling,
performance work, a decision prototype, verification maintenance, a substantial
phased refactor, or selected solution capture and refresh. A procedure may use
another for a concrete gap; do not require a chain simply because it exists.

Read relevant existing consumer knowledge when it can avoid repeated
investigation; follow the [retrieval guide](../_shared/references/project-knowledge.md).
Do not bootstrap a knowledge store or load unrelated history.

If delegation is authorized and useful, follow the
[native role guide](../_shared/references/native-roles.md). Otherwise complete
the procedure in the parent. Preserve existing authorization across routine
repairs and checks; return changed scope or uncovered promotion for decision.
For delivery tracking or publication, use available
`project-management:delivery-lifecycle` within its consumer policy.

For an opted-in task with available `codex_workflow_*` tools, maintain an explicit
task record with its issue, delivery stage, status and scoped candidate inputs.
Record check evidence and request review only at the intended checkpoint. Hook
nominations name a workflow and optional owned role; read that installed skill
and assign the role through the current spawn tool when useful. Record assignment
and completion separately, with the actual candidate and evidence. Unknown
results remain unknown; task records and hook output grant no new authority.

Check records default to native `capture_mode: "hook"`. If the client does not
provide typed shell status to hooks, explicitly configure future checks with
`capture_mode: "parent"` and record every actual tool-caller result through
`codex_workflow_evidence`. Use completed structured integer results for pass or
failure; if completion cannot be established, record `check_unknown` with a real
bounded artifact. The parent owns complete observed check history and must not
claim consecutive failures across an incomplete or ambiguous result. Changing
capture mode changes the task contract and makes earlier evidence stale. Never
infer exit status from command output. Hooks neither execute checks nor change
capture mode for the parent.

Finish with the result, evidence and remaining uncertainty at the requested
endpoint. Source edits, merge, release, deployment and provider operation are
distinct actions; routing grants none of them by itself.
