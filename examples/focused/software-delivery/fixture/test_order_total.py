import unittest

from order_total import Order, total_cents


class OrderTotalTests(unittest.TestCase):
    def test_plain_order_includes_shipping(self):
        self.assertEqual(total_cents(Order(10_000)), 10_500)

    def test_discount_applies_once(self):
        self.assertEqual(total_cents(Order(10_000, discount_percent=10)), 9_500)

    def test_free_shipping_removes_shipping_charge(self):
        self.assertEqual(total_cents(Order(10_000, free_shipping=True)), 10_000)

    def test_discount_and_free_shipping_are_independent(self):
        self.assertEqual(
            total_cents(Order(10_000, discount_percent=10, free_shipping=True)),
            9_000,
        )


if __name__ == "__main__":
    unittest.main()
