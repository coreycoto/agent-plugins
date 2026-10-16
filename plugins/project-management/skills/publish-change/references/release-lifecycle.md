# Draft and published releases

An agent may edit a draft within the authorized scope and publish an explicitly
approved draft. An already published release is protected: do not edit its
body, metadata or assets, delete/recreate it, or move its tag to effect a
correction. A beta or prerelease with `isDraft=false` is published. A name,
version suffix or `isPrerelease` flag never substitutes for draft state. This
agent workflow does not prohibit the owner from making manual corrections.

Before a covered action:

1. Resolve the exact host and repository (including stable repository ID where
   available), numeric release ID and tag. Use an authenticated read that can
   see drafts. An empty list, 404, permissions failure, timeout, malformed or
   ambiguous response is unknown state, not permission to create or mutate.
2. Bind the reviewed candidate to the resolved source commit behind the tag,
   artifact names and digests, and the final public body. A branch name or
   `target_commitish` alone does not prove the tagged commit. Verify the intended
   destination and exact payload; draft-edit authority does not permit publish.
3. Verify current `isDraft` is the boolean `true` (`draft` in GitHub REST).
   Refuse a published stable or prerelease even when an older read was draft.
   Explicit publication approval must cover this draft, source/artifacts and
   final body. Preserve that approval through routine continuation only while
   its scope and candidate constraints remain valid.
4. Check existing command and tool denials. A blanket release-edit denial can
   block a draft edit or publication despite workflow-level permission. Report
   the conflict and leave the operation blocked. Do not replace it with a broad
   allow, change transport, use REST/GraphQL/another connector, or wrap commands
   to bypass it. Enforcement changes need separately authorized review.
5. Re-read immediately before writing by the same stable identity. Refuse
   changed repository/release/tag/source/artifacts/body or unknown state;
   re-review a changed candidate and obtain new approval when required. Inspect
   supported conditional-write semantics. Re-reading narrows the race window;
   it does not atomically prevent another actor from publishing before the
   write. If atomic protection is required and unavailable, stop the mutation.

Draft edits must leave the release draft. Publication is one authorized
transition from draft to published; it does not authorize a later edit. Read
back the stable release ID, state, body, source and artifacts after the action.
On an ambiguous outcome, preserve the failure receipt and inspect current state
before any retry. If it is now published, do not retry an edit or publication.
Offer an owner correction or a new release for a requested published change.

These are instructions, not an executable release guard. A shell prefix policy
cannot query release state or cover arbitrary HTTP and connector paths. A
trusted `PreToolUse` hook needs qualified event delivery, concrete tool schemas,
fresh authenticated reads and explicit supported denials; hook errors may
continue the operation. A state-aware operation must own its write and verify
authorization independently of model-supplied flags. Neither a preflight
boolean nor an observed draft guarantees safety against concurrent publication.
Use only a separately reviewed, supported enforcement path when one is needed.
