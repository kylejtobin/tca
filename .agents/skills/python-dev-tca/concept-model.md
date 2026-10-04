---
type: Construct
description: "A full domain thing or durable fact, including the one that holds the fact before it. Holds semantic scalars, value objects, and concept models. Lives in domain/<context>/<concept>.py."
---

```python
# domain/shop/order.py
from pydantic import BaseModel, ConfigDict, RootModel

from domain.shop.type import Amount, CardToken, Currency, CustomerId, OrderId
from domain.shop.value import Approval, Decline, Discount, Failure, Lines


class Order(BaseModel):
    """A customer's request to buy some lines in one currency, paid with one card."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    id: OrderId
    customer: CustomerId
    card: CardToken
    currency: Currency
    lines: Lines

    @property
    def pricing(self) -> "ReadDiscount":
        return ReadDiscount(order=self)


class PricedOrder(BaseModel):
    """An order with the discount the promotions system gave its customer."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    order: Order
    discount: Discount

    @property
    def id(self) -> OrderId:
        return self.order.id

    @property
    def card(self) -> CardToken:
        return self.order.card

    @property
    def currency(self) -> Currency:
        return self.order.currency

    @property
    def amount(self) -> Amount:
        return Amount(self.order.lines.amount.root * (100 - self.discount.percent.root) // 100)

    @property
    def charge(self) -> "Charge":
        return Charge(order=self)
```
