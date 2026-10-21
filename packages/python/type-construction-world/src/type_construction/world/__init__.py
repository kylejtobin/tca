"""The classes a developer writes an application with.

An application is a module of subclasses of the classes below, and nothing else.
There are no functions, handlers, validators or steps. Constructing the classes is
running the program, and ``pydantic.ValidationError`` is the only failure path.

Why these classes are enough: an application is data, control flow, computation and I/O.

- Data: a field is a product, a union ``A | B`` is a sum, ``tuple[T, ...]`` is
  repetition, ``Scalar`` is a primitive with an invariant, a ``StrEnum`` subclass is an
  enumeration, ``Value`` is a composite part. Those are the algebraic data types.
- Control flow: a field is a sequence (``Paid`` holds ``Charged``, so ``Charged``
  exists first); a union is a branch; a tuple is iteration; a fact holding the
  previous fact is accumulation; a constraint on a ``Scalar`` or the choice of a
  union member is a rule.
- Computation: a derived value is a derivation kind, ``Times`` or ``Sum``, declared
  with its operands; a rule over several values is a relation kind, ``AtMost``,
  ``Beyond``, ``Between`` or ``Equal``, whose refusal is one outcome and whose
  construction is the other; a choice among elements is a selection kind, ``Least``,
  ``Greatest``, ``First`` or ``Only``. A program declares each as a subclass with its
  own classes as the parameters, and writes no expression.
- I/O: ``Request`` arrives on a ``Route``; ``Record`` is what a party says;
  ``Action`` asks a ``Connection`` and hears a ``Record``; ``Reply`` leaves.
  A library kind per transport (HTTP first) subclasses ``Connection`` and
  ``Action`` and carries the one piece of Python that calls a client.
- Deployment: ``Config`` holds the connections and settings from the environment;
  each value the deployment sets is a ``Setting``, a lenient root, because the
  environment is text.

Five shapes are used to write them: a field annotated with one of your classes,
a ``Field(...)`` constraint, a union, a tuple, and a ``@computed_field``.

The engine constructs your classes as their fields become fillable: each pass asks
Pydantic for every class not yet constructed, from the instances its fields name, and
a class whose fields are still missing waits for the next pass. It deserializes the
request, performs each action and deserializes its response, serializes the reply, and
opens and closes clients. It adds no class and holds no state. A class or field
written for the engine's sake is a defect.

Every configuration here is strict: no coercion, no undeclared fields, frozen
instances, defaults validated. A value the business does not have has no type.
Code constructs in Python mode, where ``Quantity("3")`` is refused. Input from
the world is validated at the edge in the mode the edge needs: an HTTP body with
``model_validate_json``, where ``3`` constructs ``Quantity``; a command line with
``model_validate(tree, strict=False)``, where every leaf is text and ``"3"``
constructs ``Quantity``; the environment through ``Setting`` roots. The classes
stay strict; the call chooses the mode.

The interface is defined once. ``Route[Q, A]`` with the fields and docstrings on
``Q`` and ``A`` is read by the command line, which renders options and help from
``Q``'s JSON schema, and by HTTP (FastAPI), which derives the request body, the
response schema and the OpenAPI document from the same classes. A docstring under
a field is its description in both.

Example, a shop that prices an order and charges for it::

    class Quantity(Scalar[int]):
        root: int = Field(gt=0)

    class PlaceOrder(Request):
        sku: Sku
        quantity: Quantity

    class Price(Record):
        amount: Amount

    class Quote(Get[Catalog, Price]):
        order: PlaceOrder

    class Placed(Fact):
        order: PlaceOrder
        price: Price

    class Charge(Post[Payments, Payment, Charged]):
        placed: Placed

    class Paid(Fact):
        placed: Placed
        charged: Charged

    class OrderPaid(Reply[Paid]):
        @computed_field
        @property
        def charge(self) -> ChargeId:
            return self.of.charged.charge

    class Checkout(Route[PlaceOrder, OrderPaid]): ...
"""

from abc import abstractmethod
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from functools import partial
from typing import Generic, LiteralString, Self, TypeVar, override
from uuid import UUID, uuid4

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, RootModel, model_validator
from pydantic_core import PydanticCustomError
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = [
    "Action",
    "AtMost",
    "Between",
    "Beyond",
    "Config",
    "Connection",
    "Duration",
    "Equal",
    "Fact",
    "First",
    "Greatest",
    "Identity",
    "Instant",
    "Least",
    "Measure",
    "Only",
    "Record",
    "Reply",
    "Request",
    "Route",
    "Scalar",
    "Setting",
    "Sum",
    "Times",
    "Value",
]

ROOT = ConfigDict(frozen=True, strict=True, validate_default=True)
"""Configuration for a class over one primitive: strict, frozen, defaults validated."""

PRODUCT = ConfigDict(
    frozen=True,
    strict=True,
    extra="forbid",
    validate_default=True,
    use_attribute_docstrings=True,
)
"""Configuration for a class of fields: strict, frozen, no undeclared fields, defaults validated.

``use_attribute_docstrings`` makes a docstring written under a field its description,
which the command line shows as help text and the OpenAPI document shows on the property.
"""


class Scalar[T](RootModel[T]):
    """One primitive with an invariant.

    Subclass it with the primitive and the constraint, and use the subclass as a
    field type everywhere the value appears. A field is never typed as a bare
    primitive, because a bare primitive carries no rule and no name.

    A rule on a value is a ``Scalar`` subclass whose constraint refuses the values
    the business does not have::

        class Quantity(Scalar[int]):
            root: int = Field(gt=0)

        class LargeAmount(Scalar[Decimal]):
            root: Decimal = Field(gt=100)

    The value is read as ``.root``. ``Quantity(0)`` raises ``ValidationError``.
    """

    model_config = ROOT


SETTING = ConfigDict(frozen=True, validate_default=True)
"""Configuration for a value the deployment sets: frozen, defaults validated, lenient, because it
arrives as text from the environment and pydantic-settings validates it in Python mode."""


class Setting[T](RootModel[T]):
    """One value the deployment sets: an address, a credential, a limit.

    Subclass it with the primitive and the constraint, and use the subclass as a
    field type on a ``Connection`` or a ``Config``. It is read from the environment,
    where every value is text, so it accepts text and constructs the primitive; its
    constraint still applies::

        class Retries(Setting[int]):
            root: int = Field(ge=0)

    A business value is a ``Scalar``, which is strict; a deployment value is a
    ``Setting``. Neither is written as the other.
    """

    model_config = SETTING


class Instant(RootModel[AwareDatetime]):
    """The moment a thing was constructed.

    Declare it as a field on a ``Fact`` that concludes at a moment. It constructs
    itself when the fact is constructed; nothing supplies it::

        class Placed(Fact):
            order: PlaceOrder
            at: Instant
    """

    model_config = ROOT
    root: AwareDatetime = Field(
        default_factory=partial(datetime.now, UTC),
        description="A timezone-aware datetime; defaults to now in UTC at construction.",
    )


class Identity(RootModel[UUID]):
    """What distinguishes one thing from another of the same class.

    Declare it as a field on a ``Fact`` that identifies a thing. It constructs
    itself when the fact is constructed; nothing supplies it. Two facts never
    share one::

        class Placed(Fact):
            order: PlaceOrder
            id: Identity
    """

    model_config = ROOT
    root: UUID = Field(
        default_factory=uuid4,
        description="A UUID; defaults to a fresh UUID4 at construction.",
    )


class Duration(RootModel[timedelta]):
    """A length of time, more than none."""

    model_config = ROOT
    root: timedelta = Field(gt=timedelta(0), description="A positive timedelta.")


class Value(BaseModel):
    """A composite part with no standing of its own.

    Subclass it for a thing that is held by other things and is nothing by
    itself: an address, a line of an order, a money amount with its currency.
    Its fields are typed as your classes. A whole that knows something about its
    elements is a ``Value`` holding a tuple with a ``@computed_field``::

        class Lines(Value):
            lines: tuple[Line, ...]

            @computed_field
            @property
            def total(self) -> Amount: ...
    """

    model_config = PRODUCT


class Request(BaseModel):
    """What arrives on a route.

    Subclass it with the fields the caller sends, each typed as one of your
    classes. The engine deserializes the request body as this class; a body that
    does not construct is refused with ``ValidationError`` before anything runs.
    Owned by this program's contract.
    """

    model_config = PRODUCT


class Record(BaseModel):
    """What an external party says.

    Subclass it with the fields this program reads from the party's response,
    under the party's names as aliases::

        class Charged(Record):
            charge: ChargeId = Field(alias="id")

    A party's response is deserialized as the ``Record`` an ``Action`` hears,
    by alias only, Pydantic's default: ``{"id": "c1"}`` constructs and ``{"charge": "c1"}``
    is refused. A field the party sends that is not declared is refused. A test
    plays the party with the alias, ``Charged(id=ChargeId("c1"))``.

    A party that names everything in one convention gets one subclass with an
    ``alias_generator`` and no per-field alias::

        class Stripe(Record):
            model_config = ConfigDict(alias_generator=to_camel)

    A value nested in the party's payload is read with ``AliasPath`` and no
    wrapper class::

        amount: Amount = Field(validation_alias=AliasPath("data", "amount", "value"))

    A party's stated refusal is a ``Record`` too, heard as one member of a union:
    ``Post[Payments, Payment, Charged | Declined]``. When the party sends a tag,
    each record declares it as a ``Literal`` field and the union is
    ``Annotated[Charged | Declined, Field(discriminator="status")]``. A party
    that does not answer is not a ``Record``; the client's exception propagates.
    """

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        extra="forbid",
        validate_default=True,
        use_attribute_docstrings=True,
        serialize_by_alias=True,
    )


class Fact(BaseModel):
    """What the business concludes.

    Subclass it with fields typed as the things the conclusion is made from: the
    request, a record a party said, a prior fact, a ``Value``. The fields are
    the fact's dependencies; the engine constructs the fact once every field's
    class exists. What the fact knows from what it holds is a ``@computed_field``.

    A choice between two conclusions is two ``Fact`` subclasses whose fields
    differ in a constrained ``Scalar`` that a computed field produced, written as
    a union where they are held. The computed field returns the root of a
    ``Scalar`` over the union of the constrained scalars, so Pydantic chooses::

        class Priced(Scalar[LargeAmount | SmallAmount]): ...

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

    The engine reads what each computed field produces and constructs the fact
    whose need was produced; the other is skipped.

    State over time is a fact holding the previous fact. No method, validator or
    branch is written on a fact.
    """

    model_config = PRODUCT


class Measure(Fact):
    """A derived value: a fact whose ``root`` the framework computes from what it holds.

    A program never computes a value. It declares the value's class as a subclass of a
    derivation kind, ``Times`` or ``Sum``, with the operands as the parameters, and reads
    the result as ``.root``, as it reads a ``Scalar``::

        class LineTotal(Times[UnitPrice, Quantity]): ...

    The engine constructs a derivation when its operands exist, like any fact. An operand
    is a scalar the run holds, which is one a request, a record or a value carries, or
    another derivation. A derivation is itself an operand of a relation, a selection or a
    further derivation.
    """

    @property
    @abstractmethod
    def root(self) -> Decimal:
        """The derived value, exact: every operand is read as a ``Decimal``."""


type Numeric = Scalar[Decimal] | Scalar[int] | Measure
"""What a derivation, a relation or a selection operates on: a scalar over a number, or a
derived value."""


def refused(message: LiteralString, value: BaseModel, bound: BaseModel) -> PydanticCustomError:
    """The ``relation`` refusal a relation kind raises when it does not hold, naming the two
    operands' classes. The engine reads a ``relation`` refusal as the fact not existing, so a
    union of the facts that hold each outcome is the choice."""
    return PydanticCustomError(
        "relation", message, {"value": type(value).__name__, "bound": type(bound).__name__}
    )


class Times[A: Numeric, B: Numeric](Measure):
    """The product of two values.

    ::

        class LineTotal(Times[UnitPrice, Quantity]): ...

    A constant factor is a scalar with a default, given as the field's default on the
    subclass, so nothing has to carry it::

        class Rate(Scalar[Decimal]):
            root: Decimal = Decimal("0.9")

        class Reduced(Times[LineTotal, Rate]):
            right: Rate = Rate()
    """

    left: A
    """The first factor."""
    right: B
    """The second factor."""

    @property
    @override
    def root(self) -> Decimal:
        return Decimal(self.left.root) * Decimal(self.right.root)


class Sum[E: Numeric](Measure):
    """The sum of every element's value.

    The elements are what a child run produced once per element, collected in order::

        class OrderTotal(Sum[LinePaid]): ...
    """

    of: tuple[E, ...]
    """The values summed, in element order; none sums to zero."""

    @property
    @override
    def root(self) -> Decimal:
        return sum((Decimal(e.root) for e in self.of), Decimal(0))


class AtMost[A: Numeric, B: Numeric](Fact):
    """A relation between two values: ``value`` is at most ``bound``.

    A rule that compares two values is declared as a relation kind with the two values as
    its parameters, and each outcome is the fact that holds the relation that makes it
    true::

        class Small(AtMost[LineTotal, Threshold]): ...
        class Large(Beyond[LineTotal, Threshold]): ...

        class FullPrice(Fact):
            line: Line
            tier: Small

        class Discounted(Fact):
            line: Line
            tier: Large

        class Charge(Post[Payments, Payment, Charged]):
            priced: Discounted | FullPrice

    The relation that holds constructs, and the one that does not refuses with ``relation``,
    which the engine reads as the fact not existing; so exactly one of ``Discounted`` and
    ``FullPrice`` exists, and the union is the choice. ``AtMost`` and ``Beyond`` over the
    same two operands are complements, and the proof reads them as disjoint. A bound that is
    a business constant is a scalar with a default, given as the field's default on the
    subclass::

        class Threshold(Scalar[Decimal]):
            root: Decimal = Decimal(100)

        class Small(AtMost[LineTotal, Threshold]):
            bound: Threshold = Threshold()

    At startup the proof reads the constraints on both operands and refuses a relation that
    can never hold, or can never refuse.
    """

    value: A
    """The value the relation is about."""
    bound: B
    """What the value is compared with."""

    @model_validator(mode="after")
    def holds(self) -> Self:
        """Refuse with ``relation`` when the value exceeds the bound."""
        if Decimal(self.value.root) > Decimal(self.bound.root):
            refusal = refused("{value} exceeds {bound}", self.value, self.bound)
            raise refusal
        return self


class Beyond[A: Numeric, B: Numeric](Fact):
    """A relation between two values: ``value`` is beyond ``bound``. The complement of
    ``AtMost`` over the same two operands; see ``AtMost`` for how a rule is written with the
    two."""

    value: A
    """The value the relation is about."""
    bound: B
    """What the value is compared with."""

    @model_validator(mode="after")
    def holds(self) -> Self:
        """Refuse with ``relation`` when the value does not exceed the bound."""
        if Decimal(self.value.root) <= Decimal(self.bound.root):
            refusal = refused("{value} is within {bound}", self.value, self.bound)
            raise refusal
        return self


class Between[A: Numeric, L: Numeric, U: Numeric](Fact):
    """A relation among three values: ``value`` is at least ``lower`` and at most ``upper``.

    ::

        class Eligible(Between[Age, MinimumAge, MaximumAge]): ...

    Its complement is the union of the two relations outside it: ``Beyond[U, A]`` for a
    value under the lower bound, written with the operands reversed, and ``Beyond[A, U]``
    for one over the upper.
    """

    value: A
    """The value the relation is about."""
    lower: L
    """The least the value may be."""
    upper: U
    """The most the value may be."""

    @model_validator(mode="after")
    def holds(self) -> Self:
        """Refuse with ``relation`` when the value is under the lower bound or over the
        upper."""
        if Decimal(self.value.root) < Decimal(self.lower.root):
            refusal = refused("{value} is under {bound}", self.value, self.lower)
            raise refusal
        if Decimal(self.value.root) > Decimal(self.upper.root):
            refusal = refused("{value} is over {bound}", self.value, self.upper)
            raise refusal
        return self


class Equal[A: Numeric, B: Numeric](Fact):
    """A relation between two values: ``value`` equals ``bound``, compared exactly.

    ::

        class Settled(Equal[AmountPaid, AmountDue]): ...
    """

    value: A
    """The value the relation is about."""
    bound: B
    """What the value must equal."""

    @model_validator(mode="after")
    def holds(self) -> Self:
        """Refuse with ``relation`` when the two values differ."""
        if Decimal(self.value.root) != Decimal(self.bound.root):
            refusal = refused("{value} differs from {bound}", self.value, self.bound)
            raise refusal
        return self


class Least[E: Numeric](Fact):
    """The element whose value is least.

    A choice among elements is declared as a selection kind with the element class as its
    parameter. The engine collects the elements a child run produced, and ``chosen`` is the
    one selected::

        class Cheapest(Least[LineTotal]): ...

    Ties go to the earliest element.
    """

    of: tuple[E, ...] = Field(min_length=1)
    """The elements chosen among, in element order; at least one."""

    @property
    def chosen(self) -> E:
        """The element whose value is least."""
        return min(self.of, key=lambda e: Decimal(e.root))


class Greatest[E: Numeric](Fact):
    """The element whose value is greatest; see ``Least``. Ties go to the earliest element."""

    of: tuple[E, ...] = Field(min_length=1)
    """The elements chosen among, in element order; at least one."""

    @property
    def chosen(self) -> E:
        """The element whose value is greatest."""
        return max(self.of, key=lambda e: Decimal(e.root))


class First[E: BaseModel](Fact):
    """The first element, in element order; see ``Least``. Any element class, not only a
    numeric one."""

    of: tuple[E, ...] = Field(min_length=1)
    """The elements chosen among, in element order; at least one."""

    @property
    def chosen(self) -> E:
        """The first element."""
        return self.of[0]


class Only[E: BaseModel](Fact):
    """The one element, when there is exactly one.

    A rule that a collection holds a single thing. With more than one, or none, it refuses
    with ``relation``, which the engine reads as the fact not existing, so a fact holding
    ``Only[Quote]`` and one holding ``Several[Quote]`` are a choice on how many came back::

        class Sole(Only[Quote]): ...
    """

    of: tuple[E, ...]
    """The elements, in element order."""

    @property
    def chosen(self) -> E:
        """The one element."""
        return self.of[0]

    @model_validator(mode="after")
    def holds(self) -> Self:
        """Refuse with ``relation`` unless there is exactly one element."""
        if len(self.of) != 1:
            refusal = PydanticCustomError("relation", "{n} elements, not one", {"n": len(self.of)})
            raise refusal
        return self


class Connection(BaseModel):
    """A party as the deployment names it.

    Subclass a library kind's connection, such as ``Http`` or ``Keyed``, once per
    party. Its fields are ``Setting`` subclasses: address, credential, limits, read
    from the environment. A ``Config`` holds one field per connection.

    ``open`` and ``close`` are abstract: the library kind implements them, holding
    what it opened, a client, in a ``PrivateAttr``, outside validation and outside
    the frozen fields. The server kind calls ``open`` once for every connection at
    startup and ``close`` once at shutdown, through the engine's ``opened``. A
    connection with no library kind cannot be constructed.
    """

    model_config = PRODUCT

    @abstractmethod
    async def open(self) -> None:
        """Open what reaching the party needs, once, at startup."""

    @abstractmethod
    async def close(self) -> None:
        """Close what ``open`` opened, once, at shutdown."""


class Action[P: Connection, T: Record](BaseModel):
    """What the business asks party ``P``, hearing ``T``.

    Subclass a library kind's action, such as ``Post[P, S, T]`` or ``Get[P, T]``,
    with fields typed as the fact that intends the action. The library kind
    declares what the action sends and where as abstract properties, which the
    subclass implements as plain properties::

        class Charge(Post[Payments, Payment, Charged]):
            placed: Placed

            @property
            def sends(self) -> Payment:
                return Payment(amount=self.placed.amount)

            @property
            def resource(self) -> Resource:
                return Resource("/charges")

    The action holds its party as ``party``, the connection the deployment
    configured for ``P``; the engine fills it like any other field, from the
    config, so the action exists once the fact that intends it and the party
    both exist. Then the engine awaits ``perform``, and the library kind's
    ``perform`` sends through ``self.party`` and returns the record validated
    with ``T.model_validate_json``, or raises. ``perform`` is abstract: an action
    with no library kind cannot be constructed.
    """

    model_config = PRODUCT
    party: P
    """The connection this action goes through: the deployment's ``P``."""

    @abstractmethod
    async def perform(self) -> T:
        """Ask ``self.party`` and return what it said as ``T``; the library kind's verb."""


F_co = TypeVar("F_co", bound=Fact, covariant=True)
"""``Reply``'s fact, covariant: a ``Reply[Paid]`` is a ``Reply[Fact]``, so a route's bound
``Reply[Fact]`` admits every reply. Declared the old way because the new syntax infers
invariance for a field."""


class Reply(BaseModel, Generic[F_co]):
    """What the caller receives: the one fact ``F`` it is made from, and its words.

    Subclass it with the fact as its parameter and a ``@computed_field`` for each
    value the caller is told. The fact is held as ``of``, declared here with
    ``Field(exclude=True)``, so ``model_dump_json`` and the OpenAPI response schema
    carry the computed fields only; ``self.of`` is typed as ``F`` in code and is
    required at construction. A reply declares no fields of its own::

        class OrderPaid(Reply[Paid]):
            @computed_field
            @property
            def charge(self) -> ChargeId:
                return self.of.charged.charge

    A reply made from several facts holds the fact that holds them. Owned by this
    program's contract.
    """

    model_config = PRODUCT
    of: F_co = Field(
        exclude=True, description="The fact this reply is made from; never serialized."
    )


class Route[Q: Request, A: Reply[Fact]](BaseModel):
    """One thing the program does: receives ``Q`` and answers ``A``.

    Subclass it with the request and the reply, or a union of replies, as its
    parameters and no fields. The class name is the business's name for the
    route; the server library kind derives the address from it::

        class Checkout(Route[PlaceOrder, OrderPaid | OrderDeclined]): ...

    An instance is one answered request: ``request`` is what arrived and
    ``reply`` is what the program made of it. The engine constructs the route
    like any other class, once the reply exists, and that construction is the
    end of the run. At startup the engine checks that every class of the
    program can exist from some route's request and the deployment's
    connections.
    """

    model_config = PRODUCT
    request: Q
    """What arrived."""
    reply: A
    """What the program answered."""


class Config(BaseSettings):
    """The deployment: connections and settings, from the environment and ``.env``.

    Subclass it with one field per ``Connection`` and one ``Setting`` per value the
    deployment sets directly. Nested fields are read with a double underscore: ``PAYMENTS__URL``,
    ``PAYMENTS__KEY``. A ``.env`` file in the working directory is read with the
    same names. A missing or malformed variable fails at startup with the field
    named::

        class ShopConfig(Config):
            catalog: Catalog
            payments: Payments
    """

    model_config = SettingsConfigDict(
        frozen=True,
        strict=True,
        extra="forbid",
        validate_default=True,
        use_attribute_docstrings=True,
        env_nested_delimiter="__",
        env_file=".env",
    )
