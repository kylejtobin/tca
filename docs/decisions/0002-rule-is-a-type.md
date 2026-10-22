# 0002. A rule is a constrained Scalar, a relation kind, or a union member

Status: accepted

## Context

A business rule such as "quantity is positive", "a line over the threshold is discounted" or "the amount fits the tier" needs a place in the program, and the place must be one the checker reads and the proof can refuse.

## Rejected

`@model_validator(mode="after")` on a `Fact`, raising `ValueError` when the rule fails: it runs after an instance exists, applies to one class only, cannot be read from `model_fields`, and returns the same type it checked, so the knowledge that the check passed is not carried. A computed field on a fact returning the root of a `Scalar` over a union of two constrained scalars, `Priced(Scalar[LargeAmount | SmallAmount])`, so that Pydantic chooses the class: the comparison is an expression the developer writes, the checker types it and verifies nothing about it, and the proof cannot read what it compares.

## Decision

A rule on one value is a `Scalar` subclass with the constraint in `Field(...)`: `class Quantity(Scalar[int]): root: int = Field(gt=0)`. A rule that compares values is a relation kind, `AtMost`, `Beyond`, `Between` or `Equal`, subclassed with the compared classes as its parameters (0048), and each outcome is the fact that holds the relation that makes it true: `class Small(AtMost[LineTotal, Threshold])` held by `FullPrice`, `class Large(Beyond[LineTotal, Threshold])` held by `Discounted`, and `Discounted | FullPrice` where the outcome is held. The relation that holds constructs; the one that does not refuses with `relation`, which the engine reads as the fact not existing, so the union is the choice (0003). No `model_validator` or `field_validator` appears on a page; the one validator a relation needs is written once on the kind. A `@computed_field` is a projection: it reads fields and constructs a declared class from what it read, and computes nothing; a value computed from several is a derivation kind.

## Evidence

`Quantity(0)` raises `ValidationError` with `greater_than`. `Duration(timedelta(0))` raises `greater_than`. a line of fifty gold constructed `Large` and `Discounted`; a three-line order of tea, gold and jam held `FullPrice`, `Discounted`, `FullPrice`. `Allowed(value=Quantity(11), lower=Quantity(1), upper=Quantity(10))` raised one error of type `relation`, "Quantity is over Quantity"; `Same(value=Quantity(3), bound=Quantity(4))` raised `relation`.

## Consequences

Unwritable: a validator on a page; a comparison or an arithmetic expression in a computed field. The smell check reports `model_validator` and `field_validator` as `VALIDATOR`, and `sum(`, `min(`, `max(`, `len(` and an operator in a `return` as `COMPUTATION`. Refuted by a rule that cannot be expressed as a constraint on a root or as a relation between held values; that is a missing relation kind.
