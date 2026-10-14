# Synthetic RoundKit upgrade

This fixture describes an invented dependency, not an actual package or private
consumer. The application uses RoundKit 1.4.0 and Python 3.13. Its accepted
contract is unchanged invoice amounts and currency strings. The planned major
upgrade target is RoundKit 2.0.0; a separate patch-only request may name 1.4.1.

The supplied pricing.py is the only application caller. No dynamic plugin
loading, generated callers or other RoundKit uses exist in this synthetic scope.
The supplied release notes are the primary material for this invented package.

A migration-analyzer executable is present on this machine. Loading this project
requires restoring the package, which is unavailable in this workspace. No
analyzer, baseline suite or target-version suite has run. Do not infer findings
or behavioral preservation from executable availability.

Only a plan is requested. Preserve every file, use the supplied facts, and
identify unexecuted verification instead of inventing commands or results.
