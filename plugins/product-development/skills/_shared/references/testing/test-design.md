# Design a useful behavioral test

Source basis: Beck chs. 1-4/25-29; Meszaros chs. 5/10/21; GOOS chs. 5/21/23-24;
Fowler ch. 4. See [source map](sources.md). Defect probes below are adaptations.

## Select the purpose and next example

First identify specification, regression, characterization or experiment. For a
specification/regression, name the accepted rule and expected result before
using implementation details to construct assertions. For characterization,
follow [legacy change](legacy-refactoring.md); do not pretend captured output is
an independently specified correct answer.

Keep Beck's Test List of known examples and uncertainties, then implement one
useful increment. An outline is not a demand to write every test up front. Choose
a small success case, a discriminating boundary or the reproduced failure. Reduce
step size when feedback surprises you; do not turn tiny steps into a universal
ceremony. Sketch the observable assertion first when construction obscures intent.

## Make the oracle able to disagree

Use a hand-worked accepted example, independently reviewed fixture, trusted
external reference, or justified invariant. Transparent arithmetic in a test is
allowed: Beck's Evident Data makes relationships visible. Reusing the production
transformation to calculate its own expected output is different. Shared value
types or builders are not forbidden, but their defects can correlate failures;
verify critical helpers separately.

Choose values that expose plausible mistakes: unequal argument values, just
below/at/above a bound, different owners, empty versus absent, and nonintegral
values when conversions matter. Do not produce dozens of equivalent rows solely
for coverage. Give parameterized cases stable names and include distinguishing
parameters in failure output.

Use Four-Phase Test: arrange the relevant fixture, exercise the behavior, verify
the outcome, release owned resources. One test condition may require multiple
assertions, including unchanged state after a refusal. Keep causal inputs visible.
Guard an essential precondition with a failing assertion instead of silently
skipping the assertion path. An intentionally parameterized case table is not
the same as adapting expectations to whatever result the program returned.

## Observe feedback honestly

For new behavior or a repair, observe the meaningful failure and subsequent pass.
A missing symbol can be an initial TDD step; an import, syntax or environment
failure does not demonstrate detection of the intended behavioral defect. For
existing correct behavior, a new test may pass immediately. Do not break the
product merely to manufacture a red/green story. Characterization and test
consolidation use baseline and sensitivity evidence instead.

Beck's Fake It is a temporary implementation step followed by generalization;
it is not permission to hardcode a fixture answer in the delivered system.
When a failing test reveals a design problem, separate the necessary seam or
interface improvement from the intended behavior change. Preserve the external
contract or explicitly review its change.

## Verify precision without overspecification

Assert information important to the contract, not incidental representation,
private call ordering, generated IDs or wall-clock values. Exact serialized bytes
are appropriate when signatures, digests or wire compatibility require them.
Interaction assertions are appropriate for meaningful effects such as preventing
a second charge; they are not categorically inferior to state assertions.
Snapshots need a reviewable semantic purpose and an explanation of intentional
deltas. Never blanket-update them to erase a regression.

For a consequential new oracle or a proposed test retirement, consider a known
bad implementation or one bounded defect in isolated scratch. Keep the expected
answer fixed. First establish a passing control, then check the intended assertion
rejects the fault. Distinguish assertion detection, surviving/equivalent mutation,
invalid code, dependency error and timeout. Restore scratch and preserve evidence;
never mutate a shared candidate while another check reads it.

Finish with the condition, oracle authority, real/doubled boundary, observed
outcomes, exact command and remaining limits. Extend the owner suite and run its
required checks; a focused pass does not replace candidate qualification.
