# 0003. A choice is a union in a field annotation

Status: accepted

## Context

A field may hold one of several classes, chosen by what constructs.

## Rejected

`Ordered[T]`, a `RootModel` applying `union_mode="left_to_right"`, "tried in the order written; the last cannot refuse". Two defects: the definition fails on a TypeVar root, and its semantics are try-this-otherwise-that, a branch written as a kind. A generic type alias `type Ordered[T] = Annotated[T, Field(union_mode="left_to_right")]` was verified to work and was also rejected, because the order of attempts is not a thing in the business. The engine constructing every member and skipping the one that refuses: a `try` around a construction the run never needed to attempt. Leaving two members that can both construct to a test.

## Decision

A choice is `A | B` in a field annotation under Pydantic's default union mode. Each member says fully what it is: through a relation it holds (0048), a record one action heard, or a scalar whose constraint tells it from the other member's. In the run, a member whose own fields are never filled, or whose relation refuses, is never built, and the holder takes whichever member exists (0021); the holder's union is the choice, and nothing is skipped. At startup the proof decides, from the relations' constraints and the scalars' bounds, whether two members can both hold, and refuses them as `overlap` (0051).

## Evidence

`class Ordered[T](RootModel[T])` with `root: Annotated[T, Field(union_mode="left_to_right")]` raised `RuntimeError` at definition. `type Ordered[T] = Annotated[T, Field(union_mode="left_to_right")]` produced core schema `mode: left_to_right` and chose `Priced` for `{"amount": 5}` and `Unpriced` for `{"amount": 0}`. The same two members with no annotation, under smart mode, chose the same. Pydantic's documentation states smart-mode tie-breaking may change between minor releases. In the engine's test program, `Concluded.valued: tuple[Cheap | Dear, ...]` held, per element, the one of `Cheap` and `Dear` whose relation held: two elements at 2.50 gave two `Cheap`, one at 25 gave a `Dear`. `Either.which: AtOrUnder | Exactly`, told apart by `AtMost` and `Equal` over the same operands, was refused at startup as `overlap`.

## Consequences

Unwritable: `Ordered`, `union_mode` on a page. Members of a union on a page are disjoint by construction, and the proof refuses a pair that can both hold. Refuted by a business choice whose members cannot be told apart by what they hold; that is a missing class, not a reason for ordering.
