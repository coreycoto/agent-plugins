# Decide what change is worth making

Use for a consequential design or modernization choice, not a routine edit.
Start with the capability, reliability problem or cost of change to improve.
Describe the problem without embedding a preferred framework or replacement.
A technology's age, an advisory score or an unfamiliar design is not sufficient
reason to rewrite it. Nor does current success make required modernization wrong.

## Evidence before scope

Keep a concrete example of maintenance friction: the requested change, rule,
actual callers, coordination required and consequence. Use focused history when
it adds evidence. Separate churn from semantic change; generated updates,
formatting, large automated batches and squashed commits can distort it. A
committer identity is not a measure of knowledge or competence. Combine history
with current structure, incidents and upcoming work; avoid invented effort/ROI.

Compare materially different options where uncertainty warrants it: retain the
structure, repair one seam, incrementally replace a responsibility, or perform a
larger redesign. Include coexistence and retirement costs, not only destination
code. Define the next useful slice and a condition for stopping or reconsidering.
Do not require a quota of alternatives once the choice is routine or settled.

## Judge an interface through its callers

Show a representative caller before and after a consequential abstraction.
Name the decisions, ordering or failure handling that it no longer coordinates,
and new obligations it acquires. A collection of smaller helpers may simply
scatter the same burden. A larger coherent operation may hide mechanics well,
but must still expose consequential partial failure and ownership semantics.

Concentrate decisions that change together, not code that merely looks alike.
Two similar loops with different identity and recovery rules need not share a
framework. A common policy repeatedly drifting across callers may deserve a
single owner. File length, number of layers, or a pattern name is not a verdict.
Preserve accepted API and persisted contracts when moving responsibility.

## Make uncertainty actionable

Record the assumption most likely to change the choice and the cheapest faithful
experiment that could contradict it. Specify observation and stop conditions
before building a prototype; do not turn exploratory code into a rollout by
accident. For multi-version transitions, use `rehearse-migration` when execution
is in scope. For disputed competing event sequences, use `check-protocol`.

Complete the existing design/assessment artifact, not another mandatory design
registry. Retain alternatives and evidence only to the degree they help an
implementer or reviewer act. The procedures here are [original adaptations](sources.md),
not universal rules attributed to every book in the reading list.
