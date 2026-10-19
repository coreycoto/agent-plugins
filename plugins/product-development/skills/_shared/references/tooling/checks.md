# Repository checks

Use the consumer's existing check commands, configuration and installed tools.
Distinguish a finding, an execution failure and unavailable coverage. A clean
result only qualifies the boundary actually inspected.

## Secret scanning

Choose Gitleaks's scan boundary explicitly. For repositories with the shown
configuration, typical commands are:

```sh
gitleaks dir --redact --no-banner --config .gitleaks.toml .
gitleaks git --pre-commit --staged --redact --no-banner --config .gitleaks.toml .
gitleaks git --log-opts=--all --redact --no-banner --config .gitleaks.toml .
```

Omit `--config` when that file does not exist. A directory scan covers present
files, a staged scan covers the proposed commit, and a Git scan covers selected
locally available history. `--all` cannot scan unfetched refs in a shallow clone.
Keep redaction enabled. Report rule and location without copying credentials
into another artifact. Removing current text does not revoke a secret or erase
past copies; rotation and history repair need their corresponding scope.

Inspect diagnostics even when interpreting an exit code. Incomplete scans and
scanner/Git errors are not clean results. Repair the environment without
bypassing an existing hook. Use narrow reviewed exceptions for verified false
positives. Scanner success cannot establish that a value never left the host.

## Shell scripts

Use the shebang and repository settings to select ShellCheck's supported dialect.
Read `.shellcheckrc` and local directives before changing exclusions. Forcing
Bash on Zsh does not validate Zsh; ShellCheck does not support that dialect.
Use `zsh -n` separately for each Zsh file when available. Additional operands
can be script arguments rather than independently parsed files.

Fix quoting, splitting and portability at source. Keep intentional suppressions
narrow and explained. Syntax/static checks do not exercise PATH precedence,
repeated sourcing or hook behavior; use the consumer's isolated shell checks for
those contracts. Sourcing an unfamiliar file can execute side effects.

## Git LFS

Inspect the exact checkout and tracking before treating a pointer as corruption:

```sh
git lfs version
git lfs ls-files
git lfs status
git check-attr filter -- path/to/asset
```

Git history stores pointers; LFS content is separate. Smudging may be disabled,
authentication may fail, or a remote object may be missing. Local history does
not prove remote object availability. When retrieval is within the task, verify
the ref and local changes, then fetch only the required content:

```sh
git lfs pull --include='path/to/asset' --exclude=''
```

Pull downloads objects and updates working files. Verify the actual content
afterward. Tracking changes attributes and does not convert old commits;
`git lfs migrate` can rewrite history. Keep either distinct from ordinary object
retrieval rather than replacing a missing pointer target with invented content.

Sources: [Gitleaks](https://github.com/gitleaks/gitleaks),
[ShellCheck dialects](https://www.shellcheck.net/wiki/SC1071),
[Git LFS](https://git-lfs.com/),
[LFS pull](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-pull.adoc).
