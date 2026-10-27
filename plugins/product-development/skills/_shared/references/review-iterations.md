# Bounded review iterations

Use this procedure when an authorized review includes repair and another pass,
or when several reviewers' findings must be reconciled. An ordinary review can
finish after one pass. Use the available native reviewer under the parent
skill's authority; this procedure requires no particular model or provider.

## Establish the boundary

Identify the intent, base, exact candidate or working diff, existing edits and
completed checks. Set a finite review budget from consumer guidance or the task;
when neither specifies one, allow at most three passes before reporting the
remaining decision. A budget limits repeated work, not the evidence required
for acceptance. Do not edit the candidate while its independent review runs.

The initial pass covers the requested change in its caller and test context.
Keep a compact record of material findings in the existing response or task
record; no new ledger file is required. Give each distinct failure scenario a
stable identifier with its trigger, consequence, evidence, affected candidate
and status. Keep that identifier when a finding is repaired, disputed or
reopened, rather than counting each mention as a new defect.

## Reconcile and revisit

The parent checks each claim against the accepted contract. Record the resolving
change and check, or a reason supported by evidence for declining it. Separate
an optional improvement from a required repair. Judge severity by the reachable
consequence and contract: an infrequent authorization bypass or data-loss path
does not become cosmetic because it is rare.

After an authorized repair, run affected checks and identify the new candidate.
Send the reviewer the change since its previous pass, remaining finding IDs and
their evidence. Concentrate follow-up on those surfaces and their affected
callers. A changed invariant, dependency or conflict resolution may invalidate
earlier conclusions outside the edited lines; expand that affected review
instead of assuming the previous verdict still applies. A new candidate does
not automatically require rereading every unaffected part of the original diff.

## End with an evidenced disposition

Finish when material findings have an evidenced resolution and review covers
the current behavior, or report what prevents that conclusion. An unsupported
objection need not cause another repair merely to obtain agreement. Optional
style suggestions or presentation-only edits need no further pass unless they
change a reviewed contract. Do not grow the task to satisfy unrelated requests.

When the budget ends or a material dispute cannot be resolved from available
evidence, state the open finding, competing claims and smallest next decision
or check. Do not label exhaustion, silence, a timeout, a score or reviewer
consensus as approval. Any further passes follow the task's resource authority;
the parent still owns acceptance and the authorized delivery endpoint.
