---
type: Construct
description: "What this program publishes: its request or its reply. Holds semantic scalars, value objects, and concept models. Lives in domain/<context>/api.py."
---

```python
# domain/shop/api.py
from pydantic import BaseModel, ConfigDict, RootModel

from domain.shop.type import Amount, Currency, OrderId
from domain.shop.value import Approval, Decline, Discount, Failure


class PublishedOrder(BaseModel):
    """What this program publishes of a priced order."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    id: OrderId
    amount: Amount
    currency: Currency
    discount: Discount


class OrderConfirmed(BaseModel):
    """This program's reply that an order was paid."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    order: PublishedOrder
    payment: Approval


class OrderRejected(BaseModel):
    """This program's reply that an order's charge was declined."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    order: PublishedOrder
    payment: Decline


class OrderUnsettled(BaseModel):
    """This program's reply that an order's charge could not be attempted."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    order: PublishedOrder
    payment: Failure


class OrderReply(RootModel[OrderConfirmed | OrderRejected | OrderUnsettled]):
    """This program's reply to a checkout."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
```
