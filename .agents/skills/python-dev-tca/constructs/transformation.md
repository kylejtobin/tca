---
type: Construct
description: "Shape of a derivation: a property of one returned expression on the model that holds its inputs, and the closed algebra it may use."
---

# Transformation

On the model that holds every input:

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

Where several things provide the inputs, a model that holds them:

```python
class PositionSubmission(BaseModel):
    """A position sent to the clearing house, with the house's reply to it."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    position: Position
    reply: ClearingReply

    @property
    def outcome(self) -> PositionOutcome:
        return PositionOutcomeConstructor.validate_python(self, from_attributes=True)
```

On a collection:

```python
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

The closed algebra: what a returned expression is built from:

| The expression | In the venue |
|---|---|
| a Pydantic constructor given fields | `PersistPosition(position=self)` |
| a declared field or derivation read | `self.prior.account` |
| arithmetic over those values | `self.prior.net_quantity.root + {Side.BUY: 1, Side.SELL: -1}[self.fill.side] * self.fill.quantity.root` |
| a fold over a declared collection | `sum((bid.quantity.root for bid in self.root), Decimal(0))` |
| an extremum along a declared ranked value space | `Price(max(bid.price.root for bid in self.root))` |
| selection by a proven key | `AliasPath("root", 0)` on `BestBid.bid` |
| an ordered union whose only refusal is the fallback | `TopBidConstructor.validate_python(self, from_attributes=True)` |
| a union given a held thing | `PositionOutcomeConstructor.validate_python(self, from_attributes=True)` |
| a total case table over one `StrEnum` or `Literal` | `{Side.BUY: 1, Side.SELL: -1}[self.fill.side]` |
| recursion through a declared recursive field | `self.prior.net_quantity` |

Constructed:

`PositionStateConstructor.validate_json('{"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}').net_quantity` is `NetQuantity(Decimal("3"))`.

`PositionStateConstructor.validate_json('{"prior": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "fill": {"order_id": "O2", "account": "A1", "instrument": "ESZ6", "side": "sell", "price": "101.75", "quantity": "5"}}').net_quantity` is `NetQuantity(Decimal("-2"))`.

`Bids.model_validate_json("[]").depth` is `Depth(Decimal(0))`.

`PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"error": "halted"}}').outcome` is a `RefusedPosition` whose `reason` is `RefusalReason.HALTED`.

In the file:

- Each derivation is a `@property` taking `self`, with a return annotation and a body of one `return`.
- The returned value is a constructed type: `NetQuantity`, `Depth`, `PersistPosition`, `TopBid`, `PositionOutcome`.
- The same fields give an equal output on every read.
- `@computed_field` appears on a contract model, for a fact derived from the contract's own fields.
- An operation outside the table is reported as a construction gap.
- Placement: on its owner. A model holding a foreign thing and a domain thing lives in `integration/clearing/<meaning>.py`: `submission.py`.
