---
name: review-closeout
description: Assess review findings or completed work against its acceptance conditions and prepare verified closeout with necessary follow-up.
---

# Review Closeout

Start from the requested endpoint, exact candidate and consumer completion
policy. Inspect the relevant review and validation evidence. Separate verified
results, assumptions, remaining gates and unresolved risks; code written or a
pull request opened is insufficient when the endpoint requires more.

Assess each material finding against the actual change. Distinguish a supported
regression, stale assertion, unrelated failure and an open product or policy
decision. Identify the smallest resolving check or repair. Carry routine fixes
within the existing scope and authorization rather than reopening approval for
each review comment. New requirements remain decisions for the owner.

Classify follow-up by consequence: needed for this endpoint, a separately tracked
improvement, a durable project solution, or no action supported by the evidence.
Use consumer destinations and taxonomy. Do not auto-close blockers or convert
an isolated observation into a universal policy.

When a solved problem has reusable evidence and the user wants it retained,
use `product-development:capture-solution` if available. Preserve problem,
cause, verified remedy and limits in the consumer's chosen location. This is
selective routing; closeout does not require a documentation, skill or memory
write, and memory updates still need the user's explicit request.

Use `gh-steward` for composed follow-up across GitHub records. Ordinary issue or
pull-request work may use the existing connector or native `gh` under consumer
policy. Apply only authorized changes and verify resulting state. A local
assessment does not authorize posting review responses or closing records.

Finish with the closeout decision, candidate and evidence, remaining blockers,
follow-up owner when known and next action. Use `handoff-work` if another context
must continue the task. Follow the
[decision rubric](../_shared/references/agent-decision-rubric.md).
