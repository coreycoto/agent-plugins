---
name: review-code
description: Review an exact code candidate for supported defects, regressions, requirement gaps, and meaningful missing evidence using relevant lenses.
---

# Review Code

Identify the exact candidate, base or working diff, originating intent and
consumer standards. Read changed code in caller context. A named branch or PR
selects review scope; it does not authorize checkout changes or external posts.
For uncommitted work, record the diff state so conclusions remain traceable.

Assess intended behavior and repository rules separately. Follow changed
contracts into actual consumers and tests; use the
[impact guide](../_shared/references/change-impact.md) when data or external
boundaries extend beyond symbol references. Choose depth according to the
change's coupling, state and consequences. Small diffs can still affect serious
invariants; a sound change need not produce findings.

Read selected sections of the
[review lenses](../_shared/references/review-lenses.md) only for relevant security,
performance, data, API or lifecycle concerns. Do not apply every lens, invent
risk probabilities, or treat a style preference as a defect. Check whether
existing deterministic tooling already covers a rule.

For each retained finding, state the concrete trigger, incorrect consequence,
location, supporting contract and smallest resolving check. Reproduce a
suspected defect where practical. Mark an unproven concern and its missing
evidence; reviewer agreement alone does not establish correctness. Distinguish
required repairs from optional improvements and unrelated existing issues.
Deduplicate findings without losing distinct failure scenarios.

For authorized independent review, use `pd_reviewer` on the fixed candidate with
read-only scope. Use actual native tools rather than model-name commands or an
external review service. Review does not authorize shipping or credential access.

Complete with supported findings, relevant checked surfaces and material
coverage limits. State whether acceptance remains blocked and why. Apply fixes
only when already requested, through
[implement-change](../implement-change/SKILL.md); revalidate affected conclusions
after the candidate changes. A no-findings result does not prove unexercised
provider or live behavior.
