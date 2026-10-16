# Public release writing

Write for people installing, upgrading or using the released product. Explain
useful capabilities and changes, supported versions and compatibility,
installation or migration steps, and material user-facing limitations. Include
enough detail for the consumer to decide what changes and act successfully.
Communication owns this audience-selection guidance; a publication workflow
applies it before release.

Select facts from development notes rather than copying the entire changelog,
handoff or verification report. Exclude internal conversations, agent/task
context, permission or approval history, operational boundaries, unrelated
scope exclusions, and qualification or release-gate commentary. Keep those in
internal handoffs and verification receipts. Do not strip a real compatibility
condition merely because it was discovered during qualification.

For example, given these synthetic development notes:

> Adds JSON coverage export for Runner 2. Requires Runner 2.4 or newer. Replace
> `coveragePath` with `coverage.output`. Streaming export is unavailable; large
> reports are buffered in memory. The owner approved release after our chat.
> We did not deploy the dashboard. Adapter qualification is incomplete and this
> evidence does not establish a consumer release gate.

A suitable public body is:

> Export coverage as JSON with Runner 2.4 or newer. When upgrading, replace
> `coveragePath` with `coverage.output`. Reports are buffered in memory, so
> allow memory for the full report when exporting large runs.

Reject the approval/chat sentence, unrelated dashboard boundary and internal
qualification ending. Retain the minimum version, changed configuration key
and memory limitation because they affect installation or use. If an adapter
actually lacks support, state its concrete compatibility status where relevant
instead of substituting a generic assurance disclaimer.

Review the complete rendered public body, including generated notes and any
appended ending. Check every claim against supplied evidence, verify migration
instructions, and remove internal context without hiding a material limitation.
Do not infer publication authority from an approved prose edit. After
publication, leave corrections to the authorized owner or a subsequent release
under the publication workflow's lifecycle rules.
