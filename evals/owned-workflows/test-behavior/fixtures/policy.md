# Checkout policy

`invoice_total(subtotal_cents, member)` returns subtotal plus shipping for valid
nonnegative integer subtotals and a boolean membership flag. Members pay no
shipping. Nonmembers pay 500 cents below 5000 cents and no shipping at or above
5000 cents. Subtotals are never doubled or reduced. Validation of invalid inputs
is outside this task.

The assigned task changes `test_checkout.py` only. Use standard-library unittest.
The production file and this policy are fixed evidence. Report a discovered
production defect instead of changing its behavior in this tests-only task.
