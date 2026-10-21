# 0029. A program is one module named by the entry-point group

Status: accepted

## Context

The engine and every server kind must find a program's routes and its config.

## Rejected

Walking a package with `pkgutil` for `Route` subclasses: a search over the filesystem for something the program should declare.

## Decision

A program's `pyproject.toml` declares `[project.entry-points."type_construction.programs"] shop = "shop"`; the entry's name is the command and its value is the module. A program's classes are the classes in `vars(module)` whose `__pydantic_generic_metadata__["origin"]` is `None`: Pydantic registers every parametrization, `Says[Catalog, Price]`, in the module beside the developer's `Quote`, and those carry an origin. `routes(module)` returns the `Route` subclasses, `config(module)` the one `Config` subclass, `arguments(route)` its `Q` and `A`, `hears(action)` and `party(action)` its `T` and `P` resolved through any library kind's type variables.

## Evidence

`vars(shop)` held `Says` and `Says[Catalog, Price]` beside `Quote`; with parametrizations excluded, `hears(Charge)` was `Charged` and `party(Charge)` was `Payments`; `routes()` returned `Checkout` and `RequoteSku` in definition order; `config()` returned `ShopConfig`; `arguments(Checkout)` returned `(PlaceOrder, OrderPaid)`.

## Consequences

A route in a module the entry point does not name is not part of the program. Refuted by a program that must span modules; then the named module re-exports them.
