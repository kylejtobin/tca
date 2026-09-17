---
type: Reference
description: How a frozen identityless product is constructed and compared by value. Read when a descriptive or measured meaning is exhausted by its field values.
---

# Value Object

## Use

Use for one descriptive or measured meaning with no identity, occurrence, lifecycle, or independent reference beyond its fields. Equality of all fields exhausts its meaning.

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

[Spread](semantic-scalar.md) is the nonnegative width. `Quote` owns the bid, spread, and derived ask; do not name the whole product for one of its fields.

- Every field is a semantic scalar, value object, union, or collection; a reference to an identified concept is its identity scalar, not the concept model.
- Store the independent parameters and derive every implied fact.
- Reparameterize a cross-field relation so invalid combinations have no representation.
- Represent meaningful absence or distinct alternatives by named union variants, never nullable fields.

## Do Not

- add an identity field
- store a derived field beside its source fields
- use a mutable constituent
- hold a client, resource, action interpreter, or current-state pointer
- replace the value object with an anonymous tuple or dictionary
