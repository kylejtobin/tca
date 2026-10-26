"""Architecture §6 collections and §8 identity: scoped closure and reported time."""

from datetime import UTC, datetime
from decimal import Decimal

from type_construction.program import Completed, Frontier, Host, Observation, evaluate

from .closure import DELIVERY, PAIR, TIMED, Clock, Deadline
from .fulfillment import ORDER, Carrier, Order, OrderId, Total, Weight
from .support import Calls, installment, names, proposal, receipted, settled


def test_closing_one_order_leaves_the_other_collection_open() -> None:
    second = Order(id=OrderId("ORD-8"), total=Total(Decimal(50)), weight=Weight(Decimal(12)))
    host = Host(PAIR, {})
    host.open("pair", {"first": ORDER, "second": second})
    host.deliver("pair", installment("one", "ORD-7", "20"))
    host.deliver("pair", installment("two", "ORD-8", "30"))

    host.deliver("pair", settled("first-closed"))
    first_closed = host.state("pair").evidence
    host.deliver("pair", installment("late", "ORD-7", "10"))

    assert host.state("pair").evidence == first_closed
    assert isinstance(host.advance("pair").result, Frontier)
    host.deliver("pair", installment("still-open", "ORD-8", "5"))
    assert len(host.state("pair").evidence) == len(first_closed) + 1
    host.deliver("pair", settled("second-closed", "ORD-8"))
    result = host.advance("pair").result
    assert isinstance(result, Completed)
    assert result.outcome.value.one.paid.root == Decimal(20)
    assert result.outcome.value.two.paid.root == Decimal(35)


def carrier(delivery: str, relationship: str, payload: dict[str, str]) -> Observation:
    return Observation(Carrier, delivery, "result", payload, through=relationship)


def test_nested_parcel_closure_does_not_close_sibling_or_parent() -> None:
    host = Host(DELIVERY, {})
    host.open("order", {"order": ORDER})
    for ref in ("PCL-1", "PCL-2"):
        host.deliver(
            "order",
            carrier(
                f"dispatch-{ref}", "ParcelsDispatched", {"order_id": "ORD-7", "reference": ref}
            ),
        )
    host.deliver("order", carrier("scan-one", "Scans", {"parcel_ref": "PCL-1", "location": "hub"}))
    evidence = host.state("order").evidence
    host.deliver("order", carrier("stray", "Scans", {"parcel_ref": "PCL-9", "location": "hub"}))
    assert host.state("order").evidence == evidence

    host.deliver("order", carrier("delivered-one", "Delivered", {"parcel_ref": "PCL-1"}))
    evidence = host.state("order").evidence
    host.deliver("order", carrier("late", "Scans", {"parcel_ref": "PCL-1", "location": "door"}))

    assert host.state("order").evidence == evidence
    host.deliver("order", carrier("scan-two", "Scans", {"parcel_ref": "PCL-2", "location": "van"}))
    assert len(host.state("order").evidence) == len(evidence) + 1
    assert isinstance(host.advance("order").result, Frontier)
    host.deliver("order", carrier("delivered-two", "Delivered", {"parcel_ref": "PCL-2"}))
    assert isinstance(host.advance("order").result, Frontier)
    host.deliver("order", carrier("all-dispatched", "AllDispatched", {"order_id": "ORD-7"}))
    result = host.advance("order").result
    assert isinstance(result, Completed)
    assert {
        t.parcel.reference.root: tuple(s.location.root for s in t.scans)
        for t in result.outcome.value.tracked
    } == {"PCL-1": ("hub",), "PCL-2": ("van",)}
    evidence = host.state("order").evidence
    host.deliver(
        "order",
        carrier("late-parcel", "ParcelsDispatched", {"order_id": "ORD-7", "reference": "PCL-3"}),
    )
    assert host.state("order").evidence == evidence


def test_deadline_closes_only_on_correlated_expiry_evidence_and_replays_without_clock() -> None:
    due = Deadline(datetime(2020, 1, 1, tzinfo=UTC))
    clock = Calls()
    host = Host(TIMED, {"Expire": clock, "SendReceipt": receipted})
    host.open("order", {"order": ORDER, "due": due})
    result = host.advance("order").result
    assert names(result) == {"Expire"}
    host.perform("order", proposal(result, "Expire").effect)
    attempt = clock.received[0][1]
    host.deliver(
        "order",
        Observation(
            Clock, "scheduled", "receipt", {"at": due}, about=attempt.effect, claims=attempt
        ),
    )
    host.deliver("order", installment("one", "ORD-7", "20"))
    ready = host.advance("order").result
    assert names(ready) == {"SendReceipt"}
    host.perform("order", proposal(ready, "SendReceipt").effect)
    evidence = host.state("order").evidence

    host.deliver(
        "order",
        Observation(
            Clock,
            "wrong-deadline",
            "result",
            {"at": Deadline(datetime(2020, 1, 2, tzinfo=UTC))},
            about=attempt.effect,
            claims=attempt,
        ),
    )

    assert host.state("order").evidence == evidence
    assert isinstance(host.advance("order").result, Frontier)
    host.deliver(
        "order",
        Observation(Clock, "expired", "result", {"at": due}, about=attempt.effect, claims=attempt),
    )
    outcome = host.advance("order").result
    assert isinstance(outcome, Completed)
    assert outcome.outcome.value.paid.root == Decimal(20)
    evidence = host.state("order").evidence
    host.deliver("order", installment("late", "ORD-7", "30"))
    assert host.state("order").evidence == evidence
    assert evaluate(TIMED, host.state("order")) == outcome
    assert len(clock.received) == 1
