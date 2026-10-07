---
name: test-behavior
description: Add or improve independent regression evidence through an appropriate public contract, avoiding assertions that reproduce implementation logic.
---

# Test Behavior

Identify the behavior, acceptance source and regression the test must catch.
Inspect current tests and public entry points before choosing the seam. Match
the seam to the actual scenario: a multi-caller or persistent-state bug cannot
be locked down by an unrelated shallow helper test. Read the
[behavioral testing guide](../_shared/references/behavioral-testing.md) when
selecting or strengthening the evidence.

Use an independent expected result: a worked specification example, known-good
fixture, invariant or separately derived oracle. Do not compute expectations
with the same algorithm under test, snapshot the current bug, or merely confirm
that metadata and implementation agree. Keep fixtures representative and failure
messages specific.

For test-first work or a regression repair, observe the intended failure before
the fix, then the pass after it. A failing import or setup is not the behavioral
failure. Build one useful slice at a time so each observation informs the next.
For already implemented behavior, prove the test's sensitivity with a known
bad case or a bounded mutation in isolated scratch when that adds confidence.

Control time, randomness, filesystem and external boundaries only where needed.
Keep deterministic contract tests independent of provider accounts. Mocks
should preserve boundary behavior, not bypass the very path being tested.
Separate synthetic tests from real integration or product observation and label
what each proves.

Retain distinct contracts when consolidating tests. Removing duplicates requires
evidence that remaining cases still catch their regressions; coverage percentage
alone is insufficient. Do not add tests for trivial reversible changes or
mirror internal structure simply to increase counts.

Complete with the behavioral contract, seam, independent oracle, observed
failure/pass or sensitivity evidence, focused command and remaining limitations.
Run affected consumer-required checks. A green suite does not establish behavior
outside the exercised contract.
