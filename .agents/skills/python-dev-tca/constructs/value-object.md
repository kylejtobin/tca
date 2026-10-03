---
type: Construct
description: "Shape and configuration of a frozen product with no identity, equal when its fields are equal."
---

# Value object

```python
class Bid(BaseModel):
    """A resting offer to buy at a price and quantity."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    price: Price
    quantity: Quantity
```

Two fields that must agree are stored as the independent one and the difference, and the other is derived:

```python
class Spread(RootModel[Decimal]):
    """The width between a quote's bid and its ask, zero or more."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: Decimal = Field(ge=0)


class Quote(BaseModel):
    """A bid price and the spread above it at which an instrument is quoted."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    bid: Price
    spread: Spread

    @property
    def ask(self) -> Price:
        return Price(self.bid.root + self.spread.root)
```

Constructed:

`Bid(price=Price(Decimal("101.5")), quantity=Quantity(Decimal("3")))` is a `Bid`.

`Bid.model_validate_json('{"price": "101.5", "quantity": "3"}')` is an equal `Bid`: two bids with equal fields are the same bid.

`Bid.model_validate_json('{"price": "101.5"}')` raises `ValidationError`: a `Bid` holds both.

`Quote.model_validate_json('{"bid": "101.5", "spread": "0.25"}').ask` is `Price(Decimal("101.75"))`.

`Quote.model_validate_json('{"bid": "101.5", "spread": "-0.25"}')` raises `ValidationError`: a quote whose ask is below its bid has no representation.

In the file:

- Every field is a semantic scalar, a value object, a union alias, or a tuple of those: `price: Price`, `quantity: Quantity`.
- Its fields are its whole meaning: `Bid` is equal to any `Bid` with the same `price` and `quantity`.
- An identified thing is referred to by its identity scalar: `InstrumentId`.
- What the fields determine is a `@property` on the value object: `Quote.ask`.
- The stored fields are the independent ones, so every pair that constructs is a valid pair: `bid` and `spread`.
- Placement: `domain/venue/value.py`.
