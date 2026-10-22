---
name: tca-python-dev
description: "How to build an application on Type Construction Architecture: the classes you subclass, the five shapes you write them with, how a rule, a derived value, a choice and a collection are written as declarations, the loop from route to parties, how to run the program, the engine's contract, and the questions developers ask answered with classes. Use before writing any application code in a TCA project."
---

# TCA Python Dev

You write an application as subclasses of the classes in `type_construction.world` and `StrEnum`, and nothing else. Constructing those classes is running the program. `ValidationError` is the only failure path. The engine reads your classes, proves them at startup, and runs them; you never call it, extend it, or write around it.

## Why these classes are enough

An application is data, control flow, computation, I/O and deployment. Each is one Pydantic construct the checker reads.

- **Data.** A field is a product. A union `A | B` is a sum. `tuple[T, ...]` is repetition. `Scalar` is a primitive with an invariant. A `StrEnum` subclass is an enumeration. `Value` is a composite part.
- **Control flow.** A field is a sequence: `Paid` holds `Charged`, so `Charged` exists first. A union is a branch. A tuple is iteration. A fact holding the previous fact is accumulation. A `Scalar` constraint is a rule.
- **Computation.** A derived value is a derivation kind declared with its operands. A rule over values is a relation kind whose refusal is the other outcome. A choice among elements is a selection kind. You declare each with your own classes as its parameters and write no expression.
- **I/O.** `Request` arrives on a `Route`. `Record` is what a party says. `Action` asks a `Connection` and hears a `Record`, or one of several. `Reply[F]` leaves, made from the fact `F`. A library kind per transport carries the only Python that calls a client.
- **Deployment.** `Config` holds the connections and settings; each value the deployment sets is a `Setting`.

There is no construct for a function, a handler, a validator, a loop, a step or a state machine. Each is one of the above written as procedure, and the smell check refuses it on a page.

## The classes

From `type_construction.world`. Every class is strict, frozen and forbids undeclared fields; a docstring under a field is its description everywhere the field is shown.

| class | what it is | owner | its fields |
|---|---|---|---|
| `Scalar[T]` | one business value: a primitive with its invariant, read as `.root`; with a default root, a constant that exists in every run | you | `root: T = Field(gt=..., min_length=..., pattern=...)` |
| `Setting[T]` | one deployment value: address, credential, limit; lenient, because the environment is text | the deployment | `root: T` with its constraint |
| `Value` | a composite part with no standing of its own; arrives inside a request or a record | you | your scalars and values |
| `Request` | what arrives on a route; a tuple field declares elements | your contract | your scalars, values and enumerations; `tuple[E, ...]` for several |
| `Record` | what a party says, read by alias only; a tuple field declares elements | the party | your classes; `Literal` tags; `Field(alias=...)` per party name, or `alias_generator=to_camel` on a subclass for the whole party; `AliasPath` for a nested value |
| `Fact` | what the business concludes | you | the request, records, prior facts, values, relations, derivations, selections, an element |
| `Action[P, T]` | what the business asks party `P`, hearing `T`, one record class or a union of them; the kind holds `party: P`, filled from the config | you | the fact that intends it; `sends` and `resource` as properties the library kind declares |
| `Reply[F]` | what the caller receives: the fact `F` as `of`, never serialized, and computed fields that are its words | your contract | none |
| `Connection` | a party as the deployment names it; comes from a library kind, which opens and closes it | the deployment | `Setting` subclasses |
| `Route[Q, A]` | one thing the program does; the class name is its name; the kind holds `request: Q` and `reply: A`, and an instance is one answered request | your contract | none |
| `Config` | the deployment, one per program, from the environment and `.env`; nested names joined with `__` | the deployment | one `Connection` per party, one `Setting` per value |

The computation kinds, each a `Fact` you subclass with your classes as the parameters and no fields of your own:

| kind | what it declares | read as |
|---|---|---|
| `Times[A, B]` | the product of two values | `.root`, a `Decimal` |
| `Sum[E]` | the sum of every element's value, zero for none | `.root` |
| `Under[A, B]`, `AtMost[A, B]`, `Equal[A, B]`, `AtLeast[A, B]`, `Beyond[A, B]`, `Differs[A, B]` | `value` is under, at most, equal to, at least, beyond, or other than `bound`; `Under` and `AtLeast`, `AtMost` and `Beyond`, `Equal` and `Differs` are complements | the fact that holds it |
| `Between[A, L, U]` | `value` is at least `lower` and at most `upper` | the fact that holds it |
| `Least[E]`, `Greatest[E]` | the element whose value is least, or greatest | `.chosen` |
| `First[E]` | the first element | `.chosen` |
| `Only[E]` | the one element, when there is exactly one | `.chosen` |

`A`, `B`, `L`, `U` and `E` are a `Scalar` over `Decimal` or `int`, or another derivation; the checker refuses anything else. Each kind declares its meaning once, as Pydantic reads it, and both construction and the proof read that one declaration: a relation is one comparison restricted to the orderings its `Literal` admits, a selection's shape is its tuple annotation, a derivation's root is computed at construction by its operation. Ready-made: `Instant` and `Identity` are fresh scalars the engine constructs for each holder; `Duration` is a positive `timedelta`. A `StrEnum` subclass is a closed word list.

## The five shapes

1. A field annotated with one of your classes. Never a bare primitive and never `None`: a primitive carries no rule, an absence is a class, and the proof refuses both.
2. A `Field(...)` constraint on a `Scalar` or `Setting` root: `gt`, `ge`, `le`, `min_length`, `max_length`, `pattern`.
3. A union `A | B` where a choice is held. Pydantic constructs the member that exists; write members a relation, a record or a selection tells apart, and the proof refuses a pair it cannot show exclusive.
4. A tuple `tuple[T, ...]` for several of one thing. On a request or a record it declares elements; on a fact it collects what exists once per element.
5. A subclass of a computation kind with your classes as its parameters. A `@computed_field` only on a reply, for a word the caller is told, reading fields and constructing a declared class.

## A rule is a type

Put a rule on one value where the value is born, as a constrained `Scalar`:

```python
class Quantity(Scalar[int]):
    """How many of a product an order asks for."""
    root: int = Field(gt=0)
```

`Quantity(0)` raises `ValidationError`. Nothing downstream rechecks it, because nothing downstream can be handed a `Quantity` that is not one.

A rule that compares values is a relation kind, and each outcome is the fact that holds the relation that makes it true:

```python
class Threshold(Scalar[Decimal]):
    """The line total above which a line is discounted."""
    root: Decimal = Decimal(100)

class Small(AtMost[LineTotal, Threshold]): ...

class Large(Beyond[LineTotal, Threshold]): ...

class FullPrice(Fact):
    line: Line
    tier: Small
    due: LineTotal

class Discounted(Fact):
    line: Line
    tier: Large
    due: Reduced

class Charge(Says[Payments, Charged]):
    priced: Discounted | FullPrice
```

For a line total of 7.50, `Small` constructs and `Large` refuses, so `FullPrice` exists and `Discounted` is never built; `Charge` holds whichever exists. You wrote no `if`, no expression and no validator. `Threshold` is a constant, a scalar with a default root, and exists in every run by being declared: nothing supplies it and nothing defaults it on a subclass. At startup the proof reads the bounds on both operands and refuses a relation that can never hold or never refuse, and reads the orderings `Small` and `Large` admit and proves `Discounted | FullPrice` exclusive.

## A derived value is declared

```python
class LineTotal(Times[UnitPrice, Quantity]):
    """What a line costs: its unit price times its quantity."""

class Reduced(Times[LineTotal, Rate]):
    """What a discounted line pays: its total at the rate."""
```

`LineTotal` constructs when a `UnitPrice` and a `Quantity` exist in its scope, and `.root` is their product, computed and validated at construction. `Rate` is a constant. The arithmetic lives once, on the kind, and the proof reads what the product can be from what its operands can be. A derivation is an operand of a relation, a selection or another derivation.

## Several of one thing

Write `tuple[E, ...]` on the request, hold `E` on the per-element classes, and `tuple[X, ...]` on the fact that collects:

```python
class PlaceOrder(Request):
    lines: tuple[Line, ...]

class Quote(Says[Catalog, Price]):
    line: Line

class LinePaid(Fact):
    priced: Discounted | FullPrice
    charged: Charged

class Paid(Fact):
    screened: Screened
    lines: tuple[LinePaid, ...]
    cheapest: Cheapest
```

`Line` is an element because the request holds it as a tuple. `Quote`, `LineTotal`, `Small`, `Large`, `Charge` and `LinePaid` exist once per line, in that line's scope; `Paid` exists once and receives every `LinePaid` in order. The engine performs every line's `Quote` together. A record a party says about a line may hold a tuple too; its elements get scopes under the line's, and a fact in the line's scope collects them. A reply's fact exists once per run, so it collects; it never holds an element directly.

## A choice among elements is declared

```python
class Cheapest(Least[LineTotal]):
    """The line that costs least."""
```

The engine collects every line's `LineTotal` and constructs `Cheapest` once; `self.of.cheapest.chosen` on the reply is the chosen one. A selection over no element refuses, the same way a relation refuses: a choice among nothing does not exist, so declare the outcome for none, or refuse an empty collection at the request with `Field(min_length=1)`. `Only[E]` is the shape `tuple[E]` and refuses unless there is exactly one element.

## A party that says no

A refusal the party states is a record, heard as one member of a union, and the fact that holds it is an outcome:

```python
class Clear(Record):
    status: Literal["clear"]

class Flagged(Record):
    status: Literal["flagged"]
    reason: Reason

class Screen(Says[Fraud, Clear | Flagged]):
    order: PlaceOrder

class Screened(Fact):
    order: PlaceOrder
    clear: Clear

class Refused(Fact):
    order: PlaceOrder
    flagged: Flagged

class Checkout(Route[PlaceOrder, OrderPaid | OrderRefused]): ...
```

The party's text validates as `Clear | Flagged`, told apart by the `Literal` each declares; the fact holding the one that arrived constructs; its reply is returned. An action performed on one branch only, the `Charge` that follows a clear screen, holds a premise that decides the branch, `Screened`, and the proof refuses one that would be performed whichever branch held. A transport error is the client's exception and propagates.

## The loop

Start from the route and work backward to the parties. Each step writes one class, and `just check` names the next.

1. Write the route: `class Checkout(Route[PlaceOrder, OrderPaid])`. Write `PlaceOrder` with the fields the caller sends and a docstring under each. Write `class OrderPaid(Reply[Paid])` with a computed field for each value the caller gets, reading `self.of`.
2. Write the fact the reply is made from: `Paid`.
3. For each fact, state what it is and what values it can have, then write its fields. Each field is the request, a prior fact, a record, a value, a relation, a derivation, a selection, or an element. Write the ones that do not exist. Repeat until every field bottoms out.
4. When a field is a primitive, ask what values the business has for it and write the `Scalar` with that constraint before finishing the fact. When a rule compares values, write the relation subclasses and the fact for each outcome. When a value is computed, write the derivation subclass. When one of several is chosen, write the selection subclass. When a value is a constant, write the scalar with its default root.
5. For each record, write the action that hears it, with `sends` and `resource`, and the connection it is toward as a library kind's subclass with `Setting` fields.
6. Write the config: one field per connection.
7. Register the program and run a route from the shell. Fix the class `just check` or the startup proof names and run again.

For a change, start at step 2 with the reply that changes or step 3 with the fact that gains a field. Add classes; there is no function to edit.

## Run it

In the program's `pyproject.toml`:

```toml
[project.entry-points."type_construction.programs"]
orders = "orders"

[project.scripts]
orders = "type_construction.cli:main"
```

The entry's name is the command; its value is the module holding the routes and the config. Then:

```
orders checkout --sku tea --quantity 3 --ship-to.city Boston --lines '{"sku": "tea", "quantity": 3}'
```

A route is a subcommand named from its class, `RequoteSku` as `requote-sku`. A scalar is one option, with its class name as the metavar, its docstring as help and its bounds after it; a `Value` field is dotted; a tuple repeats; a tuple of values takes one JSON object per repeat; a `StrEnum` lists its choices. `orders` alone lists the routes and the variables the deployment reads. Connections come from the environment or `.env`: `PAYMENTS__URL`, `PAYMENTS__KEY`. A program that does not prove, a request that does not construct, a run that stalls or a reply whose word refuses exits 1 with the class and the field named; an unknown route exits 2. The HTTP server, when built, serves the same routes from the same classes with the same descriptions in its OpenAPI document; choosing one or both changes no class.

## What the engine does with your classes

The contract. You rely on it; you never implement any of it.

- **At startup, the proof.** Places every class: the request, its scalars and values, the connections and the constants once per run; an element once per element of the request or record that declares it; a record where its hearer is; a scalar or value where its carrier is; every other class where its premises are, and one level above what it collects. Refuses the program, naming every fault at once in your class names, as one `ValidationError`: `missing`, a field no class fills; `cycle`, classes that hold each other; `twice`, a class with two sources, a scalar two carriers hold, a record two actions hear, a party the config holds twice; `unplaceable`, a class whose fields name two sibling elements; `collects`, a tuple over a class that is not one level down; `route`, a route whose reply would exist once per element; `unreached`, a class the reply of no route leads to; `unmodeled`, a bare primitive, an enumeration on a fact, `None`; `boundary`, a request that holds what does not arrive, a config that holds a business value; `config`, no one deployment; `ambiguous`, two union members not proven exclusive; `never`, a relation its operands' intervals make certain or impossible; `undiscriminated`, two records one action hears that no field tells apart; `undecided`, an action performed on one branch of a choice that holds nothing deciding it.
- **Receive.** An HTTP body is validated strict as `Q` in JSON mode. A command line is validated leniently from text. Your classes stay strict in code.
- **Construct.** Each pass asks Pydantic for every class of the route not yet in its scope whose premises are present, `model_validate` from the instances its fields name; a fresh scalar is constructed for the holder; a tuple field is every child scope's instance in element order, the empty tuple for no element, so a sum of nothing is zero and a choice among nothing refuses. A relation or a selection that refuses does not hold in that scope, and a union member that never holds is never built, so the holder's union is the choice. A request, a record and a value bring the scalars and values they hold into their scope. A pass that builds nothing ends the request naming each relation or selection that did not hold, with the ordering observed, leaving out one whose complement held.
- **Act.** An action constructs when its premises are present; then `perform` runs through its library kind and the response is validated as `T`, a union choosing its member, and the record enters the scope the action was built in, its elements fanning out under it. The actions of one pass run together in one task group; one client's exception cancels the others and propagates in an `ExceptionGroup`. The engine never retries, times out or compensates: those are the library kind's, and an idempotency key is a field on the action.
- **Answer.** The reply constructs from its fact, the route constructs from the request and the reply, and that is the end of the run; the reply's computed fields are serialized, and `model_dump` of the reply is the derivation of the answer.
- **Lifecycle.** Every connection is opened once at startup and closed once at shutdown; when one fails to open, those already opened are closed and the failure propagates.
- **Observe.** Every answer is a span named for the route, with one child span per action carrying the party's and the record's class names. No contents are recorded. The deployment chooses the exporter.
- **Fail.** A `ValidationError` propagates to the caller; a client's exception propagates in the pass's `ExceptionGroup`. A party's stated refusal is a `Record` in a union, not an exception.

## Questions developers ask

**Where does the logic go?** In types that only construct for the values the rule allows: a constrained `Scalar` for one value, a relation kind for a comparison, a derivation kind for a computed value, a selection kind for a choice among several. See the sections above.

**How is the order of operations determined?** It is not; it falls out of `model_fields`. `Charge` holds `Discounted | FullPrice`, so `Charge` cannot construct until one has; `FullPrice` holds `Small`, which holds `LineTotal`, which holds the `UnitPrice` the catalog's record carries. Each pass builds what can be built. "Reserve before charge" means `Charge` holds `Reserved`.

**Where does state live?** In the current fact of a context. `Cart` holds the previous `Cart` and the arrival that changed it. This version serves one request per context.

**Why does the proof say a class has two sources?** Because a scalar is named by its role: the catalog's `UnitPrice` and the reply's `OrderTotal`, never `Amount` on both. A scope holds one instance per class, and a fact that needs the value two carriers both hold holds the carrier.

**Why does the proof say my action is undecided?** Because it would be performed whichever branch of a choice held. Make the action from the premise that decides the branch: the charge holds the clear screen, not the order.

**Where does a constant go?** A scalar with a default root, held where it is compared. Nothing supplies it and nothing defaults it on a subclass.

**Performance.** One pydantic-core construction per class per scope, the proof once at startup, clients opened once.

**Debugging.** `ValidationError` carries `loc`, the field path, and `input`. The proof reports faults before a port is bound. A stall names the relation that refused and the ordering it saw. The trace shows the route and each party call as spans named by your classes.

**Databases.** A library kind, the same shape as HTTP: a `Connection` with `Setting` fields, an `Action` with `statement` as a property, a `Record` for the rows. `perform` executes and validates the result set as `T`.

**Escape hatches.** One: `perform` in a library kind, where Python calls a client. Anything else you cannot express is a missing class or a missing kind, and that is a defect in the framework.

**Why not FastAPI plus Pydantic?** FastAPI validates the request and response models; the handler between them is unchecked Python. Here the middle is classes: basedpyright checks every reference, the proof places and refuses the graph, Pydantic constructs the whole thing, and the trace comes for free.

## What you never write

- A function or a method on a page. Write a class, a `@property` the library kind declared, or a `@computed_field` on a reply.
- A `model_validator` or `field_validator`. Write the `Scalar` constraint, or the relation kind and the fact for each outcome.
- An `if`, a loop, a `try`, a `gather`, an arithmetic expression, `min` or `max`. Write a union, a tuple, a derivation, a relation, a selection, and let `ValidationError` propagate.
- A field typed `str`, `int`, `Decimal`, `datetime`, or `None`. Write the `Scalar`, and a class for the absent case.
- A default on a field so the engine has something: `bound: Threshold = Threshold()`. Write the constant's default root once, on the scalar.
- A log line. The engine's spans carry your class names.
- A class or field that exists for the engine: an id it reads, a status it checks, a tag the party did not send.
- A second copy of anything: a schema document, a mapper between an API model and a domain model, a list of your classes.

## Done

`just check` is green: the smell check on the program, basedpyright strict, and the run of each route from the shell against the product's acceptance rows.

## Not built

The HTTP library kind, `Http`, `Keyed`, `Post`, `Get`, and the HTTP server; a SQL kind; contexts that persist across requests; the pytest-bdd binding of the feature files. The world, the engine and the command line exist and type-check. The decisions are in `docs/decisions/`; the remaining work is `TODO.md`.
