# Compare conditional guidance and named steering

Issue [#37](https://github.com/coreycoto/agent-plugins/issues/37) adds 17 original
synthetic read-only decisions. Public files define tasks and expectations; the
existing private evaluation workflow owns authorized model execution. These
visible smoke/deep examples assess recommendations, not executed repairs or
representative held-out effectiveness. No new runtime is introduced.

| Suite | Existing skill | Added cases |
| --- | --- | --- |
| [premise-reset](premise-reset/evals.json) | diagnose-problem | Shared premise, allocator defect, even census, required affinity, routine bug, sampled profile, incomplete capture |
| [resource-bounds](resource-bounds/evals.json) | improve-performance | Partial-cycle peak, over-budget repair, sampled maximum |
| [repeatable-work](repeatable-work/evals.json) | phased-refactor | Mechanical tool qualification, simple direct edit |
| [principle-steering](principle-steering/evals.json) | engineering-workflow | Named premise reset, routine request, named coordination within authority |
| [engineering-judgment](engineering-judgment/evals.json) | design-change | Independent status facts, canonical capacity claim |

## Freeze the comparison before running

Use identical tasks, available tools, model and budgets in fresh declared-input
workspaces. Freeze exact procedure and supporting-resource bytes for three arms:

A. Prior procedures and their closure at
`d35ee5333a569884af424f8d76d01b619b7fd98b`.
B. Revised procedures and conditional references, with named steering absent.
In this counterfactual staged closure, omit the new steering paragraph from
engineering-workflow and the engineering-principles.md index. Freeze the derived
snapshot and hashes before running; keep other procedure bytes equal to C and
verify no dangling link remains in the measured closure.
C. Final revised procedures and references, including named steering.

Keep explicit body-loading and natural selection separate. Named requests test
steering, not ordinary automatic discovery. Unnamed cases assess the relevant
diagnosis/design/performance procedure; the ordinary router case checks overhead.
Principle mentions establish neither reading, adherence nor useful outcomes.

Keep expected outputs, rubrics, assertions and original fixtures outside the
measured workspace. Stage only workspace_files and the selected instruction
closure. Use neutral project-shaped paths and ordinary prompts; do not reveal
arm labels or grading expectations. Semantic judges receive frozen tasks and
raw facts with sanitized arm/model identities. The index itself is part of the
treatment and cannot be hidden in C.

Alternate arm order across repeated paired cases. Report all attempt and grading
denominators, failures and unavailable observations, separately by model/client.
Judge required behavior and legitimate exceptions first, then unnecessary work
and caller/operating burden, then observed task wall time and token usage. Keep
setup/grading costs separate and missing counters explicit. LOC or source-size
reductions alone establish neither quality nor savings.

Calibrate semantic judges with requirement-derived correct answers and deliberate
wrong answers before trusting results. Controls must distinguish a 96 MiB peak
from net-zero growth, uniform defects from worker skew, independent status facts
from exclusive claims, and a useful codemod from a gratuitous script. Preserve
reasonable alternative designs. Keep controls and expected grades outside the
measured workspace. Add independent unseen domains before broader adoption;
do not tune on validation outcomes and keep calling them held out.

## Deterministic qualification

The four new suites reuse _readonly_oracle.py; engineering-judgment retains
_engineering_oracle.py. Freeze each helper in its immediate-parent layout with
original fixtures and oracle entrypoints. These helpers compare source bytes
without executing fixture code. They reject edits, additions, deletions and
symlinks; separate semantic rubrics judge recommendations. The runner must
independently freeze/hash its .agents instruction closure.

```sh
uv run --locked pytest tests/test_upgrade_simplification_evals.py tests/test_engineering_workflows.py
```

This qualifies staging and scope graders, including their independence from
response wording. It does not calibrate semantic judges or establish model
effectiveness, actual body exposure, native discovery or consumer activation.
Provider-funded trials need separately authorized execution through the existing
workflow; these qualifications remain unrun until observed.
