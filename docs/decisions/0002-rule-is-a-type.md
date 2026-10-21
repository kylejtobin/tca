# 0002. A rule is a constrained Scalar or a union member

Status: accepted

## Context

A business rule such as "a discount applies over 100" or "quantity is positive" needs a place in the program.

## Rejected

`@model_validator(mode="after")` on a `Fact`, raising `ValueError` when the rule fails. The validator runs after an instance exists, applies to one class only, cannot be read from `model_fields`, and returns the same type it checked, so the knowledge that the check passed is not carried.

## Decision

A rule on one value is a `Scalar` subclass with the constraint in `Field(...)`: `class Quantity(Scalar[int]): root: int = Field(gt=0)`. A rule that decides between outcomes is two scalars with disjoint constraints, `LargeAmount` with `gt=100` and `SmallAmount` with `gt=0, le=100`, held by two facts, with a union where they are held. A derived value gets its constrained class through a computed field typed as the union of the scalars, returning the root of a `Scalar` over that union, `Priced(Scalar[LargeAmount | SmallAmount])`, so Pydantic chooses the class at construction. No `model_validator` or `field_validator` appears on a page.

## Evidence

`Quantity(0)` raises `ValidationError` with `greater_than`. `Duration(timedelta(0))` raises `greater_than`. `Priced(Decimal("150")).root` is a `LargeAmount`, `Priced(Decimal("50")).root` is a `SmallAmount`, `Priced(Decimal("0"))` raises `greater_than`. In the engine, `Placed.amount -> LargeAmount | SmallAmount` returning `Priced(total).root` made `FullPrice` construct for quantity 3 and `Discounted` for quantity 50 (0042).

## Consequences

Unwritable: a validator on a page. The smell check reports `model_validator` and `field_validator` as `PARSE-METHOD`. Refuted by a rule that cannot be expressed as a constraint on a root or as disjoint constraints across members; none has been found.
