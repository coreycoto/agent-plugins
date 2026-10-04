# Contributor agent guidance

Use a current issue for substantive work. Respect the requested delivery stage
and preserve consumer authority. Installation, source preparation and merge do
not authorize provider operations, deployment, releases or data publication.

Portable plugin identity lives in root `plugin.json`. Skills use the fixed
`skills/` directory. Client metadata belongs under namespaced `extensions` and
client files under the matching directory. Preserve immutable upstream source
pins, documented compatibility adaptations and license attribution.

Run relevant checks and fix failures caused by a change. Keep deterministic
contract tests independent of provider accounts. Prefer native Git for source
commits and pushes; use the GitHub connector with the current head SHA for an
authorized interactive merge. No raw transcripts, credentials or operational
configuration belong in public source.
