# 0040. Every behavior is named by the Pydantic call that performs it

Status: accepted

## Context

Prose about the system drifted into metaphor and claims no reader could check. Behaviors the system relied on were described without the call that produced them.

## Decision

A sentence in a record, a docstring or the skill that describes a behavior names the Pydantic feature or call that performs it: `model_validate_json`, `Field(exclude=True)`, `use_attribute_docstrings`, `model_json_schema`, the default union mode. A sentence that names none is removed. Records and scenarios contain classes, calls, values and error types, not adjectives.

## Evidence

Every record from 0002 onward names the call in its Decision or Evidence field; the world module's docstring names the call for each configuration key.

## Consequences

A claim with no call behind it is not written. Refuted by nothing.
