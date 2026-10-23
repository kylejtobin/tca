"""Declarations whose features interact: one operation under two collections, a collection source
per element with its own closure, an ordinary validator beside delayed evidence and a dependent
effect, a correlation unique only as a whole, and a request and a fact with native aliases.

An order holds lines in a cart and lines among gifts. Every line is a ``Line``, with a sku and
the warehouse it ships from; two lines may share a sku. The carrier ships one line per request,
and the same request is sent for a cart line and a gift line. Reviewers approve lines, several
approvals per line, and say per line when that line's review is closed. A line is eligible when
an ordinary validator on the fact says so. Nothing here is written for the interpreter.
"""

from decimal import Decimal
from typing import Self

from pydantic import Field, model_validator

from type_construction.program import Binding, Correlation, Interaction, Program, Source
from type_construction.world import Fact, Only, Record, Scalar, Value


class OrderId(Scalar[str]):
    root: str = Field(min_length=1)


class Sku(Scalar[str]):
    root: str = Field(min_length=1)


class Warehouse(Scalar[str]):
    root: str = Field(min_length=1)


class Quantity(Scalar[int]):
    root: int = Field(gt=0)


class Reviewer(Scalar[str]):
    root: str = Field(min_length=1)


class Tracking(Scalar[str]):
    root: str = Field(min_length=1)


class Total(Scalar[Decimal]):
    root: Decimal = Field(gt=0)


class Paid(Scalar[Decimal]):
    root: Decimal = Field(ge=0)


class Line(Value):
    sku: Sku
    warehouse: Warehouse
    quantity: Quantity


class Cart(Value):
    lines: tuple[Line, ...]


class Gifts(Value):
    lines: tuple[Line, ...]


class Order(Value):
    id: OrderId
    cart: Cart
    gifts: Gifts


class ProcessOrder(Value):
    """The command: ship every line of the order, cart and gifts."""

    order: Order


class ShipLine(Value):
    """What the program sends the carrier for one line, whichever collection holds it."""

    order: OrderId
    line: Line


class LineShipped(Record):
    order: OrderId = Field(alias="order_id")
    tracking: Tracking


class LineDone(Fact):
    line: Line
    shipment: LineShipped


class Shipments(Fact):
    """The outcome: every cart line and every gift line shipped, each in its own tuple."""

    order: Order
    cart: tuple[LineDone, ...]
    gifts: tuple[LineDone, ...]


class Lined(Value):
    id: OrderId
    lines: tuple[Line, ...]


class ReviewLines(Value):
    """The command: have each line reviewed."""

    order: Lined


class LineApproved(Record):
    order: OrderId = Field(alias="order_id")
    sku: Sku
    warehouse: Warehouse
    reviewer: Reviewer


class LineReviewClosed(Record):
    order: OrderId = Field(alias="order_id")
    sku: Sku
    warehouse: Warehouse


class LineApprovals(Fact):
    """One line and every approval it received before its review closed."""

    line: Line
    approvals: tuple[LineApproved, ...]


class AllReviewed(Fact):
    order: Lined
    lines: tuple[LineApprovals, ...]


class SoleApproval(Only[LineApproved]):
    """The one approval of a line, when there is exactly one."""


class LineDecided(Fact):
    line: Line
    approval: SoleApproval


class AllDecided(Fact):
    order: Lined
    lines: tuple[LineDecided, ...]


class Priced(Value):
    id: OrderId
    total: Total


class FulfillOrder(Value):
    order: Priced


class CaptureRequest(Value):
    order: OrderId
    amount: Total


class Captured(Record):
    order: OrderId = Field(alias="order_id")
    amount: Paid


class Eligible(Fact):
    """An order whose capture matches its total, by an ordinary validator and no declared
    relation: the interpreter does not read it, so it cannot know whether it will hold."""

    order: Priced
    payment: Captured

    @model_validator(mode="after")
    def _matches(self) -> Self:
        if self.payment.amount.root != self.order.total.root:
            msg = "the capture does not match the total"
            raise ValueError(msg)
        return self


class ShipOrder(Value):
    """What the program sends the carrier: it needs the order alone."""

    order: OrderId


class OrderShipped(Record):
    order: OrderId = Field(alias="order_id")
    tracking: Tracking


class Dispatched(Fact):
    eligible: Eligible
    shipment: OrderShipped


class AliasedRequest(Value):
    """A request whose field is named for the party: a native alias on a sent class."""

    order: OrderId = Field(alias="order_ref")


class AliasedAnswer(Record):
    order: OrderId = Field(alias="order_ref")
    tracking: Tracking


class AliasedFact(Fact):
    """A conclusion whose field has an alias: native, and nothing to do with any party."""

    order: Priced = Field(alias="the_order")
    answer: AliasedAnswer


CARRIER = Source("carrier")
REVIEWERS = Source("reviewers")
PAYMENTS = Source("payments")

BY_ORDER = (Correlation(received="order", subject="order.id"),)
BY_LINE = (
    *BY_ORDER,
    Correlation(received="sku", subject="order.lines.*.sku"),
    Correlation(received="warehouse", subject="order.lines.*.warehouse"),
)
BY_SKU = (*BY_ORDER, Correlation(received="sku", subject="order.lines.*.sku"))

SHIP_LINE = Interaction(
    source=CARRIER, sends=ShipLine, receives=(LineShipped,), correlated=BY_ORDER
)
LINE_APPROVALS = Interaction(
    source=REVIEWERS, receives=(LineApproved,), correlated=BY_LINE, closed_by=LineReviewClosed
)
LINE_CLOSING = Interaction(source=REVIEWERS, receives=(LineReviewClosed,), correlated=BY_LINE)
APPROVALS_BY_SKU = Interaction(
    source=REVIEWERS, receives=(LineApproved,), correlated=BY_SKU, closed_by=LineReviewClosed
)
CLOSING_BY_SKU = Interaction(source=REVIEWERS, receives=(LineReviewClosed,), correlated=BY_SKU)
CAPTURE = Interaction(
    source=PAYMENTS, sends=CaptureRequest, receives=(Captured,), correlated=BY_ORDER
)
SHIP_ORDER = Interaction(
    source=CARRIER, sends=ShipOrder, receives=(OrderShipped,), correlated=BY_ORDER
)
ALIASED = Interaction(
    source=CARRIER, sends=AliasedRequest, receives=(AliasedAnswer,), correlated=BY_ORDER
)

SHIPPING = Program(
    goal=Shipments,
    accepts=ProcessOrder,
    interactions=(SHIP_LINE,),
    bound=(
        Binding(premise="cart", subject="order.cart.lines"),
        Binding(premise="gifts", subject="order.gifts.lines"),
    ),
)
REVIEWING = Program(
    goal=AllReviewed, accepts=ReviewLines, interactions=(LINE_APPROVALS, LINE_CLOSING)
)
DECIDING = Program(
    goal=AllDecided, accepts=ReviewLines, interactions=(LINE_APPROVALS, LINE_CLOSING)
)
DECIDING_BY_SKU = Program(
    goal=AllDecided, accepts=ReviewLines, interactions=(APPROVALS_BY_SKU, CLOSING_BY_SKU)
)
DISPATCHING = Program(goal=Dispatched, accepts=FulfillOrder, interactions=(CAPTURE, SHIP_ORDER))
ALIASING = Program(goal=AliasedFact, accepts=FulfillOrder, interactions=(ALIASED,))


def line(sku: str, warehouse: str, quantity: int = 1) -> Line:
    return Line(sku=Sku(sku), warehouse=Warehouse(warehouse), quantity=Quantity(quantity))


ORDER = ProcessOrder(
    order=Order(
        id=OrderId("o-7"),
        cart=Cart(lines=(line("tea", "w1"), line("tea", "w1"))),
        gifts=Gifts(lines=(line("tea", "w1"),)),
    )
)
"""Three equal lines: two in the cart, one among the gifts."""

REVIEW = ReviewLines(
    order=Lined(id=OrderId("o-7"), lines=(line("tea", "w1"), line("tea", "w2"), line("mug", "w1")))
)
"""Three lines, unique only by sku and warehouse together."""

PRICED = FulfillOrder(order=Priced(id=OrderId("o-7"), total=Total(Decimal("50.00"))))
