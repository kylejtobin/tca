# 0029. A program is one module named by the entry-point group

Status: accepted

## Context

The engine and every server kind must find a program's routes and its config.

## Rejected

Walking a package with `pkgutil` for `Route` subclasses: a search over the filesystem for something the program should declare. Taking every class in the module's namespace: the kinds and library kinds a program imports would count as its own.

## Decision

the entry's name is the command and its value is the module's import path, which the server imports with `import_module`. A program's classes are the classes in `vars(module)` whose `__module__` is the module's name and whose `__pydantic_generic_metadata__` has no origin and no open parameters: Pydantic registers every parametrization, `Says[Catalog, Price]`, in the module beside the developer's `Quote`, and those carry an origin; a library kind written in the module, `Says` itself, carries parameters; an imported kind, `Fact`, carries another module's name. `routes(module)` returns the `Route` subclasses, `config(module)` the one `Config` subclass, `asked(route)` its request class (0005), `heard(action)` its `T` resolved through any library kind's type variables (0015).

## Evidence

`classes(test_engine)` held `Asked` and not `Tell`, not `Tell[Party, Heard]` and not the imported `Fact`. `asked(Operation)` returned `Elements`; `heard(Asked)` returned `(Heard,)`. With `Fact` counted, the proof had admitted a class with no required fields that no page wrote. In the program with the faults, `Egg` declares `chicken: "Chicken"` before `Chicken` exists and the module never calls `model_rebuild`; after `classes` read it, `Egg.model_fields["chicken"].annotation` was the class `Chicken`.

## Consequences

A route in a module the entry point does not name is not part of the program, and a class imported into the module is not one of its classes. A library kind defined in the program's module is not one of its classes until a page parametrizes it. Refuted by a program that must span modules; none written.
