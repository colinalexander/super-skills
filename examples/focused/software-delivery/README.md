# Software delivery: seeded order-total defect

This runnable fixture contains a defect: a percentage discount is applied twice when an order also has free shipping.

- **Trigger:** the task is to reproduce, repair, test, and prove a code change without broad cleanup.
- **Non-trigger:** redesigning pricing or checkout architecture belongs to other skills.
- **Fixture:** [`fixture/order_total.py`](fixture/order_total.py) and [`fixture/test_order_total.py`](fixture/test_order_total.py).
- **Reference artifact:** [`reference-output/order_total.py`](reference-output/order_total.py) is one bounded repair.
- **Verification:** run `python3 -m unittest discover -s fixture -p 'test_*.py'` before and after applying a repair.

The initial fixture intentionally contains one failing test. Modify only this example directory.
