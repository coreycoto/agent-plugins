def invoice_total(subtotal_cents: int, member: bool) -> int:
    shipping_cents = 0 if member or subtotal_cents > 5000 else 500
    return subtotal_cents + shipping_cents
