# Simplify the current diff

Use during accepted implementation or an explicitly requested simplification.
The goal is easier understanding with the same behavior. A clear implementation
can remain unchanged. This is an [original adaptation of pinned upstream
mechanisms](sources.md), using the consumer's coding standards.

## Identify the owned change

Start from the task's base and current patch, including task-owned uncommitted
work. Separate pre-existing and concurrent edits before choosing refinements.
Limit edits to the task-owned change and the smallest necessary context; reading
callers does not authorize cleaning them up. An edited file is not blanket
permission to rewrite its other functions.

Look for avoidable nesting, unclear names, repeated decisions or a delegating
wrapper that adds no rule, variation or useful boundary. Prefer explicit flow
when it helps a reader follow the condition and effect. Explain how a proposed
extraction concentrates a responsibility; moving the same coordination into
more helpers can increase the burden.

Keep abstractions that own a domain rule, compatibility seam, error/recovery
policy or resource lifetime. Similar-looking code can have different ownership
or ordering. Keep comments explaining reasons and constraints. Fewer lines,
fewer functions or a preferred syntax are not sufficient evidence of improvement.
Do not impose language-specific style rules beyond the consumer's standards.

## Preserve behavior and finish validation

Check return values, errors, defaults/coercions, evaluation and effect order,
mutation, serialization and resource lifetime where the refinement reaches them.
For example, moving an authorization check after a write is a behavior change
even when the successful return value is identical. Keep a useful protection
boundary if inlining it would make its policy easier to bypass.

Choose the smallest understandable refinement; leave already-clear code alone
and avoid unrelated fixes. Return a consequential unresolved behavior choice to
the existing task rather than burying it in cleanup.

Inspect the final diff and run affected behavioral checks plus consumer-required
verification on the final candidate. A refinement after a passing run invalidates
affected evidence under the consumer's existing rules. Do not manufacture a new
suite for a low-impact edit or repeatedly run broad checks without a new change
or uncertainty. Report significant refinements and remaining limits at the
authorized endpoint; this reference adds no automatic hook or separate agent.
