"""The classes a developer writes an application with.

An application is a module of subclasses of the classes below, and nothing else. There are no
functions, handlers, validators or steps. Constructing the classes is running the program, and
``pydantic.ValidationError`` is the only failure path.

Why these classes are enough: an application is data, control flow, computation, I/O and
deployment, and each is one Pydantic construct.

- Data: a field is a product, a union ``A | B`` is a sum, ``tuple[T, ...]`` is repetition,
  ``Scalar`` is a primitive with an invariant, a ``StrEnum`` subclass is an enumeration,
  ``Value`` is a composite part. Those are the algebraic data types.
- Control flow: a field is a sequence (a fact holds the fact that came before it); a union is a
  branch; a tuple is iteration; a fact holding the previous fact is accumulation; a constraint
  on a ``Scalar`` or the choice of a union member is a rule.
- Computation: a derived value is a derivation kind, ``Times`` or ``Sum``; a rule over two values
  is a relation kind, ``Under``, ``AtMost``, ``Equal``, ``AtLeast``, ``Beyond`` or ``Differs``,
  or ``Between`` over three; a choice among elements is a selection kind, ``Least``,
  ``Greatest``, ``First`` or ``Only``. A program declares each as a subclass with its own
  classes as the parameters and writes no expression.
- I/O: ``Request`` arrives on a ``Route``; ``Record`` is what a party says; ``Action`` asks a
  ``Connection`` and hears a ``Record``; ``Reply`` leaves. A library kind per transport
  subclasses ``Connection`` and ``Action`` and carries the one piece of Python that calls a
  client.
- Deployment: ``Config`` holds the connections and settings from the environment; each value
  the deployment sets is a ``Setting``, a lenient root, because the environment is text.

Each kind declares its meaning once, as something Pydantic reads, and both construction and the
startup proof read that one declaration. A relation is the restriction of one shared comparison
to the outcomes it admits, written as a ``Literal`` type: construction computes the ordering of
its operands and Pydantic admits or refuses it, and the proof reads the admitted set. A
selection's shape is its tuple annotation: ``tuple[E]`` is exactly one and ``tuple[E, ...]``
with ``min_length=1`` is at least one. A derivation declares one operation, which computes its
root at construction and tells the proof what the root can be from what its operands can be.
A constant is a scalar with a default root. Nothing has a validator the proof cannot read.

Every configuration here is strict: no coercion, no undeclared fields, frozen instances,
defaults validated. A value the business does not have has no type. Code constructs in Python
mode, where ``Quantity("3")`` is refused. Input from the world is validated at the edge in the
mode the edge needs: an HTTP body with ``model_validate_json``, a command line with
``model_validate(tree, strict=False)``, the environment through ``Setting`` roots. The classes
stay strict; the call chooses the mode.
"""

from abc import abstractmethod
from collections.abc import Callable, Mapping
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from functools import partial, reduce
from operator import mul
from typing import TYPE_CHECKING, Annotated, Generic, Literal, NamedTuple, TypeIs, TypeVar
from uuid import UUID, uuid4

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, RootModel, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = [
    "Action",
    "AtLeast",
    "AtMost",
    "Between",
    "Beyond",
    "Compare",
    "Comparison",
    "Config",
    "Connection",
    "Derived",
    "Differs",
    "Duration",
    "Equal",
    "Fact",
    "First",
    "Greatest",
    "Identity",
    "Instant",
    "Interval",
    "Least",
    "Measure",
    "Numeric",
    "Only",
    "Ordering",
    "Primitive",
    "Record",
    "Relation",
    "Reply",
    "Request",
    "Route",
    "Scalar",
    "Selection",
    "Setting",
    "Sum",
    "Times",
    "Under",
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

``use_attribute_docstrings`` makes a docstring written under a field its description, which the
command line shows as help text and the OpenAPI document shows on the property.
"""

type Primitive = (
    str | int | float | bool | bytes | Decimal | datetime | date | time | timedelta | UUID | Enum
)
"""What a ``Scalar`` is over: one of Python's value types, or an enumeration."""


class Scalar[T: Primitive](RootModel[T]):
    """One primitive with an invariant.

    Subclass it with the primitive and the constraint, and use the subclass as a field type
    everywhere the value appears. A field is never typed as a bare primitive, because a bare
    primitive carries no rule and no name, and the proof refuses one::

        class Quantity(Scalar[int]):
            root: int = Field(gt=0)

    The value is read as ``.root``. ``Quantity(0)`` raises ``ValidationError``. A business
    constant is a scalar with a default root, and exists in every run by being declared::

        class Threshold(Scalar[Decimal]):
            root: Decimal = Decimal(100)
    """

    model_config = ROOT


SETTING = ConfigDict(frozen=True, validate_default=True)
"""Configuration for a value the deployment sets: frozen, defaults validated, lenient, because it
arrives as text from the environment and pydantic-settings validates it in Python mode."""


class Setting[T](RootModel[T]):
    """One value the deployment sets: an address, a credential, a limit.

    Subclass it with the primitive and the constraint, and use the subclass as a field type on
    a ``Connection`` or a ``Config``. It is read from the environment, where every value is
    text, so it accepts text and constructs the primitive; its constraint still applies::

        class Retries(Setting[int]):
            root: int = Field(ge=0)

    A business value is a ``Scalar``, which is strict; a deployment value is a ``Setting``.
    Neither is written as the other.
    """

    model_config = SETTING


class Instant(Scalar[AwareDatetime]):
    """The moment a thing was constructed.

    Declare it as a field on a ``Fact`` that concludes at a moment. It is fresh: the engine
    constructs one for each holder at the moment the holder is asked for, and nothing supplies
    it::

        class Placed(Fact):
            order: PlaceOrder
            at: Instant
    """

    root: AwareDatetime = Field(
        default_factory=partial(datetime.now, UTC),
        description="A timezone-aware datetime; now, in UTC, at construction.",
    )


class Identity(Scalar[UUID]):
    """What distinguishes one thing from another of the same class.

    Declare it as a field on a ``Fact`` that identifies a thing. It is fresh: the engine
    constructs one for each holder, and two holders never share one::

        class Placed(Fact):
            order: PlaceOrder
            id: Identity
    """

    root: UUID = Field(default_factory=uuid4, description="A UUID4, fresh at construction.")


class Duration(Scalar[timedelta]):
    """A length of time, more than none."""

    root: timedelta = Field(gt=timedelta(0), description="A positive timedelta.")


class Value(BaseModel):
    """A composite part with no standing of its own.

    Subclass it for a thing that is held by other things and is nothing by itself: an address,
    a line of an order, a money amount with its currency. Its fields are typed as your classes.
    A value arrives inside a request or a record, and brings the scalars and values it holds
    into the run with it::

        class Line(Value):
            sku: Sku
            quantity: Quantity
    """

    model_config = PRODUCT


class Request(BaseModel):
    """What arrives on a route.

    Subclass it with the fields the caller sends, each typed as one of your classes: scalars,
    values, enumerations, and tuples of them. A tuple field declares elements: each element gets
    a run of its own under the request's. The engine deserializes the request body as this
    class; a body that does not construct is refused with ``ValidationError`` before anything
    runs. Owned by this program's contract.
    """

    model_config = PRODUCT


class Record(BaseModel):
    """What an external party says.

    Subclass it with the fields this program reads from the party's response, under the party's
    names as aliases::

        class Charged(Record):
            charge: ChargeId = Field(alias="id")

    A party's response is deserialized as the ``Record`` an ``Action`` hears, by alias only,
    Pydantic's default: ``{"id": "c1"}`` constructs and ``{"charge": "c1"}`` is refused. A field
    the party sends that is not declared is refused. A test plays the party with the alias,
    ``Charged(id=ChargeId("c1"))``.

    A party that names everything in one convention gets one subclass with an
    ``alias_generator`` and no per-field alias::

        class Stripe(Record):
            model_config = ConfigDict(alias_generator=to_camel)

    A value nested in the party's payload is read with ``AliasPath`` and no wrapper class::

        amount: Amount = Field(validation_alias=AliasPath("data", "amount", "value"))

    A party's stated refusal is a ``Record`` too, heard as one member of a union:
    ``Post[Payments, Payment, Charged | Declined]``. The members are told apart by a
    ``Literal`` field each declares, ``status: Literal["succeeded"]`` and
    ``status: Literal["declined"]``, or by a key one requires and the other does not; the proof
    refuses a union of records it cannot tell apart. A tuple field on a record declares
    elements, each with a run of its own under the record's. A party that does not answer is
    not a ``Record``; the client's exception propagates.
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

    Subclass it with fields typed as the things the conclusion is made from: the request, a
    record a party said, a prior fact, a value, an element, a relation, a derivation, a
    selection. The fields are the fact's premises; the engine constructs the fact once every
    premise exists, in the run where they exist. What the fact knows from what it holds is a
    ``@computed_field`` that reads its fields and constructs a declared class; it computes
    nothing.

    A choice between two conclusions is two ``Fact`` subclasses, each holding the relation that
    makes it true, written as a union where the choice is held::

        class FullPrice(Fact):
            line: Line
            tier: Small

        class Discounted(Fact):
            line: Line
            tier: Large

        class Charge(Post[Payments, Payment, Charged]):
            priced: Discounted | FullPrice

    Exactly one of ``Small`` and ``Large`` constructs for a line, so exactly one conclusion
    exists, and the proof refuses a union whose members it cannot show exclusive. State over
    time is a fact holding the previous fact. No method, validator or branch is written on a
    fact.
    """

    model_config = PRODUCT


class Interval(NamedTuple):
    """What a numeric class can be: a lower and an upper bound, each a ``Decimal`` or ``None``
    for unbounded, and whether each is strict. The proof reads a scalar's interval from its
    ``Field`` bounds, a constant's from its default, and a derivation's from its operation."""

    low: Decimal | None = None
    """The least the value can be; ``None`` for no lower bound."""
    low_strict: bool = False
    """Whether the value is strictly above ``low``."""
    high: Decimal | None = None
    """The most the value can be; ``None`` for no upper bound."""
    high_strict: bool = False
    """Whether the value is strictly below ``high``."""


type Operand = Numeric | tuple[Numeric, ...]
"""What an operation reads from one operand field: a numeric, or a tuple of them."""


def roots(operand: Operand) -> tuple[Decimal, ...]:
    """The decimal roots of one operand: the one root of a numeric, or each root of a tuple of
    them."""
    if isinstance(operand, tuple):
        return tuple(Decimal(element.root) for element in operand)
    return (Decimal(operand.root),)


class Derived(NamedTuple):
    """How a derivation kind computes its root from its operand fields, and what the root can
    be from what the operands can be: one declaration both construction and the proof read.

    It is the ``default_factory`` of the kind's ``root``: Pydantic calls it with the validated
    operands and validates the result as a finite ``Decimal``. The proof calls ``interval`` with
    one interval per operand field, the element's interval for a tuple field."""

    operands: tuple[str, ...]
    """The fields the operation reads, in order."""
    value: Callable[[tuple[Decimal, ...]], Decimal]
    """The root, from the roots of the operands, every element of a tuple operand among them."""
    interval: Callable[[tuple[Interval, ...]], Interval]
    """What the root can be, from what each operand field can be."""

    def __call__(self, data: Mapping[str, Operand]) -> Decimal:
        """The root computed from the validated operands."""
        return self.value(tuple(r for name in self.operands for r in roots(data[name])))


def multiplied(values: tuple[Decimal, ...]) -> Decimal:
    """The product of the values; one for none."""
    return reduce(mul, values, Decimal(1))


def summed(values: tuple[Decimal, ...]) -> Decimal:
    """The sum of the values; zero for none."""
    return sum(values, Decimal(0))


def product_interval(operands: tuple[Interval, ...]) -> Interval:
    """What a product of two values can be. With both values bounded below by zero or more it
    is bounded below by the product of the lower bounds, and bounded above by the greatest
    product of the endpoints when both are bounded above; with a value that can be negative or
    is unbounded below it is unbounded. Strictness is dropped, which widens the interval and
    keeps it sound."""
    left, right = operands
    if left.low is None or right.low is None or left.low < 0 or right.low < 0:
        return Interval()
    if left.high is None or right.high is None:
        return Interval(low=left.low * right.low)
    corners = (
        left.low * right.low,
        left.low * right.high,
        left.high * right.low,
        left.high * right.high,
    )
    return Interval(low=min(corners), high=max(corners))


def sum_interval(operands: tuple[Interval, ...]) -> Interval:
    """What a sum of any number of elements can be, zero for none: bounded below by zero when
    no element can be negative, bounded above by zero when none can be positive."""
    (element,) = operands
    low = Decimal(0) if element.low is not None and element.low >= 0 else None
    high = Decimal(0) if element.high is not None and element.high <= 0 else None
    return Interval(low=low, high=high)


class Measure(Fact):
    """A derived value: a fact whose ``root`` its operation computes from what it holds.

    A program never computes a value. It declares the value's class as a subclass of a
    derivation kind, ``Times`` or ``Sum``, with the operands as the parameters, and reads the
    result as ``.root``, as it reads a ``Scalar``::

        class LineTotal(Times[UnitPrice, Quantity]): ...

    The engine constructs a derivation when its operands exist, like any fact, and Pydantic
    computes and validates the root at construction: each kind declares ``root`` after its
    operands, with its ``Derived`` operation as the default factory, since Pydantic validates
    fields in declaration order and a base class's field comes first. To the checker every
    derivation has a ``root``. An operand is a scalar the run holds, or another derivation. A
    derivation is itself an operand of a relation, a selection or a further derivation.
    """

    if TYPE_CHECKING:
        root: Decimal


type Numeric = Scalar[Decimal] | Scalar[int] | Measure
"""What a derivation, a relation or a selection operates on: a scalar over a number, or a
derived value."""


class Times[A: Numeric, B: Numeric](Measure):
    """The product of two values.

    ::

        class LineTotal(Times[UnitPrice, Quantity]): ...

    A constant factor is a scalar with a default root, which exists in every run by being
    declared::

        class Rate(Scalar[Decimal]):
            root: Decimal = Decimal("0.9")

        class Reduced(Times[LineTotal, Rate]): ...
    """

    left: A
    """The first factor."""
    right: B
    """The second factor."""
    root: Decimal = Field(
        default_factory=Derived(("left", "right"), multiplied, product_interval),
        exclude=True,
        description="The product, computed at construction.",
    )


class Sum[E: Numeric](Measure):
    """The sum of every element's value.

    The elements are what the runs under this one produced, one per element, collected in
    order; none sums to zero::

        class Lines(Sum[LineTotal]): ...
    """

    of: tuple[E, ...]
    """The values summed, in element order."""
    root: Decimal = Field(
        default_factory=Derived(("of",), summed, sum_interval),
        exclude=True,
        description="The sum, computed at construction; zero for no element.",
    )


type Ordering = Literal[-1, 0, 1]
"""The outcome of comparing two values: the first is under, equal to, or beyond the second."""


class Comparison(NamedTuple):
    """One comparison a relation kind makes between two of its operand fields: the one
    declaration construction and the proof read.

    It is the ``default_factory`` of the kind's ordering field: Pydantic calls it with the
    validated operands, it computes the ordering, and Pydantic admits the ordering through the
    field's ``Literal`` type or refuses it. The proof reads the same field: the two operands,
    and the admitted outcomes from the annotation."""

    left: str
    """The field compared."""
    right: str
    """The field it is compared with."""

    def __call__(self, data: Mapping[str, Operand]) -> int:
        """The ordering of the two validated operands: -1, 0 or 1."""
        (left,) = roots(data[self.left])
        (right,) = roots(data[self.right])
        return (left > right) - (left < right)


def is_given(data: object) -> TypeIs[dict[str, object]]:
    """Whether what a validator received is a dict of fields."""
    return isinstance(data, dict)


class Relation(Fact):
    """A rule over several values: a fact that constructs when the rule holds and refuses when
    it does not.

    Every relation kind subclasses this and declares its meaning as ordering fields: each is
    typed by a ``Literal`` of the outcomes it admits and carries, as ``Field`` metadata, a
    ``Comparison`` of two operand fields as its ``default_factory``. Pydantic computes the
    ordering from the validated operands and admits it or refuses it with ``literal_error``;
    the engine reads a refusal of a relation as the fact not existing, so a union of the facts
    that hold each outcome is the choice. The
    proof reads the same fields: it tells two relation kinds apart by the outcomes they admit,
    decides from the operands' intervals whether a relation can ever hold or ever refuse, and
    refuses a union two relations cannot tell apart. An ordering is computed and never given:
    one supplied in the input is dropped before validation.
    """

    @model_validator(mode="before")
    @classmethod
    def computed(cls, data: object) -> object:
        """Drop any ordering supplied in the input, so the only ordering is the computed one."""
        if is_given(data):
            orderings = {
                name
                for name, field in cls.model_fields.items()
                if isinstance(field.default_factory, Comparison)
            }
            return {key: value for key, value in data.items() if key not in orderings}
        return data


class Compare[A: Numeric, B: Numeric, O: Ordering](Relation):
    """A relation between two values, restricted to the outcomes ``O`` admits.

    The six relation kinds over two values are this class with the admitted outcomes fixed:
    ``Under`` admits -1, ``AtMost`` -1 and 0, ``Equal`` 0, ``AtLeast`` 0 and 1, ``Beyond`` 1,
    ``Differs`` -1 and 1. Two kinds whose admitted outcomes are disjoint are complements over
    the same operands, and the proof reads them as such.
    """

    value: A
    """The value the relation is about."""
    bound: B
    """What the value is compared with."""
    ordering: Annotated[
        O,
        Field(
            default_factory=Comparison("value", "bound"),
            exclude=True,
            repr=False,
            description="The ordering of value against bound, computed at construction.",
        ),
    ]


class Under[A: Numeric, B: Numeric](Compare[A, B, Literal[-1]]):
    """``value`` is under ``bound``. The complement of ``AtLeast``."""


class AtMost[A: Numeric, B: Numeric](Compare[A, B, Literal[-1, 0]]):
    """``value`` is at most ``bound``. The complement of ``Beyond``.

    A rule that compares two values is declared as a relation kind with the two values as its
    parameters, and each outcome is the fact that holds the relation that makes it true::

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

    The relation that holds constructs, and the one that does not refuses, which the engine
    reads as the fact not existing; so exactly one of ``Discounted`` and ``FullPrice`` exists,
    and the union is the choice. A bound that is a business constant is a scalar with a default
    root, and exists in every run by being declared. At startup the proof reads the bounds on
    both operands and refuses a relation that can never hold, or can never refuse.
    """


class Equal[A: Numeric, B: Numeric](Compare[A, B, Literal[0]]):
    """``value`` equals ``bound``, compared exactly. The complement of ``Differs``.

    ::

        class Settled(Equal[AmountPaid, AmountDue]): ...
    """


class AtLeast[A: Numeric, B: Numeric](Compare[A, B, Literal[0, 1]]):
    """``value`` is at least ``bound``. The complement of ``Under``."""


class Beyond[A: Numeric, B: Numeric](Compare[A, B, Literal[1]]):
    """``value`` is beyond ``bound``. The complement of ``AtMost``; see ``AtMost`` for how a
    rule is written with the two."""


class Differs[A: Numeric, B: Numeric](Compare[A, B, Literal[-1, 1]]):
    """``value`` differs from ``bound``. The complement of ``Equal``."""


class Between[A: Numeric, L: Numeric, U: Numeric](Relation):
    """A relation among three values: ``value`` is at least ``lower`` and at most ``upper``.

    ::

        class Eligible(Between[Age, MinimumAge, MaximumAge]): ...

    Two orderings are computed: ``lower`` against ``value``, and ``value`` against ``upper``,
    each admitting -1 and 0. Its complement is the union of ``Under[A, L]`` and
    ``Beyond[A, U]``.
    """

    value: A
    """The value the relation is about."""
    lower: L
    """The least the value may be."""
    upper: U
    """The most the value may be."""
    below: Annotated[
        Literal[-1, 0],
        Field(
            default_factory=Comparison("lower", "value"),
            exclude=True,
            repr=False,
            description="The ordering of lower against value, computed at construction.",
        ),
    ]
    above: Annotated[
        Literal[-1, 0],
        Field(
            default_factory=Comparison("value", "upper"),
            exclude=True,
            repr=False,
            description="The ordering of value against upper, computed at construction.",
        ),
    ]


class Selection[E: BaseModel](Fact):
    """A choice among elements: a fact over the elements the runs under this one produced,
    whose ``chosen`` is the one selected.

    Every selection kind subclasses this, and its shape is its tuple annotation, which Pydantic
    constructs and the proof reads: ``tuple[E, ...]`` with ``min_length=1`` is at least one
    element, ``tuple[E]`` is exactly one. With no element there is nothing to choose, and the
    selection refuses: a choice among nothing does not exist, and a fact that holds it does not
    either.
    """

    of: tuple[E, ...] = Field(min_length=1)
    """The elements chosen among, in element order; at least one."""


class Least[E: Numeric](Selection[E]):
    """The element whose value is least.

    A choice among elements is declared as a selection kind with the element class as its
    parameter. The engine collects the elements the runs under this one produced, and
    ``chosen`` is the one selected::

        class Cheapest(Least[LineTotal]): ...

    Ties go to the earliest element.
    """

    @property
    def chosen(self) -> E:
        """The element whose value is least."""
        return min(self.of, key=lambda e: Decimal(e.root))


class Greatest[E: Numeric](Selection[E]):
    """The element whose value is greatest; see ``Least``. Ties go to the earliest element."""

    @property
    def chosen(self) -> E:
        """The element whose value is greatest."""
        return max(self.of, key=lambda e: Decimal(e.root))


class First[E: BaseModel](Selection[E]):
    """The first element, in element order; see ``Least``. Any element class, not only a
    numeric one."""

    @property
    def chosen(self) -> E:
        """The first element."""
        return self.of[0]


class Only[E: BaseModel](Selection[E]):
    """The one element, when there is exactly one.

    A rule that a collection holds a single thing, declared as the shape ``tuple[E]``: with
    none or with more than one it refuses, which the engine reads as the fact not existing::

        class Sole(Only[Quote]): ...
    """

    of: tuple[E]
    """The one element."""

    @property
    def chosen(self) -> E:
        """The one element."""
        return self.of[0]


class Connection(BaseModel):
    """A party as the deployment names it.

    Subclass a library kind's connection, such as ``Http`` or ``Keyed``, once per party. Its
    fields are ``Setting`` subclasses: address, credential, limits, read from the environment.
    A ``Config`` holds one field per connection.

    ``open`` and ``close`` are abstract: the library kind implements them, holding what it
    opened, a client, in a ``PrivateAttr``, outside validation and outside the frozen fields.
    The server kind calls ``open`` once for every connection at startup and ``close`` once at
    shutdown, through the engine's ``opened``. A connection with no library kind cannot be
    constructed.
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

    Subclass a library kind's action, such as ``Post[P, S, T]`` or ``Get[P, T]``, with fields
    typed as the fact that intends the action. The library kind declares what the action sends
    and where as abstract properties, which the subclass implements as plain properties::

        class Charge(Post[Payments, Payment, Charged]):
            placed: Placed

            @property
            def sends(self) -> Payment:
                return Payment(amount=self.placed.amount)

            @property
            def resource(self) -> Resource:
                return Resource("/charges")

    The action holds its party as ``party``, the connection the deployment configured for
    ``P``; the engine fills it like any other field, from the config, so the action exists once
    the fact that intends it and the party both exist. Then the engine awaits ``perform``, and
    the library kind's ``perform`` sends through ``self.party`` and returns the record validated
    as ``T``, or raises. ``perform`` is abstract: an action with no library kind cannot be
    constructed. An action performed on one branch of a choice and not the other holds a
    premise that decides the choice; the proof refuses one that does not.
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

    Subclass it with the fact as its parameter and a ``@computed_field`` for each value the
    caller is told. The fact is held as ``of``, declared here with ``Field(exclude=True)``, so
    ``model_dump_json`` and the OpenAPI response schema carry the computed fields only;
    ``self.of`` is typed as ``F`` in code and is required at construction. A reply declares no
    fields of its own::

        class OrderPaid(Reply[Paid]):
            @computed_field
            @property
            def charge(self) -> ChargeId:
                return self.of.charged.charge

    A reply made from several facts holds the fact that holds them. Owned by this program's
    contract.
    """

    model_config = PRODUCT
    of: F_co = Field(
        exclude=True, description="The fact this reply is made from; never serialized."
    )


class Route[Q: Request, A: Reply[Fact]](BaseModel):
    """One thing the program does: receives ``Q`` and answers ``A``.

    Subclass it with the request and the reply, or a union of replies, as its parameters and
    no fields. The class name is the business's name for the route; the server library kind
    derives the address from it::

        class Checkout(Route[PlaceOrder, OrderPaid | OrderDeclined]): ...

    An instance is one answered request: ``request`` is what arrived and ``reply`` is what the
    program made of it. The engine constructs the route like any other class, once the reply
    exists, and that construction is the end of the run. A route exists once per run; the proof
    refuses one whose reply would exist once per element.
    """

    model_config = PRODUCT
    request: Q
    """What arrived."""
    reply: A
    """What the program answered."""


class Config(BaseSettings):
    """The deployment: connections and settings, from the environment and ``.env``.

    Subclass it, once per program, with one field per ``Connection`` and one ``Setting`` per
    value the deployment sets directly. Nested fields are read with a double underscore:
    ``PAYMENTS__URL``, ``PAYMENTS__KEY``. A ``.env`` file in the working directory is read with
    the same names. A missing or malformed variable fails at startup with the field named::

        class Deployment(Config):
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
