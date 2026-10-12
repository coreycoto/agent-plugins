# Test strategy and confidence audit

Source basis: Meszaros chs. 3-6/12-14; GOOS chs. 1/4-5; Continuous Delivery
chs. 4-5/7-9. See [source locators](sources.md). The evidence map is an adaptation.

## Begin with the decision

Select one capability, change or reported confidence gap. Record the baseline,
affected public contracts, current tests and authorized endpoint. An audit is
read-only until changes are assigned. Distinguish product defects, test defects,
harness/configuration defects and unavailable evidence; do not repair the wrong
one merely to obtain green output.

Ask what could fail for a user or downstream consumer, not which files have the
fewest tests. Include risk from wrong values, absence, duplicates, ordering,
partial effects, compatibility, authorization and resource limits where relevant.
For a small pure function, two decisive examples may be sufficient; a durable
handoff needs evidence at its actual commit and observation boundaries.

Create a small map using the [evidence template](evidence-template.md). Reuse an
existing issue or consumer map instead of creating a second catalog. Trace an
important condition through the assertion and fixture to the executed code.
A title, test count, coverage counter or reported command is not that trace.
Sample first and disclose sampling; do not call a partial inventory exhaustive.

## Choose evidence along separate axes

| Purpose | Typical boundary | Important limitation |
| --- | --- | --- |
| Rule/specification | Function or cohesive component | May not exercise wiring, serialization or storage |
| Characterization | Existing observable seam | Preserves observed behavior, including possible defects |
| Collaboration/contract | Real producer and consumer or owned adapter | Simulated transport does not prove provider configuration |
| Persistence/recovery | Real store, transaction, fresh handle/process as needed | State retained in the harness may invalidate restart claims |
| Acceptance | User-facing API, CLI, UI or library behavior | Startup alone is not the requested result |
| Resource/operational | Representative workload and deployed boundary | A small fixture or instrumented run may not represent production |
| Exploratory | A charter and observations | Useful findings are not automatically a repeatable regression suite |

Describe doubles, environment and size separately from purpose. Use the smallest
boundary that can detect the relevant fault, then retain additional layers for
distinct integration, configuration or user-value risks. A pyramid is a cost and
feedback heuristic, not a mandated proportion of case rows.

## Diagnose the suite before prescribing changes

Read representative passing tests as well as failures. Identify weak or circular
oracles, hidden fixture causes, global mocks, unawaited tasks, missing discovery,
untyped fixtures, incidental snapshots and slow setup. Map each observation to a
concrete consequence and proposed check. A smell is a lead, not an automatic
violation. Examples: shared immutable input may be safe; shared mutable state
without isolation may make tests order-dependent.

Evaluate the harness too: intended tests are discovered once; parameter values
remain identifiable; assertions execute; failure exit codes survive wrappers;
empty/partial results cannot qualify; cleanup works after failure; caches include
relevant inputs; instrumentation does not change a measured resource claim.
For typed languages, verify the relevant test roots are actually compiled.
Transpiling and executing a test do not by themselves establish static checking.

Prioritize by consequence, likelihood supported by evidence, ability to detect,
feedback delay and maintenance cost. Do not invent numerical risk probabilities.
First improve the oracle or seam that blocks the next useful change. Then reduce
fixture friction and redundant evidence. Broad folder churn rarely belongs first.

## Finish the audit

Report strengths to preserve, supported gaps, uncertain gaps, and a small ordered
work plan. For each change, name the invariant preserved and the evidence that
would demonstrate improvement. A baseline failure without a matching baseline run
is an unattributed failure, not automatically pre-existing. Preserve required
checks while proposing changes to their cost or selection separately.

Measure diagnosis time, meaningful fault detection, unintended test churn and
equivalent-work runtime where possible. More tests, fewer files or higher coverage
can accompany improvement but do not define it.
