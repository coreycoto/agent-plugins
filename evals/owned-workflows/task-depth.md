# Compare task depth within existing workflows

Issue [#39](https://github.com/coreycoto/agent-plugins/issues/39) adds ten original
synthetic read-only tasks using existing skill entrypoints. These are visible
smoke/deep cases for a bounded adoption decision, not representative held-out
coverage or proof of model effectiveness.

| Suite | Existing skill | Cases |
| --- | --- | --- |
| task-depth-development | product-development:engineering-workflow | Equivalent work, routine label, unavailable profile, requested delivery stages |
| task-depth-product | product-management:product-discovery | Cohort composition, settled requirement, unavailable retention evidence |
| task-depth-writing | communication:write-prose | Request versus attempt evidence, prompt rewrite only, concise status |

The source references are described in [conditional task depth](../../docs/task-depth.md).
There is no new discoverable command, agent or evaluation runtime.

## Freeze the comparison

Use identical task inputs, available tools, model and resource budgets in fresh
declared-input workspaces. Freeze exact package and supporting-reference bytes:

A. Current existing procedures and closure at
`c3e693ee407481298e29f71f3eeca764e6108fa7`.
B. The candidate existing procedures with their conditional depth references.
C. An experimental command that explicitly loads the same reference as B, using
the existing authorized runner's supported staging mechanism. If that mechanism
is unavailable, leave C unrun rather than create a runtime or publish a skill.
Freeze and record its exact wrapper, trigger description, closure and invocation.

Keep B and C's substantive guidance equal. C must preserve prompt-rewrite versus
execution authority, so its effects are not confounded by an extra permission
gate. Compare explicit body exposure separately from natural task selection;
explicit command invocation does not prove automatic discovery. Record native
body-use observations when available and leave unsupported observations unknown.

Alternate arm order across repeated paired cases. Record all attempt and grading
denominators, unavailable tools and failures, separately per model and client.
Assess correct conclusions, method fit, evidence traceability, scope violations,
unnecessary work, task wall time and token/cost evidence. More elaborate language
or naming a discipline is not a successful outcome. Keep setup and grading costs
separate. Adopt a command only if its incremental usefulness warrants discovery
and maintenance cost; retaining only references or reverting them remain valid.

## Grading and boundaries

Stage only declared workspace_files and the selected procedure closure. Keep
evals.json, rubrics, expectations, _readonly_oracle.py and oracle entrypoints
outside the measured workspace. Freeze/hash fixtures and graders independently,
preserving the immediate-parent helper layout. The runner must also freeze and
verify the exact .agents instruction inventory; the scope helper excludes that
namespace and cannot establish instruction integrity.

The unchanged-source assertions check file bytes and reject unexpected product
artifacts or symlinks. They deliberately accept an unsupported written answer:
independent semantic grading must reject it. They establish no evidence that a
method ran, a draft was understood or an authorized implementation continued.
The delivery-stage task checks recommended actions only. Before claiming actual
continuation, use the existing runner and suitable execution tasks with observed
completed-command evidence; these read-only cases are insufficient.

Calibrate semantic judges with independently worked controls before a trial:
candidate builds complete only 60/100 units; aggregate adoption is 4/6 then 3/6,
while organic cohorts are 4/5 then 2/2; the delivery ledger has four requests,
five attempts, two delivered requests, one queued and one unknown at cutoff.
Also include wrong controls: skipped work is a speedup, composition proves
causation, a timeout proves failure, a second agent's agreement is ground truth,
or a routine edit requires expert interviews. Keep controls outside measured
workspaces. Do not require one exact tool or prose shape when alternatives answer
the same question faithfully.

The fixtures are synthetic and sample-limited. Add independent unseen domains
and adversarial controls before broader adoption. Include real execution-stage
and prompt-rewrite tasks separately; provider-funded trials need their own
authorization. These cases do not add trigger train/validation coverage. Do not
tune on observed validation outcomes and continue calling them held out.

## Author qualification

```sh
uv run --locked pytest tests/test_upgrade_simplification_evals.py
```

This qualifies metadata, staging, frozen scope graders and mutation sensitivity.
Normal publisher checks qualify package integrity and attribution. Semantic judge
calibration, paired model trials, native discovery, actual body use, execution
continuation and reader comprehension remain unrun until separately observed.
