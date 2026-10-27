# PR continuation and bounded review trials

These eleven synthetic read-only cases exercise existing skills:

| Suite | Procedure | Decisions |
| --- | --- | --- |
| `pr-continuation` | `project-management:handoff-work` | Already-solved goal, changed invariant ownership, valid rebase with concurrent remote work, verified human contributor credit |
| `review-iterations` | `product-development:review-code` | Affected follow-up scope, serious rare defect at the pass limit, resolved review with only optional feedback |
| `ready-pr-handoff` | `project-management:delivery-lifecycle` | Queued PR without control authority, stale control result, verified open ready PR, local-only endpoint |

The fixtures supply facts and task boundaries, not expected recommendations.
Independent semantic rubrics and correct/incorrect calibration responses remain
grader-only. Each suite has one smoke case; all cases belong to deep. Three
checks separate fixture preservation, workflow judgment and authority/evidence
limits. The shared frozen `_readonly_oracle.py` checks only product-file scope;
the runner must separately freeze and verify the loaded instruction closure.

Run `uv run --locked pytest tests/test_upgrade_simplification_evals.py` for
deterministic staging, preservation and frozen-grader sensitivity. This accepts
unchanged inputs and rejects edited, added, deleted and symlinked fixtures; it
does not score the recommendations or execute Git, GitHub, rebase or queue APIs.

For semantic trials, compare prior and candidate skill closures on the same
fixtures, model, tool permissions and finite budgets, with an optional
no-procedure arm. Load only the selected procedure and its contained references.
Keep rubrics, controls and grader support outside measured workspaces. Calibrate
the fixed grader on the supplied correct and incorrect responses before scoring
model outputs, and retain actual results, errors and missing observations.
Assess each decision and legitimate exception rather than averaging away an
authority violation or serious defect. Do not describe deterministic author
qualification or calibration response metadata as observed model effectiveness.

Live branch concurrency and automatic-merge controls require separate consumer
and runtime verification; these supplied snapshots cannot establish it.

The optional evaluator's current closure loader confines resources to `skills/`.
Its planning check accepts the two Project Management suites, but rejects
`review-code`'s existing transitive links to package-level license files. Full
closure staging for that suite remains unavailable in that runner. Preserve the
supporting content and report this as a harness limitation, not a model failure
or permission to omit references. Semantic model trials remain unrun for all
three suites; fixture qualification and planned workspaces do not replace them.
