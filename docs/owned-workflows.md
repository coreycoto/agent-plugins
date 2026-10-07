# Owned workflow selection and migration

The four public packages contain 33 self-contained skills. Choose a direct task
entry point; `product-development:engineering-workflow` is an optional router.
Product policy, verification commands, permissions and knowledge remain in the
consumer repository. A local task ends with a verified local result; publication
requires the corresponding delivery authority.

| Need | Owned entry point |
| --- | --- |
| Explain current code or its history | `product-development:understand-codebase` |
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

In Codex, invoke a qualified name with `$`, for example
`$product-development:diagnose-problem`. Other hosts may expose different syntax.
Installed files do not prove that an existing session has reloaded discovery.
Native agent setup remains an explicit `manage-codex-agents` operation in the
owning package. Roles are optional; skills work without delegation.

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

The local candidate retains existing package versions and is unreleased. Assign
release versions, qualify native acquisition/discovery and update downstream
source pins during authorized release preparation. Local builds and tests do not
activate installed packages or qualify real provider behavior.
