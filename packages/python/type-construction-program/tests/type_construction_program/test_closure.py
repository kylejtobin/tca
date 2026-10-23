"""Question 4 of foundations §18: how does a closed tuple's admission support an evolving source
without making the host a second business interpreter?

The hypothesis under test is the simplest one: the items held so far are the collection. Two
experiments break it. One approval held so far constructs ``Only``, and a second approval
refutes it; the greatest of two bids is the current maximum, and a third bid overturns it. The
repair is a declared closure: the interaction names the evidence after which the source says
nothing more, the evaluator waits for exactly that evidence and seals the collection at it, and
admission refuses what arrives after. A tuple supplied in the input is closed at acceptance.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from type_construction.program import (
    Blocked,
    Closed,
    Completed,
    InvocationId,
    Program,
    Refusal,
    Refutation,
    Unclosed,
    accept,
    acknowledge,
    admit,
    evaluate,
)

from . import auction, review
from .drive import delivered, frontier, only, performing

NOW = '{"at": "2026-10-23T12:00:00Z"}'
TIMER_SET = '{"at": "2026-10-23T13:00:00Z"}'
ELAPSED = '{"at": "2026-10-23T13:00:00Z"}'
CLOSE_REVIEW = '{"case_id": "case-3"}'


def approval(reviewer: str) -> str:
    return f'{{"case_id": "case-3", "reviewer": "{reviewer}"}}'


def bid(amount: str) -> str:
    return f'{{"lot_id": "lot-7", "amount": "{amount}"}}'


def test_one_received_approval_does_not_establish_only() -> None:
    program = review.REVIEW
    invocation = accept(program, InvocationId("rev"), review.CASE)
    invocation = admit(program, invocation, delivered(review.REVIEWERS, "a-1", approval("ren")))

    held = frontier(evaluate(program, invocation))
    assert held.dispatch == ()
    (unclosed,) = [a for a in held.awaiting if isinstance(a, Unclosed)]
    assert unclosed == Unclosed(
        element=review.Approval, source=review.REVIEWERS, closing=review.ReviewClosed, held=1
    )

    (first,) = invocation.evidence
    assert isinstance(first.value, review.Approval)
    assert review.Sole(of=(first.value,)).chosen == first.value

    invocation = admit(program, invocation, delivered(review.REVIEWERS, "a-2", approval("kai")))
    assert isinstance(evaluate(program, invocation), type(held))
    invocation = admit(program, invocation, delivered(review.REVIEWERS, "c-1", CLOSE_REVIEW))
    result = evaluate(program, invocation)
    assert isinstance(result, Blocked)
    (reason,) = result.reasons
    assert isinstance(reason, Refutation)
    assert reason.kind is review.Sole
    assert reason.premise.endswith("Decided.approval")


def test_one_approval_and_then_closure_decides_the_case() -> None:
    program = review.REVIEW
    invocation = accept(program, InvocationId("rev"), review.CASE)
    invocation = admit(program, invocation, delivered(review.REVIEWERS, "a-1", approval("ren")))
    invocation = admit(program, invocation, delivered(review.REVIEWERS, "c-1", CLOSE_REVIEW))
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, review.Decided)
    assert result.goal.approval.chosen.reviewer == review.Reviewer("ren")


def test_a_current_maximum_is_not_final_while_more_may_arrive() -> None:
    program = auction.AUCTION
    invocation = accept(program, InvocationId("auc"), auction.LOT)
    invocation, _ = performing(program, invocation, NOW)
    invocation, deadline = only(program, invocation)
    invocation = acknowledge(program, invocation, deadline.identity, TIMER_SET)
    invocation = admit(program, invocation, delivered(auction.BIDDERS, "b-1", bid("10")))
    invocation = admit(program, invocation, delivered(auction.BIDDERS, "b-2", bid("20")))

    open_bidding = frontier(evaluate(program, invocation))
    assert open_bidding.dispatch == ()
    (unclosed,) = [a for a in open_bidding.awaiting if isinstance(a, Unclosed)]
    assert unclosed.held == 2

    amounts = tuple(e.value.amount for e in invocation.evidence if isinstance(e.value, auction.Bid))
    assert auction.Highest(of=amounts).chosen == auction.Amount(Decimal(20))

    invocation = admit(program, invocation, delivered(auction.BIDDERS, "b-3", bid("30")))
    invocation = admit(
        program, invocation, delivered(auction.CLOCK, "t-1", ELAPSED, answers=deadline.identity)
    )
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, auction.Hammered)
    assert result.goal.highest.chosen == auction.Amount(Decimal(30))
    assert len(result.goal.highest.of) == 3


def test_closure_is_declared_or_the_program_is_refused() -> None:
    with pytest.raises(ValidationError) as refusal:
        Program(
            goal=auction.Hammered,
            accepts=auction.RunAuction,
            interactions=(auction.UNCLOSED_BIDS, auction.READ_CLOCK, auction.TIMER),
        )
    message = str(refusal.value)
    assert "Hammered.highest.of" in message
    assert "Bid" in message
    assert "declares no closure" in message


def test_a_tuple_supplied_in_the_input_is_closed_at_acceptance() -> None:
    sealed = auction.SealedBids(
        lot=auction.Lot(id=auction.LotId("lot-7")),
        amounts=(
            auction.Amount(Decimal(3)),
            auction.Amount(Decimal(9)),
            auction.Amount(Decimal(4)),
        ),
    )
    invocation = accept(auction.SEALED, InvocationId("sealed"), sealed)
    result = evaluate(auction.SEALED, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, auction.Hammered)
    assert result.goal.highest.chosen == auction.Amount(Decimal(9))
    assert auction.SEALED.interactions == ()


def test_an_item_after_closure_is_refused_and_a_redelivery_is_one_claim() -> None:
    program = auction.AUCTION
    invocation = accept(program, InvocationId("auc"), auction.LOT)
    invocation, _ = performing(program, invocation, NOW)
    invocation, deadline = only(program, invocation)
    invocation = acknowledge(program, invocation, deadline.identity, TIMER_SET)
    invocation = admit(program, invocation, delivered(auction.BIDDERS, "b-1", bid("10")))
    invocation = admit(
        program, invocation, delivered(auction.CLOCK, "t-1", ELAPSED, answers=deadline.identity)
    )
    closing = invocation.evidence[-1]

    with pytest.raises(Refusal) as refusal:
        admit(program, invocation, delivered(auction.BIDDERS, "b-2", bid("40")))
    assert refusal.value.reason == Closed(received=auction.Bid, by=closing.id)

    redelivered = admit(program, invocation, delivered(auction.BIDDERS, "b-1", bid("10")))
    assert redelivered == invocation
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, auction.Hammered)
    assert result.goal.highest.chosen == auction.Amount(Decimal(10))


def test_closing_with_nothing_said_is_refuted_not_awaited() -> None:
    program = auction.AUCTION
    invocation = accept(program, InvocationId("auc"), auction.LOT)
    invocation, _ = performing(program, invocation, NOW)
    invocation, deadline = only(program, invocation)
    invocation = acknowledge(program, invocation, deadline.identity, TIMER_SET)
    invocation = admit(
        program, invocation, delivered(auction.CLOCK, "t-1", ELAPSED, answers=deadline.identity)
    )
    result = evaluate(program, invocation)
    assert isinstance(result, Blocked)
    (reason,) = result.reasons
    assert isinstance(reason, Refutation)
    assert reason.kind is auction.Highest
