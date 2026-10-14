# Version-upgrade reference trials

These synthetic read-only decisions exercise design-change with its optional
version-upgrade catalog. Cases cover a default that changes without a signature
change, an unused removed API, an unavailable analyzer and a routine patch bump.
The invented package and supplied release material avoid provider accounts and
do not describe a real dependency's compatibility.

The frozen source-preserved assertion checks only unchanged workspace files.
It never imports pricing.py. The separate semantic rubric judges affected-site
selection, discriminating examples, tool-evidence limits and proportional scope.
An unchanged workspace alone does not establish a useful or correct catalog.

Follow the [corpus staging and grader contract](../README.md): stage only declared
workspace_files and the selected skill closure. Keep expected outputs, rubrics,
original fixtures, assertions and _readonly_oracle.py outside the agent workspace;
the runner independently freezes them and the exposed instruction closure.

Compare the fixed base design-change closure with the candidate closure using
the same task inputs, model/client, access and budgets. Record actual reference
exposure, missed deltas, false positives, unnecessary work, latency and cost.
These visible smoke/deep cases are not held-out or representative coverage.

Local qualification:

```sh
uv run --locked pytest tests/test_upgrade_simplification_evals.py
```

Author tests qualify source preservation and grader separation. Semantic model
trials, automatic reference use and comparative effectiveness remain unrun until
observed through the existing evaluation workflow; no new runner is introduced.
