---
name: project-governance
description: Audit project practices and records against the consumer's documented rules and prepare evidence-backed repairs or policy decisions.
---

# Project Governance

Inspect the current consumer policy and records relevant to the requested
review. For each material gap, identify the rule, observed state, evidence and
practical effect. Distinguish undocumented practice, stale records and a policy
contradiction; they need different remedies.

Project identity, field definitions, ranking, hierarchy, labels, actors and
delivery stages remain consumer-owned. Report missing or inconsistent policy
for a decision instead of normalizing it by assumption. Keep generic workflow
mechanics separate from product-specific rules and provider capabilities.

For authorized delegation, use `pm_governance_auditor` for a bounded read-only
audit or `pm_documentation_steward` for accepted documentation edits. Assign
record or file scope and validation; policy decisions remain with the parent.
Read the [agent routing guide](../_shared/references/codex-agent-routing.md).

Propose the smallest coherent repair with affected records, rationale and a
success condition. Preserve historical evidence and unrelated configuration.
A recurring correction may support a documentation improvement when its cause
is established; one anecdote does not establish universal policy. Write such
changes only within the authorized documentation scope.

Use `gh-steward` for composed governance changes across records, fields, labels
or relationships. Ordinary single-record work can use the existing connector
or native `gh` under consumer policy. Show the reviewable delta, apply only the
authorized scope, and inspect the resulting state. Preserve existing
authorization across routine repairs; ask only when the policy choice or action
is uncovered.

Finish with verified gaps, proposed or applied repairs, unresolved consumer
decisions and remaining evidence limits. Follow the
[decision rubric](../_shared/references/agent-decision-rubric.md).
