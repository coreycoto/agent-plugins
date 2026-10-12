# Refactor a test suite without losing its purpose

Source basis: Meszaros chs. 2/12/15-17/24; GOOS chs. 20-24; Feathers ch. 18;
Fowler chs. 2-4. See [source map](sources.md).

## Diagnose before moving files

Pick a bounded capability. Inventory its important conditions, test entrypoints,
fixtures, helper dependencies, runtime requirements and current failures. Read
both assertions and setup. Establish a fixed baseline and retain which evidence
is unknown. Do not equate repeated executed lines with redundant tests.

| Symptom or smell | Investigate | Candidate improvement |
| --- | --- | --- |
| Obscure Test / Mystery Guest | Hidden cause or unrelated fixture detail | Minimal fixture and visible causal values |
| Conditional Test Logic | Adaptation to uncontrolled state or unexecuted checks | Explicit cases and Guard Assertions |
| Assertion Roulette | Failure gives no condition or meaningful diff | Focused condition and diagnostic assertions |
| Erratic Test | Shared state, time, asynchronous work or resources | Isolation and controlled synchronization |
| Fragile Test | Incidental representation or collaborator internals | Public behavior and precise expectations |
| High Test Maintenance Cost | Coupled fixtures, duplicate conditions, unclear ownership | Narrow helper contracts and evidence-backed consolidation |
| Hard-to-Test Code | Implicit dependencies or mixed responsibilities | A justified production seam or Humble Object |

These are hypotheses to investigate, not style violations inferred from a file's
length. A difficult test can reveal a production-design problem; a new fixture
abstraction may merely hide it.

## Choose organization deliberately

Meszaros presents Testcase Class per Class, per Feature and per Fixture as
alternatives. Translate these to files/modules/describe blocks without insisting
on classes in a functional language. Feature grouping helps find consumer
conditions. Fixture/state grouping can clarify a stateful component. Class grouping
is convenient when it matches a cohesive contract, but should not fossilize every
private production method.

Keep physical ownership separate from runtime selection. Existing discovery,
tags and task runners can select fast, database, native or hosted subsets without
a global directory migration. Preserve compiler roots, discovery patterns,
parameterized identities and CI selectors during movement. An excluded test is
not a faster test.

## Sequence changes for reviewability

Establish missing protection first. Change fixture construction without changing
expected meaning. Move or rename tests mechanically in a separate reviewable
step. Then improve assertions or consolidate conditions with explicit rationale.
Perform production decomposition under `phased-refactor`, protecting the contract
with tests that need not mirror the new implementation structure.

Reuse setup when it reduces conceptual duplication. Do not collapse independent
oracles into one production-derived answer, or replace readable cases with a
large branching test interpreter. A lifecycle test may deliberately exercise
several transitions for one recovery condition; splitting it must preserve that
temporal relationship. Do not delete a wait/check before understanding whether
it is a synchronization boundary rather than a duplicate assertion.

For each retired case record its condition, old detection, retained replacement
and why the replacement covers the same fault at an adequate boundary. A known
bad case or bounded defect probe can strengthen this claim. Retain separate
native, wiring or resource tests when they detect a different failure. No deletion
quota, target file count, blanket snapshot regeneration or automatic flaky-test
quarantine follows from this procedure.

## Measure equivalent work

Compare like-for-like case selection, fixture sizes, runtime versions, warm/cold
caches, workers and instrumentation. Record wall time and variability, not just
a single best run. A smaller fixture must still cross the boundary that gave it
meaning. Share immutable setup or compile once where appropriate; retain a real
fresh runtime in tests whose condition is restart or lifecycle behavior.

Finish with the preserved conditions, discovery/type-check parity, isolated/order
checks, diagnostic improvements, measured cost and residual risks. Keep the
consumer's existing release/candidate checks; faster development feedback is a
complement to them.
