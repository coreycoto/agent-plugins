---
name: assess-data-quality
description: Assess a specific dataset or derived artifact for its declared use using provenance, independently justified expectations, semantic checks, and explicit population or sampling limits without repairing source data.
---

# Assess Data Quality

Resolve the dataset revision, intended decision/use, accepted quality rules and
access/resource scope. Read existing contracts and source inventories before
asking for missing policy. Do not invent freshness targets, acceptable error
rates or a composite quality score. Code correctness and successful processing
are separate from whether these data are fit for the declared use.

Identify lineage: acquisition, source versions, transformations, configuration,
reference data and any model-generated interpretations. Name what independently
establishes the expected population and units of measurement. A processed-input
list from the same discovery step cannot by itself establish source completeness.
Use the [assessment guide](references/fitness-evidence.md) to choose relevant
checks and distinguish semantic defects from legitimate exceptions.

Work read-only against a fixed snapshot or an explicitly bounded live read.
Use available consumer queries/tools; respect cost, time, access and redaction
limits. If the dataset can change during inspection, record the isolation and
observation window. Sample only with an explicit selection method; retain the
population, denominator, exclusions and what the sample cannot establish.

Check the relevant dimensions: expected partitions, identity and revision
rules, relationships, units/coordinate systems, null and unknown values, time
semantics, and independent accuracy evidence where available. Keep source facts
separate from derived interpretations. For each check, record expected versus
observed outcome and the basis of the expectation. Unsupported thresholds or
missing reference truth yield a qualification gap, not an invented pass/fail.

Attribute findings cautiously: source limitation, acquisition loss, transformation
error, stale materialization or insufficient evidence. Retain legitimate
exceptions and small counterexamples; do not silently drop, deduplicate, impute
or repair records. A suspicious observation is not automatically a source defect.

Complete with dataset identity, purpose, lineage, coverage/denominators, checks
and query evidence, findings, accepted exceptions, sample limits and fitness
conclusion bounded to supported requirements. A useful result may be conditional
or unverified. Return an authorized code defect through `diagnose-problem` and
`test-behavior`; data correction, new policy, publication, backfills and provider
writes require their own scope. No new data platform or scanner is required.
