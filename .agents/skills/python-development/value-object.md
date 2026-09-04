---
type: construct
---

# Value object

## Definition

A frozen `BaseModel` composing scalars into a small value with no identity, equal by value: a measurement, a description, an amount. The composition layer between the semantic scalar and the concept model.

## Required form

```python
class Spread(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    best_bid: Price
    width: SpreadWidth

    @cached_property
    def best_ask(self) -> Price:
        return Price(self.best_bid.root + self.width.root)
```

## Reparameterization

- A relation no single field constrains is part of the composite proof, never a guard after it.
- Reparameterize so the relation collapses into one constrained field plus a derivation.
- `Spread` holds `best_bid` and a non-negative `width` and derives `best_ask`: an inverted spread has no representation.
- A reparameterization that seems to distort the model means the related fields are their own concept, not yet factored.

## Sorting

- A small identity-less composition of scalars, equal by value → this construct.
- A single value → [semantic scalar](semantic-scalar.md).
- A full domain thing or fact, anything with domain identity or a kind pin → [concept model](concept-model.md).
- Program placement → lives in `domain/<context>/value.py`; see [topology](topology.md).

## Allowed

- `class X(BaseModel)` with `model_config = ConfigDict(frozen=True, extra="forbid")`, fields scalars or value objects
- a cross-field relation reparameterized into one constrained field plus a derivation
- derivations implying the value's facts

## Forbidden

- a bare primitive field
- a `T | None` field
- a kind pin or any identity field
- a client or handle as a field
- a validator asserting a relation between fields
- a stored field derivable from the others
- a tuple or dict of primitives carrying the parts without the proof or the name
- a dataclass pair carrying the shape without construction as proof
