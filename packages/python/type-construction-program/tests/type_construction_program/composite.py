"""Declarations whose features interact: one operation under two collections, a collection source
per element with its own closure, a condition over delayed evidence and the effect it governs, a
correlation unique only as a whole, and a request and a fact with native aliases.

An order holds lines in a cart and lines among gifts. Every line is a ``Line``, with a sku and
the warehouse it ships from; two lines may share a sku. The carrier ships one line per request,
and the same request is sent for a cart line and a gift line. Reviewers approve lines, several
approvals per line, and say per line when that line's review is closed. An order is eligible
when an ordinary validator on the fact says so; where the business means the shipment to wait
for that, it says so with ``When``, and where it holds both jointly it says nothing. Nothing here
is written for the interpreter.
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

from type_construction.program import Binding, Correlation, Interaction, Program, Source, When
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
    relation: the interpreter does not read it, and does not need to."""

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


class Quotes(Fact):
    """At least two quotes, by a native field constraint at a construction boundary of its own."""

    quotes: tuple[Quoted, ...] = Field(min_length=2)


class Catalogued(Fact):
    """At least two lines quoted, by a constraint on the goal's own field, and the desk pinged:
    joint construction. The constraint refuses the goal with fewer quotes; it orders nothing
    between the quotes and the ping, since nothing here declares that the ping waits."""

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


class CataloguedWhenQuoted(Fact):
    """The desk pinged only once at least two lines are quoted: the condition at a boundary of
    its own, and the ping declared to wait for it."""

    order: Lined
    pinged: When[Quotes, Pinged]


class CataloguedWhenQuotedViaDesk(Fact):
    """The same, with the ping in a plain fact under the condition."""

    order: Lined
    desk: When[Quotes, PingDesk]


class CataloguedWhenQuotedViaCheckedDesk(Fact):
    """The same, with the ping behind an opaque identity validator under the condition."""

    order: Lined
    desk: When[Quotes, CheckedPingDesk]


class GatedDesk(Fact):
    """The conditional inside a plain fact: the wrapper around the ``When``."""

    pinged: When[Quotes, Pinged]


class CataloguedViaGatedDesk(Fact):
    """The same, with the conditional wrapped rather than the result."""

    order: Lined
    desk: GatedDesk


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
    """The shipment demanded only once the order is eligible: the business says the shipment
    waits, and says it with ``When``. The eligibility is judged by its own validator at its own
    boundary; the evaluator reads nothing of it."""

    shipment: When[Eligible, OrderShipped]


class PaidShipment(Fact):
    """The payment and the shipment together: a result that holds a record its condition also
    holds."""

    payment: Captured
    shipment: OrderShipped


class DispatchedWithPayment(Fact):
    """The paid shipment demanded only once the order is eligible: the condition and the result
    share the capture, which the condition demands; the conditional gates the shipment alone."""

    shipment: When[Eligible, PaidShipment]


class JointlyDispatched(Fact):
    """The eligibility and the shipment both demanded, jointly: nothing here says the shipment
    waits for the eligibility, so it does not. The validator on ``Eligible`` refuses the
    eligibility, and with it this fact, when the capture comes back short; it orders nothing."""

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
    payment and the shipment: natively, the same business values are accepted and refused. Like
    ``JointlyDispatched`` it demands everything jointly; the validator is a postcondition of the
    goal, judged when the goal constructs."""

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


class TakeNotes(Value):
    """The command: ship an order with its notes, each note revalidated wherever it is held."""

    order: Priced
    notes: tuple[Noted, ...]


class Noting(Fact):
    """The notes at a construction boundary of their own, and the shipment, jointly."""

    noted: Notes
    shipment: OrderShipped


class FlatNoting(Fact):
    """The notes on the goal's own field, beside the shipment, jointly: the goal constructs
    natively once the shipment is there, with the context its notes require."""

    notes: tuple[Noted, ...] = Field(min_length=1)
    shipment: OrderShipped


class ShippedWhenNoted(Fact):
    """The shipment demanded only once the notes are constructed at their own boundary."""

    shipment: When[Notes, OrderShipped]


class Counted(Value):
    """A note validated again wherever it is held, whose validator returns a replacement counting
    the validations it has been through: natively, every class that holds it validates it once
    more, and the count says how many boundaries it crossed."""

    model_config = ConfigDict(
        frozen=True, strict=True, extra="forbid", revalidate_instances="always"
    )

    reviewer: Reviewer
    passes: int = 0

    @model_validator(mode="after")
    def _counted(self) -> Self:
        return self.model_copy(update={"passes": self.passes + 1})


class CountedOrder(Value):
    """The command: ship an order with one counted note."""

    order: Priced
    note: Counted


class ShippedWhenCounted(Fact):
    """The shipment demanded once the note is there: the conditional is one more class holding
    the note, so native construction validates the note once more at it."""

    shipment: When[Counted, OrderShipped]


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
    """The shipment demanded only once the order is eligible by a declared relation: the same
    business as ``Dispatched``, with the condition's check written as a relation inside the
    condition's boundary rather than as a validator."""

    shipment: When[DeclaredEligible, OrderShipped]


class FlatDeclared(Fact):
    """The same condition as a declared relation on the goal that holds everything, and the
    shipment demanded only once the relation holds: the relation is a construction boundary of
    its own, so it is the condition directly, with no fact around it."""

    order: Priced
    payment: Captured
    matched: Matches
    shipment: When[Matches, OrderShipped]


class Doubly(Fact):
    """Two constructions, each behind a validator the evaluator does not read, each needing its
    own effect, and nothing declared between them: joint."""

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
    """The shipment demanded only once the approvals, padded, are at least two."""

    shipment: When[Seconded, OrderShipped]


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
    shipment: When[Prefaced, OrderShipped]


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


class SecondedCatalogueWhenQuoted(Fact):
    """The desk pinged only once the quotes, padded, are at least two."""

    order: Lined
    pinged: When[SecondedQuotes, Pinged]


class Settled(Fact):
    """The shipment demanded only once the capture is covered by an annotated validator."""

    shipment: When[Covered, OrderShipped]


class Released(Fact):
    """The shipment demanded only once the order is endorsed by at least two approvals."""

    shipment: When[Endorsed, OrderShipped]


class ShipmentChecked(Fact):
    """A condition that requires the shipment it would govern: the capture matches the total,
    checked on a fact that also holds the shipment."""

    order: Priced
    payment: Captured
    shipment: OrderShipped

    @model_validator(mode="after")
    def _matches(self) -> Self:
        if self.payment.amount.root != self.order.total.root:
            msg = "the capture does not match the total"
            raise ValueError(msg)
        return self


class Circular(Fact):
    """The shipment demanded only once a condition that itself needs the shipment holds: an
    order that cannot be kept, which the program refuses at declaration."""

    shipment: When[ShipmentChecked, OrderShipped]


class LineQuoted(Fact):
    """One line and its quote."""

    line: Line
    quote: Quote


class LineShippedWhenQuoted(Fact):
    """One line shipped only once it is quoted: a conditional per element."""

    line: Line
    shipment: When[LineQuoted, LineShipped]


class QuotedShipments(Fact):
    """Every line quoted and then shipped, each on its own."""

    order: Lined
    lines: tuple[LineShippedWhenQuoted, ...]


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
JOINT_DISPATCHING = Program(
    goal=JointlyDispatched, accepts=FulfillOrder, interactions=(CAPTURE, SHIP_ORDER)
)
DISPATCHING_WITH_PAYMENT = Program(
    goal=DispatchedWithPayment, accepts=FulfillOrder, interactions=(CAPTURE, SHIP_ORDER)
)
GUARDED_DISPATCHING = Program(
    goal=GuardedDispatched, accepts=FulfillOrder, interactions=(CAPTURE, GUARDED_SHIP)
)
FLAT_DISPATCHING = Program(
    goal=FlatDispatched, accepts=FulfillOrder, interactions=(CAPTURE, SHIP_ORDER)
)
FLAT_DECLARED_DISPATCHING = Program(
    goal=FlatDeclared, accepts=FulfillOrder, interactions=(CAPTURE, SHIP_ORDER)
)
NOTING = Program(goal=Noting, accepts=TakeNotes, interactions=(SHIP_ORDER,))
FLAT_NOTING = Program(goal=FlatNoting, accepts=TakeNotes, interactions=(SHIP_ORDER,))
NOTED_SHIPPING = Program(goal=ShippedWhenNoted, accepts=TakeNotes, interactions=(SHIP_ORDER,))
COUNTED_SHIPPING = Program(
    goal=ShippedWhenCounted, accepts=CountedOrder, interactions=(SHIP_ORDER,)
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
SECONDED_CATALOGUING_WHEN_QUOTED = Program(
    goal=SecondedCatalogueWhenQuoted, accepts=ReviewLines, interactions=(QUOTE, PING)
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
CATALOGUING_WHEN_QUOTED = Program(
    goal=CataloguedWhenQuoted, accepts=ReviewLines, interactions=(QUOTE, PING)
)
CATALOGUING_WHEN_QUOTED_VIA_DESK = Program(
    goal=CataloguedWhenQuotedViaDesk, accepts=ReviewLines, interactions=(QUOTE, PING)
)
CATALOGUING_WHEN_QUOTED_VIA_CHECKED_DESK = Program(
    goal=CataloguedWhenQuotedViaCheckedDesk, accepts=ReviewLines, interactions=(QUOTE, PING)
)
CATALOGUING_VIA_GATED_DESK = Program(
    goal=CataloguedViaGatedDesk, accepts=ReviewLines, interactions=(QUOTE, PING)
)
QUOTED_SHIPPING = Program(
    goal=QuotedShipments, accepts=ReviewLines, interactions=(QUOTE, SHIP_LINE)
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
TAKEN = TakeNotes.model_validate(
    {"order": PRICED.order, "notes": ({"reviewer": Reviewer("ren")},)}, context={}
)
"""An order with one note, constructed under a context as its notes require."""
COUNTED = CountedOrder.model_validate({"order": PRICED.order, "note": {"reviewer": "ren"}})
"""An order with one counted note, validated once by the time it is accepted, as the order's
field."""
ONE_LINE = ReviewLines(order=Lined(id=OrderId("o-7"), lines=(line("tea", "w1"),)))
TALLY = Count(id=OrderId("o-7"), tally=Tally(counts=[1, 1]))
