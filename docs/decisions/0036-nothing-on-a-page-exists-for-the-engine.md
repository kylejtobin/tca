# 0036. Nothing on a page exists for the engine

Status: accepted

## Context

The first engine's pages carried computed ids, `before` counts, `pause` and `accepted` fields, bodiless classes, `.text` endings and tags the party never sent, each so the engine had something to bind. The second design's pages carried `Unreachable` so the engine had a type to construct when a client raised.

## Decision

Every class and field on a page is a thing the business has. The test of a line is whether a reader who knows the business and not the engine would write it. A line that exists so the engine can find, bind, mark or tag something is a defect in the engine, and the engine changes.

## Evidence

Each construct in Context was removed with no loss to the program; the engine's design changed each time (0010, 0011, 0012, 0021).

## Consequences

The engine reads `model_fields`, generic arguments and docstrings, never a field the developer wrote for it. Refuted by nothing.
