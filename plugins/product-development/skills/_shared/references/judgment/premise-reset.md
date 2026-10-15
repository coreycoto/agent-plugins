# Reconsider the premise behind repeated failed fixes

Use when multiple observed fixes fail the same requirement while assuming the
same cause or design constraint. Two such failures are a useful signal to pause
that line of repair, not a universal attempt quota. A routine bug does not need
this procedure. Keep failed, interrupted and unknown results distinct.

Write the shared premise in one sentence. Separate the observed mechanism from
the assumption about why it occurs. For example, worker-local free lists can
explain where reusable memory remains without explaining why the same workers
always receive more frees than allocations. A more elaborate allocator might
compensate for work assignment that creates the imbalance.

For an accumulation or imbalance, use existing evidence or a bounded rerunnable
query to count both stock and relevant flows by actor, role, tenant, shard, key
or phase. Retain units, denominators, observation window and source identity.
Compare distributions across relevant runs; a total or average can hide a
concentrated problem. Use the [repeatable-work guide](repeatable-work.md) when
a saved query or script makes the observation reproducible.

If the same partitions accumulate the problem, trace what assigns their work,
identity or resource ownership. State a competing explanation and a prediction
that distinguishes it. In an authorized isolated experiment, vary assignment
while preserving useful work, or vary the suspected local mechanism while
holding assignment fixed. Association alone does not establish the cause.

An even census weakens the particular skew hypothesis; it does not establish
that the original premise is correct or exclude a uniform defect. Missing actors,
short windows and aggregated identities can conceal an imbalance. Required
affinity, isolation or ordering may make asymmetric assignment legitimate.

Compare changing the source of the imbalance with compensating for it, preserving
accepted constraints. Rotation, randomization and shared pools are possible
designs, not prescribed fixes. Do not weaken a requirement to rescue a hypothesis.
Use [systems diagnosis](systems-diagnosis.md) for delayed effects and
[benchmarking](../benchmarking.md) for equivalent work and transient bounds.

Before another fix under the same premise, retain what the failures establish,
the premise, the distribution or other discriminating evidence, and the revised
hypothesis. Report unresolved causes honestly. Diagnostic scope grants no new
provider operation or broader product repair. This is an
[adaptation of pinned pstack mechanisms](sources.md), not a claim that every
repeated failure is an allocation or scheduling problem.
