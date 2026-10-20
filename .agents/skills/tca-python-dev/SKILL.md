---
name: tca-python-dev
description: "Type Construction Architecture for Python, the reference: what a program is, the rules, the kinds, the schema, and what the engine is. Use before writing, reviewing, or refactoring any Python in a TCA project, before the first class exists. The loop is tca-modeling."
---

# TCA Python Dev

TCA is a system developers build their architecture with: they write the things their world is made of as Pydantic types, and that list is the running application, proven before it runs, readable as the business, written reliably by a person or a model. The product is the modeling experience; the engine exists to make it true and never appear. The measure of every decision is whether a developer says less, says it once, and says only their world.

The engine is Pydantic. Its one mechanic is that constructing a type is the computation and refusal is the only control flow: a step is a type constructed from the prior fact and what arrived, a choice is a union whose members each refuse what they are not so Pydantic picks, a sequence is a tuple of those, and the whole run is one construction chaining into the next. The engine has no branch, no lookup and no check of its own because validation already is all three.

Code under this skill is written one way: by the loop in `tca-modeling`.

## MUST NOT

- You MUST NOT bend the developer's page to make the engine simple. Every `@computed_field id`, every `before: Count`, every `pause: Duration` on a fact, every `.text`, every `Literal` tag the party never sent is the engine's convenience paid for on the page.
- You MUST NOT treat a developer's model as a bag the engine fills by reflection and reads back by name. The models are the live program.
- You MUST NOT write the branch, the lookup, the flag or the extra field first and attach a type afterward.
- You MUST NOT add a kind, a parameter, a declaration or a mechanism because a program needed something, before asking which existing kind already says it.
- You MUST NOT resolve a disagreement between Pydantic and the type checker, or between the engine and the proof, by weakening a type, adding `Any`, `None`, `InstanceOf`, a default, a cast or an ignore.

## MUST

- Before any line, you MUST say what the thing is in the business, its valid states and its owner, and only then its kind.
- For every behavior you MUST find the shape that makes the right outcome the only thing Pydantic can construct, and you MUST let construction be the computation.
- You MUST measure every engine decision by one question: does the developer say less, say it once, and say only their world. A duplication on the page is an engine bug.
- You MUST make the thing the thing: a priced order prices, a charge charges, a reply is what happened seen from outside; the engine reads what the models are and adds nothing.
- Where one thing could be said two ways, you MUST choose one, make the other unwritable, and say which and why.
- You MUST ask what Pydantic and Python already do before writing anything of your own, and use it as they document it.
- You MUST stop the moment you reach for any of the above and return to the type.

## The kinds

A developer writes the things their world is made of as Pydantic types, and constructing those types is the program running. Construction has exactly these shapes, so these are the kinds:

| shape Pydantic constructs | kind |
|---|---|
| a root over one primitive | `Scalar`, and `Vocabulary` over a word list |
| a product of fields | a thing: `Fact`, `Value`, `Record`, `Request`, `Reply`, `Connection`, `Action`, `Config` |
| a union tried left to right, members refusing | `Ordered` |
| a tuple | `Many` |
| a validator that refuses | the invariant on any thing |
| a computed field | what a thing knows from what it holds |
| a generic parameter | what a kind declares: the party, what it says, the request, the replies |

Each kind: what it is in the business, its states, its owner, and the shape that forces it.

- **Fact.** What the business concludes when something arrives. States: constructed or refused. Owner: developer. Shape: fields are the one arrival and the one prior, bound by type; an `Instant` when it concludes at a moment and an `Identity` when it distinguishes a thing, which the engine fills; the refusal is one validator; what it knows is a computed field. Nothing else is a field.
- **Arrival.** What comes from outside. Owner: whoever says it. A `Request` on a route is owned by this program's contract. A `Record` is owned by another party, under its names. Nothing else arrives.
- **Reply.** What happened, seen from outside. Owner: this program's contract. Shape: fields bound by type from the facts the context walked.
- **Route.** One thing the program accepts and what it answers. Owner: this program's contract. Shape: parameters `Q`, `A`, and `P` for what it sends while working; one field, its name, because the business names it.
- **Connection.** A party as the deployment names it. Owner: deployment. Shape: fields only. How it is reached belongs to a library kind.
- **Action.** An intention toward a party. Owner: developer. States: constructed or refused. Shape: parameters are the party and what it says; fields are the fact that intends it; what it sends and where are computed fields found by type. The verb belongs to the library kind.
- **Config.** The deployment. Owner: deployment. Shape: fields are the connections and settings.
- **Scalar, Vocabulary, Value, Many, Ordered.** As the table.
- **Instant, Identity, Duration.** A moment, what distinguishes a thing, a length of time. Owner: the business, but the first two cannot be on a page as input before they exist, so the engine supplies them.
- **What the engine says.** Each is a party's answer where the engine is the party. `Clock` is the engine as a `Connection`, supplied like an `Instant`; a wait is an `Action[Clock, Elapsed]` whose computed field is the `Duration`, so `Elapsed` has no fields. A schedule says a moment came, and the fact that holds it declares its `Instant`, so `Tick` has no fields. A party that takes what was sent and says nothing: `Sent`, no fields. A party that did not answer: `Unreachable` holds what the library said, not which party, because the prior fact knows. A live context reads itself back before the party speaks: `Started[C]`, no fields, parameterized so a fact binds it by type. A parent holds every child's answer as one arrival: `Gathered[R]`. A child is started by an action toward this program as a party; its shape is derived at the first program with children.

## The engine

What no type can be, and so is the engine, in full: validating bytes at the edge as the declared type; constructing the next fact from the context's fact and the arrival; constructing an action's call from its parameters and fields, sending it, and validating the text as what the party says; supplying the moment and a fresh identity; holding each context's current fact and delivering arrivals one at a time in order; opening every connection once and closing it at stop; constructing the reply from the walk. Nothing else.

The procedure, in four named places and nowhere else: `deliver`, which holds each context's current `Context` and constructs `Next` for each arrival in order; `send`, which turns a `Call` into bytes through the library and validates the text as `T`; `open` and `close`, once each per connection; `serve`, the edge, which validates bytes as `Request` and writes `Answered.reply`.

The proof is the engine's things, constructed from the program before anything runs. For each fact and arrival it holds the one class that holds both, or their one `Ordered`. For each fact at rest it holds the one `Reply` its route answers. A program missing any of these is refused, every fault at once, in the developer's names. `deliver` constructs the class the proof holds; it never searches. The engine reads field annotations and generic parameters. It never reads a name.

## The schema

```python
# type_construction/world.py

ROOT = ConfigDict(frozen=True, strict=True, validate_default=True, revalidate_instances="never")
PRODUCT = ConfigDict(frozen=True, strict=True, extra="forbid", validate_default=True, revalidate_instances="never")


class Scalar[T](RootModel[T]):
    """One meaning over one primitive."""
    model_config = ROOT


class Vocabulary(StrEnum):
    """One meaning from a closed word list."""


class Instant(RootModel[AwareDatetime]):
    """The moment a fact was constructed; the engine supplies it."""
    model_config = ROOT


class Identity(RootModel[UUID]):
    """What distinguishes a thing; kept from an input, else the engine mints it."""
    model_config = ROOT


class Duration(RootModel[timedelta]):
    """A length of time, more than none."""
    model_config = ROOT
    root: timedelta = Field(gt=timedelta(0))


class Ordered[T](RootModel[T]):
    """Alternatives tried in the order written; the last cannot refuse."""
    model_config = ROOT
    root: Annotated[T, Field(union_mode="left_to_right")]


class Many[T](RootModel[tuple[T, ...]]):
    """Several of one thing, held whole."""
    model_config = ROOT


class Value(BaseModel):
    """A composite part with no standing of its own."""
    model_config = PRODUCT


class Record(BaseModel):
    """Another party's thing, under its names."""
    model_config = ConfigDict(**PRODUCT, validate_by_name=True, validate_by_alias=True, serialize_by_alias=True)


class Request(BaseModel):
    """What this program accepts on a route."""
    model_config = PRODUCT


class Reply(BaseModel):
    """What happened, seen from outside; each field bound by type from the facts walked."""
    model_config = PRODUCT


class Fact(BaseModel):
    """What the business concludes: the one arrival and the one prior it holds, by type."""
    model_config = PRODUCT


class Connection(BaseModel):
    """A party as the deployment names it: its fields, nothing else."""
    model_config = PRODUCT


class Clock(Connection):
    """The engine as the party that says time passed; the engine supplies it."""


class Action[P: Connection, T: Record](BaseModel):
    """An intention toward party `P`, which says `T`: holds the fact that intends it."""
    model_config = PRODUCT


class RouteName(Scalar[str]):
    """How the business names a route."""
    root: str = Field(min_length=1)


class Route[Q: Request, A: Reply, P: Reply = Reply](BaseModel):
    """Receives `Q`, answers one of `A`, sends each `P` while working; declared once by name."""
    model_config = PRODUCT
    name: RouteName


class Config(BaseSettings):
    """The deployment: its connections and settings, by path from the environment."""
    model_config = SettingsConfigDict(**PRODUCT, env_nested_delimiter="__")


class Failure(Scalar[str]):
    """What the library said when the party did not answer."""
    root: str = Field(min_length=1)


class Unreachable(Record):
    """The party did not answer."""
    failure: Failure


class Started[C: Connection](Record):
    """The program began listening to `C`."""


class Gathered[R: Reply](Record):
    """Every child answered."""
    replies: Many[R]


class Sent(Record):
    """The party took what was sent and says nothing."""


class Elapsed(Record):
    """The time asked for has passed."""


class Tick(Record):
    """A moment the schedule marks."""
```

```python
# type_construction_httpx/__init__.py — the library kind for a party reached over HTTP.

class Url(Scalar[HttpUrl]):
    """Where the party is."""


class Key(Scalar[SecretStr]):
    """The credential the business holds for the party."""
    root: SecretStr = Field(min_length=1)


class NoKey(Value):
    """The party asks for no credential."""


class Resource(Scalar[str]):
    """Where the party accepts a thing, as the party names it."""
    root: str = Field(min_length=1)


class Http(Connection):
    url: Url
    key: Key | NoKey


class Post[P: Http, T: Record](Action[P, T]):
    """Sends the one `Record` it concludes to the one `Resource` it concludes."""


class Get[P: Http, T: Record](Action[P, T]):
    """Asks the one `Resource` it concludes."""
```

```python
# type_construction/engine.py — the engine's own things, each constructed from the program.

class Context(BaseModel):
    """One context's walk so far; constructed anew with each fact."""
    model_config = PRODUCT
    walked: Many[Fact]


class Next(BaseModel):
    """The fact that follows: the one class holding both, constructed by Pydantic from them."""
    model_config = PRODUCT
    context: Context
    arrival: Request | Record
    fact: Fact


class Call[P: Connection, T: Record](BaseModel):
    """An action as its library kind sends it: constructed from the action's parameters and fields."""
    model_config = PRODUCT
    party: P
    action: Action[P, T]


class Answered(BaseModel):
    """A context at rest and its route's reply, constructed by type from the walk."""
    model_config = PRODUCT
    context: Context
    reply: Reply
```

## Decided

Each decision names what it forbids and what refutes it.

- A fact that concludes at a moment declares an `Instant`; one that distinguishes a thing declares an `Identity`. The engine fills both. Forbids a moment on every fact. Refuted when a program needs the moment of a fact that did not declare it.
- A wait is an `Action[Clock, Elapsed]`; its computed field is the `Duration`. Forbids a `Duration` on a fact. Refuted when a wait is not an intention.
- A child answers its parent only as `Gathered[R]`. A `Reply` never arrives. Forbids acting on each child as it lands. Refuted when a program needs that.
- `Record` forbids fields it did not declare. The declaration is what this program reads, not the party's schema. Refuted when a party may add fields without the program's consent.

## What each need becomes

| when the business needs | the developer writes |
|---|---|
| a step | a `Fact` holding the prior and the arrival |
| a choice on what arrived | two facts holding different arrivals |
| a choice on what a thing holds | an `Ordered` whose members refuse, the last unable to |
| a state | a class; the state is which class exists |
| an absence | a named member of a union, like `NoKey`, or a fact not yet constructed |
| a rule | one validator that refuses |
| what a thing knows | a computed field |
| several of one thing | `Many`, and a computed field for what the whole knows |
| an effect | an `Action` holding the fact that intends it |
| a party that did not answer | a fact holding `Unreachable` |
| a wait | an `Action[Clock, Elapsed]` |
| time, identity | an `Instant` or `Identity` field the engine supplies |

## A page

The first program. The first test constructs it.

```python
class Sku(Scalar[str]):
    root: str = Field(min_length=1)


class Quantity(Scalar[int]):
    root: int = Field(gt=0)


class Amount(Scalar[Decimal]):
    root: Decimal = Field(gt=0)


class ChargeId(Scalar[str]):
    root: str = Field(min_length=1)


class Payments(Http):
    """The payment party."""


class Payment(Record):
    """What the payment party accepts."""
    amount: Amount


class Charged(Record):
    """What the payment party says when it charged."""
    charge: ChargeId = Field(alias="id")


class PlaceOrder(Request):
    sku: Sku
    quantity: Quantity


class Placed(Fact):
    """An order the shop accepted."""
    order: PlaceOrder

    @computed_field
    @property
    def amount(self) -> Amount: ...


class Charge(Post[Payments, Charged]):
    """The shop charges for the order."""
    placed: Placed

    @computed_field
    @property
    def payment(self) -> Payment:
        return Payment(amount=self.placed.amount)

    @computed_field
    @property
    def resource(self) -> Resource:
        return Resource("/charges")


class Paid(Fact):
    """An order the party charged."""
    placed: Placed
    charged: Charged


class Unpaid(Fact):
    """An order the party could not be reached for."""
    placed: Placed
    unreachable: Unreachable


class OrderPaid(Reply):
    paid: Paid


class OrderUnpaid(Reply):
    unpaid: Unpaid


checkout = Route[PlaceOrder, OrderPaid | OrderUnpaid](name=RouteName("checkout"))


class ShopConfig(Config):
    payments: Payments
```

## A test

A test constructs a type, asserts that it constructs or raises `ValidationError`, and reads what it knows. The first test is the page: each class from its inputs, each refusal refused, and `serve` answering `checkout` with `OrderPaid` over a party that says `Charged` and `OrderUnpaid` over one that does not.

## Done

Run checks only as `just` declares them. Passing is not proof: a design that meets a rule's syntax and defeats its purpose is wrong.

## Beside this page

- The loop: `tca-modeling`. The list and its check: `tca-noun-list`. The scan for procedure: `smell-check`. Names: `naming-guidelines`.
