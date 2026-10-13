---
name: python-dev-tca
description: "Type Construction Architecture for Python. A program is declared as Pydantic types, and construction is the only operation. Use before writing, reviewing, or refactoring any Python in a TCA project, before the first class exists."
---

# Python Dev TCA

Whenever you model, always ask these three questions:

1. Remove every body. Do the types alone still specify the domain? If what remains is a pipeline, there is no model.
2. Which types are named for a stage of the run? Each is workflow inhabiting a class, and the domain thing under it has no type. Delete it.
3. Are the inhabitants of the types in bijection with the states of the domain? If not, the model is wrong. Remodel from the domain; do not patch the type.

Every type you write sits on one of these levels, and its fields hold only types from the levels above it; a type you cannot place by its fields is procedure.

```text
Scalar
↓
Value
↓
Thing
↓
Alternative
↓
Crossing
```

Every class you write is a `BaseModel`, a `RootModel` or a `StrEnum`. Every field is typed as one of your own classes, a union of them, or a tuple of them; a primitive appears only as the root of a `RootModel`; a root is read only by its own type, by a property that constructs a new scalar from it, or where it leaves to a library in `interpret`, a composition root's callback, or a provider's `client`. There is no `dict`, `list`, `set`, `Any`, `None` or `Optional` anywhere: not in a field, a root, an argument or an expression. The only functions are one `interpret` on each interpreter and the callbacks of the composition root, each a single returned expression, and the reading and writing of a format in `parser/`; anything else a class knows is a property with a single returned expression. An interpreter holds its action and its provider; a provider holds what the deployment names and the library does not read for itself, and derives a client that keeps nothing between crossings; config is a `BaseSettings` of providers and value objects the environment constructs by name, and the deployment's config is the program; config and its providers are the only classes not strict, since the environment is strings; nothing is held that is not one of your classes. Construction is the only operation: a step you are about to write is a class you have not named.

Only an interpreter's `interpret` and a composition root's callback read or write JSON: what arrives constructs a model by `model_validate_json`, and what leaves is `model_dump_json`. Everywhere else a model is constructed from a model already held, by `model_validate` with `from_attributes=True`; nothing else is ever passed to `model_validate`.
A format that is not JSON is read by a maintained library that yields JSON, and is then the line above.
Only a format no library yields JSON from is read by a format type in `parser/`, and nothing outside `parser/` reads a format.

An action carries every rule its effect must follow; the system it calls enforces them, and its reply is read once into the domain's outcome.

## Its files, in dependency order

```text
 1  domain/<context>/type.py               semantic-scalar.md  ordered-union.md  collection.md
 2  integration/<system>/model.py          foreign-model.md
 2  parser/<format>.py                     format-type.md
 3  domain/<context>/value.py              value-object.md  collection.md
 4  integration/<system>/provider.py       provider.md
 5  domain/<context>/<concept>.py          union.md  concept-model.md  action.md
 6  domain/<context>/api.py                contract-model.md
 7  config.py                              config.md
 8  integration/<system>/<meaning>.py      transformation.md
 9  integration/<system>/interpreter.py    effect-interpreter.md
10  api/<context>.py                       route.md                 (a process; a package has no transport)
11  main.py                                composition-root.md      (a process)
11  <package>/__init__.py                  composition-root.md      (a package)
```

A file imports only the files above it. Its constructs are on the pages beside it. The shop, every class in its group, is drawn one crossing at a time in `whole-program.md`.
