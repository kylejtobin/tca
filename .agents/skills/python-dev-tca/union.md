---
type: Construct
description: "Closed alternatives on one axis, each a class holding its own facts. Holds its variants. Lives beside them."
---

```python
# domain/shop/discount.py
from pydantic import BaseModel, ConfigDict, TypeAdapter

from domain.shop.type import Percent


class LoyaltyDiscount(BaseModel):
    """The share of the total the promotions system takes off for a customer."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    percent: Percent


class NoDiscount(BaseModel):
    """The promotions system holds no discount for a customer."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )

    @property
    def percent(self) -> Percent:
        return Percent(0)


DiscountState = LoyaltyDiscount | NoDiscount
DiscountStateConstructor: TypeAdapter[DiscountState] = TypeAdapter(DiscountState)
```

```python
# domain/shop/order.py
class PaidOrder(BaseModel):
    """A priced order the payment provider charged."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    order: PricedOrder
    payment: Approval


class DeclinedOrder(BaseModel):
    """A priced order the payment provider declined to charge."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    order: PricedOrder
    payment: Decline


class UnsettledOrder(BaseModel):
    """A priced order the payment provider could not attempt to charge."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    order: PricedOrder
    payment: Failure


OrderOutcome = PaidOrder | DeclinedOrder | UnsettledOrder
OrderOutcomeConstructor: TypeAdapter[OrderOutcome] = TypeAdapter(OrderOutcome)
```
