---
type: Construct
description: "Shape and configuration of a frozen typed sequence that has meaning of its own."
---

# Collection

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

A bound on the collection goes on `root`:

```python
    root: tuple[Bid, ...] = Field(max_length=10)
```

Several with no meaning of their own are a tuple field on their owner:

```python
    bids: tuple[Bid, ...]
```

Constructed:

`Bids.model_validate_json('[{"price": "101.5", "quantity": "3"}, {"price": "101.25", "quantity": "2"}]')` is `Bids` holding two `Bid`s in the order sent. Its `depth` is `Depth(Decimal("5"))`.

`Bids.model_validate_json("[]")` is `Bids` holding none. Its `depth` is `Depth(Decimal(0))`.

`Bids.model_validate_json('[{"price": "101.5", "quantity": "3"}, {"price": "0", "quantity": "2"}]')` raises `ValidationError`: no `Bids` is constructed.

In the file:

- The class is `RootModel[tuple[Bid, ...]]`.
- The member is a declared type: `Bid`.
- The several have a meaning of their own: `Bids` are best first.
- Order and duplicates are kept as sent.
- Where the source forbids duplicates, the route holds the array as sent, so a duplicate is still there to be seen.
- An association with arbitrary keys has no form on this substrate, and is reported as a construction gap.
- Placement: beside its members, in their file.
