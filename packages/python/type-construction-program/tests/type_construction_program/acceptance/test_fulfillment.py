"""Product §4; architecture §§6, 8: conditional work, eligibility, admission and ownership.

Tests use the retained public declaration spelling; behavior is authoritative, not that
spelling. No engine implementation exists yet. Collection must fail until it is supplied.
"""

from decimal import Decimal
from typing import Annotated

import pytest
from pydantic import AfterValidator

from type_construction.program import (
    Blocked,
    Completed,
    Goal,
    Host,
    Observation,
    Program,
    When,
)
from type_construction.world import Record

from .fulfillment import (
    FULFILLMENT,
    HEAVY,
    ORDER,
    Acknowledge,
    Acknowledged,
    Carrier,
    CollectPayment,
    Covers,
    Fulfillment,
    Mail,
    Order,
    OrderId,
    Paid,
    PaidOrder,
    PaymentReported,
    Payments,
    Ship,
    Shipped,
    ShipWhenPaid,
    Total,
    Tracking,
    Weight,
)
from .support import Calls, names, payment, payment_json, proposal


def test_missing_payment_acquires_evidence_and_runs_independent_work_without_shipping() -> None:
    collector, shipper, mailbox = Calls(), Calls(), Calls()
    host = Host(FULFILLMENT, {"CollectPayment": collector, "Ship": shipper, "Acknowledge": mailbox})
    host.open("order", {"order": ORDER})

    result = host.advance("order").result

    assert names(result) == {"CollectPayment", "Acknowledge"}
    assert len(result.ready) == 2
    assert collector.received == shipper.received == mailbox.received == []
    host.perform("order", proposal(result, "CollectPayment").effect)
    host.perform("order", proposal(result, "Acknowledge").effect)
    assert len(collector.received) == len(mailbox.received) == 1
    assert shipper.received == []
    assert names(host.advance("order").result) == set()


@pytest.mark.parametrize(
    "amount,can_ship", [("20", False), ("49.99", False), ("50", True), ("50.01", True)]
)
def test_payment_boundary_controls_actual_shipment(*, amount: str, can_ship: bool) -> None:
    collector, shipper = Calls(), Calls()
    host = Host(FULFILLMENT, {"CollectPayment": collector, "Ship": shipper})
    host.open("order", {"order": ORDER})
    collect = proposal(host.advance("order").result, "CollectPayment")
    host.perform("order", collect.effect)

    host.deliver("order", payment(collector.received[0][1], amount))
    result = host.advance("order").result

    assert names(result) == ({"Ship", "Acknowledge"} if can_ship else {"Acknowledge"})
    assert len(host.state("order").evidence) == 1
    if can_ship:
        ship = proposal(result, "Ship")
        host.perform("order", ship.effect)
        assert len(shipper.received) == 1
        assert shipper.received[0][0].request.order == OrderId("ORD-7")
    else:
        assert shipper.received == []
        assert all(i.effect.interaction != "Ship" for i in host.state("order").intents)


@pytest.mark.parametrize(
    "order,can_ship", [(ORDER, True), (HEAVY, False)], ids=["eligible", "too-heavy"]
)
def test_payment_does_not_override_carrier_eligibility(*, order: Order, can_ship: bool) -> None:
    collector, shipper = Calls(), Calls()
    host = Host(FULFILLMENT, {"CollectPayment": collector, "Ship": shipper})
    host.open("order", {"order": order})
    host.perform("order", proposal(host.advance("order").result, "CollectPayment").effect)
    attempt = collector.received[0][1]

    host.deliver(
        "order",
        Observation(
            Payments,
            "paid",
            "result",
            payment_json(order.id.root, "50"),
            "json",
            about=attempt.effect,
            claims=attempt,
        ),
    )
    result = host.advance("order").result

    assert ("Ship" in names(result)) is can_ship
    if can_ship:
        host.perform("order", proposal(result, "Ship").effect)
    assert len(shipper.received) == int(can_ship)


@pytest.mark.parametrize(
    "source,order_id,amount",
    [(Mail, "ORD-7", "50"), (Payments, "ORD-9", "50"), (Payments, "ORD-7", "-5")],
    ids=["wrong-source", "wrong-order", "malformed"],
)
def test_rejected_report_cannot_authorize_shipping_but_valid_report_can(
    source: type, order_id: str, amount: str
) -> None:
    collector, shipper = Calls(), Calls()
    host = Host(FULFILLMENT, {"CollectPayment": collector, "Ship": shipper})
    host.open("order", {"order": ORDER})
    host.perform("order", proposal(host.advance("order").result, "CollectPayment").effect)
    attempt = collector.received[0][1]

    host.deliver(
        "order",
        Observation(
            source,
            "bad",
            "result",
            payment_json(order_id, amount),
            "json",
            about=attempt.effect,
            claims=attempt,
        ),
    )

    assert host.state("order").evidence == ()
    assert len(host.state("order").observations) == 1
    assert "Ship" not in names(host.advance("order").result)
    assert shipper.received == []
    host.deliver("order", payment(attempt, "50", "good"))
    host.perform("order", proposal(host.advance("order").result, "Ship").effect)
    assert len(shipper.received) == 1


def test_receipt_waits_for_payment_result() -> None:
    collector, shipper = Calls(), Calls()
    host = Host(FULFILLMENT, {"CollectPayment": collector, "Ship": shipper})
    host.open("order", {"order": ORDER})
    host.perform("order", proposal(host.advance("order").result, "CollectPayment").effect)
    attempt = collector.received[0][1]

    host.deliver(
        "order",
        Observation(
            Payments,
            "receipt",
            "receipt",
            {"reference": " pay-9 "},
            about=attempt.effect,
            claims=attempt,
        ),
    )
    waiting = host.advance("order").result

    assert "Ship" not in names(waiting)
    assert "CollectPayment" not in names(waiting)
    assert shipper.received == []
    host.deliver("order", payment(attempt, "50"))
    host.perform("order", proposal(host.advance("order").result, "Ship").effect)
    assert len(shipper.received) == 1


def test_equal_orders_in_distinct_invocations_do_not_share_evidence() -> None:
    collector = Calls()
    host = Host(FULFILLMENT, {"CollectPayment": collector})
    for invocation in ("one", "two"):
        host.open(invocation, {"order": ORDER})
        host.perform(invocation, proposal(host.advance(invocation).result, "CollectPayment").effect)
    first, second = (attempt for _, attempt in collector.received)

    host.deliver("two", payment(first, "50"))
    host.deliver("one", payment(first, "50"))

    assert first.effect != second.effect
    assert host.state("two").evidence == ()
    assert "Ship" in names(host.advance("one").result)
    assert "Ship" not in names(host.advance("two").result)


def referenced(order: PaidOrder) -> PaidOrder:
    if order.payment.reference.root != "PAY-9":
        message = "payment is outside the required series"
        raise ValueError(message)
    return order


class ReferencedShipment(When[Annotated[PaidOrder, AfterValidator(referenced)], Shipped]):
    pass


class ReferencedFulfillment(Record):
    order: Order
    shipment: ReferencedShipment
    acknowledged: Acknowledged


@pytest.mark.parametrize("reference,can_ship", [(" pay-9 ", True), ("pay-1", False)])
def test_complete_condition_metadata_governs_dispatch(*, reference: str, can_ship: bool) -> None:
    program = Program(
        Goal(ReferencedFulfillment, accepts=("order",)),
        (CollectPayment, Ship, Acknowledge),
        artifact="referenced@1",
    )
    collector, shipper = Calls(), Calls()
    host = Host(program, {"CollectPayment": collector, "Ship": shipper})
    host.open("order", {"order": ORDER})
    host.perform("order", proposal(host.advance("order").result, "CollectPayment").effect)
    attempt = collector.received[0][1]

    host.deliver(
        "order",
        Observation(
            Payments,
            "paid",
            "result",
            payment_json("ORD-7", "50", reference),
            "json",
            about=attempt.effect,
            claims=attempt,
        ),
    )
    result = host.advance("order").result

    assert ("Ship" in names(result)) is can_ship
    if can_ship:
        host.perform("order", proposal(result, "Ship").effect)
    assert len(shipper.received) == int(can_ship)


@pytest.mark.parametrize("reported_weight", ["12", "13"], ids=["valid-holder", "holder-refuses"])
def test_holder_validation_runs_after_justified_shipment(reported_weight: str) -> None:
    collector, shipper, mailbox = Calls(), Calls(), Calls()
    host = Host(FULFILLMENT, {"CollectPayment": collector, "Ship": shipper, "Acknowledge": mailbox})
    host.open("order", {"order": ORDER})
    first = host.advance("order").result
    host.perform("order", proposal(first, "CollectPayment").effect)
    host.perform("order", proposal(first, "Acknowledge").effect)
    host.deliver("order", payment(collector.received[0][1], "50"))
    acknowledged = mailbox.received[0][1]
    host.deliver(
        "order",
        Observation(
            Mail,
            "ack",
            "result",
            {"order_id": "ORD-7"},
            about=acknowledged.effect,
            claims=acknowledged,
        ),
    )
    host.perform("order", proposal(host.advance("order").result, "Ship").effect)
    shipped = shipper.received[0][1]

    host.deliver(
        "order",
        Observation(
            Carrier,
            "shipped",
            "result",
            {"order_id": "ORD-7", "tracking": "T-1", "weight": Decimal(reported_weight)},
            about=shipped.effect,
            claims=shipped,
        ),
    )
    result = host.advance("order").result

    assert len(shipper.received) == 1
    assert names(result) == set()
    if reported_weight == "13":
        assert isinstance(result, Blocked)
    else:
        expected = Fulfillment(
            order=ORDER,
            shipment=ShipWhenPaid(
                condition=PaidOrder(
                    order=ORDER,
                    payment=PaymentReported.model_validate_json(payment_json("ORD-7", "50")),
                    covered=Covers(value=Paid(Decimal(50)), bound=Total(Decimal(50))),
                ),
                result=Shipped(
                    order_id=OrderId("ORD-7"), tracking=Tracking("T-1"), weight=Weight(Decimal(12))
                ),
            ),
            acknowledged=Acknowledged(order_id=OrderId("ORD-7")),
        )
        assert isinstance(result, Completed)
        assert result.outcome.value == expected
    assert names(host.advance("order").result) == set()
    assert len(shipper.received) == 1


def test_json_input_is_normalized_and_owned_before_work_is_requested() -> None:
    host = Host(FULFILLMENT, {})

    state = host.open("order", {"order": '{"id":" ord-7 ","total":"50","weight":"12"}'}, "json")

    assert state.accepted["order"] == ORDER
    assert names(host.advance("order").result) == {"CollectPayment", "Acknowledge"}
