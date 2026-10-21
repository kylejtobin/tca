# 0018. A field's docstring is its description

Status: accepted

## Context

CLI help text and OpenAPI property descriptions are read from `FieldInfo.description`. A developer documents classes with docstrings and should document fields the same way.

## Rejected

`Field(description=...)` on every field. Setting descriptions from the field type's docstring in `__pydantic_init_subclass__` followed by `model_rebuild(force=True)`: the help text changed and the JSON schema did not, so the mechanism was unreliable.

## Decision

`use_attribute_docstrings=True` in `PRODUCT` and in `Record`'s config. A docstring written under a field is its description. A type's docstring reaches OpenAPI through `$defs`; a server kind that needs it as a fallback for an undocumented field reads `annotation.__doc__` when it builds its parser.

## Evidence

`class PlaceOrder(Request)` with `sku: Sku` followed by the docstring `"""The product ordered."""`: `model_json_schema()["properties"]["sku"]["description"]` is `"The product ordered."`; `["$defs"]["Sku"]["description"]` is `Sku`'s class docstring. `CliApp.format_help(PlaceOrder)` showed `--sku str  The product ordered. (required)`.

## Consequences

`Field(description=...)` is not written on a page. `use_attribute_docstrings` reads the class's source, so it applies to classes written in a module and not to classes made with `exec` or `create_model`; every page is a module. Refuted by nothing.

