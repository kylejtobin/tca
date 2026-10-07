---
type: Construct
description: "A sum: closed alternatives on one axis, each a class holding its own facts. Holds its variants. Lives beside them."
---

```python
# domain/shop/order.py
class PaidOrder(BaseModel):
    """A priced order the payment provider charged."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    order: PricedOrder
    payment: Approval


class DeclinedOrder(BaseModel):
    """A priced order the payment provider declined to charge."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    order: PricedOrder
    payment: Decline

    @property
    def customer(self) -> CustomerId:
        return self.order.order.customer

    @property
    def id(self) -> OrderId:
        return self.order.id

    @property
    def reasons(self) -> DeclineReasons:
        return self.payment.reasons

    @property
    def notice(self) -> "WriteNotice":
        return WriteNotice(order=self)


class UnsettledOrder(BaseModel):
    """A priced order the payment provider could not attempt to charge."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    order: PricedOrder
    payment: Failure


class OrderOutcome(RootModel[PaidOrder | DeclinedOrder | UnsettledOrder]):
    """What became of a priced order at the payment provider."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def order(self) -> PricedOrder:
        return self.root.order

    @property
    def payment(self) -> Approval | Decline | Failure:
        return self.root.payment
```
