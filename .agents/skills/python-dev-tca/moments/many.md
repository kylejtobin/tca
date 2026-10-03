---
type: Moment
description: "What to write when there are several: a tuple held whole and folded in one expression, or one construction per arrival."
---

# Many

You are about to write:

```python
for bid in bids:
    total += bid.quantity
```

Declare the several that exist together as one thing holding a tuple, with each question about them as one expression:

```python
class Bid(BaseModel):
    """A resting offer to buy at a price and quantity."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    price: Price
    quantity: Quantity


class Bids(RootModel[tuple[Bid, ...]]):
    """The resting bids for one instrument, best first."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )

    @property
    def top(self) -> TopBid:
        return TopBidConstructor.validate_python(self, from_attributes=True)

    @property
    def depth(self) -> Depth:
        return Depth(sum((bid.quantity.root for bid in self.root), Decimal(0)))
```

`Bids.model_validate_json('[{"price": "101.5", "quantity": "3"}, {"price": "101.25", "quantity": "2"}]')` is `Bids` holding two `Bid`s, constructed by one call.

Declare the several that arrive one at a time as one construction each, each holding the one before:

```python
class Position(BaseModel):
    """One account's holding in one instrument, the fold of its fills."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    prior: "FlatPosition | Position"
    fill: Fill

    @property
    def account(self) -> AccountId:
        return self.prior.account

    @property
    def instrument(self) -> InstrumentId:
        return self.prior.instrument

    @property
    def net_quantity(self) -> NetQuantity:
        return NetQuantity(
            self.prior.net_quantity.root
            + {Side.BUY: 1, Side.SELL: -1}[self.fill.side] * self.fill.quantity.root
        )

    @property
    def persistence(self) -> "PersistPosition":
        return PersistPosition(position=self)
```

`Position.net_quantity` reads `self.prior.net_quantity`, which reads its own `prior`, down to `FlatPosition.net_quantity`.

The hard case, constructed:

`Bids.model_validate_json("[]")` is `Bids` holding no `Bid`. Its `top` is `NoBids` and its `depth` is `Depth(Decimal(0))`.

`Bids.model_validate_json('[{"price": "101.5", "quantity": "3"}, {"price": "101.25", "quantity": "2"}]').depth` is `Depth(Decimal("5"))`.

`Bids.model_validate_json('[{"price": "101.5", "quantity": "3"}, {"price": "0", "quantity": "2"}]')` raises `ValidationError`: one malformed bid and no `Bids` is constructed.

`PositionStateConstructor.validate_json('{"prior": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "fill": {"order_id": "O2", "account": "A1", "instrument": "ESZ6", "side": "sell", "price": "101.75", "quantity": "5"}}').net_quantity` is `NetQuantity(Decimal("-2"))`: the net of both fills.

In the file:

- Several that exist together are one class over `tuple[Bid, ...]`: `Bids`.
- Each question about the several is a `@property` of one `return`: `Bids.top`, `Bids.depth`.
- The fold is a generator inside the returned constructor: `Depth(sum((bid.quantity.root for bid in self.root), Decimal(0)))`.
- The fold has a starting value, `Decimal(0)`, so the empty `Bids` has a `depth`.
- Several that arrive one at a time are one `Position` each, and each holds the one before as `prior`.
- One `execute` makes one request and constructs one reply.
