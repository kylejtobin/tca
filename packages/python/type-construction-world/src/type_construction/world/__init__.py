"""Declarative value and computation primitives.

This module holds reusable building blocks for declaring a business program as Pydantic
types. It does not execute a program. Nothing here runs an invocation, admits external
evidence, persists history, calls an external system, or projects an interface; none of those
is implemented in this tree.

What it provides:

- Values: ``Scalar`` is one primitive with an invariant, ``Setting`` is a lenient scalar for a
  value supplied as text, ``Value`` is a composite part, ``Record`` is what an external party
  says under that party's names, ``Fact`` is a conclusion made of the values it holds, and
  ``Duration`` is a positive length of time. A field is a product, a union ``A | B`` is a sum,
  and ``tuple[T, ...]`` is a finite repetition.
- Derivations: ``Times`` and ``Sum`` hold a value computed from their operands at construction.
- Relations: ``Under``, ``AtMost``, ``Equal``, ``AtLeast``, ``Beyond`` and ``Differs`` compare
  two values and ``Between`` relates three. Each admits some orderings and refuses the others.
- Selections: ``Least``, ``Greatest``, ``First`` and ``Only`` choose among elements by the
  shape of their tuple.
- Supporting machinery: ``Computation`` and ``Derived`` compute a field from its operands,
  ``Comparison`` and ``Shape`` are the conditions a relation or selection refuses by,
  ``Interval`` bounds what a numeric class can be, and ``Refusals`` and ``REFUTED`` separate a
  condition that did not hold from a failure of construction.

A computed field is a ``Computation`` in its annotation and ``COMPUTED`` as its default: its
operands determine it, and a value given for it is refused. A relation is one shared
comparison restricted to the orderings its ``Literal`` admits. A selection's shape is its
tuple annotation.

Selections and aggregations operate on the finite tuple they are given. A ``Sum`` is the sum of
that tuple, ``Only`` refuses a tuple that does not hold exactly one element, and ``Least``
refuses an empty one. None of them establishes that the tuple is the complete content of an
external source; whether a source is closed is a separate question this module does not answer.

Every configuration here is strict, frozen, and refuses undeclared fields, except ``Setting``,
which accepts text. Code constructs in Python mode, where ``Quantity("3")`` is refused. A caller
that validates data from outside chooses the validation mode that data needs. Construction
refuses a value with ``pydantic.ValidationError``; a refusal whose every error is ``REFUTED``
says that a declared condition did not hold over validated operands, and any other error is a
failure of construction. Errors raised outside validation are not ``ValidationError``.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from functools import reduce
from operator import mul
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Final,
    Literal,
    LiteralString,
    NamedTuple,
    get_args,
)
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    GetCoreSchemaHandler,
    RootModel,
    ValidationError,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
)
from pydantic_core import CoreSchema, PydanticCustomError, core_schema

__all__ = [
    "REFUTED",
    "AtLeast",
    "AtMost",
    "Between",
    "Beyond",
    "Compare",
    "Comparison",
    "Computation",
    "Condition",
    "Derived",
    "Differs",
    "Duration",
    "Equal",
    "Fact",
    "First",
    "Greatest",
    "Interval",
    "Least",
    "Measure",
    "Numeric",
    "Only",
    "Ordering",
    "Primitive",
    "Record",
    "Refusals",
    "Refutable",
    "Relation",
    "Scalar",
    "Selection",
    "Setting",
    "Shape",
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

``use_attribute_docstrings`` makes a docstring written under a field its description, which
appears in the field's JSON schema.
"""

type Primitive = (
    str | int | float | bool | bytes | Decimal | datetime | date | time | timedelta | UUID | Enum
)
"""What a ``Scalar`` is over: one of Python's value types, or an enumeration."""


class Scalar[T: Primitive](RootModel[T]):
    """One primitive with an invariant.

    Subclass it with the primitive and the constraint, and use the subclass as a field type
    wherever the value appears, so that the rule and the name travel with the value. A bare
    primitive carries neither::

        class Quantity(Scalar[int]):
            root: int = Field(gt=0)

    The value is read as ``.root``. ``Quantity(0)`` raises ``ValidationError``. A constant is a
    scalar with a default root::

        class Threshold(Scalar[Decimal]):
            root: Decimal = Decimal(100)
    """

    model_config = ROOT


SETTING = ConfigDict(frozen=True, validate_default=True)
"""Configuration for a value supplied as text: frozen, defaults validated, lenient, so that
text constructs the primitive."""


class Setting[T](RootModel[T]):
    """One value supplied as text, such as an address or a limit.

    Subclass it with the primitive and the constraint. It accepts text and constructs the
    primitive; its constraint still applies::

        class Retries(Setting[int]):
            root: int = Field(ge=0)

    A ``Scalar`` is strict; a ``Setting`` is lenient. Nothing in this module reads the
    environment or any other source for it.
    """

    model_config = SETTING


class Duration(Scalar[timedelta]):
    """A length of time, more than none."""

    root: timedelta = Field(gt=timedelta(0), description="A positive timedelta.")


class Value(BaseModel):
    """A composite part with no standing of its own.

    Subclass it for a thing that is held by other things and is nothing by itself: an address,
    a line of an order, a money amount with its currency. Its fields are typed as your classes::

        class Line(Value):
            sku: Sku
            quantity: Quantity
    """

    model_config = PRODUCT


class Record(BaseModel):
    """What an external party says.

    Subclass it with the fields this program reads from the party's response, under the party's
    names as aliases::

        class Charged(Record):
            charge: ChargeId = Field(alias="id")

    A party's payload validates as the ``Record`` by alias only, Pydantic's default:
    ``{"id": "c1"}`` constructs and ``{"charge": "c1"}`` is refused. A field the party sends that
    is not declared is refused. Code constructs one with the alias, ``Charged(id=ChargeId("c1"))``.

    A party that names everything in one convention gets one subclass with an
    ``alias_generator`` and no per-field alias::

        class Stripe(Record):
            model_config = ConfigDict(alias_generator=to_camel)

    A value nested in the party's payload is read with ``AliasPath`` and no wrapper class::

        amount: Amount = Field(validation_alias=AliasPath("data", "amount", "value"))

    A party's stated refusal is a ``Record`` too, one member of a union such as
    ``Charged | Declined``. Members can be told apart by a ``Literal`` field each declares,
    ``status: Literal["succeeded"]`` and ``status: Literal["declined"]``. This module does not
    check that a union of records is unambiguous. A party that does not answer is not a
    ``Record``, and this module does not model it.
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

    Subclass it with fields typed as the things the conclusion is made from: a record a party
    said, a prior fact, a value, a relation, a derivation, a selection. The fields are the
    fact's premises; constructing the fact validates them and holds them.

    A choice between two conclusions is two ``Fact`` subclasses, each holding the relation that
    makes it true, written as a union where the choice is held::

        class FullPrice(Fact):
            line: Line
            tier: Small

        class Discounted(Fact):
            line: Line
            tier: Large

        class Priced(Fact):
            priced: Discounted | FullPrice

    Two relations with disjoint admitted orderings over the same operands cannot both
    construct. This module does not prove that for an arbitrary union. A ``Fact`` records
    which premises it was made from; it does not say where they came from.
    """

    model_config = PRODUCT


class Interval(NamedTuple):
    """What a numeric class can be: a lower and an upper bound, each a ``Decimal`` or ``None``
    for unbounded, and whether each is strict. A derivation's ``Derived`` operation computes the
    interval of its root from the intervals of its operands. Nothing in this tree consumes
    intervals yet."""

    low: Decimal | None = None
    """The least the value can be; ``None`` for no lower bound."""
    low_strict: bool = False
    """Whether the value is strictly above ``low``."""
    high: Decimal | None = None
    """The most the value can be; ``None`` for no upper bound."""
    high_strict: bool = False
    """Whether the value is strictly below ``high``."""

    @property
    def empty(self) -> bool:
        """Whether no value is in the interval: bounds that cross, or meet with either strict."""
        if self.low is None or self.high is None:
            return False
        return self.low > self.high or (
            self.low == self.high and (self.low_strict or self.high_strict)
        )


type Operand = Numeric | tuple[Numeric, ...]
"""What a computation reads from one operand field: a numeric, or a tuple of them."""


def roots(operand: Operand) -> tuple[Decimal, ...]:
    """The decimal roots of one operand: the one root of a numeric, or each root of a tuple of
    them."""
    if isinstance(operand, tuple):
        return tuple(Decimal(element.root) for element in operand)
    return (Decimal(operand.root),)


class Uncomputed:
    """The one value a computed field has before construction computes it: the field's
    default, which no input can produce, in Python or in JSON, since nothing deserializes to
    this object and a caller who passes it has given nothing."""

    def __repr__(self) -> str:
        return "COMPUTED"


COMPUTED: Final[Any] = Uncomputed()
"""The default of every computed field: construction replaces it with the computed value. To
the checker it is no value at all, so the field keeps the type its annotation declares."""


REFUTED: Final[LiteralString] = "refuted"
"""The error type of a declared condition that did not hold over validated operands: a
relation's ordering outside its ``Literal``, or a selection's elements outside its tuple's
shape. The kind raises it at the one boundary where only the condition can refuse, so a
refusal whose every error is this type says only that a declared condition did not hold over
these operands; any other error is a failure of the construction."""


@dataclass(eq=False)
class Refusals:
    """What the declared conditions refused during one validation: the validation context a
    construction passes to ``model_validate``, which Pydantic hands every validator as
    ``info.context``. A condition that refuses notes itself here, with the field it validated,
    and stamps its error with the number of that note, so the error is traced to the validator
    that executed and to nothing raised anywhere else. Local to one validation call, and nothing
    keeps it after."""

    noted: list[tuple[str, Condition]] = field(default_factory=list)

    def refusing(self, name: str, condition: Condition) -> int:
        """A condition refusing at a field: its number in this validation."""
        self.noted.append((name, condition))
        return len(self.noted) - 1


class Condition:
    """The one place a refutable kind's declared condition refuses: a field's schema adapter
    that lets Pydantic's own validation of the declared type, a ``Literal`` of orderings or a
    tuple shape, admit or refuse what construction produced from validated operands. Its
    refusal is ``REFUTED`` at the field, and, when the validation carries ``Refusals`` as its
    context, noted there and stamped with the note's number. Pydantic's own error, its location
    and its message are kept as raised."""

    def refused(
        self, info: ValidationInfo, message: LiteralString, **context: str | int
    ) -> PydanticCustomError:
        """The refusal of this condition over validated operands, noted in the validation's
        ``Refusals`` when it carries one."""
        refusals, name = info.context, info.field_name
        if isinstance(refusals, Refusals) and name is not None:
            context["refusal"] = refusals.refusing(name, self)
        return PydanticCustomError(REFUTED, message, dict(context))


class Computation(ABC):
    """A field whose value is a function of the operand fields declared before it: the one
    declaration construction reads.

    It is the ``Annotated`` metadata of the field, whose default is ``COMPUTED``. Pydantic
    validates the operands first, in declaration order, then reaches the field with the
    default and calls this computation on the validated operands, and the result passes
    through the field's own type: a ``Decimal`` root, or a ``Literal`` of the orderings a
    relation admits, which refuses what it does not admit as ``REFUTED``. Any other
    input, in Python or in JSON, equal to the result or not, is refused with ``computed``: the
    field is a consequence of its operands and never given. An operand that did not construct
    leaves the field refused with ``uncomputed`` beside the operand's own error.

    Validation is the boundary: what Pydantic validated, in Python or in JSON, is computed, and
    a validated instance is held by identity wherever it is held. ``model_construct`` validates
    nothing, by Pydantic's contract, so nothing it makes is a computed value, and nothing in
    this module calls it. An instance's identity in memory is not a durable identity for the
    evidence it was built from.
    """

    operands: tuple[str, ...]
    """The fields the computation reads, in order."""

    @abstractmethod
    def computed(self, roots: tuple[Decimal, ...]) -> Decimal | int:
        """The result, from the roots of the operands in order, every element of a tuple
        operand among them."""

    def __get_pydantic_core_schema__(
        self, source: object, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """The field's schema: this computation around the field's own type."""
        return core_schema.with_info_wrap_validator_function(self.validated, handler(source))

    def validated(
        self, given: object, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
    ) -> object:
        """The result validated by the field's type when nothing was given; a refusal when
        something was, or when an operand did not construct."""
        name = info.field_name
        if given is not COMPUTED:
            code, message = "computed", "{field} is computed from {operands} and never given"
            raise PydanticCustomError(
                code, message, {"field": name, "operands": " and ".join(self.operands)}
            )
        absent = [operand for operand in self.operands if operand not in info.data]
        if absent:
            code, message = (
                "uncomputed",
                "{field} is computed from {operand}, which did not construct",
            )
            raise PydanticCustomError(
                code, message, {"field": name, "operand": " and ".join(absent)}
            )
        operands: tuple[Operand, ...] = tuple(info.data[operand] for operand in self.operands)
        result = self.computed(tuple(r for operand in operands for r in roots(operand)))
        return self.admitted(result, handler, info)

    def admitted(
        self,
        result: Decimal | int,
        handler: ValidatorFunctionWrapHandler,
        info: ValidationInfo,  # noqa: ARG002
    ) -> object:
        """The result validated by the field's type; a kind whose type can refuse only its
        declared condition names the refusal ``REFUTED``."""
        return handler(result)


@dataclass(frozen=True)
class Derived(Computation):
    """How a derivation kind computes its root from its operand fields, and what the root can
    be from what the operands can be.

    ``interval`` takes one interval per operand field, the element's interval for a tuple
    field."""

    operands: tuple[str, ...]
    """The fields the operation reads, in order."""
    value: Callable[[tuple[Decimal, ...]], Decimal]
    """The root, from the roots of the operands, every element of a tuple operand among them."""
    interval: Callable[[tuple[Interval, ...]], Interval]
    """What the root can be, from what each operand field can be."""

    def computed(self, roots: tuple[Decimal, ...]) -> Decimal:
        """The root, from the roots of the operands."""
        return self.value(roots)


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

    A program declares the value's class as a subclass of a derivation kind, ``Times`` or
    ``Sum``, with the operands as the parameters, and reads the result as ``.root``, as it reads
    a ``Scalar``::

        class LineTotal(Times[UnitPrice, Quantity]): ...

    Pydantic computes and validates the root at construction: each kind declares ``root`` after
    its operands, with its ``Derived`` operation as the field's metadata and ``COMPUTED`` as its
    default, since Pydantic validates fields in declaration order and a base class's field
    comes first. A root given at construction is refused. To the checker every derivation has
    a ``root``. An operand is a numeric scalar or another derivation. A derivation is itself an
    operand of a relation, a selection or a further derivation.
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

    A constant factor is a scalar with a default root::

        class Rate(Scalar[Decimal]):
            root: Decimal = Decimal("0.9")

        class Reduced(Times[LineTotal, Rate]): ...
    """

    left: A
    """The first factor."""
    right: B
    """The second factor."""
    root: Annotated[Decimal, Derived(("left", "right"), multiplied, product_interval)] = Field(
        default=COMPUTED, exclude=True, description="The product, computed at construction."
    )


class Sum[E: Numeric](Measure):
    """The sum of every element's value in the tuple it is given.

    The elements are a finite tuple, summed in order; an empty tuple sums to zero::

        class Lines(Sum[LineTotal]): ...

    The sum is of the tuple supplied. It does not establish that the tuple holds every element
    an external source has or will have.
    """

    of: tuple[E, ...]
    """The values summed, in element order."""
    root: Annotated[Decimal, Derived(("of",), summed, sum_interval)] = Field(
        default=COMPUTED,
        exclude=True,
        description="The sum, computed at construction; zero for no element.",
    )


type Ordering = Literal[-1, 0, 1]
"""The outcome of comparing two values: the first is under, equal to, or beyond the second."""

SIGN: Final[dict[int, str]] = {-1: "<", 0: "=", 1: ">"}
"""How an ordering reads: the first operand under, equal to, or beyond the second."""


@dataclass(frozen=True)
class Comparison(Computation, Condition):
    """One comparison a relation kind makes between two of its operand fields: the ordering
    of the first against the second, which the field's ``Literal`` admits or refuses. The two
    operands and the admitted outcomes are both readable from the field's declaration."""

    operands: tuple[str, str]
    """The field compared, and the field it is compared with."""

    @property
    def left(self) -> str:
        """The field compared."""
        return self.operands[0]

    @property
    def right(self) -> str:
        """The field it is compared with."""
        return self.operands[1]

    def computed(self, roots: tuple[Decimal, ...]) -> int:
        """The ordering of the two operands: -1, 0 or 1."""
        left, right = roots
        return (left > right) - (left < right)

    def admitted(
        self, result: Decimal | int, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
    ) -> object:
        """The ordering admitted by the field's ``Literal``, or ``REFUTED``: the field's type is
        the admitted orderings and the input is the computed one, so what it refuses here is the
        condition not holding, named with the two operand fields, the classes of their
        validated values and the ordering observed."""
        try:
            return handler(result)
        except ValidationError:
            observed = "{left} {sign} {right}"
            raise self.refused(
                info,
                observed,
                left=self.left,
                right=self.right,
                left_class=type(info.data[self.left]).__name__,
                right_class=type(info.data[self.right]).__name__,
                sign=SIGN[int(result)],
                ordering=int(result),
            ) from None


class Refutable(Fact):
    """A fact that exists to refuse: a relation or a selection, whose refusal, when every error
    is one its own declared conditions raised, says only that the conditions do not hold over
    these operands. The kind owns that distinction, and reads
    it from the validation that executed: validated with ``Refusals`` as the context, each
    condition that refused noted itself there and stamped its error; a refutation is a refusal
    whose errors and notes correspond one to one, each error ``REFUTED`` at the noted field of
    this class, raised by the ``Condition`` this class declares there. An operand that did not
    construct, a value given for a computed field, ``REFUTED`` raised by any other validator,
    at the condition's field or elsewhere, or a condition refusing deeper inside an operand, is
    a failure. A caller reads this through ``refuted`` and need not interpret any error itself."""

    @classmethod
    def refuted(cls, refusal: ValidationError, refusals: Refusals) -> bool:
        """Whether a refusal of this kind, validated with ``refusals`` as its context, is its
        declared conditions not holding, and nothing else."""
        stamped: list[int] = []
        for error in refusal.errors():
            number = (error.get("ctx") or {}).get("refusal")
            if error["type"] != REFUTED or not isinstance(number, int):
                return False
            if not 0 <= number < len(refusals.noted):
                return False
            name, condition = refusals.noted[number]
            own = cls.model_fields.get(name)
            if own is None or not any(meta is condition for meta in own.metadata):
                return False
            if tuple(error["loc"]) != (name,):
                return False
            stamped.append(number)
        return sorted(stamped) == list(range(len(refusals.noted)))


class Relation(Refutable):
    """A rule over several values: a fact that constructs when the rule holds and refuses when
    it does not.

    Every relation kind subclasses this and declares its meaning as ordering fields: each is
    typed by a ``Literal`` of the outcomes it admits and carries a ``Comparison`` of two
    operand fields as its metadata, with ``COMPUTED`` as its default. Pydantic computes the
    ordering from the validated operands and admits it or refuses it as ``REFUTED``. A union
    of the facts that hold each outcome can express a choice. An ordering is computed and never
    given: one supplied in the input is refused.
    """


class Compare[A: Numeric, B: Numeric, O: Ordering](Relation):
    """A relation between two values, restricted to the outcomes ``O`` admits.

    The six relation kinds over two values are this class with the admitted outcomes fixed:
    ``Under`` admits -1, ``AtMost`` -1 and 0, ``Equal`` 0, ``AtLeast`` 0 and 1, ``Beyond`` 1,
    ``Differs`` -1 and 1. Two kinds whose admitted outcomes are disjoint are complements over
    the same operands.
    """

    value: A
    """The value the relation is about."""
    bound: B
    """What the value is compared with."""
    ordering: Annotated[O, Comparison(("value", "bound"))] = Field(
        default=COMPUTED,
        exclude=True,
        repr=False,
        description="The ordering of value against bound, computed at construction.",
    )


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

        class Priced(Fact):
            priced: Discounted | FullPrice

    The relation that holds constructs, and the one that does not refuses with ``REFUTED``. A
    bound that is a business constant is a scalar with a default root.
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
    below: Annotated[Literal[-1, 0], Comparison(("lower", "value"))] = Field(
        default=COMPUTED,
        exclude=True,
        repr=False,
        description="The ordering of lower against value, computed at construction.",
    )
    above: Annotated[Literal[-1, 0], Comparison(("value", "upper"))] = Field(
        default=COMPUTED,
        exclude=True,
        repr=False,
        description="The ordering of value against upper, computed at construction.",
    )


class Shape(Condition):
    """A selection's tuple shape as its condition: the one declaration construction reads.

    It is the ``Annotated`` metadata of a selection's ``of``. Pydantic validates the elements
    first, as a tuple of any number of the element class, and reports an omitted field or an
    invalid element as it does for any field; then the validated elements pass through the
    field's own declared shape, ``tuple[E, ...]`` with ``min_length=1`` or ``tuple[E]``, which
    can refuse nothing but their number, so what it refuses there is the condition not holding,
    raised as ``REFUTED`` with Pydantic's own words and the count.
    """

    def __get_pydantic_core_schema__(
        self, source: object, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """The field's schema: the elements validated as any number of the element class, then
        the declared shape over the validated elements."""
        (element,) = (a for a in get_args(source) if a is not Ellipsis)
        elements = handler.generate_schema(tuple[element, ...])
        declared = handler(source)
        return core_schema.chain_schema(
            [elements, core_schema.with_info_wrap_validator_function(self.admitted, declared)]
        )

    def admitted(
        self,
        elements: tuple[object, ...],
        handler: ValidatorFunctionWrapHandler,
        info: ValidationInfo,
    ) -> object:
        """The validated elements admitted by the declared shape, or ``REFUTED``."""
        try:
            return handler(elements)
        except ValidationError as refusal:
            why, said = "; ".join(e["msg"] for e in refusal.errors()), "{why}"
            raise self.refused(info, said, why=why, count=len(elements)) from None


class Selection[E: BaseModel](Refutable):
    """A choice among elements: a fact over a finite tuple of elements, whose ``chosen`` is the
    one selected.

    Every selection kind subclasses this, and its shape is its tuple annotation, which Pydantic
    constructs: ``tuple[E, ...]`` with ``min_length=1`` is at least one element, ``tuple[E]`` is
    exactly one. With no element there is nothing to choose, and the selection refuses with
    ``REFUTED``. The shape is the field's ``Shape`` metadata.

    A selection chooses among the tuple it is given. It does not establish that the tuple is
    complete, so it does not establish that nothing else exists, that an element is unique
    among an external source's contents, or that the choice is final.
    """

    of: Annotated[tuple[E, ...], Shape()] = Field(min_length=1)
    """The elements chosen among, in element order; at least one."""


class Least[E: Numeric](Selection[E]):
    """The element whose value is least.

    A choice among elements is declared as a selection kind with the element class as its
    parameter. It is constructed from a tuple of elements, and ``chosen`` is the one selected::

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

    A rule that a supplied tuple holds a single thing, declared as the shape ``tuple[E]``: with
    none or with more than one it refuses with ``REFUTED``::

        class Sole(Only[Quote]): ...
    """

    of: Annotated[tuple[E], Shape()]
    """The one element."""

    @property
    def chosen(self) -> E:
        """The one element."""
        return self.of[0]
