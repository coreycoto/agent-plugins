---
name: implement-change
description: Complete accepted software intent in small behaviorally useful slices, preserving concurrent work and validating the requested result.
---

# Implement Change

Read the work source, consumer contracts and exact checkout before editing.
Identify accepted behavior, owned files, existing edits and requested endpoint.
Resolve factual questions from source first. Return consequential unsettled
product or architecture choices; do not reopen settled decisions or require
a plan document for an understood small task.

Make the smallest complete change. For substantial work, use vertical slices
that exercise useful behavior through the relevant layers, with prerequisites
and focused validation. Follow repository generators, inventories and tests
through moves. Read the [impact guide](../_shared/references/change-impact.md)
when callers, shared data or migrations may be affected. Preserve unrelated
and concurrent changes instead of resetting the checkout.

Use existing abstractions where they express the domain. Add an abstraction
only when it concentrates a real rule, variation or responsibility. Avoid
speculative features and cleanup unrelated to acceptance. For a bug, retain a
reproducer; use [test-behavior](../test-behavior/SKILL.md) when independent
regression evidence is warranted. Reversible low-impact edits need proportionate
checks rather than tests that mirror their implementation.

Run focused validation, then consumer-required checks. Fix failures caused by
the change and identify pre-existing or environment failures separately. Inspect
the final diff for omissions and unintended changes. Use
[verify-product](../verify-product/SKILL.md) when the endpoint requires actual
user behavior, and [review-code](../review-code/SKILL.md) when review is needed.
Do not repeat broad checks after they pass without a new change or uncertainty.

Before pushing a release candidate, resolve the consumer's CI selection for
the same base and final candidate and run every locally runnable selected
check. Focused tests do not replace the complete selected suites. Use the
repository's verification command or gate when provided; keep its commands and
policy in the consumer. Retain candidate-bound commands, typed exit statuses
and unavailable prerequisites. Later changes invalidate affected results;
failed, interrupted or unknown checks do not establish readiness. Keep
hosted-only qualification pending until separately observed.

For authorized delegation, assign `pd_implementer` bounded intent, owned files
and success conditions; `pd_transformer` suits explicit mechanical rules with
deterministic completion. Both preserve concurrent work. Use native Git
isolation when the consumer or task requires it; cleanup is a separate action.

Complete the authorized endpoint and report changed behavior, files, validation
and limits. Routine repair continues under existing authority. Publication,
provider operations and scope expansion remain decisions outside a local edit.
