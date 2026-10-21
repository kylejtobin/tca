# 0023. The interface is defined once

Status: accepted

## Context

A program must be runnable from a shell and over HTTP without the developer writing a parser, a handler, a help string or a schema.

## Rejected

A root `BaseSettings` built with `create_model` at startup holding one `CliSubCommand` per route; an engine-assembled model. `CliSettingsSource.root_parser` for the CLI's parser, typed `type[BaseSettings]` and validating in Python mode (0027). Starlette alone for HTTP, which would require writing body validation, 422 mapping and OpenAPI generation.

## Decision

`Route[Q, A]` with the docstrings on `Q` and `A` is the definition. The CLI kind takes the route from the first argument, renders its options from `Q.model_json_schema()` parsed into node classes (0027), validates the option tree with `Q.model_validate(tree, strict=False)` (0026), and prints `A.model_dump_json()`. The HTTP kind registers one FastAPI path operation per route with `Q` as the body and `A` as `response_model`, which yields 422 with Pydantic's errors and the OpenAPI document from the same schema. Choosing CLI, HTTP or both changes no class, and the two edges describe every field with the same sentence because they read one document.

## Evidence

The CLI rendered `--sku SKU  The product ordered. (min length 1)` and `--currency {USD,EUR}` from the request's schema alone; see 0027. FastAPI's derivation is documented behavior, not yet run in this repository.

## Consequences

A hand-written parser, handler, help string or schema in a program is a defect. Refuted by a transport that cannot be derived from `Q` and `A`; that kind writes its own conversion to one of them.
