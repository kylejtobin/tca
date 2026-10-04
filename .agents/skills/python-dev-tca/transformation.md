---
type: Construct
description: "A fact its owner's fields determine, read as one returned expression. Holds nothing of its own. Lives on its owner; where a foreign thing and a domain thing together determine it, in integration/<system>/<meaning>.py."
---

```python
# integration/payments/attempt.py
from pydantic import BaseModel, ConfigDict

from domain.shop.order import OrderOutcome, OrderOutcomeConstructor, PricedOrder
from integration.payments.model import ChargeReply


class ChargeAttempt(BaseModel):
    """A priced order's charge, with the payment provider's reply to it."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    order: PricedOrder
    payment: ChargeReply

    @property
    def outcome(self) -> OrderOutcome:
        return OrderOutcomeConstructor.validate_python(self, from_attributes=True)
```
