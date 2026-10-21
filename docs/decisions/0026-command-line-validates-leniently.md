# 0026. The command line validates with model_validate(tree, strict=False)

Status: accepted

## Context

argv is text. A request may hold a `Value`, a `tuple`, a `StrEnum`, a `Decimal`. The class is strict.

## Rejected

`model_validate_strings`: refused a list with `string_type` at `()`, so no `tuple` field can arrive from argv through it. `CliApp.run`: validates in Python mode against the strict class and refused.

## Decision

The CLI builds a nested dict of text from the parsed options and calls `Q.model_validate(tree, strict=False)`. The lenient mode is chosen per call at the edge; the class stays strict in code.

## Evidence

From `{"quantity": "3", "amount": "2.50", "currency": "USD", "ship_to": {"city": "Boston"}, "skus": ["tea", "milk"], "lines": [{"sku": "tea", "quantity": 3}]}`: the lenient call constructed every field; the strict call refused five locations (`int_type`, `is_instance_of` twice, `tuple_type` twice); the lenient call with `"quantity": "0"` refused `greater_than` at `("quantity",)`; with an extra key refused `extra_forbidden` at `("x",)`.

## Consequences

HTTP keeps `model_validate_json`, strict, because a JSON client sends typed values. The CLI and the environment are text edges and lenient. Refuted by nothing.
