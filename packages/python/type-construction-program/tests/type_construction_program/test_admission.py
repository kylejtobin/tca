"""The receiving relationship at admission: what ties a delivery to an invocation, and what is
refused. These are contract experiments over an in-memory history. They show what the
declarations require of admission; they do not demonstrate a durable host's behavior under
concurrent, early or redelivered input (acceptance N3 to N6 need a host)."""

from decimal import Decimal

import pytest

from type_construction.program import (
    Closed,
    Conflict,
    Delivered,
    DeliveryId,
    InvocationId,
    NotAccepted,
    Refusal,
    Uncorrelated,
    Unmatched,
    accept,
    admit,
)

from . import fulfillment
from .drive import delivered, only, performing

CAPTURED = '{"order_id": "o-1", "amount": "50.00", "id": "ch_1"}'
CAPTURED_MORE = '{"order_id": "o-1", "amount": "60.00", "id": "ch_1"}'
OTHER_ORDER = '{"order_id": "o-2", "amount": "50.00", "id": "ch_2"}'
APPROVED = '{"order_id": "o-1", "reviewer": "ren"}'


def test_the_same_delivery_twice_is_one_claim_and_a_different_payload_is_a_conflict() -> None:
    program = fulfillment.FULFILLMENT
    invocation, _ = only(program, accept(program, InvocationId("inv"), fulfillment.ORDER))
    once = admit(program, invocation, delivered(fulfillment.PAYMENTS, "wh-1", CAPTURED))
    twice = admit(program, once, delivered(fulfillment.PAYMENTS, "wh-1", CAPTURED))
    assert twice == once
    assert len(once.evidence) == 1
    with pytest.raises(Refusal) as refusal:
        admit(program, once, delivered(fulfillment.PAYMENTS, "wh-1", CAPTURED_MORE))
    reason = refusal.value.reason
    assert isinstance(reason, Conflict)
    assert reason == Conflict(
        delivery=Delivered(delivery=DeliveryId("wh-1")), prior=once.evidence[0].id
    )


def test_equal_field_values_do_not_correlate_without_the_declared_relationship() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    with pytest.raises(Refusal) as refusal:
        admit(program, invocation, delivered(fulfillment.PAYMENTS, "wh-2", OTHER_ORDER))
    reason = refusal.value.reason
    assert isinstance(reason, Uncorrelated)
    assert reason.received is fulfillment.Captured
    assert reason.correlation == fulfillment.BY_ORDER[0]
    assert reason.found == fulfillment.OrderId("o-2")
    assert reason.expected == (fulfillment.OrderId("o-1"),)


def test_a_record_is_admitted_only_from_the_source_declared_for_it() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    with pytest.raises(Refusal) as refusal:
        admit(program, invocation, delivered(fulfillment.PAYMENTS, "ap-1", APPROVED))
    reason = refusal.value.reason
    assert isinstance(reason, Unmatched)
    assert reason.source == fulfillment.PAYMENTS
    assert fulfillment.Approved not in reason.tried
    with pytest.raises(Refusal):
        admit(program, invocation, delivered(fulfillment.CARRIER, "ap-1", APPROVED))
    admitted = admit(program, invocation, delivered(fulfillment.APPROVALS, "ap-1", APPROVED))
    assert isinstance(admitted.evidence[0].value, fulfillment.Approved)


def test_a_receive_held_as_one_record_takes_no_second_answer() -> None:
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    invocation, _ = performing(program, invocation, CAPTURED)
    with pytest.raises(Refusal) as refusal:
        admit(program, invocation, delivered(fulfillment.PAYMENTS, "wh-3", CAPTURED_MORE))
    assert refusal.value.reason == Closed(
        received=fulfillment.Captured, by=invocation.evidence[0].id
    )


def test_an_input_the_program_does_not_accept_opens_no_invocation() -> None:
    order = fulfillment.Order(id=fulfillment.OrderId("o-1"), total=fulfillment.Total(Decimal(1)))
    with pytest.raises(Refusal) as refusal:
        accept(fulfillment.FULFILLMENT, InvocationId("inv"), order)
    assert refusal.value.reason == NotAccepted(
        expected=fulfillment.FulfillOrder, given=fulfillment.Order
    )
