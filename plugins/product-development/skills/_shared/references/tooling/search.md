# Search and navigation

Choose the smallest search that can answer the question from an explicit
checkout. Prefer ripgrep for text and initial file discovery; use fd for richer
filename predicates when available. Return paths when selecting files, and
bounded line-numbered matches when inspecting contents.

```sh
rg --no-config --files -g '*.py' src tests
rg --no-config -n --color never -F -e 'parse_config' -- src tests
rg --no-config -l -F -e 'parse_config' -- src tests
rg --no-config --hidden -n --color never -e 'python-version' -- .github
```

`-F` treats the pattern literally; `-e` accepts a pattern starting with a dash;
`--` separates path operands. `--no-config` keeps personal ripgrep settings from
changing automated output. Hidden and ignored files are omitted by default.
`--hidden` includes hidden paths but still respects ignores; `--no-ignore`
changes that boundary too. Scope either expansion to the paths the task needs.

Ripgrep exits zero for matches, one for no match, and two for an error. A missing
path, permission failure or prematurely truncated pipeline does not prove
absence. `git grep` searches tracked files and is a useful fallback with that
coverage limit. Check upstream pipeline errors separately from an empty result.

Use fzf interactively only when a person is available. For unattended discovery,
supply a candidate list and filter without opening a terminal UI:

```sh
rg --no-config --files -0 src | FZF_DEFAULT_OPTS= FZF_DEFAULT_OPTS_FILE= \
  fzf --read0 --print0 --filter='parser' --no-sort
```

Clear inherited fzf options and preserve NUL record boundaries for arbitrary
filenames. A fuzzy result is a candidate, not a unique exact identity. Check the
candidate count and exact path before a write; never silently select the first
match. Pass paths as arguments rather than interpolating them into shell code.
Plain fzf, interactive zoxide queries and shell completion can block unattended
work. Navigation history is a hint; confirm the checkout before operating there.

Use a noninteractive, bounded file preview. If bat is available, disable paging
and select the relevant line range; otherwise use a plain-text reader. Do not
mistake a preview limit for complete search coverage or expose private matching
content in public output. A missing convenience tool need not trigger an install.

Sources: [ripgrep](https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md),
[fd](https://github.com/sharkdp/fd), [fzf](https://github.com/junegunn/fzf),
[bat](https://github.com/sharkdp/bat), [zoxide](https://github.com/ajeetdsouza/zoxide).
