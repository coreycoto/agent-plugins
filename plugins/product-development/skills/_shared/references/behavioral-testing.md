# Independent behavioral evidence

Before meaningful behavioral implementation, identify the accepted invariant,
credible failure cases and independently expected outcomes. Include boundaries,
ordering or partial completion when the actual change makes them relevant.
Use small test-and-code slices so observations inform the next case; do not
require an exhaustive failure inventory or all tests before any implementation.
Tests for existing behavior, characterization and newly discovered failures
remain useful; current behavior alone does not establish the accepted contract.

## Owning boundary and placement

Choose a public seam that observes the intended contract: exported operation,
request, command, storage interface or user flow. “Public” is relative to the
component being specified; not every behavior requires a browser test. State
what the chosen seam catches and what it leaves unexercised. A concurrency bug
may need multiple callers; a pipeline bug may need the actual envelope chain.

Prefer the existing suite at the smallest boundary that can prove the rule.
Pure calculations may belong in unit tests; serialization, persistence, retries
or coordination often need integration tests. Use end-to-end coverage for a
user contract that lower seams cannot establish. Extend an existing case or
suite when clear; a new file is reasonable for a distinct responsibility, not
merely because a new incident occurred. When several layers retain coverage,
name the different failure each catches, such as calculation versus transport
wiring. Similar assertions or shared executed lines do not prove redundancy.

## Independent expectations and sensitivity

Derive expected behavior independently. A worked example from accepted rules,
known-good fixture or invariant can disagree with the implementation. Calling
the same production transformation to produce expected values cannot catch its
mistake. Full-output snapshots need meaningful review and should not freeze
incidental details. Coverage indicates execution, not correctness of the oracle.

For test-first work, observe each slice's intended assertion fail before its
implementation. For a regression, observe the original symptom before repair.
Ensure a failing assertion proves behavior rather than setup, import or an
unavailable dependency.
Then observe the fix and rerun the original broader scenario. A minimized test
can miss the interaction that first caused the failure.

Use fixtures and boundary fakes that retain the contract being examined. Control
clock, random seed or filesystem where these obscure the result. Keep provider
accounts out of deterministic tests; mark synthetic coverage separately from
real upstream observation. Do not mock internal calls simply to assert their
sequence unless that sequence is itself an accepted public contract.

When pruning or consolidating, retain independently specified cases and failure
messages. Demonstrate that the retained tests catch the regression before
removing its old coverage. For consequential tests or consolidation, a bounded
mutation can strengthen that evidence:

- Start with passing tests against the unchanged candidate in isolated scratch.
- Make one meaningful fault, such as an incorrect boundary comparison, missing
  tenant key or bypassed validation, and run the relevant ordinary test command.
- Keep expectations independent and unchanged. Identify the behavioral failure
  that detected the fault; syntax, import or setup errors do not establish it.
- Investigate survivors: the test may miss the fault, or the mutation may leave
  behavior unchanged. Report timeouts and invalid mutations separately rather
  than treating every nonzero exit as an assertion detecting the intended bug.

Use a known bad case when it provides the needed proof more directly. Neither
a coverage percentage nor a mutation score establishes complete correctness or
justifies a test deletion quota. Use existing tools; this guidance does not
require a new framework or mutation run for every change. Do not alter the
shared candidate during another validation run.

## Task-created probes

Inspect existing edits before creating diagnostic tests, scripts, fixtures or
instrumentation so their ownership remains clear. Before final verification,
account for those created by this task:

- Retain the smallest durable test when it protects a unique accepted contract.
- Integrate useful assertions into the owning suite and retire the redundant
  probe within authorized cleanup scope.
- Remove owned diagnostic-only residue when authorized; preserve useful failure
  evidence in the consumer's approved evidence location before cleanup.

Preserve pre-existing tests and unrelated edits unless their consolidation is
explicitly in scope and supported by retained regression evidence. When probe
ownership or cleanup authority is uncertain, preserve it and report the limit.
Slowness alone does not make a meaningful regression disposable. Keep evidence
of failed or ambiguous provider operations; never replay them for a cleaner
receipt. A review reports dispositions without authorizing source edits.
