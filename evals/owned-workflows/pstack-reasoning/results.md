# Recorded result: discard the pruning candidate

The 2026-10-15 pilot ran three synthetic tasks twice per arm using Codex CLI
0.162.1 and fixed `gpt-6.1-sol`. Separate candidate/prior and candidate/no-procedure
comparisons produced 24 target attempts, all with completed exit status 0.
One subsequent rubric call timed out; 23 attempts received grades. The private
runner labels that timeout as an execution failure, but its retained task exit
and grader error establish that it occurred during grading.

Six correct/incorrect calibration controls passed before task execution. An
earlier catalog probe under the outer workspace sandbox could not start, making
six calibration observations unavailable; the permitted invocation retained the
evaluator's own normal sandbox and catalog isolation. No target call was replayed
for a better result. Schema and resource-containment staging failures were
resolved before target execution using the adaptations in the README.

## Measurements and their limits

| Comparison | Arm | Graded / attempted | Raw checks passed / graded | Mean task process time | Mean reported total tokens |
| --- | --- | --- | --- | --- | --- |
| Prior wording | Revised candidate | 5 / 6 | 12 / 15 | 21.50 s | 43,676.5 |
| Prior wording | Prior | 6 / 6 | 14 / 18 | 21.56 s | 44,017.2 |
| No procedure | Revised candidate | 6 / 6 | 15 / 18 | 23.76 s | 46,324.5 |
| No procedure | No procedure | 6 / 6 | 11 / 18 | 18.15 s | 45,007.3 |

**The raw semantic scores are unqualified.** The judge received the frozen task,
input facts and final response, but not the target's tool events. It rejected
workspace facts such as absent AGENTS.md/Git metadata and several statements
that local checks ran. Inspection of completed command receipts establishes
those observations. The routine-case expectation also incorrectly required
checks to stay unexecuted even though a local in-memory reproducer fits the
task. The broader premise-reset corpus corrects that expectation prospectively;
the measured pilot definition and raw grades remain unchanged here.

Passing simple correct/incorrect controls did not qualify this missing-evidence
branch. A future comparison must supply relevant execution receipts to the
judge, include calibration controls for legitimate observed checks and preserve
the distinction between task failure and grader unavailability. No retrospective
score rewrite or successful regrade is claimed.

The prior comparison's matched semantic delta was zero among the five pairs
with both grades. Mean process-time and token differences were small and noisy;
the two comparisons ran concurrently. Time excludes separate catalog setup and
grading. Token values are event-reported totals including cached input, not
prices or billed cost. These measurements support no speed or cost advantage.

Invocation-local catalogs were verified for every target attempt. Qualified
entry-body observations covered 5/6 revised attempts in each comparison and
5/6 prior attempts; the no-procedure control exposed zero enabled skills.
Missing entry observations remain unknown. Premise-reference text appeared in
the temporal attempts, but multi-file commands were outside the qualified
resource-read adapter. Content exposure is not attributed reading or adherence.

## Source decision

The tested reference shrank from 382 to 338 whitespace-separated words. That
alone does not justify pruning. Discard that candidate, preserve the prior
diagnostic detail and add the general falsifiable-premise frame ahead of it.
The shipped additive combination and optional research reference are authored
changes with synthetic source qualification; this pilot does not establish their
model effectiveness, automatic selection or installed-session behavior.

The [aggregate receipt](results.json) records exact procedure, fixture, definition,
oracle and reference hashes without private catalogs, paths, configuration or raw
transcripts. Raw command and failure receipts stay in ignored local artifacts.
The original 17-case adoption comparison remains unrun in its broader scope.
