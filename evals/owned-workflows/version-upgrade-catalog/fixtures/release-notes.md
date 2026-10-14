# RoundKit synthetic release notes

## 1.4.0

quantize_money(value, *, rounding="half_even") rounds Decimal inputs to two
decimal places and returns a Decimal. Both "half_even" and "half_up" are valid
rounding arguments.

display_currency(value) is a separate formatting API.

## 1.4.1

Fixes an installation-metadata defect. Runtime APIs, defaults and supported
Python versions are unchanged from 1.4.0.

## 2.0.0

quantize_money keeps its signature and return type, but its default rounding
argument changes to "half_up". Passing rounding="half_even" remains supported.

display_currency is removed. Python 3.13 remains supported. No other API,
configuration, dependency or behavior changes apply to this synthetic scope.
