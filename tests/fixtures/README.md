`codex-session-start-output.schema.json` is the generated upstream Codex hook
contract, copied from revision
`c0c230e6730b3b3c9101b8aff4b9aea4027cea5b`:

https://github.com/openai/codex/blob/c0c230e6730b3b3c9101b8aff4b9aea4027cea5b/codex-rs/hooks/schema/generated/session-start.command.output.schema.json

The source repository uses Apache-2.0. This independent fixture rejects extra
status fields in the MCP hook response; a detailed status tool response is a
separate contract. Update this fixture only after reviewing an upstream hook
contract change.

The released `rust-v0.160.0` schema has the same contract as this fixture.
