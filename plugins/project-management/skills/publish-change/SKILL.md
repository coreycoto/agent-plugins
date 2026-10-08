---
name: publish-change
description: Prepare and carry a reviewed change through the publication or release step explicitly requested under the consumer's process.
---

# Publish Change

Inspect contribution and release guidance, the exact checkout, existing edits
and current candidate. Establish which endpoint the user requested: commit,
push, pull request, merge, release or distribution verification. Readiness for
one endpoint does not establish the next.

Prepare the concrete candidate before asking about an uncovered promotion.
Check the final diff, relevant validation, unresolved findings and source or
artifact identity. Describe the problem and resulting behavior in reviewer-facing
text, with validation and material limitations. When several ready steps need a
decision, present them together with their destinations, exact artifacts and
limits under the [delivery authority rubric](../_shared/references/agent-decision-rubric.md#delivery-authority).
Use the consumer's templates where required; omit conversational history and
abandoned approaches.

For authorized delegation, assign `pm_release_preparer` bounded local files,
accepted version or release scope, and required evidence. Read the
[agent routing guide](../_shared/references/codex-agent-routing.md). The parent
owns publication, merges and tags under the user's authorization.

Follow native Git conventions for commits and pushes. Use the GitHub connector
with the current head SHA for an authorized interactive merge, subject to the
consumer's higher-priority rules. Ordinary issue and pull-request operations
may use the available connector or native `gh`; use `gh-steward` for composed
project changes. Recheck current state immediately before the authorized action.
Keep prior authorization through routine continuation; do not repeatedly ask
when the same scope and candidate constraints still apply.

For release or distribution, retain source revision, version, immutable artifact
identity and a verified receipt for each requested destination. Preserve failed
receipts and investigate ambiguous outcomes before retrying. A tag or successful
upload alone does not verify acquisition or a consumer's running version.

Finish with the achieved publication state, links or receipts, exact candidate
and remaining gates. Cleanup, installation, deployment and business data
publication require their own task authority. Follow the
[decision rubric](../_shared/references/agent-decision-rubric.md).
