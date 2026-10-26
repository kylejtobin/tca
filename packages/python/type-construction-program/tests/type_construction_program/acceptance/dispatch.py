"""The fulfillment story continued: how a paid order is dispatched is a declared choice.

A light parcel goes by post, a heavy one by courier; the two guards are complements over the
order's weight, so the evidence that selects one refuses the other. Other programs here vary
the guards to make the choice ambiguous, leave it with no branch, make a guard depend on
evidence that must still be acquired, or break a guard, and one asks the provider for an
approval it may decline. The same generic declarations are used throughout; nothing is added
to the engine for any of them."""

from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from type_construction.program import (
    Bound,
    Correlate,
    Goal,
    Interaction,
    Premises,
    Program,
    When,
)
from type_construction.world import AtLeast, AtMost, Beyond, Fact, Record, Scalar, Value

from .fulfillment import (
    Acknowledge,
    Acknowledged,
    Carrier,
    CollectPayment,
    Liftable,
    Order,
    OrderId,
    PaidOrder,
    Payments,
    Ship,
    Shipped,
    Total,
    Tracking,
    Weight,
)


class PostLimit(Scalar[Decimal]):
    """The most the post carries."""

    root: Decimal = Decimal(20)


class Floor(Scalar[Decimal]):
    """The total from which a parcel is insured."""

    root: Decimal = Decimal(40)


class Light(AtMost[Weight, PostLimit]):
    """The parcel can go by post."""


class Heavy(Beyond[Weight, PostLimit]):
    """The parcel needs a courier."""


class Insured(AtLeast[Total, Floor]):
    """The order is worth insuring."""


class PostRequest(Value):
    order: Annotated[OrderId, Bound("order", "id")]


class Posted(Fact):
    order: OrderId = Field(alias="order_id")
    tracking: Tracking


class Post(Interaction[PostRequest, Posted]):
    """Hand the parcel to the post."""

    source = Carrier
    correlation = (Correlate(result=("order",), request=("order",)),)


class CourierRequest(Value):
    order: Annotated[OrderId, Bound("order", "id")]


class Couriered(Fact):
    order: OrderId = Field(alias="order_id")
    tracking: Tracking


class SendCourier(Interaction[CourierRequest, Couriered]):
    """Book a courier."""

    source = Carrier
    correlation = (Correlate(result=("order",), request=("order",)),)


class ByPost(When[Annotated[Light, Premises(value=Bound("order", "weight"))], Posted]):
    """Post, once the parcel is known to be light."""


class ByCourier(When[Annotated[Heavy, Premises(value=Bound("order", "weight"))], Couriered]):
    """Courier, once the parcel is known to be heavy."""


class Dispatch(Record):
    """The outcome: the order and how it was sent."""

    order: Order
    sent: ByPost | ByCourier


DISPATCH = Program(Goal(Dispatch, accepts=("order",)), (Post, SendCourier), artifact="dispatch@1")


class ByCourierIfInsured(
    When[Annotated[Insured, Premises(value=Bound("order", "total"))], Couriered]
):
    """Courier, once the order is known to be worth insuring: not exclusive with ByPost."""


class Overlapping(Record):
    order: Order
    sent: ByPost | ByCourierIfInsured


OVERLAPPING = Program(
    Goal(Overlapping, accepts=("order",)), (Post, SendCourier), artifact="overlapping@1"
)


class NoFallback(Record):
    """Heavy or insured: a light, cheap order satisfies neither."""

    order: Order
    sent: ByCourier | ByCourierIfInsured


NO_FALLBACK = Program(
    Goal(NoFallback, accepts=("order",)), (Post, SendCourier), artifact="nofallback@1"
)


class ByCourierWhenPaid(When[PaidOrder, Couriered]):
    """Courier, once the order is paid: a guard whose evidence must be acquired."""


class Acquiring(Record):
    order: Order
    sent: ByPost | ByCourierWhenPaid


ACQUIRING = Program(
    Goal(Acquiring, accepts=("order",)),
    (Post, SendCourier, CollectPayment),
    artifact="acquiring@1",
)


class Broken(Record):
    """A guard that is malformed for every order: a rule, not a declared condition."""

    weight: Annotated[Weight, Bound("order", "weight")]

    @model_validator(mode="after")
    def never(self) -> Self:
        msg = "the scale is broken"
        raise ValueError(msg)


class ByCourierIfBroken(When[Broken, Couriered]): ...


class Malformed(Record):
    order: Order
    sent: ByPost | ByCourierIfBroken


MALFORMED = Program(
    Goal(Malformed, accepts=("order",)), (Post, SendCourier), artifact="malformed@1"
)


class AuthRequest(Value):
    of: Annotated[OrderId, Bound("order", "id")]
    amount: Annotated[Total, Bound("order", "total")]


class Approved(Fact):
    """The provider approves."""

    order: OrderId = Field(alias="order_id")
    status: Literal["approved"]


class Declined(Fact):
    """The provider states its refusal: a record, not an absence."""

    order: OrderId = Field(alias="order_id")
    status: Literal["declined"]
    reason: str


class Authorize(Interaction[AuthRequest, Approved | Declined]):
    """Ask the provider; it approves or declines."""

    source = Payments
    correlation = (Correlate(result=("order",), request=("of",)),)


class ShipWhenApproved(When[Annotated[Approved, Bound("decision")], Shipped]):
    """Shipment demanded only by an approval; a stated refusal establishes nothing."""


class Authorized(Record):
    order: Order
    decision: Approved | Declined
    shipment: ShipWhenApproved


AUTHORIZED = Program(
    Goal(Authorized, accepts=("order",)), (Authorize, Ship), artifact="authorized@1"
)


class ShipWhenLiftable(
    When[Annotated[Liftable, Premises(value=Bound("order", "weight"))], Shipped]
):
    """Shipment demanded once the parcel is liftable."""


class ShipWhenPaidThenLiftable(When[PaidOrder, ShipWhenLiftable]):
    """Nested: paid first, then liftable, then shipment."""


class Nested(Record):
    order: Order
    shipment: ShipWhenPaidThenLiftable
    acknowledged: Acknowledged


NESTED = Program(
    Goal(Nested, accepts=("order",)), (CollectPayment, Ship, Acknowledge), artifact="nested@1"
)
