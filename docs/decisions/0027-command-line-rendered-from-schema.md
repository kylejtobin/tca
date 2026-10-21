# 0027. The command line is rendered from the request's JSON schema parsed into node classes

Status: accepted

## Context

The CLI needs one option per request field with help, choices, constraints, nesting and repetition, for strict classes whose scalars are `RootModel` subclasses.

## Rejected

`CliSettingsSource.root_parser`: typed `type[BaseSettings]`; pydantic-settings' own path for a plain model is a private wrapper under `# type: ignore`. A walk over `model_fields` with `isinstance` on annotations: ten `REFLECTION` hits and three `partially unknown` errors, each red answered with another narrowing. tyro 1.0.16: refused to build a parser, "Unsupported type annotation for field amount.root with type Decimal". cyclopts 5.2.0: rendered `--order.sku.root` with help "The root object of the model", failed with `IndexError`. argdantic 1.3.3: rendered `--order.sku.root TEXT`, validated strictly, refused five fields.

## Decision

`Schema.model_validate(Q.model_json_schema(), strict=False)` once. `Member` is a discriminated union of `Reference | Object | Array | AnyOf | Primitive`, each a `Record` of Pydantic's schema under its names with `extra="ignore"`, chosen by a callable `Discriminator` on the keys a node carries, `$ref`, `anyOf`, `type` object or array, else a primitive, with a `Tag` per member. Each member renders itself: `Primitive.option` and `.repeated` add one argument from computed `metavar` (its title), `bounds` (its constraints, or its `format` alone) and `enum`; `Object.option` recurses with a dotted prefix and `.repeated` takes one JSON object per element; `Array.option` calls its item's `repeated`; `Reference` delegates to `Schema.defs`; `AnyOf` delegates to its first form, which on Pydantic 2.13.5 is how `Decimal` is written, `anyOf` of `number` and `string`. `Schema.environment` lists a config's variables the same way.

## Evidence

Help rendered `--sku SKU  The product ordered. (min length 1)`, `--quantity QUANTITY ... (> 0)`, `--amount NUMBER  A sum of money. (> 0.0)`, `--currency {USD,EUR}`, `--ship-to.city CITY`, `--tags SKU`, `--lines JSON  One product and how many of it.`; the program help listed `PAYMENTS__URL  Where the party is. (uri)`, `PAYMENTS__KEY ... (password)`, `PAYMENTS__RETRIES ... (>= 0)`. `PlaceOrder`'s schema parsed to `Reference` properties and `Primitive` definitions; a node `{"type": "weird"}` was refused as `literal_error` at `("properties", "x", "primitive", "type")`. basedpyright strict: 0 errors.

## Consequences

The CLI, OpenAPI and any later renderer read one document, so their descriptions agree by construction. The node classes stay in the CLI package until a second reader exists. Refuted by a request shape the schema does not describe; none exists, Pydantic describes every kind.
