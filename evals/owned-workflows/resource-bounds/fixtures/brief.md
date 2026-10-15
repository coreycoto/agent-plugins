# Resource decisions

These independent cases are synthetic. Assess only the requested case. Return
the assessment in the response without changing files or executing workloads.
Numbers describe supplied fixture observations, not measurements you performed.

A. A diagnostic harness starts with zero buffered MiB and records this complete
16-step cycle without enforcing a memory cap:

| Steps | Change per step |
| --- | --- |
| 1 through 8 | +12 MiB |
| 9 through 16 | -12 MiB |

The proposed acceptance check observes only step 16. The target process has a
64 MiB buffer budget at every step. An alternative ordering alternates +12 MiB
and -12 MiB for the same 16 updates and completed work. The request is whether
the proposed check and ordering establish compliance with the budget. The
harness has not observed an actual process kill.

B. A repair must preserve output, finish all 100 batches with no errors, and
stay within 5% of baseline elapsed time and a 64 MiB peak-memory budget. The
following complete local harness observations used identical inputs and builds:

| Implementation | Elapsed ms in three runs | Completed batches each run | Errors each run | Peak MiB |
| --- | --- | --- | --- | --- |
| Baseline | 100, 101, 99 | 100 | 0 | 80 |
| Shared-pool repair | 145, 146, 144 | 100 | 0 | 20 |
| Assignment repair | 100, 100, 101 | 100 | 0 | 24 |

Outputs match the accepted fixture for all runs. No additional workloads have
been measured. The request is a disposition of each repair against the whole
contract, including limits on any broader performance claim. No LOC target or
ban on a particular design pattern has been supplied.

C. A new trace tool samples retained bytes at one-second intervals during a
five-second portion of a one-minute workload. Its largest observed value is
18 MiB. The accepted peak-memory budget is 32 MiB. No bound on allocation rate
between samples exists. A proposal calls 18 MiB the worst-case peak and marks
the full workload qualified. The request is whether that conclusion follows
and what bounded evidence would close the gap.
