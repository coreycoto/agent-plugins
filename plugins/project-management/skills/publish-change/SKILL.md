---
name: publish-change
description: Use this skill to prepare and publish a reviewed change through the consumer repository's established version-control and review process.
---

# Publish Change

Use this skill when a local change is ready for review or a repository has an
explicit release process. First inspect the consumer's contribution and release
policy, branch state, and current change. Summarize what is ready, what remains
unverified, and which publication step the user requested.

Keep local version-control work separate from hosted GitHub operations. Follow
the consumer's branch, commit, pull-request, and release conventions. For
ordinary pull-request or issue operations, use the existing GitHub connector or
native `gh` as allowed by repository policy. If publication requires composing
project or issue changes, use `gh-steward` for that coordinated plan.

Before any externally visible action, identify its target and effect and check
the latest relevant state. Publish only the step the user authorized. Do not
merge, create or move a release tag, or publish a release merely because a
change is ready for review. Confirm the resulting hosted state and report any
remaining gate separately.

See the [decision rubric](../_shared/references/agent-decision-rubric.md) for
consumer policy and authorization boundaries.
