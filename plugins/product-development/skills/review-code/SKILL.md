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
existing deterministic tooling already covers a rule. For test, fixture or
verification changes, select from the
[testing decision guide](../_shared/references/testing/README.md). Check oracle
independence or explicitly labeled characterization, executed assertions,
meaningful double boundaries, test discovery and honest recovery/stage claims.
Do not infer correctness from coverage, fewer files or reviewer agreement.

For new abstractions, compare actual caller obligations using the
[design judgment guide](../_shared/references/judgment/modernization-and-design.md).
For protocol or migration evidence, inspect enabled properties, model limits,
implementation correspondence and tested intermediate versions. A model pass
or destination test does not establish an unexercised production transition.

For each retained finding, state the concrete trigger, incorrect consequence,
location, supporting contract and smallest resolving check. Reproduce a
suspected defect where practical. Mark an unproven concern and its missing
evidence; reviewer agreement alone does not establish correctness. Distinguish
required repairs from optional improvements and unrelated existing issues.
Deduplicate findings without losing distinct failure scenarios.

For authorized independent review, use `pd_reviewer` on the fixed candidate with
read-only scope. Use actual native tools rather than model-name commands or an
external review service. Review does not authorize shipping or credential access.

When review requires several passes, use the
[bounded review procedure](../_shared/references/review-iterations.md). Keep
finding identities and candidate evidence stable, review affected changes and
open findings on later passes, and report unresolved decisions when the budget
ends. Routine reviews do not require a loop.

Complete with supported findings, relevant checked surfaces and material
coverage limits. State whether acceptance remains blocked and why. Apply fixes
only when already requested, through
[implement-change](../implement-change/SKILL.md); revalidate affected conclusions
after the candidate changes. A no-findings result does not prove unexercised
provider or live behavior.
