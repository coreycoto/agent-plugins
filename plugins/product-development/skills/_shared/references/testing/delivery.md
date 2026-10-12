# Delivery-stage verification and evidence

Source basis: Continuous Delivery chs. 2-9/12-15; GOOS walking skeleton and
acceptance loop. See [source map](sources.md). Exact-session and cache-record
checks are modern adaptations. Consumer release policy remains authoritative.

## Use stages for different feedback

Development checks answer the next local question quickly. Commit checks reject
obviously unsuitable candidates and build the deliverable. Acceptance checks
exercise user value through the real entrypoint/application driver. Later stages
can cover representative resources, exploratory work, environments and release
rehearsal. Do not relabel a startup probe as acceptance or a local stubbed adapter
as hosted provider qualification.

Keep a working walking skeleton through build, entrypoint and relevant integration
early enough to expose assumptions. It need not include the whole future platform.
An application can have well-tested internal modules that are never wired to its
actual entrypoint. A smoke test checks the assembly can start; a business scenario
checks the requested result. Both can be useful without making either universal.

Use business-level assertions and a narrow application-driver layer to isolate
incidental UI/transport mechanics. The driver must drive the actual surface, not
set internal state to make the outcome appear. Reuse production deployment
mechanisms with explicit environment configuration where supported.

## Preserve candidate and artifact identity

Build the deliverable once and promote those tested bytes where the architecture
allows it. Separate environment configuration; verify any necessary target-specific
build independently rather than claiming it is the same artifact. Keep source,
dependencies, toolchain/configuration and artifact digest tied to results. Native
package acquisition, installed bytes and an active session's discovery are separate
from source preparation. Do not publish an unreleased source change under an
already published version.

Use existing trusted command wrappers and result storage. Preserve typed exits,
logs and incomplete/failed outcomes; a started command or reassuring log line is
not completion. A cache hit requires relevant input identity and evidence accepted
by consumer policy. Moving a branch, changing fixtures/configuration or altering
test selection can invalidate earlier evidence. Do not edit a candidate during
its verification run.

Classify failure before repair: product regression, intentional contract change,
test/harness defect, configuration mismatch or unavailable prerequisite. Keep
fixed-baseline comparisons for attribution. Do not weaken expectations, silently
skip tests or alter a coverage denominator to obtain green results. Report approved
exceptions with their scope rather than extending them to a new source revision.

## Include nonfunctional and migration risks when applicable

Define a workload, environment and success/failure condition for capacity,
latency, memory, resilience, accessibility or security verification. A book's
illustrative time budget is not a universal target. Match the experiment to the
claim and retain data/measurement limitations. Automated checks complement
exploratory and domain-expert review, especially for unanticipated behavior.

For schema/data changes, test migration from supported old state with representative
retained records, coexistence of relevant old/new callers, resumability and
post-migration constraints. Rollback of application code does not automatically
undo a data migration or recover deleted data. Review expand/transition/retire
steps and evidence of restore or roll-forward where those strategies apply.
Do not perform destructive migrations or production drills merely to qualify a
local code change.

## Finish at the authorized stage

Report local checks, exact-candidate qualification, hosted acceptance, deployment
and consumer-visible verification separately. A draft can contain useful source
and test evidence while still having explicit promotion blockers. Failed or unknown
mandatory checks do not authorize release. Conversely, an unrelated production
operation is not required to finish a documentation-only draft.

Optimize the whole feedback path: retain early detection and later confidence,
reduce redundant rebuilds, and measure comparable work. Do not automatically
repeat expensive passed checks absent drift, a policy requirement or a new
uncertainty. Keep the whole team's ownership of failures without expanding an
agent's permissions.
