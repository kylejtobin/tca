---
type: Construct
description: "One transport crossing, in or out. Holds domain things, foreign models, and contract models. Lives in api/<context>.py."
---

```python
# api/shop.py
from pydantic import BaseModel, ConfigDict

from domain.shop.api import OrderReply
from domain.shop.order import Order


class CheckoutRoute(BaseModel):
    """The crossing where a customer's checkout arrives."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    order: Order


class ReplyRoute(BaseModel):
    """The crossing where this program's reply to a checkout leaves."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    outcome: OrderReply
```
