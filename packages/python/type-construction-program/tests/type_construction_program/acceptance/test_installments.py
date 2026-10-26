"""Product §4; architecture §6: per-member progress and conclusions only after closure."""

from decimal import Decimal

import pytest

from type_construction.program import Blocked, Completed, Frontier, Host, Observation

from .fulfillment import ORDER, Mail, Paid
from .installments import SETTLEMENT, SINGLE
from .support import Calls, installment, names, receipted, settled


def test_open_collection_progresses_per_member_and_preserves_equal_valued_members() -> None:
    mailbox = Calls()
    host = Host(SETTLEMENT, {"SendReceipt": mailbox})
    host.open("order", {"order": ORDER})
    assert names(host.advance("order").result) == set()

    host.deliver("order", installment("one", "ORD-7", "25"))
    host.deliver("order", installment("two", "ORD-7", "25"))
    result = host.advance("order").result

    assert isinstance(result, Frontier)
    assert len(result.ready) == 2
    assert names(result) == {"SendReceipt"}
    assert len({p.effect for p in result.ready}) == 2
    for pending in result.ready:
        host.perform("order", pending.effect)
    assert len(mailbox.received) == 2
    assert [intent.request.amount for intent, _ in mailbox.received] == [Paid(Decimal(25))] * 2
    assert not isinstance(host.advance("order").result, Completed)


def test_closure_fixes_the_aggregate_and_late_reports_cannot_change_it() -> None:
    host = Host(SETTLEMENT, {"SendReceipt": receipted})
    host.open("order", {"order": ORDER})
    host.deliver("order", installment("one", "ORD-7", "20"))
    host.deliver("order", installment("two", "ORD-7", "30"))
    ready = host.advance("order").result
    assert isinstance(ready, Frontier)
    for pending in ready.ready:
        host.perform("order", pending.effect)
    assert not isinstance(host.advance("order").result, Completed)

    host.deliver("order", settled("closed"))
    complete = host.advance("order").result

    assert isinstance(complete, Completed)
    assert complete.outcome.value.paid.root == Decimal(50)
    assert {p.amount.root for p in complete.outcome.value.installments} == {
        Decimal(20),
        Decimal(30),
    }
    assert len(complete.outcome.value.receipts) == 2
    evidence = host.state("order").evidence
    for report in (
        installment("late", "ORD-7", "10"),
        settled("closed"),
        settled("another-closure"),
    ):
        host.deliver("order", report)
        after = host.advance("order").result
        assert isinstance(after, Completed)
        assert after.outcome.value == complete.outcome.value
        assert host.state("order").evidence == evidence
        assert names(after) == set()


@pytest.mark.parametrize("amount", ["49.99", "50", "50.01"])
def test_coverage_is_decided_at_closure_not_at_partial_totals(amount: str) -> None:
    host = Host(SETTLEMENT, {"SendReceipt": receipted})
    host.open("order", {"order": ORDER})
    host.deliver("order", installment("one", "ORD-7", amount))
    open_result = host.advance("order").result
    assert isinstance(open_result, Frontier)
    assert names(open_result) == {"SendReceipt"}
    for pending in open_result.ready:
        host.perform("order", pending.effect)
    assert not isinstance(host.advance("order").result, (Completed, Blocked))

    host.deliver("order", settled("closed"))
    result = host.advance("order").result

    if amount == "49.99":
        assert isinstance(result, Blocked)
    else:
        assert isinstance(result, Completed)
        assert result.outcome.value.paid.root == Decimal(amount)


@pytest.mark.parametrize("amounts", [(), ("50",), ("20", "30")], ids=["empty", "one", "many"])
def test_unique_payment_requires_closed_collection_with_exactly_one_member(
    amounts: tuple[str, ...],
) -> None:
    host = Host(SINGLE, {})
    host.open("order", {"order": ORDER})
    for index, amount in enumerate(amounts):
        host.deliver("order", installment(f"payment-{index}", "ORD-7", amount))
    before = host.advance("order").result
    assert isinstance(before, Frontier)
    assert names(before) == set()

    host.deliver("order", settled("closed"))
    result = host.advance("order").result

    if len(amounts) == 1:
        assert isinstance(result, Completed)
        assert result.outcome.value.single.chosen.amount == Paid(Decimal(50))
    else:
        assert isinstance(result, Blocked)


def test_untrusted_or_miscorrelated_closure_cannot_finalize_a_collection() -> None:
    host = Host(SINGLE, {})
    host.open("order", {"order": ORDER})
    host.deliver("order", installment("one", "ORD-7", "50"))
    evidence = host.state("order").evidence

    host.deliver("order", settled("wrong-order", "ORD-9"))
    host.deliver(
        "order",
        Observation(Mail, "wrong-source", "result", {"order_id": "ORD-7"}, through="Settled"),
    )
    host.deliver(
        "order",
        Observation(
            Mail, "wrong-relationship", "result", {"order_id": "ORD-7"}, through="SendReceipt"
        ),
    )

    assert host.state("order").evidence == evidence
    assert isinstance(host.advance("order").result, Frontier)
    host.deliver("order", settled("valid"))
    assert isinstance(host.advance("order").result, Completed)
