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
from typing import Annotated, Self, cast

from pydantic import (
    AfterValidator,
    BeforeValidator,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)

from type_construction.program import Binding, Correlation, Interaction, Program, Source
from type_construction.world import Equal, Fact, Only, Record, Scalar, Value


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


def nonzero(payment: Captured) -> Captured:
    """An ordinary after-validator in a field annotation, not a declared relation."""
    if payment.amount.root == 0:
        msg = "nothing was captured"
        raise ValueError(msg)
    return payment


class Covered(Fact):
    """An order and a capture that an annotated validator, not a declared relation, must
    accept."""

    order: Priced
    payment: Annotated[Captured, AfterValidator(nonzero)]


class OrderApproval(Record):
    order: OrderId = Field(alias="order_id")
    reviewer: Reviewer


class OrderReviewClosed(Record):
    order: OrderId = Field(alias="order_id")


class Endorsed(Fact):
    """At least two approvals, by a native field constraint and no declared selection."""

    approvals: tuple[OrderApproval, ...] = Field(min_length=2)


class QuoteRequest(Value):
    """What the program sends the carrier for one line: a quote."""

    order: OrderId
    line: Line


class Quote(Record):
    order: OrderId = Field(alias="order_id")
    amount: Paid


class Quoted(Fact):
    line: Line
    quote: Quote


class Pinged(Record):
    order: OrderId = Field(alias="order_id")


class PingRequest(Value):
    order: OrderId


class Catalogued(Fact):
    """At least two lines quoted, by a constraint on the goal's own field, and the desk pinged.
    The constraint is on the consumer itself, not packaged in a separate fact."""

    order: Lined
    quotes: tuple[Quoted, ...] = Field(min_length=2)
    pinged: Pinged


class PingDesk(Fact):
    """The desk's ping in a plain fact."""

    pinged: Pinged


class CheckedPingDesk(Fact):
    """The desk's ping behind an opaque identity validator."""

    pinged: Pinged

    @model_validator(mode="after")
    def _same(self) -> Self:
        return self


class CataloguedViaDesk(Fact):
    order: Lined
    quotes: tuple[Quoted, ...] = Field(min_length=2)
    desk: PingDesk


class CataloguedViaCheckedDesk(Fact):
    order: Lined
    quotes: tuple[Quoted, ...] = Field(min_length=2)
    desk: CheckedPingDesk


class Tally(Value):
    counts: list[int]


class Count(Value):
    """The command: a tally of counts, held in a list."""

    id: OrderId
    tally: Tally


def padded(tally: Tally) -> Tally:
    """A validator that alters what it is given: unsupported, and the thing a construction must
    not be allowed to do to admitted evidence."""
    tally.counts.append(1)
    return tally


class Padded(Fact):
    tally: Annotated[Tally, AfterValidator(padded)]


class BadLimit(Scalar[int]):
    """A constant whose default its own constraint refuses."""

    root: int = Field(gt=0, default=0)


class Flawed(Fact):
    order: Priced
    limit: BadLimit


class ShipOrder(Value):
    """What the program sends the carrier: it needs the order alone."""

    order: OrderId


class OrderShipped(Record):
    order: OrderId = Field(alias="order_id")
    tracking: Tracking


class Dispatched(Fact):
    eligible: Eligible
    shipment: OrderShipped


class GuardedShipOrder(Value):
    """What the program sends the carrier when the business means the shipment to wait for
    eligibility: the eligibility is a premise of the request, the declared relationship."""

    eligible: Eligible


class GuardedShipped(Record):
    order: OrderId = Field(alias="order_id")
    tracking: Tracking


class GuardedDispatched(Fact):
    eligible: Eligible
    shipment: GuardedShipped


class FlatDispatched(Fact):
    """The same condition as ``Eligible`` states, moved onto the goal that holds the order, the
    payment and the shipment: natively, the same business values are accepted and refused."""

    order: Priced
    payment: Captured
    shipment: OrderShipped

    @model_validator(mode="after")
    def _matches(self) -> Self:
        if self.payment.amount.root != self.order.total.root:
            msg = "the capture does not match the total"
            raise ValueError(msg)
        return self


class Noted(Value):
    """A note that is validated again wherever it is held, by a validator that reads the
    validation's context: natively, the context the outer construction carries reaches it."""

    model_config = ConfigDict(
        frozen=True, strict=True, extra="forbid", revalidate_instances="always"
    )

    reviewer: Reviewer

    @model_validator(mode="after")
    def _in_context(self, info: ValidationInfo) -> Self:
        if info.context is None:
            msg = "validated outside any context"
            raise ValueError(msg)
        return self


class Notes(Fact):
    """At least one note: a native constraint on a field whose elements are revalidated."""

    notes: tuple[Noted, ...] = Field(min_length=1)


class Stamped(Value):
    """A stamp validated again wherever it is held, by a validator on one of its own fields that
    reads the validation's context: nothing wraps the class, the function is inside it."""

    model_config = ConfigDict(
        frozen=True, strict=True, extra="forbid", revalidate_instances="always"
    )

    reviewer: Reviewer

    @field_validator("reviewer")
    @classmethod
    def _in_context(cls, reviewer: Reviewer, info: ValidationInfo) -> Reviewer:
        if info.context is None:
            msg = "validated outside any context"
            raise ValueError(msg)
        return reviewer


class Stamps(Fact):
    stamps: tuple[Stamped, ...] = Field(min_length=1)


class Matches(Equal[Paid, Total]):
    """The capture equals the total: the same condition as ``Eligible`` states, as a declared
    relation the evaluator reads."""


class DeclaredEligible(Fact):
    """An order whose capture matches its total, by a declared relation."""

    order: Priced
    payment: Captured
    matched: Matches


class DeclaredDispatched(Fact):
    eligible: DeclaredEligible
    shipment: OrderShipped


class FlatDeclared(Fact):
    """The same condition as a declared relation, on the goal that holds everything."""

    order: Priced
    payment: Captured
    matched: Matches
    shipment: OrderShipped


class Doubly(Fact):
    """Two constructions, each behind a validator the evaluator cannot read, each resolved only
    by its own effect, and nothing declared between them."""

    eligible: Eligible
    desk: CheckedPingDesk


class DoublyDeclared(Fact):
    """The same, with the eligibility's condition declared as a relation."""

    eligible: DeclaredEligible
    desk: CheckedPingDesk


class DoublyPlain(Fact):
    """The same, with the desk's ping in a plain fact."""

    eligible: Eligible
    desk: PingDesk


class Voucher(Record):
    order: OrderId = Field(alias="order_id")
    reviewer: Reviewer


class CheckedVoucher(Fact):
    """A reviewer's voucher behind an opaque identity validator, nothing sent for it."""

    voucher: Voucher

    @model_validator(mode="after")
    def _same(self) -> Self:
        return self


class Vouched(Fact):
    eligible: Eligible
    vouched: CheckedVoucher


def seconded[R](records: tuple[R, ...]) -> tuple[R, ...]:
    """A before-validator that pads a lone record to two before the length is checked: native
    Pydantic accepts one record where the bare constraint refuses it."""
    return records if len(records) >= 2 else (*records, *records)


class Seconded(Fact):
    """At least two approvals after padding: the judgement at its own construction boundary."""

    approvals: Annotated[tuple[OrderApproval, ...], BeforeValidator(seconded), Field(min_length=2)]


class SecondedRelease(Fact):
    seconded: Seconded
    shipment: OrderShipped


class Prefaced(Fact):
    """At least two approvals, where a model validator running before field validation pads a
    lone approval: the constraint is native and the padding is not at the field."""

    approvals: tuple[OrderApproval, ...] = Field(min_length=2)

    @model_validator(mode="before")
    @classmethod
    def _second(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        given = cast("dict[str, object]", data)
        approvals = given.get("approvals")
        if not isinstance(approvals, tuple):
            return given
        lone = cast("tuple[object, ...]", approvals)
        if len(lone) != 1:
            return given
        padded: dict[str, object] = {**given, "approvals": (*lone, *lone)}
        return padded


class PrefacedRelease(Fact):
    prefaced: Prefaced
    shipment: OrderShipped


class SecondedCatalogue(Fact):
    """At least two quotes after padding, judged on the goal's own field, and the desk pinged."""

    order: Lined
    quotes: Annotated[tuple[Quoted, ...], BeforeValidator(seconded), Field(min_length=2)]
    pinged: Pinged


class SecondedQuotes(Fact):
    """At least two quotes after padding, at a construction boundary of their own."""

    quotes: Annotated[tuple[Quoted, ...], BeforeValidator(seconded), Field(min_length=2)]


class SecondedCatalogueViaFact(Fact):
    order: Lined
    quoted: SecondedQuotes
    pinged: Pinged


class Settled(Fact):
    covered: Covered
    shipment: OrderShipped


class Released(Fact):
    endorsed: Endorsed
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
GUARDED_SHIP = Interaction(
    source=CARRIER, sends=GuardedShipOrder, receives=(GuardedShipped,), correlated=BY_ORDER
)
QUOTE = Interaction(source=CARRIER, sends=QuoteRequest, receives=(Quote,), correlated=BY_ORDER)
PING = Interaction(source=CARRIER, sends=PingRequest, receives=(Pinged,), correlated=BY_ORDER)
ORDER_APPROVALS = Interaction(
    source=REVIEWERS, receives=(OrderApproval,), correlated=BY_ORDER, closed_by=OrderReviewClosed
)
ORDER_CLOSING = Interaction(source=REVIEWERS, receives=(OrderReviewClosed,), correlated=BY_ORDER)
ALIASED = Interaction(
    source=CARRIER, sends=AliasedRequest, receives=(AliasedAnswer,), correlated=BY_ORDER
)
VOUCHING = Interaction(source=REVIEWERS, receives=(Voucher,), correlated=BY_ORDER)

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
GUARDED_DISPATCHING = Program(
    goal=GuardedDispatched, accepts=FulfillOrder, interactions=(CAPTURE, GUARDED_SHIP)
)
FLAT_DISPATCHING = Program(
    goal=FlatDispatched, accepts=FulfillOrder, interactions=(CAPTURE, SHIP_ORDER)
)
FLAT_DECLARED_DISPATCHING = Program(
    goal=FlatDeclared, accepts=FulfillOrder, interactions=(CAPTURE, SHIP_ORDER)
)
DECLARED_DISPATCHING = Program(
    goal=DeclaredDispatched, accepts=FulfillOrder, interactions=(CAPTURE, SHIP_ORDER)
)
DOUBLING = Program(goal=Doubly, accepts=FulfillOrder, interactions=(CAPTURE, PING))
DOUBLING_DECLARED = Program(goal=DoublyDeclared, accepts=FulfillOrder, interactions=(CAPTURE, PING))
DOUBLING_PLAIN = Program(goal=DoublyPlain, accepts=FulfillOrder, interactions=(CAPTURE, PING))
VOUCHED = Program(goal=Vouched, accepts=FulfillOrder, interactions=(CAPTURE, VOUCHING))
SECONDING = Program(
    goal=SecondedRelease,
    accepts=FulfillOrder,
    interactions=(ORDER_APPROVALS, ORDER_CLOSING, SHIP_ORDER),
)
PREFACING = Program(
    goal=PrefacedRelease,
    accepts=FulfillOrder,
    interactions=(ORDER_APPROVALS, ORDER_CLOSING, SHIP_ORDER),
)
SECONDED_CATALOGUING = Program(
    goal=SecondedCatalogue, accepts=ReviewLines, interactions=(QUOTE, PING)
)
SECONDED_CATALOGUING_VIA_FACT = Program(
    goal=SecondedCatalogueViaFact, accepts=ReviewLines, interactions=(QUOTE, PING)
)
SETTLING = Program(goal=Settled, accepts=FulfillOrder, interactions=(CAPTURE, SHIP_ORDER))
RELEASING = Program(
    goal=Released, accepts=FulfillOrder, interactions=(ORDER_APPROVALS, ORDER_CLOSING, SHIP_ORDER)
)
FLAWED = Program(goal=Flawed, accepts=FulfillOrder)
CATALOGUING = Program(goal=Catalogued, accepts=ReviewLines, interactions=(QUOTE, PING))
CATALOGUING_VIA_DESK = Program(
    goal=CataloguedViaDesk, accepts=ReviewLines, interactions=(QUOTE, PING)
)
CATALOGUING_VIA_CHECKED_DESK = Program(
    goal=CataloguedViaCheckedDesk, accepts=ReviewLines, interactions=(QUOTE, PING)
)
PADDING = Program(goal=Padded, accepts=Count)
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
ONE_LINE = ReviewLines(order=Lined(id=OrderId("o-7"), lines=(line("tea", "w1"),)))
TALLY = Count(id=OrderId("o-7"), tally=Tally(counts=[1, 1]))
