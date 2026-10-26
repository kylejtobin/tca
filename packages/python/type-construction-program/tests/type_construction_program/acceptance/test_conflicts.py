"""Architecture §8: conflict precedes result and attempt permission; uncertainty can resolve."""

import pytest

from type_construction.program import Host, Observation, UnjustifiedAttemptError

from .fulfillment import FULFILLMENT, ORDER, Mail, Payments
from .support import Calls, names, payment, payment_json, proposal


@pytest.mark.parametrize("conflict", ["different-result", "same-attempt-failure"])
def test_conflict_blocks_committed_shipment_but_independent_work_continues(conflict: str) -> None:
    collector, shipper, mailbox = Calls(), Calls(), Calls()
    host = Host(FULFILLMENT, {"CollectPayment": collector, "Ship": shipper, "Acknowledge": mailbox})
    host.open("order", {"order": ORDER})
    host.perform("order", proposal(host.advance("order").result, "CollectPayment").effect)
    attempt = collector.received[0][1]
    host.deliver("order", payment(attempt, "50"))
    ready = host.advance("order").result
    shipment = proposal(ready, "Ship")
    acknowledgement = proposal(ready, "Acknowledge")
    admitted = host.state("order").evidence

    report = (
        payment(attempt, "60", "contradiction")
        if conflict == "different-result"
        else Observation(Payments, "failed", "failed", None, about=attempt.effect, claims=attempt)
    )
    host.deliver("order", report)
    with pytest.raises(UnjustifiedAttemptError):
        host.perform("order", shipment.effect)
    host.perform("order", acknowledgement.effect)

    assert shipper.received == []
    assert len(mailbox.received) == 1
    assert host.state("order").evidence == admitted
    assert len(host.state("order").observations) == 2
    assert names(host.advance("order").result) == set()


@pytest.mark.parametrize(
    "amount,source",
    [("50", Payments), ("-5", Payments), ("60", Mail)],
    ids=["equivalent-result", "malformed-result", "unauthorized-result"],
)
def test_nonconflicting_report_does_not_withhold_a_committed_shipment(
    amount: str, source: type
) -> None:
    collector, shipper = Calls(), Calls()
    host = Host(FULFILLMENT, {"CollectPayment": collector, "Ship": shipper})
    host.open("order", {"order": ORDER})
    host.perform("order", proposal(host.advance("order").result, "CollectPayment").effect)
    attempt = collector.received[0][1]
    host.deliver("order", payment(attempt, "50"))
    shipment = proposal(host.advance("order").result, "Ship")
    admitted = host.state("order").evidence

    host.deliver(
        "order",
        Observation(
            source,
            "second",
            "result",
            payment_json("ORD-7", amount),
            "json",
            about=attempt.effect,
            claims=attempt,
        ),
    )
    host.perform("order", shipment.effect)

    assert len(shipper.received) == 1
    assert host.state("order").evidence == admitted


@pytest.mark.parametrize(
    "roles",
    [("uncertain", "failed"), ("failed", "uncertain")],
    ids=["resolution-arrives-last", "stale-uncertainty-arrives-last"],
)
def test_definitive_failure_resolves_uncertainty_independently_of_arrival_order(
    roles: tuple[str, str],
) -> None:
    collector = Calls()
    host = Host(FULFILLMENT, {"CollectPayment": collector})
    host.open("order", {"order": ORDER})
    host.perform("order", proposal(host.advance("order").result, "CollectPayment").effect)
    attempt = collector.received[0][1]

    for role in roles:
        host.deliver(
            "order", Observation(Payments, role, role, None, about=attempt.effect, claims=attempt)
        )
    retry = proposal(host.advance("order").result, "CollectPayment")
    host.perform("order", retry.effect)

    assert len(collector.received) == 2
    next_attempt = collector.received[1][1]
    assert next_attempt.effect == attempt.effect
    assert next_attempt.number == attempt.number + 1
    assert "CollectPayment" not in names(host.advance("order").result)
