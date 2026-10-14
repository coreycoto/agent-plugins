# Diff-scoped simplification reference trials

These three synthetic read-only decisions exercise implement-change with its
optional simplification reference. They assess a newly introduced forwarding
helper, a shared authorization boundary and already-clear None handling. Each
prompt selects one case; unrelated and concurrent work stays outside its scope.

The frozen source-preserved assertion checks only that the supplied brief remains
unchanged. A separate semantic rubric judges the proposed refinement, preserved
effects and caller contracts, valid no-change outcomes and scope. These trials
assess recommendations, not execution of a code edit or its behavioral tests.

Follow the [corpus staging and grader contract](../README.md): only declared
workspace_files and the selected skill closure enter the measured workspace.
Expected answers, rubrics, original fixtures, assertions and _readonly_oracle.py
stay frozen outside it. Instruction integrity is independently checked by the
runner, not inferred from the assertion's exclusion of .agents.

Compare fixed base and candidate implement-change closures with identical task
inputs, model/client, access and budgets. Record actual reference exposure,
unnecessary edits proposed, missed behavioral changes, preservation of useful
boundaries, latency and cost. An unchanged fixture is not a correctness score.
These visible smoke/deep cases are not held-out or representative coverage.

Local qualification:

```sh
uv run --locked pytest tests/test_upgrade_simplification_evals.py
```

Author tests qualify fixture/grader integrity. Semantic model trials, execution
of refinements and comparative effectiveness remain unrun until separately
observed through the existing evaluation workflow.
