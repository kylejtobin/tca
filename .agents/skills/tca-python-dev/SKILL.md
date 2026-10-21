---
name: tca-python-dev
description: "How to build an application on Type Construction Architecture: the ten Pydantic classes you subclass, the five shapes you write them with, how a rule and a choice and a collection are written as types, the loop from route to parties, how to run the program, the engine's contract, and the questions developers ask answered with classes. Use before writing any application code in a TCA project."
---

# TCA Python Dev

You write an application as subclasses of ten Pydantic classes and `StrEnum`, and nothing else. Constructing those classes is running the program. `ValidationError` is the only failure path. The engine reads your classes, proves them at startup, and runs them; you never call it, extend it, or write around it.

## Why ten classes are enough

An application is data, control flow, I/O and deployment. Each is one Pydantic construct the checker reads.

- **Data.** A field is a product. A union `A | B` is a sum. `tuple[T, ...]` is repetition. `Scalar` is a primitive with an invariant. A `StrEnum` subclass is an enumeration. `Value` is a composite part.
- **Control flow.** A field is a sequence: `Paid` holds `Charged`, so `Charged` exists first. A union is a branch. A tuple is iteration. A fact holding the previous fact is accumulation. A `@computed_field` is a derived value. A `Scalar` constraint is a rule.
- **I/O.** `Request` arrives on a `Route`. `Record` is what a party says. `Action` asks a `Connection` and hears a `Record`. `Reply[F]` leaves, made from the fact `F`. A library kind per transport carries the only Python that calls a client.
- **Deployment.** `Config` holds the connections and settings; each value the deployment sets is a `Setting`.

There is no construct for a function, a handler, a validator, a loop, a step or a state machine. Each is one of the above written as procedure, and the smell check refuses it on a page.

## The classes

From `type_construction.world`. Every class is strict, frozen and forbids undeclared fields; a docstring under a field is its description everywhere the field is shown.

| class | what it is | owner | its fields |
|---|---|---|---|
| `Scalar[T]` | one business value: a primitive with its invariant, read as `.root` | you | `root: T = Field(gt=..., min_length=..., pattern=...)` |
| `Setting[T]` | one deployment value: address, credential, limit; lenient, because the environment is text | the deployment | `root: T` with its constraint |
| `Value` | a composite part with no standing of its own | you | your classes |
| `Request` | what arrives on a route | your contract | your classes; `tuple[E, ...]` for several |
| `Record` | what a party says, read by alias only | the party | your classes; `Field(alias=...)` per party name, or `alias_generator=to_camel` on a subclass for the whole party; `AliasPath` for a nested value |
| `Fact` | what the business concludes | you | the request, records, prior facts, values, produced scalars, an element |
| `Action[P, T]` | what the business asks party `P`, hearing `T` | you | the fact that intends it; `sends` and `resource` as properties the library kind declares |
| `Reply[F]` | what the caller receives: the fact `F` as `of`, never serialized, and computed fields that are its words | your contract | none |
| `Connection` | a party as the deployment names it; comes from a library kind, which opens and closes it | the deployment | `Setting` subclasses |
| `Route[Q, A]` | one thing the program does; the class name is its name | your contract | none |
| `Config` | the deployment, from the environment and `.env`; nested names joined with `__` | the deployment | one `Connection` per party, one `Setting` per value |

Ready-made: `Instant` and `Identity` construct themselves when declared on a fact; `Duration` is a positive `timedelta`. A `StrEnum` subclass is a closed word list.

## The five shapes

1. A field annotated with one of your classes. Never a bare primitive and never `None`: a primitive carries no rule, and an absence is a class.
2. A `Field(...)` constraint on a `Scalar` or `Setting` root: `gt`, `ge`, `le`, `min_length`, `max_length`, `pattern`.
3. A union `A | B` where a choice is held. Pydantic constructs the member whose constraints hold; write members so at most one can.
4. A tuple `tuple[T, ...]` for several of one thing. On a request it is where elements come from; on a fact it collects.
5. A `@computed_field` for what a thing knows from what it holds. Type it as the class it produces.

## A rule is a type

Put the rule where the value is born, as a constrained `Scalar`:

```python
class Quantity(Scalar[int]):
    """How many of a product an order asks for."""
    root: int = Field(gt=0)
```

`Quantity(0)` raises `ValidationError`. Nothing downstream rechecks it, because nothing downstream can be handed a `Quantity` that is not one.

A rule that decides between outcomes is two scalars with disjoint constraints and two facts that hold them. A derived value gets its class from a computed field typed as the union, returning the root of a `Scalar` over that union, so Pydantic chooses:

```python
class LargeAmount(Scalar[Decimal]):
    root: Decimal = Field(gt=100)

class SmallAmount(Scalar[Decimal]):
    root: Decimal = Field(gt=0, le=100)

class Priced(Scalar[LargeAmount | SmallAmount]):
    """An amount, large or small; Pydantic decides which at construction."""

class Placed(Fact):
    order: PlaceOrder
    price: Price

    @computed_field
    @property
    def amount(self) -> LargeAmount | SmallAmount:
        return Priced(self.price.amount.root * self.order.quantity.root).root

class Discounted(Fact):
    placed: Placed
    amount: LargeAmount

class FullPrice(Fact):
    placed: Placed
    amount: SmallAmount

class Charge(Post[Payments, Payment, Charged]):
    priced: Discounted | FullPrice
```

The engine reads `Placed.amount` as what `Placed` produces. For 150 it produces a `LargeAmount`, so `Discounted` constructs and `FullPrice` is skipped. You wrote no `if` and no validator, and the checker verified every reference.

## Several of one thing

Write `tuple[E, ...]` on the request, hold `E` on the per-element classes, and `tuple[X, ...]` on the fact that collects:

```python
class PlaceOrder(Request):
    lines: tuple[Line, ...]

class Charge(Post[Payments, Payment, Charged]):
    line: Line

class LinePaid(Fact):
    line: Line
    charged: Charged

class Paid(Fact):
    order: PlaceOrder
    lines: tuple[LinePaid, ...]
```

`Line` is an element because the request holds it as a tuple. `Charge` and `LinePaid` exist once per line; `Paid` exists once and receives every `LinePaid` in order. The engine performs every line's `Charge` together. A reply's fact exists once per run, so it collects; it never holds an element directly.

## The loop

Start from the route and work backward to the parties. Each step writes one class, and `just check` names the next.

1. Write the route: `class Checkout(Route[PlaceOrder, OrderPaid])`. Write `PlaceOrder` with the fields the caller sends and a docstring under each. Write `class OrderPaid(Reply[Paid])` with a computed field for each value the caller gets, reading `self.of`.
2. Write the fact the reply is made from: `Paid`.
3. For each fact, state what it is and what values it can have, then write its fields. Each field is the request, a prior fact, a record, a value, a scalar a computed field produces, or an element. Write the ones that do not exist. Repeat until every field bottoms out.
4. When a field is a primitive, ask what values the business has for it and write the `Scalar` with that constraint before finishing the fact. When a rule decides between outcomes, write the two scalars, the `Scalar` over their union, the computed field, and the two facts.
5. For each record, write the action that hears it, with `sends` and `resource`, and the connection it is toward as a library kind's subclass with `Setting` fields.
6. Write the config: one field per connection.
7. Register the program and run a route from the shell. Fix the class `just check` or the startup check names and run again.

For a change, start at step 2 with the reply that changes or step 3 with the fact that gains a field. Add classes; there is no function to edit.

## Run it

In the program's `pyproject.toml`:

```toml
[project.entry-points."type_construction.programs"]
shop = "shop"

[project.scripts]
shop = "type_construction.cli:main"
```

The entry's name is the command; its value is the module holding the routes and the config. Then:

```
uv run shop --help                      # every route with its docstring; every variable the config reads
uv run shop checkout --help             # every field of PlaceOrder with its docstring and its constraint
uv run shop checkout --sku tea --quantity 3 --ship-to.city Boston --tags gift --tags rush
```

A `Value` field is dotted; a tuple repeats; a tuple of values takes one JSON object per repeat; a `StrEnum` lists its choices. Connections come from the environment or `.env`: `PAYMENTS__URL`, `PAYMENTS__KEY`. A value outside a constraint exits 1 with the field named. The HTTP server serves the same routes from the same classes with the same descriptions in its OpenAPI document; choosing one or both changes no class.

## What the engine does with your classes

The contract. You rely on it; you never implement any of it.

- **At startup, the proof.** Reads each route's `Q` and `A`, the reply's `F`, each action's `P` and `T`, every field annotation and every computed field's return type. Refuses the program, naming every fault at once in your class names: a record no action hears or two hear; a class no computed field produces or two produce; a field naming a class nothing produces; a party the config holds zero or two times; a cycle; a reply's fact that exists per element; a tuple collecting a class that exists once.
- **Receive.** An HTTP body is validated strict as `Q` in JSON mode. A command line is validated leniently from text. Your classes stay strict in code.
- **Construct.** Each class is `model_validate`d from the instances its fields name, in the order the annotations require. A union member that refuses is skipped. A per-element class is constructed once per element.
- **Act.** When an action's fields exist, `perform` runs through its library kind and the response is validated as `T`. Actions that need nothing from each other run together.
- **Answer.** `A(of=F)` is constructed and its computed fields serialized.
- **Lifecycle.** Every connection is opened once at startup and closed once at shutdown.
- **Observe.** Every answer is a span named for the route, with one child span per action carrying the party's and the record's class names. No contents are recorded. The deployment chooses the exporter.
- **Fail.** A `ValidationError` or a client's exception propagates to the caller. A party's stated refusal is a `Record` in a union, not an exception.

## Questions developers ask

**Where does the logic go?** In types that only construct for the values the rule allows. See "A rule is a type": the discount is two scalars, a `Scalar` over their union, a computed field, and two facts.

**How is the order of operations determined?** By `model_fields`. `Paid` holds `Charged`; `Charged` is the `T` of `Charge`; `Charge` holds `Placed`; `Placed` holds `Price`; `Price` is the `T` of `Quote`. "Reserve before charge" means `Charge` holds `Reserved`.

**Where does state live?** In the current fact of a context. `Cart` holds the previous `Cart` and the arrival that changed it. This version serves one request per context.

**A declined card is not an error.** It is a record the party sends:

```python
class Declined(Record):
    reason: DeclineReason

class Charge(Post[Payments, Payment, Charged | Declined]): ...

class Paid(Fact):
    placed: Placed
    charged: Charged

class Refused(Fact):
    placed: Placed
    declined: Declined

class Checkout(Route[PlaceOrder, OrderPaid | OrderDeclined]): ...
```

The response validates as `Charged | Declined`; the fact holding the one that arrived constructs; its reply returns 200. A transport error returns 502.

**Performance.** One pydantic-core construction per class per request, the proof once at startup, clients opened once. Measure with `pytest-benchmark`.

**Debugging.** `ValidationError` carries `loc`, the field path, and `input`. The proof reports faults before a port is bound. The trace shows the route and each party call as spans named by your classes.

**Databases.** A library kind, the same shape as HTTP: a `Connection` with `Setting` fields, an `Action` with `statement` as a property, a `Record` for the rows. `perform` executes and validates the result set as `T`.

**Collections.** See "Several of one thing". The tuple on the request is the fan-out; the tuple on the fact is the fan-in; there is no loop.

**Escape hatches.** One: `perform` in a library kind, where Python calls a client. Anything else you cannot express is a missing class or a missing library kind.

**Why not FastAPI plus Pydantic?** FastAPI validates the request and response models; the handler between them is unchecked Python. Here the middle is classes: basedpyright checks every reference, the proof verifies the graph, Pydantic constructs the whole thing, and the trace comes for free.

## What you never write

- A function or a method on a page. Write a class, a `@property` the library kind declared, or a `@computed_field`.
- A `model_validator` or `field_validator`. Write the `Scalar` constraint, or the two scalars and the union.
- An `if`, a loop, a `try`, a `gather`. Write a union, a tuple, and let `ValidationError` propagate.
- A field typed `str`, `int`, `Decimal`, `datetime`, or `None`. Write the `Scalar`, and a class for the absent case.
- A log line. The engine's spans carry your class names.
- A class or field that exists for the engine: an id it reads, a status it checks, a tag the party did not send.
- A second copy of anything: a schema document, a mapper between an API model and a domain model, a list of your classes.

## Done

`just check` is green: the smell check on the program, basedpyright strict, and the run of each route from the shell against the product's acceptance rows.

## Not built yet

The HTTP library kind, `Http`, `Keyed`, `Post`, `Get`, and the HTTP server; a SQL kind; the generated reference; contexts that persist across requests. The world, the engine and the command line exist and type-check. The decisions are in `docs/decisions/`; the remaining work is `TODO.md`.
