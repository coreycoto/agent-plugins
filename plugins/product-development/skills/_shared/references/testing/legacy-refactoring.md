# Characterization, seams and behavior-preserving change

Source basis: Feathers chs. 2-4/6/11-13/16-18/20-23/25; Fowler chs. 1-4 and
catalog mechanics; GOOS chs. 17/20. See [source map](sources.md).

## Separate three kinds of behavior

Record what must be preserved, what currently happens but is not understood,
and what is intentionally changing. Use existing issue/design records rather
than inventing a separate policy database. A suspicious behavior may be captured
as characterization and explicitly marked for review; it must not silently become
a product requirement or be silently fixed during a mechanical extraction.

Feathers's characterization technique observes a fixed implementation through a
harness and pins the result. A deliberately failing probe can reveal the actual
output; converting that observation into an expectation is legitimate in this
mode. It is not the same as updating a failed specification test to bless a bug.
Label source revision, chosen inputs, nondeterministic normalization and unresolved
questions. Capture enough to protect the intended change, not every imaginable
output or unstable byte.

## Find a seam and its enabling point

Trace effects from the proposed edit to visible results, persisted state and
outgoing calls. An interception point observes an effect; a useful pinch point
can cover several changed paths. Do not let broad observations conceal branches
whose outputs happen to coincide. Include conversions, errors and unchanged
side effects relevant to the movement.

A seam permits substitution without editing at the use site; its enabling point
chooses the behavior. Inspect existing dependency parameters, owned adapters,
module boundaries or link-time facilities before adding new abstractions. Distinguish
sensing (observing effects) from separation (removing an obstructing dependency).
Keep the tested behavior real. Replacing the very operation being asserted with
a stub defeats the purpose.

There can be a dependency dilemma: tests require a seam, yet inserting the seam
starts without protection. Feathers supplies small dependency-breaking techniques
for this situation. Make the smallest reviewable, behavior-preserving edit, use
compiler/static feedback and available broader checks, inspect the diff and add
the intended protection immediately. Do not declare a large untested rewrite safe
because the final suite eventually passes.

## Change in coherent steps

Choose the operation-specific mechanics, not only a pattern name. Extract Method
requires checking scope, assignments, return values, evaluation order and errors.
Move Method requires updating actual callers and retaining a delegating interface
when compatibility requires it. A callback extraction must preserve ownership and
lifetime, not just parameter types. Review reflection, serialization, generated
interfaces and persisted shapes beyond ordinary symbol references.

Keep Fowler's two hats visible: structural preservation versus feature/bug change.
Use a fixed behavior baseline for the former and an accepted changed expectation
for the latter. Scratch refactoring is a disposable understanding experiment, not
a deliverable to merge without the ordinary evidence. Sprout/Wrap can create a
protected foothold when direct modification is too risky; record the resulting
boundary and follow-up rather than leaving indefinite duplicate behavior.

A large design decision can be implemented through small refactorings. Select
one responsibility and a reversible path toward the desired boundary. Do not
replace the entire pipeline, test framework and delivery system in one step merely
because code generation is fast. Equally, do not demand an exhaustive redesign
before fixing a small isolated problem.

## Demonstrate both existence and connection

An extracted rule can pass its unit tests yet never be called by the application.
Retain caller/component evidence alongside focused rule tests. For persisted or
external contracts, include compatibility and real handoff tests. Characterization
shows parity at the chosen seam, not correctness of all behavior or all schedules.

Keep production and test restructuring distinguishable so coordinated mistakes
are visible. When a test must change with an interface, explain why its meaning
is unchanged and retain independent observations. Complete the authorized checks
on the exact candidate, with baseline failures, intentional changes and remaining
uncertainty explicit. Distributed crash safety requires the separate
[workflow adaptation](data-workflows.md); the 1999 catalog does not prove it.
