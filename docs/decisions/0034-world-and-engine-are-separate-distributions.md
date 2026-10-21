# 0034. `world` and `engine` are separate distributions under an empty namespace root

Status: accepted

## Context

`type-construction` ships `type_construction.world` and `type_construction.engine` together. A program that only models needs the world; only a deployment needs the engine.

## Decision

`type_construction` is a PEP 420 namespace package with no `__init__.py` in any distribution. `type-construction-world` ships `type_construction.world` and depends on pydantic and pydantic-settings. `type-construction-engine` ships `type_construction.engine` and depends on world. Server kinds depend on engine; client kinds on world. Programs are not placed in the namespace; they register through the entry-point group (0029).

## Evidence

`type-construction-world` ships `type_construction.world` and depends on pydantic and pydantic-settings; `type-construction-engine` ships `type_construction.engine` and depends on world and `opentelemetry-api`; cli depends on engine; http on world and engine; demo on world and http. The old `type-construction` distribution is gone. The workspace resolved, the dev image rebuilt, and basedpyright strict reported 0 errors across the five packages. No `__init__.py` exists at `type_construction`.

## Consequences

An import against the dependency direction is a package in the wrong row. Refuted by nothing.
