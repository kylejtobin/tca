# 0008. A nested value in a payload is an AliasPath

Status: accepted

## Context

A party nests the values the program reads: `{"data": {"id": "c1", "amount": {"value": "2.50"}}}`.

## Rejected

A `Value` class per level of nesting, written only to reach the inner field.

## Decision

`Field(validation_alias=AliasPath("data", "amount", "value"))` on the record's field.

## Evidence

`class Charged2(Record)` with `charge: ChargeId = Field(validation_alias=AliasPath("data", "id"))` and `amount: Amount = Field(validation_alias=AliasPath("data", "amount", "value"))`. `model_validate_json('{"data":{"id":"c1","amount":{"value":"2.50"}}}')` constructs `charge=ChargeId("c1")`, `amount=Amount(Decimal("2.50"))`.

## Consequences

A `Value` that holds only what a path could read is a defect. Refuted by a nested object the business itself holds as a thing; that is a `Value`.
