---
type: Construct
description: Attempt-order construction, admitted only where the strong variant's sole failure means the declared fallback.
---

# Ordered Union

## Definition

`Annotated[A | B, Field(union_mode="left_to_right")]` over variants in attempt order. Attempt order absorbs every strong-variant refusal, including constraint failures; it does not distinguish absence from a failed proof. It is admitted exactly when every possible refusal over the declared input space means the declared fallback, and forbidden everywhere else, regardless of boundary or domain location.

`Bids` holds the resting bids on one instrument's bid side, best first. Its top is a best bid or no bids, which are facts of the book, not a lookup's "found" or "answer". The alias is `TopBid`, because top of book names both the best bid and the best ask.

## Required Form

```python
class Bid(BaseModel):
    """A resting bid."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    price: Price
    quantity: Quantity


class BestBid(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    bid: Bid = Field(validation_alias=AliasPath("root", 0))


class NoBids(BaseModel):
    """The book has no resting bids."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )


TopBid = Annotated[
    BestBid | NoBids,
    Field(union_mode="left_to_right"),
]
TopBidConstructor = TypeAdapter(TopBid)


class Bids(RootModel[tuple[Bid, ...]]):
    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )

    @property
    def top(self) -> TopBid:
        return TopBidConstructor.validate_python(self, from_attributes=True)
```

- Only proven `Bids` reaches `TopBidConstructor`. A present member is already a `Bid`; the sole missing path is index zero of an empty tuple.
- `BestBid.bid` stays at the already-proven type. A stronger bid constraint would introduce another refusal cause and invalidate this membership form.
- Every strong-variant refusal is enumerated, and the alias is admitted only when each means the fallback. Prerequisites construct first: malformed bids fail `Bids`, never become `NoBids`.
- The same obligation applies to each attempt in a longer ordered union.
- The `TypeAdapter` sits beside the alias and is named for it.
- Missing membership is a constructed alternative, not `None`, a flag, or a caught exception.

## Forbidden

- attempt order admitted on location, convenience, or intended precedence alone
- an ordered union where data carries a reliable discriminator
- coercion accidents defining precedence
- `ValidationError` caught to manufacture a default, partial value, or domain refusal
- a fallback that swallows an unrelated constraint failure, unknown source change, or any refusal outside its declared meaning
- `DetailedReply | SummaryReply` when the summary accepts a constraint-invalid detailed reply; failure of the detailed proof is not evidence of a summary
- a program-owned custom validator for parsing, selection, or any other purpose
