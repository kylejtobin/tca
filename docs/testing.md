# Testing

How Type Construction Architecture tests itself. The method is the framework's own thesis applied to its evidence: a test is a value, constructing it writes the test, comparing it runs the test, and the specification is read from it.

## What a test is here

A test is a scenario: one kind, one input from one of the framework's edges, and one outcome from a closed set. It is a Pydantic instance.

```python
Scenario[Quantity](
    title="A constrained root refuses a value outside the constraint",
    record="0002",
    kind=Quantity,
    given=Json(text="0"),
    expects=Refuses(errors=(("greater_than", ()),)),
)
```

Everything that matters about this test is in its type. `kind` is `type[Quantity]`, so the checker reads the class and Pydantic refuses any class that is not it. `given` is a union of the edges, so the input is one the framework actually has. `expects` is a union of the outcomes, so the test can only expect something that can happen. `record` is the decision this scenario is evidence for, constrained to a record number, so a scenario that cannot name its decision cannot be constructed.

The suite is a tuple of these values per feature. One function runs them: it constructs the kind from the input, catches what Pydantic or the engine does, and compares it to `expects`. That function is the only procedure in the test system.

## Why not the standard form

Standard tests are procedure that asserts. The two standard forms were considered and refused.

- **pytest-bdd and a step grammar.** The feature file is parsed, each sentence matched to a function by text, the class looked up by name on a fixture, the value passed as a string. That is an interpreter with a lookup and a dict, which is the pattern this repository refuses on a page, placed in the tests that enforce the refusal. basedpyright reads none of it: a misspelled class name fails at runtime as a missing step.
- **A test function per scenario.** Typed, but the feature file is then prose written beside it, and the two drift. Nothing ties a sentence in the specification to the call that proves it.

The scenario value is more type safe than either. The checker sees the class, the input mode and the outcome. The feature file is rendered from the value, so it cannot drift. And the decision record is a field, so the line between our behavior and Pydantic's is enforced by construction, not by review.

## The shapes

All scenario kinds use the `PRODUCT` config: frozen, strict, no extra fields. They live in `type_construction.testing`.

### Inputs: the edges

A kind is constructed in exactly five ways in this framework. The input union is that list.

| member | field | edge | the call |
|---|---|---|---|
| `Json` | `text: str` | HTTP body, a party's response | `kind.model_validate_json(text)` |
| `Tree` | `value: JsonValue` | the command line | `kind.model_validate(value, strict=False)` |
| `Root` | `value: JsonValue` | a scalar written in code | `kind(value)` |
| `Held` | `fields: dict[str, BaseModel \| tuple[BaseModel, ...]]` | the engine's fold | `kind.model_validate(fields)` |
| `Environment` | `variables: dict[str, str]` | the deployment | `kind()` with those variables set |

An input that is not one of these is not an edge the framework has, and a scenario cannot hold it.

### Outcomes

| member | field | what happened |
|---|---|---|
| `Constructs[T]` | `instance: T` | construction succeeded and the instance equals this one |
| `Dumps` | `json: str` | construction succeeded and `model_dump_json()` is this text |
| `Refuses` | `errors: tuple[tuple[str, tuple[str \| int, ...]], ...]` | `ValidationError`, with these `(type, loc)` pairs in order |
| `Abstract` | | `TypeError` naming the kind as abstract |
| `Schema` | `path: tuple[str, ...]`, `value: JsonValue` | `model_json_schema()` holds this value at this path |

### The engine's and the CLI's scenarios

The same shape one level up. The kind is a route, the input is a request, the outcome is what `answer` or `prove` does.

| scenario | holds | expects |
|---|---|---|
| `Proved` | `route`, `program` | `Ordered(classes)` or `Refuses` with the proof's fault codes |
| `Answered` | `route`, `request: Json`, `config: Environment`, `program` | `Dumps` of the reply, or `Refuses` |
| `Invoked` | `argv: tuple[str, ...]`, `program` | `Exits(code, stdout_contains, stderr_contains)` |
| `Checked` | `page: str` | `Reports(hits: tuple[Hit, ...])` from the smell check |

The program a scenario names is a real module of real classes in the package's tests. The engine's is the shop: its parties are `Says[P, T]` actions whose `perform` returns a fixed record, so no transport is needed. The demo program is this module with `Post` in place of `Says`.

## What earns a scenario

A scenario pins a decision this repository made. It does not pin what Pydantic documents.

`Quantity.model_validate_json("0")` refusing with `greater_than` is Pydantic's behavior. It is a scenario only because record 0002 says a rule is a constraint, and one such scenario is the evidence; a second constraint on a second primitive adds nothing. `Reply[F]` dumping without `of`, a `Record` constructing by alias only, a `Setting` accepting the string a `Scalar` refuses, the proof naming an unheard record: those are ours, and each has a record.

The test: if the scenario's `record` field cannot be filled with a number whose record decided this behavior, the scenario is Pydantic's and is not written. If the behavior has no record and should, the record is written first.

## What stays procedure

A scenario's outcome is a value. Some of the engine's behaviors have an outcome that is a trace: two actions starting at the same instant, connections closing in reverse order across two answers, the span tree an answer emits, `Instant` differing between two constructions. These are tested as plain pytest functions beside the scenarios, under the same feature's name, and record 0033 allows exactly this: tests for procedure, written as procedure. A trace test is still named for the record it is evidence for.

## Running

The runner is one function per scenario kind, `run(scenario) -> Outcome`, and one pytest function per package, parametrized over every scenario the package's feature modules export. The assertion is `run(scenario) == scenario.expects`. Engine scenarios are awaited; `asyncio_mode` is strict, so that function carries the asyncio mark.

`just check` runs the smell check, basedpyright and pytest. CI runs the same recipe. A scenario that fails is a defect in the framework or a wrong scenario, and the record says which.

## Rendering

The feature file is read from the values. `Scenario.gherkin` is a computed field: the title, a `Given` line per class rendered from `model_fields` and their constraints, a `When` naming the edge and the input, a `Then` naming the outcome. A feature module's docstring is the `Feature:` header and the records it carries.

`just features` writes every `tests/features/*.feature` from its scenario module. CI runs it and fails on a diff, so a feature file that was edited by hand, or a scenario whose rendering changed, stops the build. The feature file is the specification a reader who knows the business and not the code reads; the scenario module is where it is written.

## Where things live

```
packages/python/type-construction-testing/src/type_construction/testing/__init__.py   the scenario kinds, run, render
packages/python/<package>/tests/scenarios/<feature>.py                                 the values, one module per feature
packages/python/<package>/tests/scenarios/<feature>_trace.py                           the procedure tests for that feature, if any
packages/python/<package>/tests/features/<feature>.feature                             rendered; never edited
packages/python/<package>/tests/programs/<name>.py                                     the programs engine and CLI scenarios run
tests/scenarios/smell_check.py, tests/features/smell_check.feature                     the checker's scenarios
```

`type-construction-testing` is a workspace package in the dev dependency group. It depends on the world and the engine.

## Adding a scenario

1. Name the record. If the behavior has none, write the record.
2. Write the classes the scenario needs in the feature module or the program module. They are real classes; the `Given` lines are rendered from them.
3. Write the value: the kind, the edge, the outcome.
4. Run `just check`. A failing scenario is read as a finding about the framework before it is read as a wrong expectation.
5. Run `just features` and commit the rendered file with the module.

## What this is not

- Not a place to assert Pydantic's documented behavior. One scenario per decided fact.
- Not a DSL. There is no step text to match and no grammar to extend; a new kind of outcome is a new union member with a field, and the checker reads it.
- Not a place for mocks of the engine. The engine's scenarios run the engine on a program whose parties return fixed records.
- Not a place to edit the feature files. They are output.
