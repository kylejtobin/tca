# 0031. Narrowing to a parametrized class is a TypeIs guard, never a cast

Status: accepted

## Context

`issubclass(c, Route)` narrows to `Route[Unknown, Unknown]` and basedpyright strict reports the result as partially unknown.

## Rejected

`cast`, `# type: ignore`, `Any`, `object` as the narrowed type.

## Decision

A function `def is_route(cls: type[object]) -> TypeIs[type[Route[Request, Reply[Fact]]]]` whose body is the `issubclass` test. The guard states the narrowed type; the checker applies it; the body stays one expression.

## Evidence

Three `reportUnknownVariableType` and `reportUnknownArgumentType` errors in `engine/__init__.py` with `issubclass` alone; zero with `is_route` and `is_reply`.

## Consequences

Every narrowing in the engine and the kinds is a named guard. Refuted by nothing.
