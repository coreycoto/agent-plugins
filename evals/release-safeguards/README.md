# Offline release safeguards experiment

This is an author investigation, not a plugin runtime, callable installer,
release client or registered hook. No provider code or credentials are used.
Tests call only pure decisions, fake writes, temporary filesystem models and
native `codex execpolicy check` against explicit files. They never execute the
release commands supplied to the policy checker.

Run the ordinary author suite, or select a pre-existing native binary explicitly:

```sh
CODEX_TEST_BINARY=/absolute/path/to/existing/codex .venv/bin/python -m pytest tests/test_release_safeguards.py
```

Do not use a package-manager shim that could install or auto-update software.
Without an explicit binary the native policy tests skip. Guard and installer
tests remain offline and run on CI. The two-read race test intentionally shows
an unsafe write after concurrent publication; it does not assert a solved race.
Public-note fixtures are editorial examples reviewed against a rubric, not an
automated language-quality grader or an agent effectiveness experiment.

The installer model tests a proposed flat-file ownership lifecycle in temporary
homes only. It omits production locking, staged publication and interruption
recovery; do not connect it to onboarding. Native forms, hook envelopes/trust,
actual client loading, connector coverage and atomic provider writes all need
separate qualification before any enforcement claim. See the
[assessment](../../docs/release-safeguards.md).
