---
name: tca_authorized_construct_value_object
description: Build a value object, the only legal shape for a small identity-less composition of scalars. MUST be invoked before composing scalars into a measurement, description, amount, span, or pair. Replaces the forbidden forms; if a tuple of primitives, a dataclass pair, a two-field dict, or a validator asserting a relation between fields is about to appear, stop and build the value object instead.
---
# Value Object

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

## Construct-Specific Doctrine

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

## Halt Rule

Halt when the value needs identity, a kind, or a field that is itself a full domain concept, or when a relation resists reparameterization. Report the row and the field or relation: the meaning is a concept model or an unfactored concept, and the table is not finished.
