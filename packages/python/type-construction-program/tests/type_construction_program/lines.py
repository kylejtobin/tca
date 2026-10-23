"""An order of several lines: one class, many occurrences.

Every line is a ``Line``. The business prices each line, ships each line, and has each line
cleared by a reviewer. Two lines may be equal in every field and are still two lines: two
prices, two shipments, two clearances. Nothing here numbers the lines or names which is which;
the declarations say only that these facts hold per line.
"""

from decimal import Decimal

from pydantic import Field

from type_construction.program import Correlation, Interaction, Program
from type_construction.world import Fact, Record, Scalar, Sum, Times, Value

from .fulfillment import APPROVALS, CARRIER, OrderId, Reviewer, Tracking


class Sku(Scalar[str]):
    root: str = Field(min_length=1)


class Quantity(Scalar[int]):
    root: int = Field(gt=0)


class UnitPrice(Scalar[Decimal]):
    root: Decimal = Field(gt=0)


class Line(Value):
    sku: Sku
    quantity: Quantity
    price: UnitPrice


class LinedOrder(Value):
    id: OrderId
    lines: tuple[Line, ...]


class ProcessOrder(Value):
    """The command: process this order, line by line."""

    order: LinedOrder


class LineTotal(Times[UnitPrice, Quantity]):
    """What one line costs."""


class Priced(Fact):
    """One line and what it costs."""

    line: Line
    total: LineTotal


class OrderTotal(Sum[LineTotal]):
    """What every line costs together."""


class Invoice(Fact):
    """The outcome: each line priced, and the total."""

    order: LinedOrder
    priced: tuple[Priced, ...]
    total: OrderTotal


class LineShipRequest(Value):
    """What the program sends the carrier: ship this line of this order."""

    order: OrderId
    line: Line


class LineShipped(Record):
    order: OrderId = Field(alias="order_id")
    tracking: Tracking


class LineDone(Fact):
    """One line and its shipment."""

    line: Line
    shipment: LineShipped


class AllShipped(Fact):
    """The outcome: every line shipped."""

    order: LinedOrder
    lines: tuple[LineDone, ...]


class LineApproved(Record):
    order: OrderId = Field(alias="order_id")
    sku: Sku
    reviewer: Reviewer


class LineCleared(Fact):
    """One line and the approval that clears it."""

    line: Line
    approval: LineApproved


class AllCleared(Fact):
    """The outcome: every line cleared."""

    order: LinedOrder
    lines: tuple[LineCleared, ...]


BY_ORDER = (Correlation(received="order", subject="order.id"),)

LINE_SHIP = Interaction(
    source=CARRIER, sends=LineShipRequest, receives=(LineShipped,), correlated=BY_ORDER
)
LINE_APPROVAL = Interaction(
    source=APPROVALS,
    receives=(LineApproved,),
    correlated=(*BY_ORDER, Correlation(received="sku", subject="order.lines.*.sku")),
)

INVOICING = Program(goal=Invoice, accepts=ProcessOrder)
SHIPPING = Program(goal=AllShipped, accepts=ProcessOrder, interactions=(LINE_SHIP,))
CLEARANCE = Program(goal=AllCleared, accepts=ProcessOrder, interactions=(LINE_APPROVAL,))


def line(sku: str, quantity: int, price: str) -> Line:
    return Line(sku=Sku(sku), quantity=Quantity(quantity), price=UnitPrice(Decimal(price)))


def order(*lines: Line) -> ProcessOrder:
    return ProcessOrder(order=LinedOrder(id=OrderId("o-9"), lines=lines))


TWO_EQUAL = order(line("A", 1, "10.00"), line("A", 1, "10.00"))
"""Two lines equal in every field."""

TWO_DISTINCT = order(line("A", 2, "10.00"), line("B", 1, "4.50"))
"""Two lines that differ."""
