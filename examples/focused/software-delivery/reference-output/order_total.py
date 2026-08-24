from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    subtotal_cents: int
    discount_percent: int = 0
    free_shipping: bool = False


def total_cents(order: Order) -> int:
    discount = order.subtotal_cents * order.discount_percent // 100
    merchandise = order.subtotal_cents - discount
    shipping = 0 if order.free_shipping else 500
    return merchandise + shipping
