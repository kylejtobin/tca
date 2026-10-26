"""Closure composed: two orders settled side by side, parcels each tracked by their own scans,
and installments closed by a deadline a clock adapter reports. Each collection closes by its
own declared rule and nothing else."""

from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints

from type_construction.program import (
    EACH,
    Bound,
    Correlate,
    Goal,
    Interaction,
    Members,
    PerMember,
    Premises,
    Program,
    Receive,
    Source,
)
from type_construction.world import Fact, Record, Scalar, Value

from .fulfillment import Carrier, Order, OrderId, PaymentReported
from .installments import InstallmentsReported, PaidTotal, Receipted, SendReceipt, Settled


class Settling(Record):
    """One order's installments and their total; which order is bound where it is used."""

    order: Order
    installments: Annotated[
        tuple[PaymentReported, ...], Members(reported=InstallmentsReported, closed_by=Settled)
    ]
    paid: Annotated[PaidTotal, Premises(of=Bound("installments", EACH, "amount"))]


class Pair(Record):
    """Two orders settled independently."""

    first: Order
    second: Order
    one: Annotated[Settling, Premises(order=Bound("first"))]
    two: Annotated[Settling, Premises(order=Bound("second"))]


PAIR = Program(
    Goal(Pair, accepts=("first", "second")), (InstallmentsReported, Settled), artifact="pair@1"
)


class ParcelRef(Scalar[str]):
    root: Annotated[str, StringConstraints(pattern=r"^PCL-[0-9]+$")]


class Location(Scalar[str]):
    root: str = Field(min_length=1)


class ParcelDispatched(Fact):
    """The carrier took one parcel of the order."""

    order: OrderId = Field(alias="order_id")
    reference: ParcelRef


class DispatchComplete(Fact):
    """The carrier took the last parcel of the order."""

    order: OrderId = Field(alias="order_id")


class ScanReported(Fact):
    """One parcel passed one place."""

    parcel: ParcelRef = Field(alias="parcel_ref")
    location: Location


class ParcelDelivered(Fact):
    """One parcel's journey is over."""

    parcel: ParcelRef = Field(alias="parcel_ref")


class ParcelsDispatched(Receive[ParcelDispatched]):
    source = Carrier
    correlation = (Correlate(result=("order",), premise=Bound("order", "id")),)


class AllDispatched(Receive[DispatchComplete]):
    source = Carrier
    correlation = (Correlate(result=("order",), premise=Bound("order", "id")),)


class Scans(Receive[ScanReported]):
    source = Carrier
    correlation = (Correlate(result=("parcel",), premise=Bound("member", "reference")),)


class Delivered(Receive[ParcelDelivered]):
    source = Carrier
    correlation = (Correlate(result=("parcel",), premise=Bound("member", "reference")),)


class Tracked(Record):
    """One parcel and the scans of its own journey, closed by its own delivery."""

    parcel: Annotated[ParcelDispatched, Bound("member")]
    scans: Annotated[tuple[ScanReported, ...], Members(reported=Scans, closed_by=Delivered)]


class Delivery(Record):
    order: Order
    parcels: Annotated[
        tuple[ParcelDispatched, ...], Members(reported=ParcelsDispatched, closed_by=AllDispatched)
    ]
    tracked: Annotated[tuple[Tracked, ...], PerMember("parcels")]


DELIVERY = Program(
    Goal(Delivery, accepts=("order",)),
    (ParcelsDispatched, AllDispatched, Scans, Delivered),
    artifact="delivery@1",
)


class Deadline(Scalar[datetime]):
    """A moment the business set."""


class Clock(Source):
    """The clock adapter: it arranges a deadline and reports its expiry."""


class DeadlineRequest(Value):
    at: Annotated[Deadline, Bound("due")]


class Scheduled(Fact):
    """The clock will report when the deadline passes: not yet expiry."""

    at: Deadline


class Expired(Fact):
    """The deadline passed, as the clock recorded it."""

    at: Deadline


class Expire(Interaction[DeadlineRequest, Expired]):
    source = Clock
    receipt = Scheduled
    correlation = (Correlate(result=("at",), request=("at",)),)


class Timed(Record):
    """Installments accepted until the deadline the clock reports; each acknowledged as it
    arrives; the total known only once the deadline has passed."""

    order: Order
    due: Deadline
    deadline: Expired
    installments: Annotated[
        tuple[PaymentReported, ...],
        Members(reported=InstallmentsReported, closed_by=Bound("deadline")),
    ]
    receipts: Annotated[tuple[Receipted, ...], PerMember("installments")]
    paid: Annotated[PaidTotal, Premises(of=Bound("installments", EACH, "amount"))]


TIMED = Program(
    Goal(Timed, accepts=("order", "due")),
    (InstallmentsReported, Expire, SendReceipt),
    artifact="timed@1",
)
