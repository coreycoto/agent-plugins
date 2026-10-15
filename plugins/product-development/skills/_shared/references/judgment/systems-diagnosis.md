# Investigate the system around the symptom

Use when latency, retries, backlog, resource exhaustion or recurring failure
crosses an individual function. Bound the affected outcome first; a systems
lens supplements a concrete reproducer and does not replace one.

Name what accumulates, what adds/removes it, the units and the observation window.
Separate requests, attempts and completed logical work. Inspect arrival rate,
completion rate, queue age, retries, errors and resource saturation as relevant.
Use actual measurements rather than assume the largest function is the limiter.
A hypothetical retry loop can amplify load after a slowdown; verify the mechanism
and its ordering before calling it the cause.

When repeated repairs fail under one assumption, use the
[premise-reset guide](premise-reset.md). Inspect relevant distributions and
role assignment before compensating for an assumed local defect. A balanced
census does not rule out a uniform defect or establish the premise.

Distinguish elapsed time, service time and waiting. Do not sum overlapping spans
as wall time. Check load-generator limits, caches, unfinished work and errors.
A fast timeout does not establish faster useful completion. A longer timeout
may hide a symptom while work and resource ownership continue accumulating.
Preserve correctness and equivalent useful work in comparisons.

For each causal hypothesis, state a prediction that differs from alternatives.
Observe or perturb one bounded condition in an authorized isolated environment.
Include delayed feedback: an immediate local improvement can coincide with
later backlog growth. Compare steady state and recovery where relevant. A causal
diagram is a hypothesis, not measured proof or permission to alter capacity.
For cyclic assignment or cleanup, inspect peaks and partial-cycle windows as
well as net change. Full-cycle cancellation may arrive after a resource limit
is exceeded. Keep required affinity and ordering intact when comparing designs.

Separate the triggering defect from conditions that allowed it to spread.
Repair a concrete bug when assigned; investigate systemic contributors only as
far as the task and evidence warrant. Neither a single-cause story nor a broad
systems narrative excuses missing evidence. Avoid blaming people from commit
history or inferring their intentions.

Record the measured limiter, failed hypotheses, experiment, useful-output result
and residual uncertainty. Reuse the [benchmarking guide](../benchmarking.md).
No queueing formula is a substitute for checking its assumptions. Meadows's
[leverage-points essay](https://donellameadows.org/archives/leverage-points-places-to-intervene-in-a-system/)
informs the attention to accumulation, delays and feedback; the software-specific
procedure is our adaptation, not a universal optimization recipe.
