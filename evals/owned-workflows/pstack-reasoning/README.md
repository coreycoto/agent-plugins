# Bounded reasoning and instruction-pruning comparison

Issue [#41](https://github.com/coreycoto/agent-plugins/issues/41) follows the
pstack research assessment. The candidate generalizes and shortens the existing
premise-reset reference. This is a component experiment, not qualification of
every reference in the release or automatic skill selection.

**Recorded disposition: discard the pruning candidate.** See the
[results and limitations](results.md). This directory preserves the measured
pilot definition, including a subsequently identified routine-case expectation
defect. Do not reuse its semantic scores as qualified evidence. Repair tool-event
evidence delivery and recalibrate the affected legitimate cases before a new run.
The shipped reference retains the prior diagnostic detail and adds the general
premise test ahead of it; that final combination was not model-compared.

## Frozen decision

Compare prior source `6523011c94f94afb716d51efcf4ed5be09a3e203`, the same
procedure closure with only premise-reset.md replaced by the candidate, and a
no-procedure control. Cases were selected before the wording edit:

- Temporal expiry failures test generalization beyond worker imbalance.
- Required hardware-domain affinity tests a legitimate constraint.
- A half-open booking interval defect tests routine direct work.

Each arm must preserve the accepted contract, evidence limits and read-only
scope. A candidate-only required-behavior loss rejects the pruning. Any benefit
claim needs observed quality, task wall time or token evidence; shorter source
alone is insufficient. Equal grades are bounded non-regression, not broad
effectiveness. Do not tune on these results and reuse them as held-out evidence.

Use the existing private output evaluator with fixed `gpt-6.1-sol`, two
repetitions and 90-second call limits. Its two-arm interface runs candidate/prior
and candidate/no-procedure as separate comparisons; this repeats the candidate
and is not one randomized three-arm experiment. Alternating order balances each
pair. Report three unique tasks separately from all attempts and repetitions.
If comparisons run concurrently, shared runtime conditions limit timing claims.

The main semantic rubric and separate authority/execution-status rubric have
correct and deliberately wrong calibration answers. Expectations and grades
stay outside measured workspaces. A frozen source assertion rejects mutations
but cannot establish diagnostic quality. Qualify native catalog isolation and
calibrate semantic discrimination before relying on task grades. Retain every
failure or unavailable attempt.

## Staging with the existing private evaluator

This suite has three checks per task and exactly one smoke case to match the
current private runtime. `--tier deep` selects all three. The larger public
reference suites remain broader author corpora; their multiple smoke cases and
two-check layout are not directly accepted by that runtime.

The runtime permits procedure resources only beneath `skills/`. In both frozen
snapshots, mechanically replace the four relative license/notice citations in
judgment/sources.md and judgment/task-depth.md with immutable public source URLs
at the baseline revision. Retain all instructional text and original source
bytes in the public package; do not remove licenses or weaken containment.
Record each replacement and before/after hashes. Any other escaping reference
is an unresolved staging error. This adaptation means the experiment qualifies
the declared snapshots, not byte-identical installed packages.

Run `agent_plugins.agents.evals.calibrate_skill_rubrics` against this suite,
then `agent_plugins.agents.evals.evaluate_skill_outputs` with the candidate
snapshot as `--repo-root`. Use `--baseline-skill-root` for the frozen prior
procedure and a separate run with `--baseline-without-skill`. Supply the fixed
model, `--repetitions 2`, `--tier deep` and the call timeout above. First use
`--no-run` to qualify staging. Native execution retains normal workspace
sandboxing, invocation-local catalog controls and authentication; no bypass,
global configuration change or new runtime is part of this experiment.

Record procedure/fixture/grader identities, explicit body and supporting-resource
observations, semantic outcomes, task wall time, tokens and unavailable counters.
Setup and grading time are separate. Keep raw events in private local artifacts;
publish only synthetic definitions and redacted aggregate results. The separate
research-coverage suite qualifies source preservation and semantic expectations;
it needs its own observed comparison before an effectiveness claim.
