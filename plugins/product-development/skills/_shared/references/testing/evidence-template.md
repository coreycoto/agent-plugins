# Bounded verification record

This template is an optional engineering adaptation. Use a few lines for a small
change and an existing issue/map for larger work. It is not a new required file,
framework or substitute for executable checks.

## Context

- Capability and accepted task; authorized endpoint.
- Baseline and candidate revision/diff; relevant runtime/tool configuration.
- Mode: specification/regression, characterization, experiment or acceptance.
- Existing failures and unavailable prerequisites, with observed provenance.

## Condition map

| Condition / credible fault | Expectation and its authority | Real boundary / doubles | Test or experiment | Observed result / limits |
| --- | --- | --- | --- | --- |
| Name the behavior, not just a source file | Rule, reviewed example, pinned baseline or trusted record | Include store/process/provider scope | Existing path, case and actual command | Pass/failure/unknown, evidence location and untested scope |

Distinguish declared instructions from observed execution. Keep parameter values,
source/fixture identity, completion status and assertion diagnostics where they
matter. Redact sensitive inputs; do not copy credentials or raw private records
into public evidence.

## Refactor additions

Identify preserved behavior, suspicious characterization and intentional changes.
Record seam/enabling point, actual callers and compatibility/data contracts.
For test retirement, map each removed condition to retained detection evidence.
For performance claims, record equal work, environment, instrumentation and
measurement variability. For recovery, state exactly what stopped, what survived
and what reconstructed state after restart.

## Conclusion

Separate supported findings from hypotheses. State which evidence qualifies the
requested stage and what still blocks another stage. Account for task-owned
probes and cleanup without discarding useful failure evidence. Do not claim
complete correctness, installed skills or deployed behavior from a passing
structural validator.
