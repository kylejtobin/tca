# 0028. A key a party may omit is `T | None = None` on a Record

Status: accepted

## Context

Pydantic's JSON schema omits `exclusiveMinimum` when a scalar has no lower bound, `description` when a field has none. A `Record` of that document needs a value for a key that is not there. The page rule says an absence is a class.

## Rejected

One record class per combination of present keys: seven optional constraints give 128 classes. A union of records differing only by an absent key.

## Decision

On a page's `Fact`, an absence is a class. On a `Record` of another party's document, a key the party may omit is `T | None = None`, as Pydantic documents optional keys; where emptiness and absence coincide, a tuple defaults to `()` and a string to `""`.

## Evidence

`Primitive` in `type_construction.cli`: seven constraint fields `Decimal | None = Field(None, alias=...)` and `str | None = None`; `enum: tuple[str, ...] = ()`; `description: str = ""`. `Schema.model_validate(PlaceOrder.model_json_schema(), strict=False)` constructed every node with those defaults where keys were absent.

## Consequences

`None` appears on a `Record` and nowhere else. The smell check runs on pages, not on library kinds. Refuted by a party that sends an explicit `null` meaning something other than absence; that key is a union member, not `None`.
