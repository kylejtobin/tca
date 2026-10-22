# 0026. The command line validates with model_validate(tree, strict=False)

Status: accepted

## Context

argv is text. A request may hold a `Value`, a `tuple`, a `StrEnum`, a `Decimal`. The class is strict.

## Rejected

`model_validate_strings`: refused a list with `string_type` at `()`, so no `tuple` field can arrive from argv through it. `CliApp.run`: validates in Python mode against the strict class and refused.

## Decision

The CLI builds a nested dict of text from the parsed options (0027) and calls `Q.model_validate(tree, strict=False)`. The lenient mode is chosen per call at the edge; the class stays strict in code.

## Evidence

From `{"name": "tea", "count": "3", "amount": "2.50", "kind": "two", "place": {"city": "Boston"}, "tags": ["gift", "rush"], "each": [{"label": "a", "size": 1}]}`: the lenient call constructed every field, `count.root` 3, `amount.root` `Decimal("2.50")`, `kind` the enumeration's member, `each[0].size.root` 1; with `--count 0` the command exited 1 with `count` and `greater_than` on standard error; with `--name` left out it exited 1 with `name` and `Field required`.

## Consequences

HTTP keeps `model_validate_json`, strict, because a JSON client sends typed values. The CLI and the environment are text edges and lenient. Refuted by nothing.
