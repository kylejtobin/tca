---
name: tca-testing
description: "How tests are written in a Type Construction Architecture repository: a test is a Scenario value holding a kind, an input from one of the five edges and an outcome from a closed union; the feature files are rendered from the values, never parsed or edited; a scenario names the decision record it is evidence for or is not written. Use before writing, changing or reviewing any test, scenario, feature file or test program in a TCA project."
---

# TCA Testing

A test is a value. You write a `Scenario` instance: the kind under test, the edge its input arrives on, and the outcome. Constructing the value is writing the test. One runner compares what happens to what the value expects. The Gherkin feature file is rendered from the values and is never written by hand. The design is `docs/testing.md`; this skill is the loop.

## Before any test

Answer three questions. A test with no answer to the first is not written.

1. **Which decision record is this evidence for?** The scenario's `record` field holds the number. If no record decided the behavior, either the behavior is Pydantic's and needs no scenario, or the record is missing and is written first.
2. **Which edge does the input arrive on?** `Json`, `Tree`, `Root`, `Held` or `Environment`. If none fits, the input is not one the framework has; find the edge the behavior actually belongs to.
3. **Which outcome?** `Constructs[T]`, `Dumps`, `Refuses`, `Abstract` or `Schema`. If the result is a trace, a timing, an order of calls or a span tree, it is a procedure test, written as a plain pytest function beside the scenarios.

## The shapes

Everything is in `type_construction.testing`. All kinds use `PRODUCT`.

```python
class Scenario[T: BaseModel](BaseModel):
    title: Title                      # the Gherkin scenario line
    record: Decision                  # Scalar[str] constrained to a record number
    kind: type[T]                     # the class under test; the checker reads it
    given: Json | Tree | Root | Held | Environment
    expects: Constructs[T] | Dumps | Refuses | Abstract | Schema

    @computed_field
    @property
    def gherkin(self) -> str: ...     # rendered from title, kind.model_fields, given, expects
```

Inputs, each the exact call an edge makes:

```python
class Json(BaseModel):        text: str                                             # kind.model_validate_json(text)
class Tree(BaseModel):        value: JsonValue                                      # kind.model_validate(value, strict=False)
class Root(BaseModel):        value: JsonValue                                      # kind(value)
class Held(BaseModel):        fields: dict[str, BaseModel | tuple[BaseModel, ...]]  # kind.model_validate(fields)
class Environment(BaseModel): variables: dict[str, str]                             # kind() under these variables
```

Outcomes:

```python
class Constructs[T: BaseModel](BaseModel): instance: T
class Dumps(BaseModel):                    json: str
class Refuses(BaseModel):                  errors: tuple[tuple[str, tuple[str | int, ...]], ...]   # (type, loc) in order
class Abstract(BaseModel):                 pass
class Schema(BaseModel):                   path: tuple[str, ...]; value: JsonValue
```

The engine's, the CLI's and the checker's scenarios are the same shape one level up: `Proved(route, program) -> Ordered | Refuses`, `Answered(route, request: Json, config: Environment, program) -> Dumps | Refuses`, `Invoked(argv, program) -> Exits`, `Checked(page) -> Reports`.

## A scenario, written

```python
"""Scalars, Instant, Identity and Duration. Records 0002, 0011."""

class Quantity(Scalar[int]):
    """How many of a product an order asks for."""
    root: int = Field(gt=0)

SCENARIOS = (
    Scenario[Quantity](
        title="A constrained root refuses a value outside the constraint",
        record="0002",
        kind=Quantity,
        given=Json(text="0"),
        expects=Refuses(errors=(("greater_than", ()),)),
    ),
)
```

It renders to:

```gherkin
Scenario: A constrained root refuses a value outside the constraint
  Given class Quantity(Scalar[int]) with root: int = Field(gt=0)
  When Quantity is constructed from the JSON 0
  Then ValidationError is raised with type greater_than at loc ()
```

The classes in a feature module are real classes. The `Given` lines are read from them, so a class the scenario does not need is a line the reader does not need.

## The loop

1. Read the record. Its Decision names the behavior; its Evidence is where this scenario will be cited.
2. Write the classes the scenario needs, in the feature module under `tests/scenarios/` or in the program module under `tests/programs/`. Programs the engine runs have `Says[P, T]` parties whose `perform` returns a fixed record.
3. Write the value and add it to `SCENARIOS`.
4. Run `just check`. A scenario that fails is first a finding about the framework. Read the actual outcome before deciding the expectation was wrong.
5. Run `just features`. Read the rendered scenario as the business reader would. If the sentence is wrong, the value is wrong; fix the value.
6. Commit the module and the rendered feature file together, naming the record.

## Rules

- **One scenario per decided fact.** Pydantic's strict-mode table, its alias handling, its constraint errors are documented by Pydantic. A record needs one scenario as evidence; a second primitive, a second constraint, a second alias adds nothing and is not written.
- **No step text.** There is no pytest-bdd, no `parsers.parse`, no fixture looked up by name, no value passed as a string to be interpreted. A new kind of input or outcome is a new union member with typed fields.
- **No edits to a feature file.** It is rendered. `just features` in CI fails on a diff.
- **No mock of the engine or of a kind.** The engine's scenarios run `prove` and `answer` on a real program. A party that returns a fixed record is a real `Action` subclass, not a patch.
- **Procedure tests are for traces only.** Order of calls, concurrency timing, spans, freshness of `Instant` and `Identity`. They are plain pytest functions, named for the record, beside the scenarios under `<feature>_trace.py`. They never duplicate a scenario.
- **`Constructs` compares whole instances.** If equality cannot be stated because a field is fresh on each construction, that is a trace test, not a looser outcome.
- **The errors tuple is complete and ordered.** `Refuses` lists every `(type, loc)` Pydantic reports, in the order it reports them. A scenario that lists one of three is wrong.

## Smells in a test

| you wrote | it is | write instead |
|---|---|---|
| a `@given`, `@when`, `@then` function | an interpreter | a `Scenario` value |
| `getattr(module, name)` | a lookup by name | the class, imported |
| `json.loads(...)` in a test | a dict nobody typed | `Json(text=...)`, parsed by the kind |
| `assert "greater_than" in str(e)` | a string search | `Refuses(errors=(("greater_than", ("quantity",)),))` |
| `MagicMock`, `patch` | a mocked kind | a `Says[P, T]` action with a fixed record |
| a scenario whose `record` you cannot fill | Pydantic's behavior | nothing, or the missing record first |
| an edit in a `.feature` file | output edited by hand | the value |
| `Any`, `object`, `cast`, `# type: ignore` | the checker refused a type | the type it named |

## Checks

`just check` runs the smell check on every program, basedpyright on every package including the tests, and pytest. `just features` renders. Both are green before a commit. Passing is not proof: a scenario that asserts what Pydantic documents passes and is still wrong.

## Where things are

- `docs/testing.md`: the design and why the standard forms were refused.
- `docs/decisions/0033`: tests are the bound scenarios; a page has none.
- `type_construction.testing`: the scenario kinds, the runner, the renderer.
- `packages/python/<package>/tests/scenarios/`, `tests/programs/`, `tests/features/`: values, programs, rendered output.
