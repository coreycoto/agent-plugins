---
name: maintain-verification
description: Create, qualify, or refresh executable consumer verification instructions and harnesses while separating instruction drift from product defects.
---

# Maintain Verification

Identify the consumer's existing verification convention and requested scope.
Select creation, qualification or refresh. Creation writes instructions grounded
in source and available tools; qualification executes them; refresh reconciles
selected instructions with current evidence. Do not assume a client-specific
skill directory or bootstrap unrelated configuration.

Inspect documented launch commands, public surfaces, current harnesses,
prerequisites, instance isolation and observable outcomes. Prefer established
tools over a new wrapper. If a new consumer skill is requested, follow available
skill-authoring guidance for frontmatter and placement. A document or harness
can suffice where that is the consumer's convention.

Read the [verification guide](../_shared/references/product-verification.md).
Instructions must name exact commands or UI steps, safe prerequisites,
readiness and instance checks, acceptance observations, evidence location and
owned cleanup. Map only relevant behaviors with a concrete entry point and
success condition; do not fabricate coverage or a feature quota.

Qualify by executing the actual instructions on the selected behavior and
retaining evidence through cleanup. An unexecuted map is a draft. Record which
paths were exercised and which need unavailable prerequisites; one successful
feature does not qualify the entire product. Rerun changed harness steps before
calling them verified.

For refresh, compare selected entries to current source and behavior. Distinguish
documentation drift, a harness gap and a product regression. Accepted policy
still governs when code violates it; do not rewrite expectations to bless a
bug. Edit only authorized verification files and harnesses. Report product
repairs separately unless explicitly assigned.

Complete with created or updated files, qualification evidence, selected
coverage, unavailable prerequisites and remaining gaps. Preserve captured
failures before owned cleanup and drive shared UI state serially. No automatic
publication, scheduler creation, credentials, global configuration or provider
operation follows from maintaining instructions.
