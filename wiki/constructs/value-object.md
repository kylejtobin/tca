---
type: Construct
description: A frozen identityless product whose meaning is exhausted by field equality.
---

# Value Object

## Definition

One descriptive or measured meaning with no identity, occurrence, lifecycle, or independent reference beyond its fields. Equality of all fields exhausts its meaning.

## Required Form

```python
class Quote(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    bid: Price
    spread: Spread

    @property
    def ask(self) -> Price:
        return Price(self.bid.root + self.spread.root)
```

[Spread](./semantic-scalar.md) is the nonnegative width. `Quote` owns the bid, the spread, and the derived ask; a product is never named for one of its fields.

- Every field is a semantic scalar, value object, union, or collection; a reference to an identified concept is its identity scalar, not the concept model, because embedding the concept would make equality depend on its whole state and fuse identity with content.
- The independent parameters are stored and every implied fact is derived.
- A cross-field relation is reparameterized so invalid combinations have no representation.
- Meaningful absence or distinct alternatives are named union variants, never nullable fields.

## Forbidden

- an identity field
- a derived field stored beside its source fields
- a mutable constituent
- a client, resource, interpreter, or current-state pointer
- an anonymous tuple or dictionary in place of the value object
