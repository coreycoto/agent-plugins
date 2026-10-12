# Testing-guidance trial corpus

This corpus uses the existing external-suite schema 3 and trigger schema 2. It
adds one artifact task and nine scenario judgments for `test-behavior`. The smoke
suite has the artifact task and three judgments; deep adds six judgments. These
are original fictional examples, not copied book code or private consumer data.

The checkout task changes tests only. Its frozen oracle runs the submitted suite
against a corrected control and four distinct defective implementations. It
requires actual assertion failures, not import errors, empty discovery, skips or
timeouts. This qualifies those particular fault detections, not all valid inputs
or the quality of every assertion. The scenario cases require semantic grading;
unchanged-file checks only establish their read-only scope.

Use the trial instructions in the [parent corpus guide](../README.md), selecting
`product-development:test-behavior` and this eval root. Preserve prompts, source
and tool/model settings for a paired baseline/candidate comparison. Freeze the
oracles and expected-output/rubric data outside the measured workspace. Preserve
the relative `fixtures/` and `oracles/` layout. The runtime independently checks
its `.agents/` procedure closure, which artifact inventory guards exclude.

The sensitivity oracle executes submitted Python tests in bounded subprocesses
with scrubbed environment and disposable directories. This is NOT a security
sandbox: use the evaluator's disposable execution host without credentials or
provider access. Do not run adversarial submissions on a trusted workstation.
No model or provider calls are made by the deterministic fixture checks.

```sh
uv run --locked pytest tests/test_testing_guidance.py
```

These tests qualify the grader against good, circular, empty, broken, skipped and
out-of-scope submissions, and validate the new local reference/corpus structure.
They do not prove that an agent loaded, followed or benefited from the skills.
No paired agent or native-discovery trial is claimed by this contribution.
The train/validation split is an authored evaluation plan, not a claim that a
held-out measurement has occurred. Never reuse tuned validation results as held out.

## Follow-on consumer evaluation

Run source-index recovery, fixture isolation, exact-artifact and test-retirement
cases against a bounded consumer checkout through its normal workflow. Grade
preserved behavior, meaningful fault detection, false alarms, unnecessary edits,
remaining evidence gaps and execution cost. Include an ordinary small edit where
invoking the entire testing library would be a regression. Keep product-specific
fixtures and results in that consumer, not this public corpus.
