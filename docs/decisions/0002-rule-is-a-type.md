# 0002. A rule is a constrained Scalar, a relation kind, or a union member

Status: accepted

## Context

A business rule such as "quantity is positive", "a line over the threshold is discounted" or "the amount fits the tier" needs a place in the program, and the place must be one the checker reads and the proof can refuse.

## Rejected

`@model_validator(mode="after")` on a `Fact`, raising `ValueError` when the rule fails: it runs after an instance exists, applies to one class only, cannot be read from `model_fields`, and returns the same type it checked, so the knowledge that the check passed is not carried. A computed field on a fact returning the root of a `Scalar` over a union of two constrained scalars, so that Pydantic chooses the class: the comparison is an expression the developer writes, the checker types it and verifies nothing about it, and the proof cannot read what it compares.

## Decision

A rule on one value is a `Scalar` subclass with the constraint in `Field(...)`: `class Quantity(Scalar[int]): root: int = Field(gt=0)`. A rule that compares values is a relation kind, `Under`, `AtMost`, `Equal`, `AtLeast`, `Beyond`, `Differs` or `Between`, subclassed with the compared classes as its parameters (0048), and each outcome is the fact that holds the relation that makes it true: `class Low(AtMost[Amount, Limit])` held by `Cheap`, `class High(Beyond[Amount, Limit])` held by `Dear`, and `Cheap | Dear` where the outcome is held. The relation that holds constructs; the one that does not refuses, which the engine reads as the fact not existing, so the union is the choice (0003). No `model_validator` or `field_validator` appears on a page, and none on a relation kind beyond the one on `Relation` that drops a supplied ordering: the rule is the `Literal` of the orderings the kind admits. A `@computed_field` is a projection: it reads fields and constructs a declared class from what it read, and computes nothing (0042); a value computed from several is a derivation kind (0047).

## Evidence

`Duration(timedelta(0))` raises `ValidationError` with `greater_than`. In the engine's test program, `Low(AtMost[Amount, Limit])` with a limit of 10 valued an element at 2.50 as `Cheap` and an element at 25 as `Dear`. `Allowed(Between[Quantity, Quantity, Quantity])` with value 11 raised one error, `literal_error` at `("above",)`; `Same(Equal[Quantity, Quantity])` for 3 and 4 raised `literal_error` at `("ordering",)`, "Input should be 0".

## Consequences

Unwritable: a validator on a page; a comparison or an arithmetic expression in a computed field. The smell check reports `model_validator` and `field_validator` as `VALIDATOR`, and `sum(`, `min(`, `max(`, `len(` and an operator in a `return` as `COMPUTATION`. Refuted by a rule that cannot be expressed as a constraint on a root or as a relation between held values; that is a missing relation kind.
