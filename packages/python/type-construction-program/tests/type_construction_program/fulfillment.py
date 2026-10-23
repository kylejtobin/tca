"""An order that ships once a payment covers it and a reviewer approves it.

Business declarations only. Nothing here says in what order anything happens, whether the
payment provider answers at once or later, or what a test will deliver. ``Shipped`` needs a
``ShippingAuthority``, which needs the ``Captured`` payment and the rule that it covers the
total; the ``ShipRequest`` needs that authority and an ``Approved`` review. The provider may
answer a charge with ``Captured``, with ``Declined``, or with a ``ChargeAccepted`` receipt and the
result later. ``Refused`` is the business conclusion when the provider declines.
"""

from decimal import Decimal

from pydantic import Field

from type_construction.program import Correlation, Interaction, Program, Source
from type_construction.world import AtLeast, Fact, Record, Scalar, Value


class OrderId(Scalar[str]):
    root: str = Field(min_length=1)


class Total(Scalar[Decimal]):
    root: Decimal = Field(gt=0)


class Paid(Scalar[Decimal]):
    root: Decimal = Field(ge=0)


class ChargeId(Scalar[str]):
    root: str = Field(min_length=1)


class HoldId(Scalar[str]):
    root: str = Field(min_length=1)


class DeclineReason(Scalar[str]):
    root: str = Field(min_length=1)


class Reviewer(Scalar[str]):
    root: str = Field(min_length=1)


class Tracking(Scalar[str]):
    root: str = Field(min_length=1)


class Order(Value):
    id: OrderId
    total: Total


class FulfillOrder(Value):
    """The command: fulfill this order."""

    order: Order


class ChargeRequest(Value):
    """What the program sends the payment provider."""

    order: OrderId
    amount: Total


class HoldRequest(Value):
    """What the program sends the payment provider to hold funds: the same body as a charge."""

    order: OrderId
    amount: Total


class ChargeAccepted(Record):
    """The provider's receipt: the charge is accepted, its result will follow."""

    charge: ChargeId = Field(alias="id")


class Captured(Record):
    order: OrderId = Field(alias="order_id")
    amount: Paid
    charge: ChargeId = Field(alias="id")


class Declined(Record):
    order: OrderId = Field(alias="order_id")
    reason: DeclineReason


class Held(Record):
    order: OrderId = Field(alias="order_id")
    hold: HoldId = Field(alias="id")


class Approved(Record):
    order: OrderId = Field(alias="order_id")
    reviewer: Reviewer


class ShipmentAccepted(Record):
    order: OrderId = Field(alias="order_id")
    tracking: Tracking


class Covers(AtLeast[Paid, Total]):
    """The payment is at least the total."""


class ShippingAuthority(Fact):
    order: Order
    payment: Captured
    covered: Covers


class ShipRequest(Value):
    """What the program sends the carrier: it requires the authority and the approval."""

    authority: ShippingAuthority
    approval: Approved


class Shipped(Fact):
    authority: ShippingAuthority
    shipment: ShipmentAccepted


class Refused(Fact):
    order: Order
    declined: Declined


class Fulfilled(Fact):
    """The outcome: shipped, or refused because the provider declined."""

    outcome: Shipped | Refused


class Settled(Fact):
    """Funds held and captured for one order: two operations with equal request bodies."""

    order: Order
    hold: Held
    capture: Captured


PAYMENTS = Source("payments")
APPROVALS = Source("approvals")
CARRIER = Source("carrier")

BY_ORDER = (Correlation(received="order", subject="order.id"),)

CHARGE = Interaction(
    source=PAYMENTS,
    sends=ChargeRequest,
    acknowledges=ChargeAccepted,
    receives=(Captured, Declined),
    correlated=BY_ORDER,
)
HOLD = Interaction(source=PAYMENTS, sends=HoldRequest, receives=(Held,), correlated=BY_ORDER)
APPROVAL = Interaction(source=APPROVALS, receives=(Approved,), correlated=BY_ORDER)
SHIP = Interaction(
    source=CARRIER, sends=ShipRequest, receives=(ShipmentAccepted,), correlated=BY_ORDER
)

FULFILLMENT = Program(goal=Fulfilled, accepts=FulfillOrder, interactions=(CHARGE, APPROVAL, SHIP))
SETTLEMENT = Program(goal=Settled, accepts=FulfillOrder, interactions=(HOLD, CHARGE))

ORDER = FulfillOrder(order=Order(id=OrderId("o-1"), total=Total(Decimal("50.00"))))
