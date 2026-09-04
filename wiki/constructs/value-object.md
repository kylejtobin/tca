---
type: Construct
description: A frozen BaseModel composing scalars into a small value with no identity.
---

# value object

## Definition

A frozen `BaseModel` composing scalars into a small value with no identity, equal by value: a measurement, a description, an amount. The composition layer between the semantic scalar and the concept model.

## Required Form

```python
class Spread(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    best_bid: Price
    width: SpreadWidth

    @cached_property
    def best_ask(self) -> Price:
        return Price(self.best_bid.root + self.width.root)
```

## Sorting Rules

A single value is a semantic scalar. A full domain thing or fact, anything with domain identity or a kind pin, is a concept model. A value object never holds a client, never pins a kind, and two value objects with equal fields are the same value.

## Replaced Forms

A tuple or dict of primitives carries the parts without the proof or the name. A dataclass pair carries the shape without construction as proof. A validator asserting a relation between fields is a check performed inside construction; the relation is reparameterized instead.

## Reparameterization

A relation no single field constrains is part of the composite proof, never a guard after it: reparameterize so the relation collapses into a single-field constraint and a derivation. `Spread` holds `best_bid` and a non-negative `width` and derives `best_ask`, so an inverted spread has no representation. A reparameterization that seems to distort the model is the signal that the related fields are their own concept, not yet factored.

## Allowed Patterns

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
