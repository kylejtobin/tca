---
type: Construct
description: "Shape of attempt-order construction, admitted only where the strong variant's sole failure means the fallback."
---

# Ordered union

```python
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

Every way `BestBid` can fail to construct from `Bids`, and what each means:

| `BestBid` fails because | It means |
|---|---|
| `root[0]` does not exist | `NoBids` |

The table has one row: every member of `Bids` is already a `Bid`, and `BestBid.bid` is typed `Bid`.

Constructed:

`Bids.model_validate_json('[{"price": "101.5", "quantity": "3"}]').top` is a `BestBid` whose `bid` is that `Bid`.

`Bids.model_validate_json("[]").top` is `NoBids`.

`Bids.model_validate_json('[{"price": "-1", "quantity": "3"}]')` raises `ValidationError` before `top` is asked: a malformed bid constructs no `Bids`.

In the file:

- The alias is `Annotated[BestBid | NoBids, Field(union_mode="left_to_right")]`, strong variant first.
- The table above has one row for each way `BestBid` fails, and every row's meaning is `NoBids`.
- A longer ordered union has such a table for each attempt.
- Where the data carries a discriminator, the alias is a plain union.
- The `TypeAdapter` is named for the alias and sits beside it.
- Placement: beside its variants, in their file.
