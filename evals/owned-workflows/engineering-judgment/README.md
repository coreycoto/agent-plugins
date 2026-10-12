# Engineering judgment and specialist trials

Three new specialist suites each supply an executable artifact task and four
selection queries. This directory supplies five read-only design judgments.
These are original synthetic fixtures, not private operational data. All are
smoke/deep cases; no claim of broader held-out coverage is made.

## What is independently checked

`_engineering_oracle.py` and each suite's oracles, evals.json expected output,
and rubrics are grader-only. Stage only workspace_files and the selected skill
closure in the measured workspace. Freeze the helper, entrypoints and original
fixtures outside it, preserving the immediate-parent layout. Grade as:

```sh
python -I -B oracles/check.py WORKSPACE RESPONSE_PATH EVENTS_PATH
```

The grader never imports or executes submitted Python. It checks unchanged
inputs, allowed artifact paths, a replayable unsafe protocol trace, migration
SQLite snapshots, or exact known dataset defects/exceptions. The protocol oracle
uses an independent event interpreter rather than the fixture's next-state code.
The migration oracle queries retained databases read-only. A separate assertion
checks a successful completed command event for the task's Python entrypoint.
It accepts a direct Python command (optional -B/-I) and a single sh/bash/zsh -c/-lc
wrapper; other forms remain unverified, not inferred from prose.

These checks establish narrow artifact facts and entrypoint execution, not that
the program computed its results honestly or explored all states. Independent
semantic review must inspect the authored analysis/rehearsal/assessment and
claimed limits. Handcrafted correct answers can pass value checks; report that
limitation. Events must be captured by the runner outside agent edit scope.
Exit 1 with FAIL is a demonstrated submission failure; unexpected errors/timeouts
are grader errors. The grader is not a security sandbox. Run agent tasks only
inside the evaluation runner's isolated workspace with scoped tools/access.

The harness-owned `.agents` closure is excluded from product-file inventory.
The runner must independently freeze/hash that closure; the exclusion alone does
not establish instruction integrity. No fixture, raw transcript or secrets from
consumer repositories belong in this public corpus.

## Compare the proposed packaging, not just against no guidance

Freeze three arms before running:

A. Existing general skills from the fixed base revision.
B. Improved general skills plus the relevant specialist procedure as an optional
reference, without the new discoverable name.
C. The candidate catalog including the specialist entrypoints.

Hold task inputs, tool permissions and budgets comparable. Compare explicit-body
outcomes separately from automatic selection among neighboring skills. Record
actual loaded resource bodies, package/client/model identity, task outcome,
missed defects, false alarms, unnecessary edits, latency and cost. Report per
model and client; do not infer transfer from one model to another. Include an
unavailable-tool case and a routine change that needs no specialist.

Train/validation trigger queries are authored here for future evaluation. Do not
tune on validation outcomes and continue calling them held out. Before broader
adoption, add independent domains and adversarial cases beyond these visible
fixtures; the examples are not a representative usefulness benchmark. Use the
existing evaluation workflow, not a new runner. A useful result may favor the
reference-only arm or no new skill.

## Local qualification

```sh
uv run --locked pytest tests/test_engineering_workflows.py
```

Author checks accept useful controls, reject missing/circular scope claims,
invalid traces, wrong snapshot values, false freshness/liveness claims, modified
inputs and unobserved commands. These are fixture/grader tests, not agent trials.
Native discovery, actual agent adherence, paired effectiveness and production
rehearsal remain unrun until separately observed. The source PR does not install
or release the candidate.
