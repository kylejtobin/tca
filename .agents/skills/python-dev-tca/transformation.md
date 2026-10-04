---
type: Construct
description: "A fact its owner's fields determine, read as one returned expression. Holds nothing of its own. Lives on its owner; where a foreign thing and a domain thing together determine it, in integration/<system>/<meaning>.py."
---

```python
# integration/promotions/reading.py
from pydantic import BaseModel, ConfigDict

from domain.shop.order import Order, PricedOrder
from integration.promotions.model import DiscountOffer


class DiscountReading(BaseModel):
    """An order, with the promotions system's offer for its customer."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    order: Order
    discount: DiscountOffer

    @property
    def priced(self) -> PricedOrder:
        return PricedOrder.model_validate(self, from_attributes=True)
```

```python
# integration/payments/attempt.py
from pydantic import BaseModel, ConfigDict

from domain.shop.order import OrderOutcome, PricedOrder
from integration.payments.model import ChargeApproved, ChargeDeclined, ChargeFailed, ChargeReply


class ChargeAttempt(BaseModel):
    """A priced order's charge, with the payment provider's reply to it."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    order: PricedOrder
    reply: ChargeReply

    @property
    def payment(self) -> ChargeApproved | ChargeDeclined | ChargeFailed:
        return self.reply.root

    @property
    def outcome(self) -> OrderOutcome:
        return OrderOutcome.model_validate(self, from_attributes=True)
```
