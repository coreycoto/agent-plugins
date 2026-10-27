# Continuing an existing PR

Use this guide when a handoff or delivery task resumes a PR or branch. Resolve
the actual repository, PR, head and target branch; do not substitute a presumed
default branch. Record the observed remote head, common ancestor, relevant
uncommitted edits and the original user-visible goal. Fetch the relevant refs
when access is available. Missing access leaves current remote state unverified.

## Reassess before updating

Read the original diff and decisions alongside changes on the target branch
since divergence. Follow affected behavior, APIs, schemas, dependencies and
invariant ownership. Look for an existing replacement when the supplied history
or code suggests one. A conflict-free patch can still restore removed behavior,
duplicate a newer implementation or solve a problem that no longer exists.
Age and overlapping filenames alone do not settle usefulness.

Choose the smallest supported next step:

- If current behavior already meets the original goal, explain the replacement
  and stop unnecessary branch work. Recommend a disposition without closing or
  otherwise changing the old PR beyond existing authority.
- If the goal and approach remain appropriate, update the branch within the
  requested delivery stage and run the relevant consumer checks.
- If the goal remains but newer contracts invalidate the approach, identify the
  needed redesign. Continue routine in-scope repairs already authorized; return
  a material scope or architecture decision before committing to broader work.

## Preserve the change and concurrent work

Use an isolated checkout when needed to protect existing edits. Retain the
original head and base so an authorized rebase can be checked against them.
Compare the old and new commit series with `git range-diff`, then inspect the
resulting behavior and final diff against the new base. Investigate lost intent
and unintended restoration of already-landed behavior; clean conflict resolution
is insufficient evidence by itself.

For an authorized update that rewrites a remote branch, bind
`--force-with-lease` to that branch's previously observed full head SHA.
Recheck remote changes before the write. A failed lease means another update
must be reconciled, not overwritten with a refreshed lease automatically.
Branch update authority does not grant merge, closure or a base-branch change.

## Preserve contributor provenance

Keep inherited commits' verified author metadata and existing co-author trailers.
Identify inherited work and new repairs separately in the handoff or requested
PR description, and link the original PR when one exists. Respect an authorized
in-place, replacement or stacked continuation rather than choosing another form
solely for convenience.

When preparing a squash, carry verified human contributor credit into the
proposed commit metadata or trailers using the consumer's convention. A link or
model attribution does not replace that credit. Do not invent an identity or
email to fill a gap; retain known provenance and report what cannot be verified.
Recheck the source PR before final continuation if it may have changed meanwhile.

Finish with the current relevance decision, preserved intent and provenance,
checks and remaining delivery gate. A recommended closure, prepared squash or
successful rebase is not an executed merge or permission for one.
