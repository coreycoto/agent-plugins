import unittest

from checkout import invoice_total


class CheckoutTests(unittest.TestCase):
    def test_invoice(self):
        result = invoice_total(2000, False)
        self.assertEqual(invoice_total(2000, False), result)
