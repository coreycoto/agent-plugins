---
name: diagnose-problem
description: Reproduce a reported software failure, distinguish competing causes with decisive probes, and verify an authorized repair against the original symptom.
---

# Diagnose Problem

Record the exact symptom, expected behavior, checkout and environment. Preserve
the original failure evidence and redact sensitive diagnostic output. Inspect
available errors and relevant consumer solution records before repeating work;
use the [retrieval guide](../_shared/references/project-knowledge.md).

Build a pass/fail reproducer that reaches the reported behavior before claiming
a cause. Prefer an existing test, actual CLI input, request or user-flow harness.
Minimize input and setup while preserving the symptom. For intermittent failures,
record trigger conditions and reproduction rate rather than calling one green
run recovery. If reproduction is blocked, report attempts and missing
prerequisites; source inspection can narrow possibilities but cannot prove a fix.

Develop competing explanations where uncertainty warrants them. Each hypothesis
needs a prediction that differs from the alternatives. Choose the smallest
probe that would discriminate: inspect a boundary, vary one condition, bisect
an isolated revision or add bounded temporary instrumentation. Preserve logs
that establish sequence without capturing credentials or unrelated user data.
Update beliefs from observations; a plausible story is not root-cause evidence.

Separate a product failure, harness defect, environment problem and stale
expectation. An accepted requirement contradicted by current code may indicate
a bug rather than an obsolete test. Preserve that decision for the owner.

When repair is authorized, use
[implement-change](../implement-change/SKILL.md) and
[test-behavior](../test-behavior/SKILL.md) at a seam that reaches the actual bug.
Rerun the original scenario as well as any minimized regression. Remove owned
temporary instrumentation after retaining useful evidence. No ambiguous provider
operation is retried merely to obtain a reproducer.

When evidence shows a recurring mistake, use the
[prevention guide](../_shared/references/recurrence-prevention.md) for a bounded
guard at the owning boundary. A diagnosis does not independently authorize a
broader structural repair; return that scope when it is not already accepted.

`pd_diagnostician` may investigate and write temporary evidence when delegated;
product edits belong to the parent or assigned implementer. Complete with the
supported cause or unresolved alternatives, probe evidence, repair result and
limits. A missing live reproducer stays explicitly unverified.
