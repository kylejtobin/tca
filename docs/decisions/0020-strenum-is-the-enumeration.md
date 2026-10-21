# 0020. StrEnum is the enumeration

Status: accepted

## Context

A closed word list needs a type.

## Rejected

`class Vocabulary(StrEnum)` with no members and no behavior, so that every enumeration subclassed a kind of the world.

## Decision

A page subclasses `StrEnum` directly. The smell check lists `StrEnum` among the bases a program class may have.

## Evidence

No run applies; the decision removes a construct. `class Currency(StrEnum)` and `class Currency(Vocabulary)` are the same line for the developer; strict Pydantic refuses any string outside the members in both.

## Consequences

Ten classes in `type_construction.world` plus `StrEnum`. Refuted by an enumeration behavior Pydantic does not give `StrEnum`; none has been found.
