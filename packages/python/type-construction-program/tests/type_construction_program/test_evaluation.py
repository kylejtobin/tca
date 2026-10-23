"""Question 2 of foundations §18: do three pure evaluation results express completed, actionable,
waiting and blocked with structured reasons?

The hypothesis under test is four exclusive results, one per condition. The first experiment
breaks it: one invocation has a request to dispatch and a receive outstanding at the same time,
so actionable and waiting are two parts of one frontier, not two states. The rest show that
attempt failure and uncertainty are neither business conclusions nor blocks, that a declined
charge is a completed negative outcome when the program declares one, and that a refuted rule
blocks with the reasons and keeps the history that led there.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from type_construction.program import (
    AnsweredOtherwise,
    Blocked,
    Completed,
    Frontier,
    InvocationId,
    Refusal,
    Refutation,
    Settled,
    Unintended,
    Unresolved,
    Unsolicited,
    accept,
    admit,
    evaluate,
    failed,
    intend,
    perform,
    uncertain,
)

from . import fulfillment
from .drive import delivered, frontier, only, performing

CAPTURED = '{"order_id": "o-1", "amount": "50.00", "id": "ch_1"}'
SHORT = '{"order_id": "o-1", "amount": "20.00", "id": "ch_1"}'
DECLINED = '{"order_id": "o-1", "reason": "insufficient funds"}'
APPROVED = '{"order_id": "o-1", "reviewer": "ren"}'
SHIPMENT = '{"order_id": "o-1", "tracking": "1Z"}'


def test_actionable_work_and_an_outstanding_receive_share_one_frontier() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    result = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in result.dispatch] == [fulfillment.ChargeRequest]
    assert result.awaiting == (
        Unsolicited(receives=(fulfillment.Approved,), source=fulfillment.APPROVALS),
    )


def test_the_four_conditions_follow_from_the_history_in_turn() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)

    invocation, charge = performing(program, invocation, CAPTURED)
    waiting = frontier(evaluate(program, invocation))
    assert waiting.dispatch == ()
    assert len(waiting.awaiting) == 1

    invocation = admit(program, invocation, delivered(fulfillment.APPROVALS, "ap-1", APPROVED))
    actionable = frontier(evaluate(program, invocation))
    assert actionable.awaiting == ()
    assert [type(d.request) for d in actionable.dispatch] == [fulfillment.ShipRequest]
    assert actionable.dispatch[0].identity != charge.identity

    invocation, _ = performing(program, invocation, SHIPMENT)
    completed = evaluate(program, invocation)
    assert isinstance(completed, Completed)
    assert isinstance(completed.goal, fulfillment.Fulfilled)
    assert isinstance(completed.goal.outcome, fulfillment.Shipped)
    assert completed.goal.outcome.shipment.tracking == fulfillment.Tracking("1Z")


def test_a_frontier_with_nothing_to_dispatch_and_nothing_awaited_cannot_exist() -> None:
    with pytest.raises(ValidationError):
        Frontier()


def test_an_attempt_failure_keeps_the_send_dispatchable_and_concludes_nothing() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    invocation, charge = only(program, invocation)
    invocation = failed(invocation, charge.identity, "connection refused")
    result = evaluate(program, invocation)
    assert isinstance(result, Frontier)
    (again,) = result.dispatch
    assert again.identity == charge.identity
    assert again.attempt == 2
    assert again.request == charge.request


def test_an_uncertain_attempt_is_outstanding_and_not_dispatched_again() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    invocation, charge = only(program, invocation)
    invocation = uncertain(invocation, charge.identity, "timed out after the request was sent")
    result = frontier(evaluate(program, invocation))
    assert result.dispatch == ()
    unresolved = [a for a in result.awaiting if isinstance(a, Unresolved)]
    assert unresolved == [
        Unresolved(
            identity=charge.identity, attempt=1, reason="timed out after the request was sent"
        )
    ]


def test_a_decline_is_a_completed_negative_outcome() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    invocation, _ = performing(program, invocation, DECLINED)
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, fulfillment.Fulfilled)
    assert isinstance(result.goal.outcome, fulfillment.Refused)
    assert result.goal.outcome.declined.reason == fulfillment.DeclineReason("insufficient funds")


def test_a_refuted_rule_blocks_with_structured_reasons_and_keeps_the_history() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    invocation, charge = performing(program, invocation, SHORT)
    result = evaluate(program, invocation)
    assert isinstance(result, Blocked)
    kinds = {type(r) for r in result.reasons}
    assert kinds == {Refutation, AnsweredOtherwise}
    (refutation,) = [r for r in result.reasons if isinstance(r, Refutation)]
    assert refutation.kind is fulfillment.Covers
    assert refutation.premise == "Fulfilled.outcome.Shipped.authority.covered"
    (otherwise,) = [r for r in result.reasons if isinstance(r, AnsweredOtherwise)]
    assert otherwise.expected is fulfillment.Declined
    assert otherwise.answered is fulfillment.Captured
    assert charge.identity in invocation.intents
    (captured,) = invocation.evidence
    assert isinstance(captured.value, fulfillment.Captured)
    assert captured.value.amount == fulfillment.Paid(Decimal("20.00"))


def test_an_attempt_without_a_committed_intent_is_refused() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    proposed = frontier(evaluate(program, invocation))
    with pytest.raises(Refusal) as refusal:
        perform(program, invocation, proposed.dispatch[0].identity, CAPTURED)
    assert isinstance(refusal.value.reason, Unintended)
    assert invocation.revision == 1


def test_an_answered_intent_takes_no_second_answer() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    invocation, charge = performing(program, invocation, CAPTURED)
    with pytest.raises(Refusal) as refusal:
        perform(program, invocation, charge.identity, DECLINED)
    assert isinstance(refusal.value.reason, Settled)
    with pytest.raises(Refusal):
        failed(invocation, charge.identity, "late failure report")
    assert intend(invocation, frontier(evaluate(program, invocation)).dispatch) == invocation
