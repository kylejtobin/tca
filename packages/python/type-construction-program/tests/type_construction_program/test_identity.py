"""Question 3 of foundations §18: how does effect identity include the invocation, the construction
occurrence and the logical repetition, so that identical premises do not collapse distinct
operations?

The hypothesis under test is the simplest durable identity: a hash of the request as sent. The
second experiment breaks it: two intended operations of one invocation have byte-equal request
bodies and must not share an identity. The identity that repairs it is the invocation, the request
class, and the occurrence of the request: the site of each premise, element indices included, or
how it was built. It is derived from the history, so it is reconstructed rather than allocated; it
is also recorded, because dispatch follows the record. ``test_occurrences`` carries the case that
the coarser identity by evidence alone fails: two equal lines of one order.
"""

import pytest

from type_construction.program import (
    Built,
    EffectIdentity,
    Intended,
    InvocationId,
    Refusal,
    Site,
    UnknownIntent,
    accept,
    admit,
    evaluate,
    failed,
    intend,
)

from . import fulfillment
from .drive import delivered, frontier, only, performing

CAPTURED = '{"order_id": "o-1", "amount": "50.00", "id": "ch_1"}'
APPROVED = '{"order_id": "o-1", "reviewer": "ren"}'


def test_a_retry_keeps_the_identity_and_numbers_a_new_attempt() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    invocation, first = only(program, invocation)
    invocation = failed(invocation, first.identity, "connection refused")
    invocation, second = only(program, invocation)
    invocation = failed(invocation, second.identity, "connection refused")
    invocation, third = only(program, invocation)
    assert first.identity == second.identity == third.identity
    assert (first.attempt, second.attempt, third.attempt) == (1, 2, 3)
    assert len([e for e in invocation.history if isinstance(e, Intended)]) == 1


def test_two_operations_with_equal_request_bodies_have_different_identities() -> None:
    program = fulfillment.SETTLEMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    result = frontier(evaluate(program, invocation))
    assert len(result.dispatch) == 2
    charge, hold = sorted(result.dispatch, key=lambda d: d.identity.operation)
    assert isinstance(charge.request, fulfillment.ChargeRequest)
    assert isinstance(hold.request, fulfillment.HoldRequest)
    assert hold.request.model_dump_json() == charge.request.model_dump_json()
    assert isinstance(hold.identity.occurrence, Built)
    assert isinstance(charge.identity.occurrence, Built)
    assert hold.identity.occurrence.parts == charge.identity.occurrence.parts
    assert hold.identity != charge.identity


def test_another_invocation_with_the_same_input_has_different_identities() -> None:
    program = fulfillment.FULFILLMENT
    one = accept(program, InvocationId("one"), fulfillment.ORDER)
    two = accept(program, InvocationId("two"), fulfillment.ORDER)
    (first,) = frontier(evaluate(program, one)).dispatch
    (second,) = frontier(evaluate(program, two)).dispatch
    assert first.request == second.request
    assert first.identity != second.identity
    assert first.identity.model_dump(exclude={"invocation"}) == second.identity.model_dump(
        exclude={"invocation"}
    )


def test_an_identity_is_reconstructed_from_the_history_not_allocated() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    before = frontier(evaluate(program, invocation))
    again = frontier(evaluate(program, invocation))
    assert before == again
    invocation = intend(invocation, before.dispatch)
    resumed = frontier(evaluate(program, invocation))
    assert resumed.dispatch == before.dispatch
    assert set(invocation.intents) == {d.identity for d in before.dispatch}
    assert before.dispatch[0].identity == EffectIdentity(
        invocation=InvocationId("inv"),
        operation="type_construction_program.fulfillment.ChargeRequest",
        occurrence=Built(
            kind="type_construction_program.fulfillment.ChargeRequest",
            parts=(
                ("order", Site(evidence=0, path=("order", "id"))),
                ("amount", Site(evidence=0, path=("order", "total"))),
            ),
        ),
    )


def test_a_request_built_from_later_evidence_names_that_evidence() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    invocation, charge = performing(program, invocation, CAPTURED)
    invocation = admit(program, invocation, delivered(fulfillment.APPROVALS, "ap-1", APPROVED))
    captured, approved = invocation.evidence
    (ship,) = frontier(evaluate(program, invocation)).dispatch
    assert isinstance(ship.identity.occurrence, Built)
    parts = dict(ship.identity.occurrence.parts)
    assert parts["approval"] == Site(evidence=approved.id)
    assert isinstance(parts["authority"], Built)
    authority = dict(parts["authority"].parts)
    assert authority["payment"] == Site(evidence=captured.id)
    assert authority["order"] == Site(evidence=0, path=("order",))
    assert isinstance(charge.identity.occurrence, Built)
    assert {s for _, s in charge.identity.occurrence.parts} == {
        Site(evidence=0, path=("order", "id")),
        Site(evidence=0, path=("order", "total")),
    }
    assert captured.answers == charge.identity


def test_an_answer_naming_another_operations_intent_is_refused() -> None:
    program = fulfillment.SETTLEMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    proposed = frontier(evaluate(program, invocation))
    invocation = intend(invocation, proposed.dispatch)
    (hold,) = [d for d in proposed.dispatch if isinstance(d.request, fulfillment.HoldRequest)]
    with pytest.raises(Refusal) as refusal:
        admit(
            program,
            invocation,
            delivered(fulfillment.PAYMENTS, "wh-1", CAPTURED, answers=hold.identity),
        )
    assert isinstance(refusal.value.reason, UnknownIntent)
    assert refusal.value.reason.answers == hold.identity
