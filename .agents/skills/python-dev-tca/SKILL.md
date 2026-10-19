---
name: python-dev-tca
description: "Type Construction Architecture for Python. A program is declared as Pydantic types, and construction is the only operation. Use before writing, reviewing, or refactoring any Python in a TCA project, before the first class exists."
---

# Python Dev TCA

Whenever you model, always ask these three questions:

1. Remove every body. Do the types alone still specify the domain? If what remains is a pipeline, there is no model.
2. Which types are named for a stage of the run? Each is workflow inhabiting a class, and the domain thing under it has no type. Delete it.
3. Are the inhabitants of the types in bijection with the states of the domain? If not, the model is wrong. Remodel from the domain; do not patch the type.

Every type you write means one of three things, by its meaning and its standing in the domain, and its fields agree with it: a field holds a type of its own layer or of any layer above it, so a thing may hold things, values and scalars, and a recursive thing holds itself; a type whose fields reach below its layer is misplaced or misnamed, and a domain type that means none of the three is procedure.

```text
Scalar    one atomic meaning, over a primitive or a library's vocabulary
↓
Value     a composite part, with no standing of its own
↓
Thing     a whole the domain acts on or concludes: a request, an intention, an outcome
```

An alternative or a collection sits on its members' layer, so each occurs at every layer. Crossing is not a layer: it is the responsibility of the constructs that stand at a boundary, the foreign record, format type, transformation, provider, interpreter, route and config. A crossing holds the domain's types and none of them holds it; a foreign record's content still has its layer, in the other system's meaning. A type lives where its meaning is defined: in the domain when the domain's language and rules define it, a reference to something another system holds included; in a system's integration when that system's contract or the deployment defines it.

Every class you write is a `BaseModel`, a `RootModel` or a `StrEnum`. Every field is typed as one of your own classes, a union of them, or a tuple of them; a primitive, or a library's vocabulary, appears only as the root of a `RootModel`; a root is read only by its own type, by a property that constructs a new scalar from it, or where it leaves to a library in `interpret`, a composition root's callback, or a provider's `client`; a library's own vocabulary that this program only hands to it there, a header's name or a media type, is a literal argument, while vocabulary this program holds or reads is a scalar. There is no `dict`, `list`, `set` or `Any` in a field, a root, an argument or a held value, and no `None` or `Optional` in a field or a root: absence is a class; a rejection predicate's expression may build a set to state that members are distinct, the one fact of a collection no constraint states. `None` is only a library's own word for absence, where a value is handed to that library: in the signature of an `interpret` or a callback, or as what a derivation hands the library. The only functions are one `interpret` on each interpreter and the callbacks of the composition root, each a single returned expression; the rejection predicates; and the parsing, serialization and validation of a format in `parser/`. An `interpret`'s expression may stand within the one `async with` that acquires the capability it uses, which is then released on every path. A rejection predicate states an invariant no constraint can, of a scalar, a collection's members or a product's fields: it is a `model_validator(mode="after")` whose body is `if not` one expression over `self`, `raise ValueError` with the member of the context's invariants it enforces, a closed vocabulary of its rules, then `return self`; it refuses and never transforms or decodes, and there is no other validator. Anything else a class knows is a property with a single returned expression, which succeeds for every valid holder. An interpreter holds its action and its provider; a provider holds what the deployment names and the library does not read for itself, and derives a client that keeps nothing between crossings; a library's contract that is mutable is not held: the provider holds its own immutable statement of it, and a derivation constructs the library's object from that. An execution's own resources, such as a library's usage and cancellation handles, are not held either: they are keyword-only arguments of `interpret` and of the callbacks that reach it, in the library's types, defaulting to `None` and passed to the library unchanged. Config is a `BaseSettings` of providers and value objects the environment names, and the deployment's config is the program; every class is strict, and the settings source decodes the environment's text against each field's type. Nothing is held that is not one of your classes. Construction is the only operation: a step you are about to write is a class you have not named.

Only an interpreter's `interpret` and a composition root's callback receive or send what crosses: what arrives is validated once, natively, by the type that stands for its contract: `model_validate_json` for JSON, `model_validate` for the Python data a library yields, and the settings source for the environment, against each field's type; what leaves is `model_dump_json`. When another system authors the contract, a foreign record validates it, and the domain's fact is constructed from that record; when this program authors the contract another system must meet, as an agent's structured output, the domain's type is the contract and the library validates against it. Inside the program, a model is constructed from a model already held, by `model_validate` with `from_attributes=True`; nothing else is passed to `model_validate` but what a crossing receives.
A library that calls back into this program, an agent with its tools, is composed by the interpreter that acquires it, from the providers' clients, the domain's types and the interpreters whose `interpret` it calls back; it is not a provider's client. A system the library reaches two ways, as a capability and as a shell, is two providers constructed from the one statement the deployment made.
A format that is neither is read by a maintained library that yields one of them, and is then the line above.
Only a format no maintained library reads is read and written by a format type in `parser/`. There, and only there, its parsing, serialization and format-specific validation use whatever procedure the format needs; its records stay strict, frozen types of the program's own, constructed directly from their typed fields; it returns its record or a validation failure, its restrictions are the format's own, and only a foreign model holds it. Nothing outside `parser/` reads or writes a format, and no rule of the domain is relaxed by it.

An action carries every rule its effect must follow; the system it calls enforces them, and its reply is read once into the domain's outcome. A request whose only purpose is its effect is its own action.

## Its files, in dependency order

```text
 1  domain/<context>/type.py               semantic-scalar.md  ordered-union.md  collection.md
 2  integration/<system>/model.py          foreign-model.md  semantic-scalar.md  collection.md
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

The table is the order you model in. Imports follow ownership, whatever a file's position: a domain file imports only domain files above it, and nothing outside the domain; an integration file imports the domain, its library and its own system's files above it, never another system's, and a foreign model imports from `parser/` the format type that reads its records; a format type imports the domain's scalars and nothing of an integration; the application imports what it composes. Nothing imports in a cycle; a type that holds itself does so within its own file. Each construct is on the page beside its file. The shop, every class in its group, is drawn one crossing at a time in `whole-program.md`.

If you believe this skill is missing the instruction your case needs, you are wrong: you have stopped modeling. Ask again what the thing is, its valid states and its owner, until the types answer. The answer is a construction, and it is on these pages because every construction is.
