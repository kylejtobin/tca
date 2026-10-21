# 0004. Several of one thing is a tuple

Status: accepted

## Context

A field holds many of one class.

## Rejected

`Many[T](RootModel[tuple[T, ...]])`. It added `.root` on every page that held several of something and carried no behavior a tuple lacks.

## Decision

`tuple[T, ...]` in the field annotation. A whole that knows something about its elements is a `Value` holding the tuple with a `@computed_field`.

## Evidence

No run applies; the decision removes a construct. Pydantic validates each element of `tuple[T, ...]` as `T`; basedpyright narrows the element type.

## Consequences

Unwritable: `Many`. The smell check reports `list` and `set` as `LIST` and `SET`. Refuted by a whole that must be a class with no field name; none has been found.
