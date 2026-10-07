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

    @property
    def currency(self) -> Currency:
        return self.order.currency

    @property
    def lines(self) -> Lines:
        return self.order.lines

    @property
    def related(self) -> FindRelated:
        return FindRelated(
            order=self, closeness=Closeness(), per_aisle=GroupSize(), limit=MatchLimit()
        )


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

```python
# domain/shop/order.py
class Recommended(BaseModel):
    """Products close enough to an order to recommend beside it."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    matches: RelatedMatches


class NothingRelated(BaseModel):
    """No product in the catalog close enough to an order to recommend."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    matches: NoMatches


class Unavailable(BaseModel):
    """A recommendation the catalog index could not give, and why."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    reason: IndexFault


class Recommendation(RootModel[Recommended | NothingRelated | Unavailable]):
    """What the catalog suggests beside an order."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
```
