---
name: test-behavior
description: Design specification/regression tests or explicitly labeled characterization through a faithful boundary, with meaningful oracles, isolated fixtures and observable results.
---

# Test Behavior

Choose specification/regression, characterization or experiment explicitly. For
specification/regression, identify the accepted behavior and its source, invariant,
credible failures and independent expected results before implementation.
Inspect current tests and public entry points; name the owning boundary and
prefer its existing suite. Match the seam to the actual scenario: a multi-caller
or persistent-state bug cannot be locked down by an unrelated shallow helper
test. Read the
[behavioral testing guide](../_shared/references/behavioral-testing.md) when
selecting or strengthening the evidence.

Use an independent expected result: a worked specification example, known-good
fixture, invariant or separately derived oracle. Do not compute expectations
with the same algorithm under test, bless a bug as a requirement, or merely confirm
that metadata and implementation agree. Keep fixtures representative and failure
messages specific. For explicitly requested characterization, instead pin observed
behavior at a fixed baseline, mark suspicious results, and do not describe them as
normative correctness. Follow the
[legacy-change procedure](../_shared/references/testing/legacy-refactoring.md).

For test-first work or a regression repair, observe the intended failure before
implementation or repair, then the pass afterward. Import or setup errors do
not establish the behavioral failure. Build one useful test-and-code slice at
a time; exhaustive failure lists and all tests up front are unnecessary.
Existing correct behavior may need a new test that passes immediately; do not
fabricate a red/green history. Use the
[test-design procedure](../_shared/references/testing/test-design.md) for Test List,
Assert First, precise assertions and sensitivity. For consequential tests or
consolidation, use a known bad case or bounded mutation
in isolated scratch when it adds confidence; investigate survivors rather than
chasing a universal mutation score.

Control time, randomness, filesystem and external boundaries only where needed.
Keep deterministic contract tests independent of provider accounts. Mocks
should preserve boundary behavior, not bypass the very path being tested.
Separate synthetic tests from real integration or product observation and label
what each proves. Read [fixtures and doubles](../_shared/references/testing/fixtures-doubles.md)
when support code obscures a condition. For temporal or committed-state claims,
use [asynchrony and persistence](../_shared/references/testing/asynchrony-persistence.md);
for data or distributed handoffs, use the explicitly modern
[workflow adaptation](../_shared/references/testing/data-workflows.md).

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
