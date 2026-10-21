# 0003. A choice is a union in a field annotation

Status: accepted

## Context

A field may hold one of several classes, chosen by what constructs.

## Rejected

`Ordered[T]`, a `RootModel` applying `union_mode="left_to_right"`, "tried in the order written; the last cannot refuse". Two defects: the definition fails on a TypeVar root, and its semantics are try-this-otherwise-that, a branch written as a kind. A generic type alias `type Ordered[T] = Annotated[T, Field(union_mode="left_to_right")]` was verified to work and was also rejected, because the order of attempts is not a thing in the business. The engine constructing every member and skipping the one that refuses: a `try` around a construction the run never needed to attempt.

## Decision

A choice is `A | B` in a field annotation under Pydantic's default union mode. Each member says fully what it is through its constrained fields, so at most one constructs from a given input. In the run, a member whose own fields are never filled is never asked for, and the holder takes whichever member exists (0021, 0042); the holder's union is the choice, and nothing is skipped. Two members constructing from one input is a modeling fault; a test surfaces it.

## Evidence

`class Ordered[T](RootModel[T])` with `root: Annotated[T, Field(union_mode="left_to_right")]` raised `RuntimeError` at definition. `type Ordered[T] = Annotated[T, Field(union_mode="left_to_right")]` produced core schema `mode: left_to_right` and chose `Priced` for `{"amount": 5}` and `Unpriced` for `{"amount": 0}`. The same two members with no annotation, under smart mode, chose the same. Pydantic's documentation states smart-mode tie-breaking may change between minor releases. In the shop, a line of three teas built `FullPrice` and never asked for `Discounted`, whose `amount: LargeAmount` was never produced; `Charge` holding `Discounted | FullPrice` took the one that existed.

## Consequences

Unwritable: `Ordered`, `union_mode` on a page. Members of a union on a page are disjoint by construction. Refuted by a business choice whose members cannot be told apart by what they hold; that is a missing class, not a reason for ordering.
