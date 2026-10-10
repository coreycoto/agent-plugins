# Owned workflow selection and migration

The four public packages contain 33 self-contained skills. Choose a direct task
entry point; `product-development:engineering-workflow` is an optional router.
Product policy, verification commands, permissions and knowledge remain in the
consumer repository. A local task ends with a verified local result; publication
requires the corresponding delivery authority.

| Need | Owned entry point |
| --- | --- |
| Explain current code or its history | `product-development:understand-codebase` |
| Assess structural maintenance friction in a selected subsystem | `product-development:understand-codebase` with its assessment mode |
| Reproduce and fix a failure | `product-development:diagnose-problem` |
| Resolve a technical choice | `product-development:design-change` |
| Implement accepted intent | `product-development:implement-change` |
| Review a candidate | `product-development:review-code` |
| Add meaningful behavioral tests | `product-development:test-behavior` |
| Exercise the actual user path | `product-development:verify-product` |
| Create or refresh verification instructions | `product-development:maintain-verification` |
| Test an uncertain technical approach | `product-development:prototype-decision` |
| Improve measured performance | `product-development:improve-performance` |
| Clarify identity, state and invariants | `product-development:model-domain` |
| Retain or refresh reusable project reasoning | `product-development:capture-solution`, `product-development:refresh-solutions` |
| Change a substantial structure | `product-development:phased-refactor` |
| Plan, sequence and deliver work | `project-management:intake`, `backlog-planning`, `delivery-lifecycle` |
| Resume or hand off work | `project-management:handoff-work` |
| Govern, review and publish | Project Management's existing governance, relationship, quarter planning, review and publishing skills |
| Discover, compare or specify product opportunities | Product Management's discovery, prioritization and requirements skills |
| Run a product learning experiment | `product-management:product-experiments` |
| Explain, draft or edit | Communication's agent-communication, write-prose and edit-prose skills |

## Improving the environment and human decisions

The existing entry points support six additional mechanisms through conditional
references, without increasing the 33-skill catalog:

| Need | Concrete result and owning workflow |
| --- | --- |
| Prevent a recurring mistake | Diagnosis/design choose a proportionate structural, type, API or executable guard; verify the known bad case and legitimate behavior. Closeout links retained reasoning and the guard. |
| Select worthwhile structural work | `understand-codebase` assesses a bounded subsystem using callers, ownership and maintenance evidence, including a justified no-change outcome. Accepted implementation continues through design/refactor. |
| Navigate and verify product behavior | `maintain-verification` links accepted behavior, source, commands and retained evidence in an optional consumer feature map. Its packaged read-only validator checks references and affected mappings without executing commands or qualifying behavior. |
| Simplify agent instructions | Private Agent Development compares prior/revised instructions on routine, conditional and boundary cases, with supporting-resource observations and fresh balanced repetitions. Public skills do not depend on the private runtime. |
| Pressure-test a product commitment | Product Discovery/Experiments expose consequential assumptions, credible alternatives and disconfirming evidence; preserve unknown costs and decision criteria. |
| Make an explanation inspectable | Communication chooses prose, tables, diagrams or richer artifacts for the reader's task, preserving uncertainty and actual decision authority. Technical-writing guidance borrows clarity principles without claiming STE compliance. |

Product facts, feature maps, verification commands and correction records remain
consumer-owned. Private maintenance can connect supplied interventions to repairs
and later recurrence evidence. These mechanisms do not create automatic monitors,
a universal registry or additional approval checkpoints.

The [author-only corpus](../evals/owned-workflows/README.md) includes deterministic
artifact tasks and separate semantic cases. A synthetic feature-map pilot drives
the existing notes fixture CLI and retains command/source evidence. That is not
a deployed-product qualification or proof of reduced human supervision.

In Codex, invoke a qualified name with `$`, for example
`$product-development:diagnose-problem`. Other hosts may expose different syntax.
Installed files do not prove that an existing session has reloaded discovery.
Native agent setup remains an explicit `manage-codex-agents` operation in the
owning package. Roles are optional; skills work without delegation.

## Skills-only local candidate trial

Use this path for one direct procedure trial; native roles are optional. In the
publisher checkout with author dependencies available, build and inspect a
candidate before changing the chosen client's installation:

```sh
uv run --locked python scripts/build_codex_package.py
uv run --locked python -B scripts/inspect_skill_installation.py \
  --candidate dist/plugin-packages/codex/plugins/product-development
```

For an authorized local client trial, Codex CLI 0.160.0's help confirms these
commands. Check the chosen client's marketplace first; if `agent-plugins` already
points to another source, use a separate trial client/home rather than replacing
that registration. The local build uses marketplace name `agent-plugins`:

```sh
codex plugin marketplace add "$PWD/dist/plugin-packages/codex"
codex plugin add product-development@agent-plugins
codex plugin list --json
```

These native commands acquire and enable the package; the diagnostic never does.
Keep existing `.agents/skills` copies and legacy locks. Select the installed/cache
package path reported by the client, then compare its actual files:

```sh
uv run --locked python -B scripts/inspect_skill_installation.py \
  --candidate dist/plugin-packages/codex/plugins/product-development \
  --installed /absolute/path/to/installed/product-development \
  --discovery-root /absolute/path/to/consumer/.agents/skills
```

Pass only existing roots you deliberately want inspected; omit a discovery root
that does not exist. A matching version alone is insufficient: inspect workflow
fingerprints, changed/missing files, and duplicate groups. Begin or reload the
chosen task using the client's supported controls, confirm its available skill
catalog, and try a bounded read-only request such as:

> Use $product-development:understand-codebase to explain how this repository's
> main command reaches its output. Finish locally; do not change files.

Retain the selected body's path and exact file SHA-256 alongside the session and
outcome. This is explicit invocation, separate from automatic selection. If the
session cannot discover the qualified skill, report that gap; explicitly reading
a built body qualifies a procedure but does not prove plugin activation.
`manage-codex-agents`, hook consent, role installation and role-selection evidence
remain a separate optional workflow. No role setup is required for a parent to
use the ordinary procedures.

## Read-only installation diagnostic

`scripts/inspect_skill_installation.py` prints JSON to stdout. It reads only the
supplied candidate, repeatable `--installed` package paths and repeatable
`--discovery-root` directories. It does not search the home/configuration, execute
Codex, install, reload, delete or run inference. Run Python with `-B` to suppress
interpreter bytecode writes. Missing or malformed inputs produce exit code 2;
a completed inspection produces 0 even when differences exist, since this is a
diagnostic rather than an adoption gate.

Plugin identity/version and declared repository are reported separately from the
workflow fingerprint. The fingerprint covers non-hidden regular files beneath
`skills/`, including references; cache directories, credential filenames and
`.pyc`, `.pem`, `.key` files are excluded. Descendant package links are rejected.
Roles, hooks, runtime code and acquisition origin are outside that fingerprint.
Discovery scans skip descendant directory links; explicitly supply a linked
skill's resolved directory if it needs inspection. Coverage is limited to supplied
locations. Reports contain metadata, paths and hashes, never skill or config text.

Duplicate names and duplicate literal bodies are separate groups. Body comparison
ignores frontmatter, normalizes CRLF and strips outer whitespace; it does not
establish semantic equivalence or matching supporting references. Repeated
observation of the same resolved file path is counted once. The candidate is not
counted as an installed duplicate.

Optional `--native-inventory /path/to/existing-plugin-list.json` retains that
supplied JSON's digest as provenance. It does not infer discovery from installation
or enablement, or guess an undocumented native output schema.
`--session-observations /path/to/observations.json --session-id SESSION` can compare
supplied observations to exact candidate file hashes using this narrow format:

```json
{
  "kind": "active-session-skill-read",
  "session_id": "SESSION",
  "skills": [{"qualified_name": "product-development:understand-codebase",
              "file_sha256": "<exact 64-character lowercase SHA-256>"}]
}
```

A matching observation covers only its listed skill body. The diagnostic cannot
authenticate supplied observations or establish that all references were loaded.
Its `reload_verified` and `automatic_selection_verified` fields remain false;
on-disk matches alone always leave active-session discovery unverified.

## Former dependency names

These are procedure replacements, not exact behavioral aliases. They preserve
useful mechanisms while following the consumer's authority and tools.

| Retired declared name | Owned destination |
| --- | --- |
| code-review | product-development:review-code |
| decisions | product-development:design-change; product-management:product-prioritization for product choices |
| diagnosing-bugs | product-development:diagnose-problem |
| domain-modeling | product-development:model-domain |
| git-worktree | product-development:implement-change isolation guidance using available native tools |
| grill-me | product-management:product-discovery |
| grill-with-docs | product-development:design-change |
| grilling | product-management:product-discovery |
| handoff | project-management:handoff-work |
| implement | product-development:implement-change |
| prototype | product-development:prototype-decision |
| research | product-development:understand-codebase; project-management:intake for broader research |
| tdd | product-development:test-behavior |
| teach | product-development:understand-codebase; communication:write-prose for teaching artifacts |
| to-spec | product-development:design-change; product-management:product-requirements |
| to-tickets | project-management:backlog-planning |
| triage | project-management:intake |
| wayfinder | product-development:understand-codebase |

The optional private Agent Development publisher separately replaces
`writing-great-skills` and `effective-agent-skills` with its owned
`agent-development:skill-surface-maintenance`. Public packages do not require it.

## Consumer migration

1. Inventory the current package revision and all consumer `.agents/skills`,
   client skill directories and lock entries. Check which bodies the active
   session actually discovers; a declared dependency alone is not usage evidence.
2. Build or acquire the reviewed owned package. Verify its complete skill bodies,
   references, attribution and exact source/version before activation.
3. Exercise representative local tasks using the qualified owned entry points.
   Preserve evidence of automatic selection separately from explicit invocation
   and useful outcomes. Resolve duplicate names/discovery before drawing usage
   conclusions.
4. Within an explicitly selected cleanup scope, remove only the superseded
   consumer copies and matching lock entries. Preserve unrelated skills and
   local adaptations. Publisher lock retirement does not perform this cleanup.
5. Record the resulting discovery state and any client reload still needed.

## Provenance and maintenance

Each adapting package ships `THIRD_PARTY_NOTICES.md`, license texts and
`skills/_shared/references/upstream-lineage.json`. These pin source material and
document adaptations; they do not cause network restoration. Legacy dependency
verification remains available for historical packages, with restoration opt-in.

Update a workflow because a real task exposes a gap. Prefer a deterministic
check, corrected interface, better tool or bounded reference when that fixes the
cause. Add a discoverable skill only for a distinct recurring task. Test positive
requests, near misses, outcomes and authority boundaries with independent
expected evidence. Proxy keyword scores and larger catalogs do not prove value.

The [author-only workflow trial corpus](../evals/owned-workflows/README.md) provides
five deterministic suites and four additional semantic cases, independent
assertions and explicit evaluation planning commands. Its offline tests qualify
the graders; model usefulness and native
discovery require separate observed trials.

Version 0.9.2 delivers the four public owned-workflow packages through GitHub
Packages only. Version 0.9.0 remains the original GitHub release artifact. Upgrades must
qualify native acquisition/discovery and update downstream source pins from the
exact reviewed release. Retain a rollback copy until the replacement is verified.
Local builds and tests do not activate installed packages or qualify provider behavior.
