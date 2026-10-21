# 0007. A party's naming convention is an alias generator

Status: accepted

## Context

A party that names every field in camelCase would need `Field(alias=...)` on every field of every record.

## Decision

One `Record` subclass per party with `model_config = ConfigDict(alias_generator=to_camel)`. Records of that party subclass it and declare fields in the domain's names with no alias.

## Evidence

`class Camel(Record): model_config = ConfigDict(alias_generator=to_camel)`; `class Refund(Camel)` with `refund_id` and `refund_amount`. `Refund.model_validate_json('{"refundId":"r1","refundAmount":"1.00"}')` constructs. `Refund.model_config["strict"]` is `True` and `["extra"]` is `"forbid"` after the merge. A payload with an extra key `x` raises `extra_forbidden` at `("x",)`.

## Consequences

A per-field alias on a record of a party that has a generator is a defect. Refuted by a party whose names follow no convention; those records use `Field(alias=...)`.
