---
type: Reference
description: How attempt order constructs alternatives when the strong variant can fail only for the declared fallback. Read when proving membership or admitting another failure-exhaustive choice.
---

# Ordered Union

## Use

Attempt order absorbs every strong-variant refusal, including constraint failures; it does not distinguish absence from a failed proof. Admit it exactly when every possible refusal over the declared input space means the declared fallback. Forbid it everywhere else, regardless of boundary or domain location.

`Bids` holds the resting bids on one instrument's bid side, best first. Its top is a best bid or no bids, not a lookup's "found" or "answer". A bare price sequence has no such venue meaning.

Name this bid-side alternative `TopBid`; top of book includes both the best bid and the best ask.

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

- Pass only proven `Bids` to `TopBidConstructor`. A present member is already a `Bid`; the sole missing path is index zero of an empty tuple.
- Keep `BestBid.bid` at the already-proven type. A stronger bid constraint would introduce another refusal cause and invalidate this membership form.
- Enumerate every strong-variant refusal. Admit the alias only when each means the fallback.
- Construct prerequisites first; malformed bids must fail `Bids`, never become `NoBids`.
- Apply the same obligation to each attempt in a longer ordered union.
- Give every variant a frozen Pydantic shape.
- Keep the `TypeAdapter` beside the alias and name it for that alias.
- Keep missing membership as a constructed alternative, not `None`, a flag, or a caught exception.

## Do Not

- admit attempt order based on location, convenience, or intended precedence alone
- use an ordered union when data carries a reliable discriminator
- use coercion accidents to define precedence
- catch `ValidationError` to manufacture a default, partial value, or domain refusal
- let a fallback swallow an unrelated constraint failure, unknown source change, or any refusal outside its declared meaning
- admit `DetailedReply | SummaryReply` when the summary accepts a constraint-invalid detailed reply: failure of the detailed proof is not evidence of a summary
- introduce a program-owned custom validator for parsing, selection, or any other purpose
