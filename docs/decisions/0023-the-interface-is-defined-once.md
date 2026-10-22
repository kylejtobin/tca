# 0023. The interface is defined once

Status: accepted

## Context

A program must be runnable from a shell and over HTTP without the developer writing a parser, a handler, a help string or a schema.

## Rejected

A root `BaseSettings` built with `create_model` at startup holding one `CliSubCommand` per route; an engine-assembled model. `CliSettingsSource.root_parser` for the CLI's parser, typed `type[BaseSettings]` and validating in Python mode (0027). The request's JSON schema parsed into node classes as the CLI's source: a second representation of the request (0027). Starlette alone for HTTP, which would require writing body validation, 422 mapping and OpenAPI generation.

## Decision

`Route[Q, A]` with the docstrings on `Q` and `A` is the definition. The CLI kind takes the route from the first argument, renders its options from `Q` through the engine's reads (0027), validates the option tree with `Q.model_validate(tree, strict=False)` (0026), and prints `A.model_dump_json()`. The HTTP kind, the second item of `TODO.md`, registers one FastAPI path operation per route with `Q` as the body and `A` as `response_model`, which yields 422 with Pydantic's errors and the OpenAPI document from the same classes. Choosing CLI, HTTP or both changes no class, and the two edges describe every field with the same sentence because they read one declaration.

## Evidence

The CLI rendered `--name NAME        The thing's name. (min length 1)` and `--kind {one,two}   Which kind.` from the request class alone, and `PARTY__RETRIES  How many times the party is asked again. (>= 0)` from the config; see 0027. The HTTP kind is unbuilt, and its evidence is the run that builds it.

## Consequences

A hand-written parser, handler, help string or schema in a program is a defect. Refuted by a transport that cannot be derived from `Q` and `A`; that kind writes its own conversion to one of them.
