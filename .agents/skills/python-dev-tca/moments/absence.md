---
type: Moment
description: "What to write when there may be none: a named constructed thing for the absence, never None, a flag, or a pending state."
---

# Absence

You are about to write:

```python
position: Position | None = client.load(account, instrument)
best = bids[0] if bids else None
```

Declare the thing that exists when there is none, as a variant of the union the field is typed as:

```python
class FlatPosition(BaseModel):
    """The holding of an account with no fills in an instrument."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    account: AccountId
    instrument: InstrumentId

    @property
    def net_quantity(self) -> NetQuantity:
        return NetQuantity(Decimal(0))


PositionState = FlatPosition | Position
PositionStateConstructor: TypeAdapter[PositionState] = TypeAdapter(PositionState)
```

```python
class Bid(BaseModel):
    """A resting offer to buy at a price and quantity."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    price: Price
    quantity: Quantity


class BestBid(BaseModel):
    """The first of the bids."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    bid: Bid = Field(validation_alias=AliasPath("root", 0))


class NoBids(BaseModel):
    """The book has no resting bids."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )


TopBid = Annotated[
    BestBid | NoBids,
    Field(union_mode="left_to_right"),
]
TopBidConstructor: TypeAdapter[TopBid] = TypeAdapter(TopBid)


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

Add the rows:

| name | is | holds | kind |
|---|---|---|---|
| FlatPosition | The holding of an account with no fills in an instrument. | AccountId, InstrumentId | concept model |
| NoBids | The book has no resting bids. | nothing | concept model |
| BestBid | The first of the bids. | Bid | concept model |
| TopBid | The top of the bids. | BestBid, NoBids | ordered union |

The hard case, constructed:

`PositionStateConstructor.validate_json('{"account": "A1", "instrument": "ESZ6"}')` is a `FlatPosition`: the clearing house's answer for an account with no fills. Its `net_quantity` is `NetQuantity(Decimal(0))`.

`Bids.model_validate_json("[]").top` is `NoBids`, and `Bids.model_validate_json("[]").depth` is `Depth(Decimal(0))`.

`Bids.model_validate_json('[{"price": "101.5", "quantity": "3"}]').top` is a `BestBid` whose `bid` is that `Bid`.

`PositionStateConstructor.validate_json("{}")` raises `ValidationError`: an answer that is neither variant constructs nothing, and it is not a `FlatPosition`.

`Bids.model_validate_json('[{"price": "-1", "quantity": "3"}]')` raises `ValidationError`: a malformed bid constructs no `Bids`, so `top` is never asked.

In the file:

- The empty case is a class with a docstring: `FlatPosition`, `NoBids`.
- The field that may hold the empty case is typed as the union: `Position.prior` is `"FlatPosition | Position"`, and `Bids.top` returns `TopBid`.
- The empty variant has every derivation its sibling has: `FlatPosition.net_quantity` beside `Position.net_quantity`.
- `FlatPosition` holds what is still known: `account` and `instrument`.
- Each union has one variant with no fields at most: `NoBids`.
- `TopBidConstructor` is given `self`, a constructed `Bids`, and `BestBid.bid` is typed `Bid`, the type `Bids` holds.
