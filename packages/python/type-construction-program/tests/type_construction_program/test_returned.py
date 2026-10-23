"""A returned payload is not evidence until it passes the admission a delivery does
(foundations §4.2, §6.2, §10.4; acceptance F1, N3, N4, N6).

The declarations are ``fulfillment`` and ``lines``. The hypothesis under test is the one the
first slice held: the result an attempt returns is the result, recorded as evidence. The
experiments break it by sending the same claims through both paths: a result for another order,
a result for the other line, a result the invocation never asked for, and a result that repeats
an answer already delivered. Each must be judged the same way whichever way it came.
"""

import pytest

from type_construction.program import (
    Ambiguous,
    Answered,
    Attempted,
    Closed,
    Completed,
    InvocationId,
    Refusal,
    Returned,
    Site,
    Uncorrelated,
    Unrequested,
    accept,
    admit,
    evaluate,
    intend,
    perform,
)

from . import fulfillment, lines
from .drive import delivered, frontier, only

CAPTURED = '{"order_id": "o-1", "amount": "50.00", "id": "ch_1"}'
CAPTURED_MORE = '{"order_id": "o-1", "amount": "60.00", "id": "ch_1"}'
OTHER_ORDER = '{"order_id": "o-2", "amount": "50.00", "id": "ch_2"}'
SHIPPED_BY_SKU = '{"order_id": "o-9", "sku": "%s", "tracking": "1Z"}'


def test_a_result_for_another_order_is_refused_whichever_way_it_comes() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    invocation, charge = only(program, invocation)
    with pytest.raises(Refusal) as by_delivery:
        admit(program, invocation, delivered(fulfillment.PAYMENTS, "wh-1", OTHER_ORDER))
    with pytest.raises(Refusal) as by_return:
        perform(program, invocation, charge.identity, OTHER_ORDER)
    assert isinstance(by_delivery.value.reason, Uncorrelated)
    assert by_delivery.value.reason == by_return.value.reason
    assert invocation.evidence == ()
    assert invocation.attempts(charge.identity) == ()


def test_a_result_this_invocation_never_asked_for_is_not_evidence() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    with pytest.raises(Refusal) as refusal:
        admit(program, invocation, delivered(fulfillment.PAYMENTS, "wh-early", CAPTURED))
    assert refusal.value.reason == Unrequested(
        received=fulfillment.Captured, sends=fulfillment.ChargeRequest
    )
    assert [type(d.request) for d in frontier(evaluate(program, invocation)).dispatch] == [
        fulfillment.ChargeRequest
    ]


def test_a_result_delivered_before_the_attempt_is_the_answer_the_attempt_then_repeats() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    invocation, charge = only(program, invocation)
    invocation = admit(program, invocation, delivered(fulfillment.PAYMENTS, "wh-1", CAPTURED))
    (early,) = invocation.evidence
    assert early.answers == charge.identity
    assert frontier(evaluate(program, invocation)).dispatch == ()

    repeated = perform(program, invocation, charge.identity, CAPTURED)
    assert repeated.evidence == invocation.evidence
    (attempt,) = [e for e in repeated.history if isinstance(e, Attempted)]
    assert attempt.outcome == Answered(evidence=early.id)

    with pytest.raises(Refusal) as refusal:
        perform(program, invocation, charge.identity, CAPTURED_MORE)
    assert refusal.value.reason == Closed(received=fulfillment.Captured, by=early.id)
    with pytest.raises(Refusal) as redelivered:
        admit(program, invocation, delivered(fulfillment.PAYMENTS, "wh-2", CAPTURED_MORE))
    assert redelivered.value.reason == refusal.value.reason


def test_a_result_for_the_other_line_does_not_answer_this_lines_request() -> None:
    program = lines.SHIPPING
    invocation = accept(program, InvocationId("inv"), lines.TWO_DISTINCT)
    proposed = frontier(evaluate(program, invocation))
    invocation = intend(invocation, proposed.dispatch)
    (for_a,) = [d for d in proposed.dispatch if d.request.model_dump()["line"]["sku"] == "A"]
    assert for_a.elements == (Site(evidence=0, path=("order", "lines", 0)),)

    program = lines.SHIPPING_BY_SKU
    invocation = accept(program, InvocationId("inv"), lines.TWO_DISTINCT)
    proposed = frontier(evaluate(program, invocation))
    invocation = intend(invocation, proposed.dispatch)
    (for_a,) = [d for d in proposed.dispatch if d.request.model_dump()["line"]["sku"] == "A"]
    (for_b,) = [d for d in proposed.dispatch if d.request.model_dump()["line"]["sku"] == "B"]
    with pytest.raises(Refusal) as by_return:
        perform(program, invocation, for_a.identity, SHIPPED_BY_SKU % "B")
    assert isinstance(by_return.value.reason, Ambiguous)
    with pytest.raises(Refusal) as by_delivery:
        admit(
            program,
            invocation,
            delivered(lines.CARRIER, "wh-b", SHIPPED_BY_SKU % "B", answers=for_a.identity),
        )
    assert by_delivery.value.reason == by_return.value.reason

    unnamed = admit(program, invocation, delivered(lines.CARRIER, "wh-b", SHIPPED_BY_SKU % "B"))
    assert unnamed.evidence[0].answers == for_b.identity
    returned = perform(program, unnamed, for_a.identity, SHIPPED_BY_SKU % "A")
    assert isinstance(returned.evidence[1].origin, Returned)
    result = evaluate(program, returned)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, lines.AllShippedBySku)
    assert [done.shipment.sku.root for done in result.goal.lines] == ["A", "B"]
