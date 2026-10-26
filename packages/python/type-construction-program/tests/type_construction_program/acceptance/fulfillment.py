"""One business program: an order is fulfilled once its payment covers its total.

An order has a total. The payment provider reports payment for that order when asked. A
``PaidOrder`` holds the order, the payment and the reusable relation that the payment covers
the total, with the relation's operands bound to this order and this payment. Shipment is
demanded by one consumer, ``ShipWhenPaid``, only after a complete ``PaidOrder`` constructs;
the carrier ships only an order it can lift. An acknowledgement to the customer is independent
of all of that. Nothing here is engine machinery: these are Pydantic types and the
relationships the engine cannot read from a type alone."""

from decimal import Decimal
from typing import Annotated, Self

from pydantic import BeforeValidator, Field, StringConstraints, model_validator

from type_construction.program import (
    Bound,
    Correlate,
    Goal,
    Interaction,
    Premises,
    Program,
    Source,
    When,
)
from type_construction.world import AtLeast, AtMost, Fact, Record, Scalar, Value


def normalized(given: object) -> object:
    """A reference as the business writes it: stripped and upper-case, before its pattern."""
    return given.strip().upper() if isinstance(given, str) else given


class OrderId(Scalar[str]):
    """An order's identity, normalized before its pattern is checked."""

    root: Annotated[str, BeforeValidator(normalized), StringConstraints(pattern=r"^ORD-[0-9]+$")]


class Total(Scalar[Decimal]):
    """What an order costs."""

    root: Decimal = Field(gt=0)


class Paid(Scalar[Decimal]):
    """What a payment paid."""

    root: Decimal = Field(gt=0)


class Weight(Scalar[Decimal]):
    """What a parcel weighs."""

    root: Decimal = Field(gt=0)


class Limit(Scalar[Decimal]):
    """The most the carrier lifts."""

    root: Decimal = Decimal(30)


class Reference(Scalar[str]):
    """The provider's reference for a payment, normalized before its pattern is checked."""

    root: Annotated[str, BeforeValidator(normalized), StringConstraints(pattern=r"^PAY-[0-9]+$")]


class Tracking(Scalar[str]):
    """The carrier's tracking number."""

    root: str = Field(min_length=1)


class Order(Value):
    """What is being fulfilled."""

    id: OrderId
    total: Total
    weight: Weight


class Payments(Source):
    """The payment provider."""


class Carrier(Source):
    """The carrier."""


class Mail(Source):
    """The customer's mailbox."""


class PaymentRequest(Value):
    """Request collection of this order's total."""

    of: Annotated[OrderId, Bound("order", "id")]
    amount: Annotated[Total, Bound("order", "total")]


class PaymentReported(Fact):
    """What the provider says it collected, under its names."""

    order: OrderId = Field(alias="order_id")
    amount: Paid
    reference: Reference


class PaymentReceipt(Fact):
    """The provider's acknowledgement that it will collect: a reference, not a payment."""

    reference: Reference


class CollectPayment(Interaction[PaymentRequest, PaymentReported]):
    """Ask the provider to collect the order's total; it may answer at once or later."""

    source = Payments
    receipt = PaymentReceipt
    correlation = (Correlate(result=("order",), request=("of",)),)
    recovery = "reconcile"


class Covers(AtLeast[Paid, Total]):
    """The payment is at least the total."""


class PaidOrder(Record):
    """This order, this payment, and that the payment covers the total."""

    order: Annotated[Order, Bound("order")]
    payment: PaymentReported
    covered: Annotated[
        Covers, Premises(value=Bound("payment", "amount"), bound=Bound("order", "total"))
    ]


class ShipmentRequest(Value):
    """What the carrier is asked: to ship this order."""

    order: Annotated[OrderId, Bound("order", "id")]


class Shipped(Fact):
    """What the carrier says it shipped."""

    order: OrderId = Field(alias="order_id")
    tracking: Tracking
    weight: Weight


class Liftable(AtMost[Weight, Limit]):
    """The parcel is within what the carrier lifts."""


class Ship(Interaction[ShipmentRequest, Shipped]):
    """Ask the carrier to ship; eligible only for a parcel it can lift, whoever demands it."""

    source = Carrier
    eligibility = Annotated[Liftable, Premises(value=Bound("order", "weight"))]
    correlation = (Correlate(result=("order",), request=("order",)),)
    recovery = "reconcile"


class ShipWhenPaid(When[PaidOrder, Shipped]):
    """Shipment is demanded by this consumer once the order is paid. The shipment must weigh
    what the order weighs: a rule about the result, checked when the result exists."""

    @model_validator(mode="after")
    def weighed(self) -> Self:
        if self.result.weight != self.condition.order.weight:
            msg = "the shipment does not weigh the order"
            raise ValueError(msg)
        return self


class AcknowledgeRequest(Value):
    """What the mailbox is asked: to acknowledge this order."""

    order: Annotated[OrderId, Bound("order", "id")]


class Acknowledged(Fact):
    """That the customer was told."""

    order: OrderId = Field(alias="order_id")


class Acknowledge(Interaction[AcknowledgeRequest, Acknowledged]):
    """Tell the customer the order was received; safe to repeat."""

    source = Mail
    correlation = (Correlate(result=("order",), request=("order",)),)
    recovery = "retry"


class Fulfillment(Record):
    """The outcome: the order, its shipment once paid, and the acknowledgement."""

    order: Order
    shipment: ShipWhenPaid
    acknowledged: Acknowledged


FULFILL = Goal(Fulfillment, accepts=("order",))
"""Fulfill one order."""

FULFILLMENT = Program(FULFILL, (CollectPayment, Ship, Acknowledge), artifact="fulfillment@1")
"""The program artifact under test."""

ORDER = Order(id=OrderId("ORD-7"), total=Total(Decimal(50)), weight=Weight(Decimal(12)))
"""An order of 50, light enough to ship."""

HEAVY = Order(id=OrderId("ORD-8"), total=Total(Decimal(50)), weight=Weight(Decimal(45)))
"""An order of 50 the carrier cannot lift."""
