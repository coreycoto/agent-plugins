UPDATE invoices SET amount_cents = CAST(amount_text AS INTEGER) * 100;
