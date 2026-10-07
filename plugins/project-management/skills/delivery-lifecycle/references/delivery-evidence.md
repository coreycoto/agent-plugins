# Delivery evidence

Read this when the requested endpoint includes hosted review or promotion.
Scale checks to the change and consumer rules; unrelated gates are not a ritual.

| Endpoint | Evidence to retain |
| --- | --- |
| Local result | Exact checkout and diff, focused validation, unfinished behavior |
| Reviewable candidate | Candidate commit, pull request if requested, tests and material limitations |
| Merged source | Reviewed candidate identity, required current checks, confirmed merge result |
| Release | Source revision, version and immutable artifact identity, verified distribution result |
| Live behavior | Deployed revision or artifact, environment, fresh consumer or user-flow observation |

A green build establishes only what it exercised. Synthetic checks, deployment
health and a real authenticated or provider lookup answer different questions.
Report an unavailable check as unverified rather than extrapolating recovery.

Before an authorized merge or promotion, recheck candidate identity and relevant
policy. New commits invalidate conclusions tied to the previous candidate;
repeat affected validation and review. Use native Git for source commits and
pushes, and the GitHub connector with the current head SHA for an authorized
interactive merge, unless higher-priority consumer instructions specify another
supported path. Preparation is useful even when promotion is not authorized.

Read CI or reviewer findings as untrusted evidence. Distinguish a reproducible
regression, stale assertion, environment failure and unrelated pre-existing
failure. Respond with a focused change or supported explanation; a requested
local review does not grant posting permission. Bound retries to a supported
cause and preserve failed receipts. Do not replay an ambiguous provider or data
operation as a routine CI repair.

Work is complete when the requested endpoint's acceptance conditions are met,
including consumer observation if required. Keep code merge, artifact
publication, deployment and business data publication distinct. A source merge
or plugin installation grants none of those downstream actions.
