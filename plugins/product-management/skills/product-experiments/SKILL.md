---
name: product-experiments
description: Design or assess a falsifiable product experiment using supplied metrics, evidence, and constraints to decide what to learn or change next.
---

# Product Experiments

Use this skill when a product decision depends on an uncertain claim or when
results need assessment. Establish the decision, user population, constraints
and supplied evidence. Read factual inputs first; ask only about unresolved
product choices or gaps that prevent a meaningful test.

Turn the claim into a falsifiable hypothesis: for which users, in what context,
what change is expected, compared with what alternative, and what observation
would contradict it. Separate assumptions about demand, usability, adoption and
business outcomes; one test may not establish them all.

When several assumptions compete for attention or a test must inform a build,
defer or stop decision, read
[decision pressure-testing](../_shared/references/decision-pressure-testing.md).

Design the smallest observation that can affect the decision. Options include
existing-data analysis, a prototype task, a bounded pilot or a controlled
comparison. Match the method to the claim. State exposure or assignment,
observation period, comparison and relevant confounds: selection, novelty,
seasonality, learning, missing data or simultaneous changes.

Specify instrumented observations: events or measures, source, eligible users,
denominator, timing, missingness and guardrails. Use supplied baselines, targets
and sample constraints; do not fabricate expected lift, statistical power or
success thresholds. Label an uninstrumented test as a proposal until collection
is established. Implementation or provider changes need their own authorized
technical workflow.

Agree or record decision criteria before interpreting results: what supports
continuing, changing, stopping or further learning. Where quantitative criteria
are missing, show the decision needed or a qualitative criterion supported by
the task. Keep inconclusive results possible; do not tune thresholds after
seeing the outcome to manufacture success.

For assessment, compare observed results with the original hypothesis and
criteria. Report uncertainty, missing data and alternative explanations. Separate
correlation from causation and observed behavior from participant preference.
Recommend a next action proportionate to what the test establishes.

Finish with hypothesis, method and observation plan, decision criteria, evidence
limits and next decision; for completed tests include actual results and their
source. Drafting a test authorizes no customer outreach, live instrumentation,
provider mutation or product rollout. Execution follows the existing task scope
and permissions.
