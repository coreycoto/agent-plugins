# GitHub tools and exact-candidate evidence

Use the available GitHub connector for supported PR/issue lifecycle operations.
Use native Git for checkout state, staging, commits and pushes. Use gh for
Actions checks/logs or a concrete connector capability/access gap; inspect the
actual callable tools and state the gap before a lifecycle write through a
fallback. Installed software does not establish authentication or authority.

Follow the consumer's delivery process and existing authorization. Fixing a
check does not independently authorize merge, release, deployment or comments.
Do not bypass command policies by using a connector or another shell spelling.
Apply [release safeguards](../../publish-change/references/release-lifecycle.md)
when selecting a release operation.

Identify repository, head branch, base and exact intended commit. Set the
repository explicitly for CLI reads rather than relying on another checkout:

```sh
gh pr view NUMBER --repo OWNER/REPO \
  --json number,state,headRefOid,baseRefName,isDraft,statusCheckRollup
gh pr checks NUMBER --repo OWNER/REPO
gh run view RUN_ID --repo OWNER/REPO --log-failed
```

Replace placeholders from current evidence. Compare `headRefOid` with the pushed
candidate and each workflow's head SHA. Pending, skipped, cancelled and failed
checks are distinct from successful required checks. Inspect review threads,
required reviews, branch protection and mergeability before authorized promotion.
An old green head does not qualify a later commit; recheck the expected head at
the write boundary and use an API's expected-head condition where supported.

Reuse the matching open PR instead of creating another. Prefer structured
connector arguments for title and body. When a CLI fallback is necessary, write
exact multiline text to a UTF-8 file and pass `--body-file`. Use `gh api --input`
for structured JSON rather than interpolating prose or JSON into shell code.
After an uncertain write, inspect current state before retrying.

Check `gh auth status` when diagnosing a CLI access gap. Never print tokens or
put credentials into commands or source. Preserve the host's credential helper,
managed proxy and destination-scoped authentication. A successful package read,
Git fetch or connector call does not prove another transport has the same access.
Use an existing credential through its supported helper for an authorized
operation rather than changing global Git configuration to repair one checkout.

Report PR/issue URLs with the verified candidate and relevant limitations.
Check results do not establish merge, release or deployment completion. After
merge, inspect the actual merge commit and its main CI before a separately
authorized publication. Record release and installed/runtime verification as
their own stages; retain failed or ambiguous operation receipts.

These mechanics apply to local and cloud development hosts with compatible
tools. Inspect actual Git/network access and client support; a marketplace pin
or cloud environment declaration alone does not establish loaded capabilities.
Keep personal account names, paths and default repositories in consumer setup.

Sources: [PR checks](https://cli.github.com/manual/gh_pr_checks),
[PR view](https://cli.github.com/manual/gh_pr_view),
[workflow runs](https://cli.github.com/manual/gh_run_view),
[API](https://cli.github.com/manual/gh_api).
