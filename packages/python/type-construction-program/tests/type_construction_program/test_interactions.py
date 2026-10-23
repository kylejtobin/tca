"""Question 1 of foundations §18: can one interaction kind express an immediate response, a
delayed response, an unsolicited receive and a timer without erasing their differences?

The declarations are ``fulfillment`` and ``auction``. The hypothesis under test is the simplest
one: the answer a send returns is the result. The experiments show where that holds, where it
fails, and the one distinction that repairs it: a send's acknowledgement is a role of its own,
recorded against the attempt, and the premise is satisfied only by the declared result,
whenever and however it arrives.
"""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import TypeAdapter, ValidationError

from type_construction.program import (
    Acknowledged,
    Attempted,
    Blocked,
    Completed,
    Correlation,
    Delivered,
    EffectIdentity,
    Interaction,
    InvocationId,
    Program,
    Refusal,
    Returned,
    Solicited,
    Unclosed,
    Uncorrelated,
    Unmatched,
    Unsolicited,
    accept,
    acknowledge,
    admit,
    evaluate,
    perform,
)
from type_construction.world import Value

from . import auction, fulfillment
from .drive import delivered, frontier, only, performing
from .fulfillment import Order

CAPTURED = '{"order_id": "o-1", "amount": "50.00", "id": "ch_1"}'
RECEIPT = '{"id": "ch_1"}'
APPROVED = '{"order_id": "o-1", "reviewer": "ren"}'
SHIPMENT = '{"order_id": "o-1", "tracking": "1Z"}'
NOON = datetime(2026, 10, 23, 12, tzinfo=UTC)
NOW = '{"at": "2026-10-23T12:00:00Z"}'
TIMER_SET = '{"at": "2026-10-23T13:00:00Z"}'
ELAPSED = '{"at": "2026-10-23T13:00:00Z"}'


def test_the_outcome_is_the_same_whether_the_result_is_immediate_or_delayed() -> None:
    program = fulfillment.FULFILLMENT

    immediate = accept(program, InvocationId("immediate"), fulfillment.ORDER)
    immediate, charge = performing(program, immediate, CAPTURED)
    assert isinstance(charge.request, fulfillment.ChargeRequest)
    immediate = admit(program, immediate, delivered(fulfillment.APPROVALS, "ap-1", APPROVED))
    immediate, ship = performing(program, immediate, SHIPMENT)
    assert isinstance(ship.request, fulfillment.ShipRequest)
    at_once = evaluate(program, immediate)

    delayed = accept(program, InvocationId("delayed"), fulfillment.ORDER)
    delayed, charge = only(program, delayed)
    assert isinstance(charge.request, fulfillment.ChargeRequest)
    delayed = acknowledge(program, delayed, charge.identity, RECEIPT)
    waiting = frontier(evaluate(program, delayed))
    assert waiting.dispatch == ()
    delayed = admit(program, delayed, delivered(fulfillment.PAYMENTS, "wh-1", CAPTURED))
    delayed = admit(program, delayed, delivered(fulfillment.APPROVALS, "ap-1", APPROVED))
    delayed, ship = performing(program, delayed, SHIPMENT)
    assert isinstance(ship.request, fulfillment.ShipRequest)
    later = evaluate(program, delayed)

    assert isinstance(at_once, Completed)
    assert isinstance(later, Completed)
    assert at_once.goal == later.goal
    assert isinstance(at_once.goal, fulfillment.Fulfilled)
    assert isinstance(at_once.goal.outcome, fulfillment.Shipped)
    assert isinstance(immediate.evidence[0].origin, Returned)
    assert isinstance(delayed.evidence[0].origin, Delivered)
    assert any(
        isinstance(e, Attempted) and isinstance(e.outcome, Acknowledged) for e in delayed.history
    )


def test_a_receipt_satisfies_no_premise_and_leaves_the_receive_outstanding() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    invocation, charge = only(program, invocation)
    invocation = acknowledge(program, invocation, charge.identity, RECEIPT)

    attempts = [e for e in invocation.history if isinstance(e, Attempted)]
    assert len(attempts) == 1
    assert isinstance(attempts[0].outcome, Acknowledged)
    assert attempts[0].outcome.receipt == fulfillment.ChargeAccepted(
        id=fulfillment.ChargeId("ch_1")
    )
    assert invocation.evidence == ()

    result = frontier(evaluate(program, invocation))
    assert result.dispatch == ()
    solicited = [a for a in result.awaiting if isinstance(a, Solicited)]
    assert len(solicited) == 1
    assert solicited[0].identity == charge.identity
    assert solicited[0].acknowledged == attempts[0].outcome.receipt
    assert solicited[0].receives == (fulfillment.Captured, fulfillment.Declined)

    with pytest.raises(ValidationError):
        TypeAdapter(fulfillment.Captured).validate_json(RECEIPT)
    with pytest.raises(Refusal) as refusal:
        admit(program, invocation, delivered(fulfillment.PAYMENTS, "wh-x", RECEIPT))
    assert isinstance(refusal.value.reason, Unmatched)
    assert refusal.value.reason.tried == (fulfillment.Captured, fulfillment.Declined)


def test_a_premise_with_no_declared_source_is_refused_at_declaration() -> None:
    with pytest.raises(ValidationError) as refusal:
        Program(
            goal=fulfillment.Fulfilled,
            accepts=fulfillment.FulfillOrder,
            interactions=(fulfillment.CHARGE, fulfillment.APPROVAL),
        )
    message = str(refusal.value)
    assert "Fulfilled.outcome.Shipped.shipment" in message
    assert "ShipmentAccepted" in message
    assert "no interaction declares a source" in message


def test_an_unsolicited_receive_waits_and_dispatches_nothing() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    invocation, _ = performing(program, invocation, CAPTURED)
    result = frontier(evaluate(program, invocation))
    assert result.dispatch == ()
    assert result.awaiting == (
        Unsolicited(receives=(fulfillment.Approved,), source=fulfillment.APPROVALS),
    )


def test_a_deadline_is_a_send_to_the_clock_and_a_receive_from_it() -> None:
    program = auction.AUCTION
    invocation = accept(program, InvocationId("auc"), auction.LOT)

    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [auction.ReadClock]
    assert any(isinstance(a, Unclosed) and a.held == 0 for a in opening.awaiting)

    invocation, read = performing(program, invocation, NOW)
    assert read.identity.premises == ()
    (reading,) = invocation.evidence
    assert reading.value == auction.Now(at=auction.Instant(NOON))

    invocation, deadline = only(program, invocation)
    assert deadline.request == auction.Deadline(
        since=auction.Now(at=auction.Instant(NOON)), grace=auction.BiddingWindow()
    )
    assert isinstance(deadline.request, auction.Deadline)
    assert deadline.request.grace.root == timedelta(hours=1)
    assert deadline.identity.premises == (reading.id,)
    invocation = acknowledge(program, invocation, deadline.identity, TIMER_SET)

    waiting = frontier(evaluate(program, invocation))
    assert waiting.dispatch == ()
    assert {type(a) for a in waiting.awaiting} == {Solicited, Unclosed}

    with pytest.raises(Refusal) as refusal:
        admit(program, invocation, delivered(auction.CLOCK, "t-1", ELAPSED))
    assert isinstance(refusal.value.reason, Uncorrelated)
    assert refusal.value.reason.correlation is None

    closed = admit(
        program, invocation, delivered(auction.CLOCK, "t-1", ELAPSED, answers=deadline.identity)
    )
    assert closed.evidence[-1].answers == deadline.identity
    assert not isinstance(evaluate(program, closed), type(waiting))


def test_the_clock_is_read_once_and_the_reading_is_reused() -> None:
    program = auction.AUCTION
    invocation = accept(program, InvocationId("auc"), auction.LOT)
    invocation, read = performing(program, invocation, NOW)
    first = frontier(evaluate(program, invocation))
    second = frontier(evaluate(program, invocation))
    assert first == second
    assert all(d.identity != read.identity for d in first.dispatch)
    assert [type(d.request) for d in first.dispatch] == [auction.Deadline]


def test_a_result_that_arrives_before_the_send_satisfies_the_premise() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    invocation = admit(program, invocation, delivered(fulfillment.PAYMENTS, "wh-early", CAPTURED))
    result = frontier(evaluate(program, invocation))
    assert all(not isinstance(d.request, fulfillment.ChargeRequest) for d in result.dispatch)
    assert invocation.intents == {}
    assert invocation.evidence[0].answers is None


def test_a_receipt_shaped_like_the_result_is_told_from_it_by_report_not_by_shape() -> None:
    """The counterexample that ruled out inferring the role from the payload: the clock's
    receipt and its result have one shape. Reported as a result, the receipt closes the bidding
    with nothing bid; reported as a receipt, the bidding stays open."""
    assert TypeAdapter(auction.Elapsed).validate_json(TIMER_SET) == auction.Elapsed(
        at=auction.Instant(NOON + timedelta(hours=1))
    )
    program = auction.AUCTION
    invocation = accept(program, InvocationId("auc"), auction.LOT)
    invocation, _ = performing(program, invocation, NOW)
    invocation, deadline = only(program, invocation)

    mislabeled = perform(program, invocation, deadline.identity, TIMER_SET)
    assert isinstance(evaluate(program, mislabeled), Blocked)

    acknowledged = acknowledge(program, invocation, deadline.identity, TIMER_SET)
    still_open = frontier(evaluate(program, acknowledged))
    assert any(isinstance(a, Unclosed) and a.held == 0 for a in still_open.awaiting)
    assert acknowledged.evidence == mislabeled.evidence[:1]


def test_a_timer_answer_naming_no_intent_cannot_be_tied_to_the_invocation() -> None:
    program = auction.AUCTION
    invocation = accept(program, InvocationId("auc"), auction.LOT)
    foreign = EffectIdentity(
        invocation=InvocationId("other"),
        operation="type_construction_program.auction.Deadline",
        premises=(1,),
    )
    with pytest.raises(Refusal):
        admit(program, invocation, delivered(auction.CLOCK, "t-9", ELAPSED, answers=foreign))


class TwoOrders(Value):
    """A command holding two orders: the one class at two sites."""

    debit: Order
    credit: Order


def test_a_class_held_at_two_sites_is_refused_not_bound_by_guess() -> None:
    """This evaluator binds a premise by its declared class, validated to be found one way. A
    program where one class is found two ways is refused with both paths named; it is not
    expressible in this slice. Occurrence binding that tells the sites apart is outcome 2."""
    by_debit = {"correlated": (Correlation(received="order", subject="debit.id"),)}
    with pytest.raises(ValidationError) as refusal:
        Program(
            goal=fulfillment.Settled,
            accepts=TwoOrders,
            interactions=(
                fulfillment.HOLD.model_copy(update=by_debit),
                fulfillment.CHARGE.model_copy(update=by_debit),
            ),
        )
    message = str(refusal.value)
    assert "TwoOrders.debit" in message
    assert "TwoOrders.credit" in message
    assert "does not say which" in message


def test_a_correlation_path_that_does_not_exist_is_refused_at_declaration() -> None:
    with pytest.raises(ValidationError) as refusal:
        Interaction(
            source=fulfillment.APPROVALS,
            receives=(fulfillment.Approved,),
            correlated=(Correlation(received="order_number", subject="order.id"),),
        )
    assert "Approved has no field path order_number" in str(refusal.value)
    with pytest.raises(ValidationError) as refusal:
        Program(goal=fulfillment.Settled, accepts=TwoOrders, interactions=(fulfillment.HOLD,))
    assert "TwoOrders has no field path order.id" in str(refusal.value)
