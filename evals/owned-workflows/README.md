# Owned workflow trial corpus

This author-only corpus supplies one small artifact task for each of five Product
Development procedures: diagnosis, direct implementation, review, product
verification, and refreshing existing knowledge. Each task belongs to both
`smoke` and `deep`; this initial corpus has no extra deep cases. These are local
consumer fixtures, not plugin runtime files or operational repositories.

`evals.json` uses external-suite schema 3. Its ordinary task prompt and declared
`workspace_files` form the measured workspace. `expected_output` and assertion
scripts are grader-only and must stay outside that workspace. Trigger queries
use schema 2, with a positive and near miss in each of train and validation.
Do not tune a description against held-out validation results and then report
those same results as held out.

Each assertion runs independently as:

```sh
python -I oracles/CHECK.py WORKSPACE RESPONSE_PATH EVENTS_PATH
```

Exit 0 means pass, exit 1 with the assertion's `FAIL:` report means a demonstrated
failure, and an unexpected traceback, another exit or timeout is a grader error.
Each suite declares top-level `grader_support: ["_oracle_support.py"]`, an
immediate-parent filename. The runtime freezes and hashes the declared helper,
assertion scripts and source fixtures outside the measured workspace, preserving
their original relative layout. Entry points resolve the shared standard-library
helper from that frozen location, two directory levels above each script.
Copying only an entry point is unsupported. Assertions never edit the submitted
workspace. Temporary copies qualify regression and review reproducers against
both the broken original and a corrected comparison.

The runtime stages the procedure closure in the measured workspace's
`.agents/skills/` and independently verifies that its exact byte inventory
remains unchanged. Product-file inventory assertions exclude `.agents/**`
because that namespace belongs to the harness; unexpected files in the product
workspace still fail. This exclusion does not establish closure integrity on
its own. The frozen evaluator snapshot and the runtime's closure comparison
are separate checks.

The verification case accepts only successful completed native command events
whose commands and observed JSON identify separate add/list invocations. Its
parser supports direct Python commands and native `sh`, `bash`, or `zsh` `-c` /
`-lc` wrappers. Other invocation forms remain unverified; a narrated command,
started event, nonzero exit or unexplained output cannot establish product
success. Saved evidence must survive disposal of the explicitly owned scratch
store, while existing user data and source stay intact.

Qualify the fixtures locally from this public repository:

```sh
uv run --locked pytest tests/test_owned_workflow_fixtures.py
uv run --locked ruff check evals/owned-workflows tests/test_owned_workflow_fixtures.py
```

These tests prove that the graders accept corrected artifacts and reject
specific broken behavior. They make no claim about skill discovery, model
adherence, usefulness in a consumer project, or a provider session.

The evaluation runtime is maintained separately in the private Agent Plugins
project. From that project's checkout, plan a paired baseline and candidate
trial against this public corpus (replace the three explicit paths):

```sh
public_repo=/absolute/path/to/agent-plugins
trial_artifacts=/absolute/path/to/local-trial-artifacts

uv run --locked python -m agent_plugins.agents.evals.evaluate_skill_outputs \
  --repo-root "$public_repo" \
  --skill product-development:diagnose-problem \
  --eval-root "$public_repo/evals/owned-workflows/diagnose-problem" \
  --tier smoke --baseline-without-skill --no-run \
  --artifact-root "$trial_artifacts/output"

uv run --locked python -m agent_plugins.agents.evals.evaluate_skill_triggers \
  --repo-root "$public_repo" \
  --skill product-development:diagnose-problem \
  --eval-root "$public_repo/evals/owned-workflows/diagnose-problem" \
  --mode real --runs 1 --no-run \
  --artifact-root "$trial_artifacts/trigger"
```

Select another suite by changing both `--skill` and `--eval-root`. `--no-run`
prepares the local plan without model or provider calls. Authorized execution
requires an explicit `--model MODEL` and removal of `--no-run`. A trigger proxy
is a separate deterministic check (`--mode proxy`), not native discovery proof.
The public repository does not depend on or ship that private runtime.

Assess package/session provenance, exact skill-body exposure, procedure
adherence, independently checked artifacts, and baseline comparison separately.
An absent or unsupported skill-body observation is unknown, not proof of a
negative trigger. One case per procedure is a smoke qualification rather than a
representative usefulness benchmark; add cases only for observed gaps or a
specific adoption decision.
