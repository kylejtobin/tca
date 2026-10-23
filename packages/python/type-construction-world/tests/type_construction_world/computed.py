"""A program whose values are computed: a line's total from its price and quantity, a reduced
total from a total and a rate, the lines' sum, and the rules that compare a total with a
threshold. Nothing here names a result: each derivation and relation declares its operands,
and construction computes the rest."""

from decimal import Decimal

from pydantic import Field

from type_construction.world import (
    AtMost,
    Between,
    Beyond,
    Equal,
    Fact,
    Scalar,
    Sum,
    Times,
    Value,
)


class UnitPrice(Scalar[Decimal]):
    """What one of a product costs."""

    root: Decimal = Field(gt=0)


class Quantity(Scalar[int]):
    """How many of a product a line asks for."""

    root: int = Field(gt=0)


class Threshold(Scalar[Decimal]):
    """The total at which a line stops being small."""

    root: Decimal = Decimal(100)


class Rate(Scalar[Decimal]):
    """What a reduced total is of the full one."""

    root: Decimal = Decimal("0.9")


class Line(Value):
    """One product's price and how many."""

    price: UnitPrice
    quantity: Quantity


class Order(Value):
    """The lines of an order, with no computed result of their own."""

    lines: tuple[Line, ...]


class LineTotal(Times[UnitPrice, Quantity]):
    """What a line costs: its price times its quantity."""


class Reduced(Times[LineTotal, Rate]):
    """A line's total at the rate."""


class Lines(Sum[LineTotal]):
    """What every line costs together."""


class Small(AtMost[LineTotal, Threshold]):
    """A line's total is at most the threshold."""


class Large(Beyond[LineTotal, Threshold]):
    """A line's total is beyond the threshold."""


class Exact(Equal[LineTotal, Threshold]):
    """A line's total is the threshold."""


class Allowed(Between[Quantity, Quantity, Quantity]):
    """A quantity is within two others."""


class Priced(Fact):
    """A line's total beside the rule that holds for it."""

    total: LineTotal
    small: Small
