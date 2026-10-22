# 0027. The command line is rendered from the request class through the engine's reads

Status: accepted

## Context

The CLI needs one option per request field with help, choices, constraints, nesting and repetition, for strict classes whose scalars are `RootModel` subclasses, and it must know exactly what the engine knows about a request and nothing else.

## Rejected

`CliSettingsSource.root_parser`: typed `type[BaseSettings]`; pydantic-settings' own path for a plain model is a private wrapper under `# type: ignore`. `CliApp.run` on 2.15.0: flattened `tuple[Value, ...]` into dotted required options and refused. `CliSettingsSource` on a `BaseSettings` twin of the request: returned a tree with dotted options, enum choices and descriptions as help, but rendered scalars as `str` and `int`, replaced repeated JSON objects instead of appending them, and required a `BaseSettings` twin per request. tyro 1.0.16: "Unsupported type annotation for field amount.root with type Decimal". cyclopts 5.2.0: rendered `--order.sku.root`, failed with `IndexError`. argdantic 1.3.3: rendered `--order.sku.root TEXT`, validated strictly, refused five fields. A walk over `model_fields` with `isinstance` on annotations as untyped dicts: ten `REFLECTION` hits. `Q.model_json_schema()` parsed into node classes, `Reference | Object | Array | AnyOf | Primitive`, chosen by a discriminator on the keys a node carries: a second representation of the request, with its own type system, that knew of `anyOf` and `$ref` and nothing of the kinds.

## Decision

The command line is the request's type, read through the engine's reads. `options(parser, Q)` adds one option per field of `Q`: for a scalar, `--name` with the class name as the metavar, the field's docstring or the class's as help, the `gt`, `ge`, `lt`, `le`, `min_length` and `max_length` metadata on its root as bounds after it, and its members as choices when the root is an enumeration; for an enumeration field, its members as choices; for a value, one dotted option per field, `--place.city`; for a tuple, one repeated option, taking the scalar's text or one JSON object per value. `tree(given, Q)` reads the parsed options back into the nested dict of text the request validates from, by the same reads, and `Q.model_validate(tree, strict=False)` constructs it (0026). `variables(Config, "")` lists the deployment's variables the same way, a connection's settings under its key with `__`. Two routes that would share a command are refused at startup as `command`. The CLI imports `holds` and `collects` from the engine and knows nothing the engine does not.

## Evidence

For a request with `name: Name`, `count: Count`, `amount: Amount`, `kind: Kind` an enumeration, `place: Place` a value with `city`, `tags: tuple[Tag, ...]` and `each: tuple[Element, ...]`, the route's help rendered `--name NAME        The thing's name. (min length 1)`, `--count COUNT      How many. (> 0)`, `--amount AMOUNT    What is offered. (> 0)` from the class docstring, `--kind {one,two}   Which kind.`, `--place.city CITY  The city it goes to. (min length 1)`, `--tags TAG         Words attached. (min length 1)` and `--each JSON        The elements, any number.`; the program's help listed `PARTY__SAYS     What the party says.` and `PARTY__RETRIES  How many times the party is asked again. (>= 0)`. From `--name tea --count 3 --amount 2.50 --kind two --place.city Boston --tags gift --tags rush --each '{"label": "a", "size": 1}' --each '{"label": "b", "size": 2}'`, `tree` was `{"name": "tea", "count": "3", "amount": "2.50", "kind": "two", "place": {"city": "Boston"}, "tags": ["gift", "rush"], "each": [...]}`, the request constructed, the route answered, and the reply printed was `{"name":"tea","words":["yes","yes"]}`. basedpyright strict: 0 errors.

## Consequences

The CLI has no document, no node classes and no discriminator; a request shape the proof accepts is one the CLI renders, since `boundary` refuses the rest (0059). Refuted by a request field the reads do not describe; none exists, since the proof refuses one.
