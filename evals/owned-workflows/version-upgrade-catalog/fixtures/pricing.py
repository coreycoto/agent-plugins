"""Synthetic application caller; importing requires the unavailable dependency."""
from decimal import Decimal

from roundkit import quantize_money


def invoice_amount(amount):
    rounded = quantize_money(Decimal(amount))
    return {"amount": str(rounded), "currency": "USD"}
