# 0017. Edges validate in the mode the edge needs; code constructs strict

Status: accepted

## Context

`Request` is strict. An HTTP body delivers JSON numbers and strings; a command line delivers strings only. `Scalar[int]` must refuse `"3"` in code and accept it from the world.

## Rejected

Loosening `Scalar` or `Request` to lax mode. `CliApp.run(PlaceOrder, cli_args)`, which validates the parsed arguments in Python mode and refuses strict root models. `model_validate_strings` for the command line, which refuses a list with `string_type`, so no `tuple` field could arrive from argv.

## Decision

HTTP validates the body with `model_validate_json`, strict, because a JSON client sends typed values. The CLI builds a nested dict of text from the parsed options and validates with `Q.model_validate(tree, strict=False)` (0026). The environment reaches `Connection` and `Config` through `Setting` roots (0025). Code constructs in Python mode. No class changes.

## Evidence

`Quantity("3")` raises; `Quantity(3)` constructs; `Amount("2.50")` raises; `Amount(Decimal("2.50"))` constructs. `PlaceOrder.model_validate_json('{"sku":"tea","quantity":3,"amount":"2.50"}')` constructs; with `"quantity":"3"` it raises; with `"amount":2.5` it constructs. `PlaceOrder.model_validate(tree, strict=False)` from a tree of text with a nested `Value`, two tuples, a `Decimal` and an enum constructed every field; the same tree strict refused five locations; with `"quantity": "0"` it raised `greater_than` at `("quantity",)`. `model_validate_strings` refused a list with `string_type` at `()`. `CliApp.run(PlaceOrder, cli_args=[...], cli_exit_on_error=False)` raised `ValidationError` for `CliAppBaseSettings`.

## Consequences

The world module has one strictness. A server kind chooses the validation call for its input. Refuted by nothing.
