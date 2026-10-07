---
name: improve-performance
description: Diagnose a software performance limiter and evaluate a bounded improvement using equivalent work, comparable measurements, and correctness evidence.
---

# Improve Performance

Establish the user-visible slow path, expected workload, environment and exact
baseline revision. Read the measurement harness before trusting its number.
Use the [benchmarking guide](../_shared/references/benchmarking.md) to verify
that completed work and errors are counted, conditions are comparable and the
measurement represents the claim.

Profile or inspect resource evidence to locate the limiter separately from
reported timings. Include load generation, I/O, serialization, synchronization
or configuration when they may dominate. A local hot function is not necessarily
the end-to-end bottleneck. If no cause is supported, investigate rather than
performing speculative rewrites.

Choose a bounded hypothesis and change only the relevant variable where
practical. Preserve output semantics, failure behavior and resource limits.
Use realistic input and production-relevant configuration. Keep correctness
checks independent of timing so fast rejection, cached no-op or skipped work
cannot appear as an improvement.

Interleave baseline and candidate observations to reduce order effects. Separate
cold and warm states when both matter. Record wall time, work count, errors,
run variation and revision or artifact identity. A single requested ballpark
can be labeled as one observation; an adoption decision needs evidence
proportionate to the uncertainty, not an arbitrary run quota.

Retain an improvement only when the relevant measure supports it and regression
checks pass. Report inconclusive results when noise or mismatched workloads
prevent comparison. Microbenchmarks need their contribution to the user path
stated; theoretical improvement is not an observed speedup.

Complete with supported limiter, change, equivalent-work evidence, before/after
units and variation, correctness results and limitations. Continue within the
requested endpoint. Do not change provider capacity, billing, production
configuration or infrastructure simply because local code performance work
was authorized.
