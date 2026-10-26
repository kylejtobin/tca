"""Product §4; architecture §6: alternatives, decision acquisition and nested conditions."""

from decimal import Decimal

import pytest

from type_construction.program import Blocked, Completed, Frontier, Goal, Host, Observation, Program
from type_construction.world import Record

from .dispatch import (
    ACQUIRING,
    AUTHORIZED,
    DISPATCH,
    MALFORMED,
    NESTED,
    NO_FALLBACK,
    OVERLAPPING,
    ByPost,
    Dispatch,
    Light,
    Posted,
    PostLimit,
)
from .fulfillment import (
    FULFILLMENT,
    HEAVY,
    ORDER,
    Acknowledge,
    Acknowledged,
    Carrier,
    CollectPayment,
    Order,
    OrderId,
    Payments,
    Ship,
    ShipWhenPaid,
    Total,
    Tracking,
    Weight,
)
from .support import Calls, names, payment, payment_json, proposal


@pytest.mark.parametrize(
    "weight,chosen", [("19.99", "Post"), ("20", "Post"), ("20.01", "SendCourier")]
)
def test_weight_boundary_selects_exactly_one_external_operation(weight: str, chosen: str) -> None:
    post, courier = Calls(), Calls()
    order = Order(id=OrderId("ORD-7"), total=Total(Decimal(50)), weight=Weight(Decimal(weight)))
    host = Host(DISPATCH, {"Post": post, "SendCourier": courier})
    host.open("order", {"order": order})

    result = host.advance("order").result
    assert names(result) == {chosen}
    host.perform("order", proposal(result, chosen).effect)

    assert len(post.received) == int(chosen == "Post")
    assert len(courier.received) == int(chosen == "SendCourier")


def test_selected_branch_completes_as_the_native_domain_value() -> None:
    post = Calls()
    host = Host(DISPATCH, {"Post": post})
    host.open("order", {"order": ORDER})
    host.perform("order", proposal(host.advance("order").result, "Post").effect)
    attempt = post.received[0][1]

    host.deliver(
        "order",
        Observation(
            Carrier,
            "posted",
            "result",
            {"order_id": "ORD-7", "tracking": "P-1"},
            about=attempt.effect,
            claims=attempt,
        ),
    )
    result = host.advance("order").result

    expected = Dispatch(
        order=ORDER,
        sent=ByPost(
            condition=Light(value=ORDER.weight, bound=PostLimit()),
            result=Posted(order_id=OrderId("ORD-7"), tracking=Tracking("P-1")),
        ),
    )
    assert isinstance(result, Completed)
    assert result.outcome.value == expected
    assert names(host.advance("order").result) == set()
    assert len(post.received) == 1


@pytest.mark.parametrize("case", ["ambiguous", "all-refused", "malformed"])
def test_unresolved_choice_cannot_invent_a_fallback(case: str) -> None:
    program = {"ambiguous": OVERLAPPING, "all-refused": NO_FALLBACK, "malformed": MALFORMED}[case]
    order = (
        Order(id=OrderId("ORD-7"), total=Total(Decimal(10)), weight=Weight(Decimal(5)))
        if case == "all-refused"
        else ORDER
    )
    post, courier = Calls(), Calls()
    host = Host(program, {"Post": post, "SendCourier": courier})
    host.open("order", {"order": order})

    result = host.advance("order").result

    assert names(result) == set()
    assert isinstance(result, Blocked)
    assert host.state("order").intents == ()
    assert post.received == courier.received == []


def test_competing_branch_acquires_decision_evidence_before_branch_work() -> None:
    collector, post, courier = Calls(), Calls(), Calls()
    host = Host(ACQUIRING, {"CollectPayment": collector, "Post": post, "SendCourier": courier})
    host.open("order", {"order": ORDER})

    first = host.advance("order").result
    assert names(first) == {"CollectPayment"}
    host.perform("order", proposal(first, "CollectPayment").effect)
    assert post.received == courier.received == []
    host.deliver("order", payment(collector.received[0][1], "20"))
    resolved = host.advance("order").result
    assert names(resolved) == {"Post"}
    host.perform("order", proposal(resolved, "Post").effect)

    assert len(post.received) == 1
    assert courier.received == []


@pytest.mark.parametrize("status,can_ship", [("approved", True), ("declined", False)])
def test_negative_business_answer_is_evidence_but_not_approval(
    *, status: str, can_ship: bool
) -> None:
    authorizer, shipper = Calls(), Calls()
    host = Host(AUTHORIZED, {"Authorize": authorizer, "Ship": shipper})
    host.open("order", {"order": ORDER})
    host.perform("order", proposal(host.advance("order").result, "Authorize").effect)
    attempt = authorizer.received[0][1]
    payload = {"order_id": "ORD-7", "status": status}
    if status == "declined":
        payload["reason"] = "insufficient funds"

    host.deliver(
        "order",
        Observation(Payments, "decision", "result", payload, about=attempt.effect, claims=attempt),
    )
    result = host.advance("order").result

    assert len(host.state("order").evidence) == 1
    assert ("Ship" in names(result)) is can_ship
    if can_ship:
        host.perform("order", proposal(result, "Ship").effect)
    assert len(shipper.received) == int(can_ship)


@pytest.mark.parametrize(
    "order,can_ship",
    [(ORDER, True), (HEAVY, False)],
    ids=["both-conditions", "only-outer-condition"],
)
def test_nested_conditions_preserve_each_prerequisite_and_independent_work(
    *, order: Order, can_ship: bool
) -> None:
    collector, shipper, mailbox = Calls(), Calls(), Calls()
    host = Host(NESTED, {"CollectPayment": collector, "Ship": shipper, "Acknowledge": mailbox})
    host.open("order", {"order": order})
    first = host.advance("order").result
    assert names(first) == {"CollectPayment", "Acknowledge"}
    host.perform("order", proposal(first, "CollectPayment").effect)
    host.perform("order", proposal(first, "Acknowledge").effect)
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
    assert len(mailbox.received) == 1


class RepackagedShipment(ShipWhenPaid):
    """Same conditional contract under another application type."""


class RepackagedFulfillment(Record):
    order: Order
    shipment: RepackagedShipment
    acknowledged: Acknowledged


def test_equivalent_domain_packaging_preserves_independent_progress() -> None:
    repackaged = Program(
        Goal(RepackagedFulfillment, accepts=("order",)),
        (CollectPayment, Ship, Acknowledge),
        artifact="repackaged@1",
    )
    for program in (FULFILLMENT, repackaged):
        collector, mailbox, shipper = Calls(), Calls(), Calls()
        host = Host(program, {"CollectPayment": collector, "Acknowledge": mailbox, "Ship": shipper})
        host.open("order", {"order": ORDER})

        result = host.advance("order").result
        assert isinstance(result, Frontier)
        assert len(result.ready) == 2
        assert names(result) == {"CollectPayment", "Acknowledge"}
        host.perform("order", proposal(result, "CollectPayment").effect)
        host.perform("order", proposal(result, "Acknowledge").effect)

        assert len(collector.received) == len(mailbox.received) == 1
        assert shipper.received == []
