# Preventing a demonstrated recurring mistake

Use when a supported recurring correction, dangerous invalid state or fragile
boundary makes a durable guard worthwhile. This is conditional design guidance,
not a closeout requirement. Identify the known mistake, accepted invariant and
owning boundary. Include a nearby legitimate case that must remain possible;
a guard that rejects both has merely moved the bug.

For a fragile public API, inspect the call a reasonable consumer would naturally
make and the relevant callers. Check whether it preserves the accepted invariant
without a hidden helper, flag combination or prerequisite call. Where scope and
compatibility allow, make that ordinary operation enforce the rule, narrow
invalid inputs or expose an exceptional operation explicitly. A wrapper does
not remove the trap while ordinary callers can bypass it. Preserve legitimate
exceptions and external or persisted contracts; an absent local caller alone
does not establish that a compatibility path is unused.

Choose the cheapest effective remedy that fits the consumer's tools:

- Concentrate a duplicated rule at its actual owner, with a narrow API that
  removes caller choices which should never have existed.
- Use types or explicit state when the compiler can exclude the invalid
  combination. Retain runtime validation for external or persisted data.
- Use a targeted dependency, schema, generator or lint check for an accepted
  structural constraint. A check should name the forbidden condition, rather
  than freeze current file layout or encode a stylistic preference.
- Use an independent behavioral regression when the failure depends on input,
  state, ordering or interactions that static checks cannot establish.

Combine remedies only when they cover distinct failure paths. Compare the
maintenance cost, false positives, migration burden and actual recurrence risk
with a local repair or no new guard. One anecdote does not justify a universal
rule. Use existing checks before adding a new framework. Expanding API or
architecture scope still needs an accepted change boundary.

Qualify through the known bad case and the legitimate near miss. Depending on
the remedy, retain a negative type compilation, targeted forbidden dependency,
independent invariant test or old-bug sensitivity in isolated scratch. For an
API remedy, exercise the ordinary public call and the legitimate exception.
Confirm that the guard's ordinary command is part of the consumer's relevant
check path; a check nobody invokes does not prevent recurrence. Do not mutate
a shared candidate during another validation run.

Report the guarded invariant, owner, evidence, command and remaining escape paths.
When useful and requested, [capture-solution](../../capture-solution/SKILL.md)
preserves reasoning, rejected alternatives and limits that code and tests cannot
express. A note supplements an executable remedy; neither authorizes global
memory, instruction changes or unrelated policy edits.
