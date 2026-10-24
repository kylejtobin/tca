"""The history owns its values (foundations §4.2, §10.2; decision 0006).

What a caller hands the history, the accepted input and each committed request, the history
copies; what the evaluator derives, requests and the goal, are constructions of its own. So a
caller that goes on changing its objects after acceptance or intent changes no recorded premise,
no evaluation and no effect identity, and a caller that changes what the evaluator handed back
changes nothing recorded either. The declarations are ``composite`` and ``fulfillment``; the
mutable value is the list of counts a ``Tally`` holds.
"""

from decimal import Decimal

from pydantic import BaseModel

from type_construction.program import (
    Blocked,
    Completed,
    Frontier,
    Impure,
    InvocationId,
    accept,
    evaluate,
    intend,
    perform,
)

from . import composite, fulfillment
from .drive import frontier

CAPTURED = '{"order_id": "o-1", "amount": "50.00", "id": "ch_1"}'
APPROVED = '{"order_id": "o-1", "reviewer": "ren"}'
SHIPPED = '{"order_id": "o-1", "tracking": "1Z"}'


def test_changing_the_callers_input_after_acceptance_changes_nothing_recorded() -> None:
    program = composite.PADDING
    given = composite.Count(id=composite.OrderId("o-7"), tally=composite.Tally(counts=[1, 1]))
    invocation = accept(program, InvocationId("own"), given)
    assert invocation.input == given
    assert invocation.input is not given
    given.tally.counts.append(99)
    assert isinstance(invocation.input, composite.Count)
    assert invocation.input.tally.counts == [1, 1]
    result = evaluate(program, invocation)
    assert isinstance(result, Blocked)
    assert result.reasons == (Impure(evidence=(0,)),)
    assert invocation.input.tally.counts == [1, 1]


def test_changing_the_callers_input_changes_no_effect_identity_or_request() -> None:
    """The input's nested values are what requests are built from. The caller's later change to
    its own object leaves the recorded premise, the request built from it and the identity of
    the effect exactly as before."""
    program = fulfillment.FULFILLMENT
    given = fulfillment.FulfillOrder(
        order=fulfillment.Order(id=fulfillment.OrderId("o-1"), total=fulfillment.Total(Decimal(50)))
    )
    invocation = accept(program, InvocationId("own"), given)
    (charge,) = frontier(evaluate(program, invocation)).dispatch
    object.__setattr__(given.order, "total", fulfillment.Total(Decimal(99)))
    (again,) = frontier(evaluate(program, invocation)).dispatch
    assert again == charge
    assert again.identity == charge.identity
    assert isinstance(again.request, fulfillment.ChargeRequest)
    assert again.request.amount.root == Decimal(50)


def test_changing_a_dispatch_after_intent_changes_no_committed_request() -> None:
    """The dispatch the evaluator hands the host is the host's; the intent the history commits is
    its own copy. The attempt's answer then admits against the recorded request."""
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("own"), fulfillment.ORDER)
    (charge,) = frontier(evaluate(program, invocation)).dispatch
    committed = intend(invocation, (charge,))
    assert committed.intents[charge.identity] == charge.request
    assert committed.intents[charge.identity] is not charge.request
    assert isinstance(charge.request, fulfillment.ChargeRequest)
    object.__setattr__(charge.request, "amount", fulfillment.Total(Decimal(1)))
    recorded = committed.intents[charge.identity]
    assert isinstance(recorded, fulfillment.ChargeRequest)
    assert recorded.amount.root == Decimal(50)
    answered = perform(program, committed, charge.identity, CAPTURED)
    assert answered.intents[charge.identity] == recorded


def test_what_the_evaluator_hands_back_is_its_own_and_changing_it_touches_no_history() -> None:
    """A constructed goal and the requests in a frontier are built from the evaluator's copies.
    Changing them changes neither the recorded evidence nor a later evaluation."""
    program = composite.SECONDED_CATALOGUING_WHEN_QUOTED
    invocation = accept(program, InvocationId("own"), composite.ONE_LINE)
    opening = frontier(evaluate(program, invocation))
    (quote,) = opening.dispatch
    assert isinstance(quote.request, composite.QuoteRequest)
    assert quote.request.line is not composite.ONE_LINE.order.lines[0]
    quoted = perform(
        program,
        intend(invocation, opening.dispatch),
        quote.identity,
        '{"order_id": "o-7", "amount": "5.00"}',
    )
    (ping,) = frontier(evaluate(program, quoted)).dispatch
    done = perform(program, intend(quoted, (ping,)), ping.identity, '{"order_id": "o-7"}')
    first = evaluate(program, done)
    assert isinstance(first, Completed)
    goal = first.goal
    assert isinstance(goal, composite.SecondedCatalogueWhenQuoted)
    quoted = goal.pinged.condition
    assert all(isinstance(e.value, BaseModel) for e in done.evidence)
    assert all(quoted.quotes[0].quote is not e.value for e in done.evidence)
    object.__setattr__(quoted, "quotes", ())
    second = evaluate(program, done)
    assert isinstance(second, Completed)
    assert isinstance(second.goal, composite.SecondedCatalogueWhenQuoted)
    assert len(second.goal.pinged.condition.quotes) == 2
    assert isinstance(evaluate(program, done), Completed | Frontier)
