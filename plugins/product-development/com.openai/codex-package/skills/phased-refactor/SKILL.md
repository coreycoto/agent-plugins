---
name: phased-refactor
description: Refactor a substantial code or test cluster in evidence-backed phases, preserving behavior through caller audits, parity checks, regression tests and measured validation. Use for selected repository-health findings or an explicitly requested broad structural refactor.
---

# Phased refactoring

For supporting upstream skills, read the package
[initialization context](../../README.md#initialize-upstream-skills-in-a-consumer-project)
and native `skills-lock.json`. Initialize selected dependencies in the consumer
project's `.agents/skills/`; keep first-party plugin skills in this package.

Turn a selected structural problem into a reviewable change with evidence that
behavior, test confidence and maintenance cost improved. Repository-health
reports identify candidates; source and caller evidence determine whether to act.
Use the repository's existing ownership, permissions and delivery rules.

## Establish a fixed baseline

Record the checkout, branch, source SHA, relevant report/tool version and local
changes before work. Refresh the authorized base without discarding local work.
Give each reviewed finding a disposition: implement, consolidate, defer, accept,
or won't fix. Investigate generated files, migrations and framework conventions
before treating repeated or large files as redundant.

Map public exports, callers, generated outputs, command discovery, routing and
classification rules. For distributed contracts, include actual producer and
consumer envelopes. Select a bounded batch of related changes and record the
behavior to preserve, intentional changes, validation commands and delivery stage.
The batch size and coverage target are repository decisions, not universal quotas.

Run a relevant baseline and distinguish existing failures from regressions. Save
comparison artifacts outside committed source. Do not delete uncertain tests to
reach a reduction target or claim an adapted baseline proves an unavailable suite.

## Make structure easy to verify

Separate mechanical movement from behavioral changes where practical. Extract
around real responsibilities; preserve public interfaces and runtime outputs.
Audit every caller before tightening shared parsing or changing semantics.
Follow generators and inventories through the move: a relocated module can
silently disappear from routing, coverage or release classification.

Use independent ownership for delegated work when authorized. Review a fixed
checkpoint; do not change Git state while a validation harness reads it.

## Organize tests around behavior

Keep fast, deterministic behavior tests separate from tests requiring workspace
dependencies, provider resources or live acceptance. Name tests by what they
actually prove: import/export contracts are not integration execution.

Factor repeated setup and assertions only when failures remain specific and the
helper cannot silently bypass the tested contract. Keep independent expected
behavior alongside generic metadata invariants. Prefer meaningful edge cases to
snapshots of whole implementations or repeated existence checks.

Inventory coverage targets independently of coverage output. Enforce the agreed
per-file metrics and reject missing or malformed evidence; importing declarative
arrays can produce high coverage without proving behavior. Before removing cases
as redundant, show that retained tests catch their regression. Use bounded
mutations in a disposable checkout when that adds meaningful confidence.

## Validate the candidate

Compare the intended unchanged surfaces with the fixed baseline: definitions,
exports, ordering, generated output and representative routing where applicable.
Run affected tests and type checks, then the required wider checks. Measure local
suite cost using a comparable baseline; label dependency adaptations and local
timings explicitly. Add failure, interruption and recovery cases when changing
stateful or durable pipelines.

Fix regressions caused by the change. Keep unchanged dependency failures visible.
Stop repeating broad checks after they pass unless a change or uncertainty
justifies another run. Request independent review for a substantial final diff
when delegation is authorized.

## Publish and evaluate

Publish the completed batch once within the authorized delivery stage to limit
CI churn. Match validation evidence to the actual candidate SHA. Keep draft
validation, full qualification, merge and production verification distinct.
A refactor does not authorize provider operations or bypass a preservation guard.

Rerun the selected repository-health analysis after the final changes. Compare
source changes separately from historical or overlay drift; report findings as
advisory unless repository policy explicitly enables enforcement. Retain useful
tests even if detector scores rise. Report suspected tool defects separately
from justified source work, and create external reports only when authorized.

The handoff records scope, source/candidate SHAs, intentional behavior changes,
caller audit, parity, coverage, regression evidence, timing, review, remaining
failures and the authorized delivery stage. Recommend the next bounded batch
from the new evidence rather than chasing every remaining score.
