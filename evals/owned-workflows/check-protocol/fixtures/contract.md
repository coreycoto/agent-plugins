# Dispatch protocol candidate

One logical operation must be accepted by the receiver at most once. A local
timeout does not undo receiver acceptance. The synthetic receiver has no
deduplication. The fixture models one operation and caps acceptances at two.
`repair=True` removes expiry-based redispatch; it is a comparison model, not a
reviewed production fix. Waiting indefinitely is permitted. No fairness or
external delivery guarantee has been accepted.

Check safety with an executable finite explorer. Report an actual bad trace,
a corrected-control result, a path that reaches done, and limits. Do not infer
universal eventual completion from a finite path. Keep source files unchanged;
create only analysis.py and evidence.json. Run `python -B analysis.py`.
The evidence object must include `unsafe_trace`, `control_has_violation` (bool),
`completion_trace`, `progress_checked` (bool), and nonempty `assumptions` and
`implementation_limits` strings. Additional evidence fields are allowed.
The final response should explain findings and actual exploration scope.

Print the same evidence JSON to stdout from the task entrypoint. The evaluation
runner records command completion separately from the files you write.
