# Catalog changes for a version upgrade

Use for a consequential runtime, framework or dependency upgrade. A routine
patch with no relevant contract change can use ordinary implementation and
focused checks; do not turn every version bump into a modernization project.
This is an [original adaptation of pinned upstream mechanisms](sources.md).

## Intersect version changes with actual use

Record the exact source and target versions, relevant lock/configuration and
toolchain inputs, preserved behavior and accepted intentional changes. Read the
version pair's current primary migration material and actual callers. Include
transitive dependencies, generated/configured entrypoints and runtime defaults
when they affect those callers. A removed API that nobody uses is not an
affected site; uncertain dynamic use remains a question to investigate.

For each relevant change, retain enough information to act:

- The primary source for the version change and the affected code/configuration
  location, with representative callers and cross-module dependencies.
- Old and new behavior; API, silent behavior, build/configuration or dependency
  category; a mechanical fix or an unresolved semantic choice.
- The minimal proposed action, independently justified expectation, discriminating
  test/probe, and remaining uncertainty or unavailable prerequisite.

Pay particular attention to changes that compile successfully: serialization,
empty versus absent values, ordering, encoding, rounding, locale/time handling,
error defaults and resource ownership. Capture a relevant baseline before
changing an affected site. Compiler success cannot settle these questions.
Do not convert a suspicious legacy behavior into a requirement or silently fix
it; distinguish preservation, characterization and intentional change using
[legacy-refactoring guidance](../testing/legacy-refactoring.md).

## Use tools and pilots for evidence

Use an existing ecosystem analyzer or codemod when it answers the question.
Distinguish present, runnable here and actually run. Record its exact inputs and
observed result; availability alone supplies no findings. Tools that write,
restore dependencies or build need permitted owned scratch and the required
access. Keep coverage gaps visible when those prerequisites are unavailable.

For an upgrade spanning many units, use the actual dependency order and qualify
one representative pilot before expanding. Feed unexpected build/runtime changes
back into the catalog and revisit the plan if they alter scope or prerequisites.
A coordinated dependency change may require a group to move together. The pilot
does not automatically authorize wider work or impose a new approval gate on
already authorized continuation.

Compare the same relevant cases on both versions when they can run. Retain
per-case outcomes, meaningful effects and any justified normalization; equal
test totals or a target-only pass do not establish unchanged behavior. If the old
runtime cannot execute, identify recorded baseline provenance and the narrower
claim the available evidence supports. Use [rehearse-migration](../../../rehearse-migration/SKILL.md)
for accepted transitions with persistent or mixed-version state.

Keep this catalog in the consumer's existing design, issue or upgrade artifact,
scaled to the affected sites. Continue through existing implementation and
candidate verification. Commands, accepted tolerances, scope and promotion
authority remain with the consumer; this reference adds no tool installation,
provider operation or release permission.
