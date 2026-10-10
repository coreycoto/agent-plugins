---
name: test-behavior
description: Add or improve independent regression evidence through an appropriate public contract, avoiding assertions that reproduce implementation logic.
---

# Test Behavior

Identify the accepted behavior and its source, invariant, credible failures and
independent expected results before meaningful behavioral implementation.
Inspect current tests and public entry points; name the owning boundary and
prefer its existing suite. Match the seam to the actual scenario: a multi-caller
or persistent-state bug cannot be locked down by an unrelated shallow helper
test. Read the
[behavioral testing guide](../_shared/references/behavioral-testing.md) when
selecting or strengthening the evidence.

Use an independent expected result: a worked specification example, known-good
fixture, invariant or separately derived oracle. Do not compute expectations
with the same algorithm under test, snapshot the current bug, or merely confirm
that metadata and implementation agree. Keep fixtures representative and failure
messages specific.

For test-first work or a regression repair, observe the intended failure before
implementation or repair, then the pass afterward. Import or setup errors do
not establish the behavioral failure. Build one useful test-and-code slice at
a time; exhaustive failure lists and all tests up front are unnecessary.
Existing behavior may still need new tests. For consequential tests or
consolidation, use a known bad case or bounded mutation
in isolated scratch when it adds confidence; investigate survivors rather than
chasing a universal mutation score.

Control time, randomness, filesystem and external boundaries only where needed.
Keep deterministic contract tests independent of provider accounts. Mocks
should preserve boundary behavior, not bypass the very path being tested.
Separate synthetic tests from real integration or product observation and label
what each proves.

Keep tests at additional layers when they catch distinct failure modes; name
those differences. Retiring duplicate tests requires evidence that retained
cases still catch their regressions; coverage percentage alone is insufficient.
Do not add tests for trivial reversible changes or mirror internal structure
simply to increase counts.

Account for task-created probes before finishing: retain unique durable tests,
integrate useful assertions into the owning suite, or remove authorized owned
diagnostic residue. Preserve useful failure evidence and uncertain ownership.
Pre-existing test deletion or consolidation needs its own task scope.

Complete with the behavioral contract, seam, independent oracle, observed
failure/pass or sensitivity evidence, focused command and remaining limitations.
Run affected consumer-required checks. A green suite does not establish behavior
outside the exercised contract.
