# Product Development

This independently selectable plugin provides the first-party `phased-refactor`
skill for evidence-led refactoring. Eighteen curated engineering skills are
optional native Vercel dependencies, declared in `skills-lock.json`. Their
source files are not bundled in this plugin. Initialize the selected dependencies
in the consumer project's `.agents/skills/`, where supported clients can discover
them directly. Our own plugin skill remains in the portable `skills/` directory.

`THIRD_PARTY_NOTICES.md` identifies upstream authors and retained license copies.

## Initialize upstream skills in a consumer project

The native `skills-lock.json` declares optional upstream skills using Vercel
Skills CLI 1.7.0's version-1 format: `source`, `sourceType`, immutable `ref`,
`skillPath` and `computedHash`. It contains only upstream dependencies, not our
first-party plugin skills. No custom ledger or client hook is required.

An agent should read this lock when asked to adopt or initialize these skills:

1. Use the **consumer project root** as the working directory. Installing the
   plugin does not install these project dependencies. Read the task's local
   guidance and review which locked skills are wanted.
2. Inspect the consumer's existing `skills-lock.json`. Preserve unrelated
   entries. If a selected name already has a different source/ref/hash, resolve
   that choice before replacing it.
3. Group the selected entries by `source` and `ref`. For each group, run the
   official CLI with exactly those names and the locked commit:

   ```sh
   npx --yes skills@1.7.0 add "<source>#<ref>" \
     --skill <selected-names-from-that-source> --agent codex --yes --copy
   ```

   Replace the placeholders from this package's lock; do not use a moving branch,
   `--global` or `--all`. The CLI writes native entries into the consumer lock
   while retaining unrelated entries and installs the selected skills into that
   consumer's `.agents/skills/`. No copy back into plugin `skills/` is needed.
4. Compare the resulting consumer entries and files with this package's original
   lock. Check source/ref/path and content hash, not only the command exit code:
   native restore can log a failure while exiting zero and recalculates hashes.
   In a publisher checkout, the read-only checker is:

   ```sh
   uv run --frozen python scripts/verify_skill_dependencies.py \
     --plugin-root <chosen-plugin-root> \
     --installed-root <consumer-project>/.agents/skills \
     --consumer-lock <consumer-project>/skills-lock.json
   ```

   This uses Node's native hash ordering and the original declared hash. It does
   not install anything. Stop on missing skills, pin drift or changed content.
5. Confirm discovery in the chosen client. For Codex, upstream skills have their
   ordinary names (for example `$code-review`), not a plugin-qualified name.
   Refresh the task's skill catalog when needed; installed files alone do not
   prove that an existing chat has loaded them. Repository policy and the
   current task's authority remain in force.

For a **new consumer project** whose own `skills-lock.json` already contains the
reviewed dependency entries, `npx --yes skills@1.7.0 experimental_install`
restores them into that project's `.agents/skills/`. The command reads only its
working directory's lock; running it in this plugin directory would restore to
the wrong project. It does not accept an alternate lock or destination path.

Maintainers update the declaration with the official CLI in an isolated project
at reviewed immutable refs, inspect the generated native lock and changed
skills, then commit only the reviewed `skills-lock.json` and notices here.
Do not commit the restored `.agents/skills/` tree into a plugin.

Format and behavior were checked against [Vercel Skills 1.7.0](https://github.com/vercel-labs/skills/tree/18f96ea131dab3b0fcc9b27cf7c6f6cbb6174680),
including its [native lock](https://github.com/vercel-labs/skills/blob/18f96ea131dab3b0fcc9b27cf7c6f6cbb6174680/src/local-lock.ts)
and [restore implementation](https://github.com/vercel-labs/skills/blob/18f96ea131dab3b0fcc9b27cf7c6f6cbb6174680/src/install.ts).
