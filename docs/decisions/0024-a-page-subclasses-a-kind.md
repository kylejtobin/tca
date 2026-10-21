# 0024. A page subclasses a kind, never one of its own classes

Status: accepted

## Context

Pydantic accepts an instance of a subclass where the parent class is annotated. `Holder(a=SubA(x=1))` constructs for a field typed `a: A` when `SubA(A)`. If a page subclassed its own fact, the subclass would be accepted wherever the parent is held, and the engine would have two classes for one field.

## Decision

Every class on a page subclasses a kind from `type_construction.world`, a library kind, or `StrEnum`. No class on a page subclasses another class of the page. Two facts that share fields are two facts.

## Evidence

`class Holder(Fact)` with `a: A`; `class SubA(A)`; `Holder(a=SubA(x=1))` constructed with `a` of class `SubA`.

## Consequences

Substitution never arises on a page. Refuted by nothing.
