# Third-party dependency notices

This plugin declares 18 optional upstream skill dependencies in native
`skills-lock.json`; it does not redistribute their skill directories. Entries
identify each original source, exact Git commit and content hash.

- [Matt Pocock's skills](https://github.com/mattpocock/skills), copyright Matt
  Pocock and contributors; MIT notice retained at `licenses/mattpocock-skills-MIT.txt`.
- [David Ondrej's skills](https://github.com/davidondrej/skills), copyright David
  Ondrej and contributors; MIT notice retained at `licenses/davidondrej-skills-MIT.txt`.

The copied notices identify the upstream works. Restoring dependencies uses the
original source files and frontmatter through the official Vercel Skills CLI;
this plugin does not maintain adapted upstream copies or a custom ledger.
The first-party `phased-refactor` skill and publisher metadata are original work.
Repository-specific guidance takes precedence over generic upstream guidance.
