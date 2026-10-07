# Comparable performance evidence

Start with a concrete claim, unit and representative workload. Inspect the
harness's timed region, completed work count, output correctness and error count.
Ensure awaited, iterated or persisted work actually occurred; fast rejection,
unconsumed lazy work or a cache hit can produce a misleading number.

Pin baseline and candidate revisions, tool/runtime versions, build mode, input,
concurrency and relevant configuration. Compare equivalent work and production-
relevant settings. If configurations differ, say what the comparison establishes.
Do not call an untuned or synthetic comparison a general winner.

Profile outside the reported timing path when instrumentation perturbs execution.
Look for the limiting CPU, I/O, synchronization, provider or load-generator
resource. Check plausible physical bounds and the fraction of total time the
changed work occupies. A helper taking little of the user path cannot explain
a large end-to-end improvement without other evidence.

Separate cold startup and warm steady state when both matter. Interleave baseline
and candidate observations, using comparable cache state and alternating order
so warmup or machine drift does not consistently favor one side. Record independent
wall time rather than summing nested event durations. Preserve raw measurements,
errors, work count and outputs in bounded local artifacts.

Scale replication to the decision. Label a requested one-run ballpark honestly;
for a meaningful comparison, repeat enough to characterize variation and report
run count, central tendency and spread. Do not declare improvement when the
difference is indistinguishable from noise. Non-comparable conditions warrant
an inconclusive verdict, not a narrowed promotional claim.

Report the measure and units, provenance, equivalent work, correctness and error
results, limiter evidence and user-path relevance. A micro result and an observed
end-to-end result answer different questions. Keep or discard a candidate from
supported evidence and preserve required behavior independently of timing.
