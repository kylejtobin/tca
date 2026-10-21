# 0006. A record validates by alias only

Status: accepted

## Context

A `Record` carries a party's field names as aliases: `charge: ChargeId = Field(alias="id")`.

## Rejected

`validate_by_name=True` beside `validate_by_alias=True`, so that tests could construct `Charged(charge=...)`. It also let the wire send `{"charge": "c1"}`, two accepted spellings of one field.

## Decision

`validate_by_alias=True`, `validate_by_name=False`, `serialize_by_alias=True`. The wire constructs from the alias only. A test plays the party with the alias: `Charged(id=ChargeId("c1"))`. The per-call `model_validate(..., by_name=True)` exists for any code that must construct by name.

## Evidence

`Charged.model_validate_json('{"id":"c1"}')` constructs. `Charged.model_validate_json('{"charge":"c1"}')` raises `missing` at `("id",)`. `Charged(charge=ChargeId("c1"))` raises `missing` at `("id",)`. `Charged(id=ChargeId("c1"))` constructs. `Charged.model_validate({"charge": ChargeId("c1")}, by_name=True)` constructs. `model_dump_json()` emits `{"id":"c1"}`.

## Consequences

Unwritable: a payload under the domain's names. Refuted by a party that sends a field under two names; that is `AliasChoices` on that field.
