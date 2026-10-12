# Fit for which use, according to which evidence?

A green pipeline establishes neither complete acquisition nor external accuracy.
Begin with a concrete use, a fixed dataset identity and authoritative rules.
Do not infer contractual thresholds from convenient observed distributions.
Profiling can expose questions without establishing acceptable error rates.

## Select dimensions rather than run every check

| Dimension | Useful check | Common false assurance |
| --- | --- | --- |
| Population | Compare expected source/time/region partitions with acquired ones | Every discovered source was processed |
| Identity | Check the declared compound identity and revision rule | Same entity ID always means duplicate |
| Relationships | Measure unmatched and multiplied joins against their intended cardinality | Output row count looks plausible |
| Meaning | Validate units, categories, CRS, nulls and effective dates | A value parses or fits a schema |
| Freshness | Compare the appropriate time to the accepted freshness requirement | Processing happened today |
| Accuracy | Compare with independent reference truth where justified | Two derived views agree with each other |

A valid revision is not a duplicate. A recorded absence can differ from zero,
unknown, not applicable and failed extraction. Preserve those meanings and the
consumer's exception policy. For geographic or temporal joins, include boundary
cases and ambiguity; do not force a match simply to increase a completeness rate.
A schema-conforming model output still needs independent semantic validation.

## Population and evidence boundaries

State whether the inspected objects are rows, entities, revisions, partitions
or sources. Keep numerator and denominator in the same unit. Name exclusions
and distinguish lack of an expected inventory from evidence that nothing is
missing. Track where expectation and actual result share an upstream dependency;
internal consistency remains useful but does not become independent truth.

For samples, preserve selection method, seed when relevant, strata, dates and
sample size. Convenience samples cannot support population-wide guarantees.
Do not invent confidence intervals without a defensible sampling model. Query
errors, unavailable partitions and exceeded read budgets are missing evidence.
Use stable snapshots where possible; overlapping live reads may disagree because
the underlying data changed. Redact sensitive values in retained examples.

## Report without silently fixing

For each material finding, retain a stable key or redacted example, the accepted
rule, expected/observed result, origin hypothesis and a decisive next check.
Preserve data that violates the rule; do not repair the inputs to obtain a clean
assessment. Distinguish a source defect from a local interpretation or join bug.
Do not report a new official quality policy merely because profiling suggests one.

Conclude per intended use: supported, supported with stated restrictions,
unsuitable against a specific accepted requirement, or unverified. Include
accuracy/freshness gaps even when structural checks pass. A blanket numerical
score obscures these distinctions unless an accepted scoring contract exists.
This is an original data-workflow adaptation; the [source scope](../../_shared/references/judgment/sources.md)
does not claim that the testing books prescribe a full data-quality standard.
