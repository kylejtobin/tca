"""The invariants where the features interact (foundations §4.1, §7.2, §8.2, §9.1, §9.4; acceptance
A3, B1 to B5, D1, N4, N6, N12).

The declarations are ``composite``. Each experiment combines what the earlier modules test one at
a time, and each names what it establishes and no more. Independent review found the defects the
first two experiments regress: a delivery identity shared across sources was one claim, and a
request class demanded under two collections was compiled once.
"""

from decimal import Decimal

import pytest

from type_construction.program import (
    Ambiguous,
    Blocked,
    Closed,
    Completed,
    Deferred,
    Dispatch,
    InvocationId,
    Malformed,
    Refusal,
    Site,
    Unclosed,
    Uncorrelated,
    accept,
    admit,
    evaluate,
    intend,
    perform,
)

from . import composite, fulfillment
from .drive import delivered, frontier, only

SHIPPED = '{"order_id": "o-7", "tracking": "1Z-%s"}'
CLOSED = '{"order_id": "o-7", "sku": "%s", "warehouse": "%s"}'
CAPTURED = '{"order_id": "o-7", "amount": "%s"}'
ORDER_SHIPPED = '{"order_id": "o-7", "tracking": "1Z"}'
ALIASED_ANSWER = '{"order_ref": "o-7", "tracking": "1Z"}'
APPROVED_O1 = '{"order_id": "o-1", "reviewer": "ren"}'


def approval(sku: str, warehouse: str, reviewer: str) -> str:
    return (
        f'{{"order_id": "o-7", "sku": "{sku}", "warehouse": "{warehouse}",'
        f' "reviewer": "{reviewer}"}}'
    )


def at(*path: str | int) -> Site:
    return Site(evidence=0, path=path)


def by_element(dispatches: tuple[Dispatch, ...]) -> dict[Site, Dispatch]:
    found: dict[Site, Dispatch] = {}
    for d in dispatches:
        (element,) = d.elements
        found[element] = d
    return found


def test_a_delivery_identity_is_scoped_to_its_source() -> None:
    """Regression: one DeliveryId at two sources was one claim, and the second payload a
    conflict."""
    program = fulfillment.FULFILLMENT
    invocation = accept(program, InvocationId("inv"), fulfillment.ORDER)
    invocation, charge = only(program, invocation)
    captured = '{"order_id": "o-1", "amount": "50.00", "id": "ch_1"}'
    invocation = admit(program, invocation, delivered(fulfillment.PAYMENTS, "evt-1", captured))
    invocation = admit(program, invocation, delivered(fulfillment.APPROVALS, "evt-1", APPROVED_O1))
    assert [type(e.value) for e in invocation.evidence] == [
        fulfillment.Captured,
        fulfillment.Approved,
    ]
    assert invocation.evidence[0].answers == charge.identity
    again = admit(program, invocation, delivered(fulfillment.APPROVALS, "evt-1", APPROVED_O1))
    assert again == invocation


def test_one_operation_under_two_collections_is_a_request_per_line_of_each() -> None:
    """Regression: the request node was compiled once per request class, so the gift line's
    request was the cart's."""
    program = composite.SHIPPING
    invocation = accept(program, InvocationId("shp"), composite.ORDER)
    opening = frontier(evaluate(program, invocation))
    requests = by_element(opening.dispatch)
    assert set(requests) == {
        at("order", "cart", "lines", 0),
        at("order", "cart", "lines", 1),
        at("order", "gifts", "lines", 0),
    }
    assert len({d.identity for d in opening.dispatch}) == 3
    assert len({d.request.model_dump_json() for d in opening.dispatch}) == 1
    assert opening.withheld == ()

    invocation = intend(invocation, opening.dispatch)
    for element, d in requests.items():
        invocation = perform(program, invocation, d.identity, SHIPPED % element.path[-3])
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, composite.Shipments)
    assert [d.shipment.tracking.root for d in result.goal.cart] == ["1Z-cart", "1Z-cart"]
    assert [d.shipment.tracking.root for d in result.goal.gifts] == ["1Z-gifts"]


def test_an_unnamed_result_for_a_per_line_request_is_not_tied_by_count() -> None:
    program = composite.SHIPPING
    invocation = accept(program, InvocationId("shp"), composite.ORDER)
    opening = frontier(evaluate(program, invocation))
    invocation = intend(invocation, opening.dispatch)
    requests = by_element(opening.dispatch)
    for element in (at("order", "cart", "lines", 0), at("order", "cart", "lines", 1)):
        invocation = perform(program, invocation, requests[element].identity, SHIPPED % "cart")
    with pytest.raises(Refusal) as refusal:
        admit(program, invocation, delivered(composite.CARRIER, "wh-last", SHIPPED % "gifts"))
    assert refusal.value.reason == Uncorrelated(received=composite.LineShipped, correlation=None)


def test_a_correlation_unique_only_as_a_whole_ties_the_record_to_one_line() -> None:
    program = composite.REVIEWING
    invocation = accept(program, InvocationId("rev"), composite.REVIEW)
    invocation = admit(
        program, invocation, delivered(composite.REVIEWERS, "a-1", approval("tea", "w2", "ren"))
    )
    assert invocation.evidence[0].element == at("order", "lines", 1)
    with pytest.raises(Refusal) as refusal:
        admit(
            program, invocation, delivered(composite.REVIEWERS, "a-2", approval("tea", "w3", "ren"))
        )
    unknown = refusal.value.reason
    assert isinstance(unknown, Uncorrelated)
    assert unknown.correlation is not None
    assert unknown.correlation.received == "warehouse"
    with pytest.raises(Refusal) as refusal:
        admit(
            program, invocation, delivered(composite.REVIEWERS, "a-3", approval("mug", "w2", "ren"))
        )
    assert refusal.value.reason == Uncorrelated(received=composite.LineApproved, correlation=None)

    by_sku = composite.DECIDING_BY_SKU
    invocation = accept(by_sku, InvocationId("rev"), composite.REVIEW)
    with pytest.raises(Refusal) as refusal:
        admit(
            by_sku, invocation, delivered(composite.REVIEWERS, "a-1", approval("tea", "w2", "ren"))
        )
    assert refusal.value.reason == Ambiguous(
        source=composite.REVIEWERS,
        admitted=(composite.LineApproved,),
        elements=(at("order", "lines", 0), at("order", "lines", 1)),
    )


def test_closing_one_lines_review_leaves_the_other_lines_open_and_their_evidence_apart() -> None:
    """Regression: a closer admitted anywhere closed every element's collection, and every
    element's tuple held every record the source said."""
    program = composite.REVIEWING
    invocation = accept(program, InvocationId("rev"), composite.REVIEW)
    for delivery, payload in (
        ("a-1", approval("tea", "w1", "ren")),
        ("a-2", approval("tea", "w2", "kai")),
        ("a-3", approval("tea", "w1", "ola")),
    ):
        invocation = admit(program, invocation, delivered(composite.REVIEWERS, delivery, payload))
    invocation = admit(
        program, invocation, delivered(composite.REVIEWERS, "c-1", CLOSED % ("tea", "w1"))
    )
    still = frontier(evaluate(program, invocation))
    held = {a.held for a in still.awaiting if isinstance(a, Unclosed)}
    assert held == {1, 0}

    with pytest.raises(Refusal) as refusal:
        admit(
            program, invocation, delivered(composite.REVIEWERS, "a-4", approval("tea", "w1", "uma"))
        )
    assert isinstance(refusal.value.reason, Closed)
    invocation = admit(
        program, invocation, delivered(composite.REVIEWERS, "a-5", approval("mug", "w1", "uma"))
    )
    invocation = admit(
        program, invocation, delivered(composite.REVIEWERS, "c-2", CLOSED % ("tea", "w2"))
    )
    invocation = admit(
        program, invocation, delivered(composite.REVIEWERS, "c-3", CLOSED % ("mug", "w1"))
    )
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, composite.AllReviewed)
    assert [[a.reviewer.root for a in each.approvals] for each in result.goal.lines] == [
        ["ren", "ola"],
        ["kai"],
        ["uma"],
    ]


def test_a_selection_per_line_is_decided_by_that_lines_closure_alone() -> None:
    program = composite.DECIDING
    invocation = accept(program, InvocationId("dec"), composite.REVIEW)
    for delivery, payload in (
        ("a-1", approval("tea", "w1", "ren")),
        ("a-2", approval("tea", "w1", "kai")),
        ("a-3", approval("tea", "w2", "ola")),
        ("a-4", approval("mug", "w1", "uma")),
        ("c-2", CLOSED % ("tea", "w2")),
        ("c-3", CLOSED % ("mug", "w1")),
    ):
        invocation = admit(program, invocation, delivered(composite.REVIEWERS, delivery, payload))
    waiting = frontier(evaluate(program, invocation))
    assert [a.held for a in waiting.awaiting if isinstance(a, Unclosed)] == [2]
    invocation = admit(
        program, invocation, delivered(composite.REVIEWERS, "c-1", CLOSED % ("tea", "w1"))
    )
    result = evaluate(program, invocation)
    assert isinstance(result, Blocked)
    (reason,) = result.reasons
    assert reason.premise == "AllDecided.lines[0].approval"


def test_an_ordinary_validator_over_delayed_evidence_defers_the_dependent_effect() -> None:
    """The capture has one declared answer and no declared relation; only a model validator may
    refuse the fact. The shipment, which needs nothing but the order, must still wait."""
    program = composite.DISPATCHING
    invocation = accept(program, InvocationId("dsp"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.CaptureRequest]
    (deferred,) = opening.withheld
    assert isinstance(deferred, Deferred)
    assert isinstance(deferred.request, composite.ShipOrder)
    assert deferred.until == ("Dispatched.eligible",)

    short = perform(
        program,
        intend(invocation, opening.dispatch),
        opening.dispatch[0].identity,
        CAPTURED % "20.00",
    )
    blocked = evaluate(program, short)
    assert isinstance(blocked, Blocked)
    (reason,) = blocked.reasons
    assert isinstance(reason, Malformed)
    assert reason.kind is composite.Eligible
    assert all(not isinstance(r, composite.ShipOrder) for r in short.intents.values())

    exact = perform(
        program,
        intend(invocation, opening.dispatch),
        opening.dispatch[0].identity,
        CAPTURED % "50.00",
    )
    assert [type(d.request) for d in frontier(evaluate(program, exact)).dispatch] == [
        composite.ShipOrder
    ]


def test_native_aliases_on_a_request_and_a_fact_keep_their_meaning() -> None:
    """Regression: the evaluator supplied premises by field name to a class that validates by
    alias, so a request or a fact with an alias never constructed."""
    program = composite.ALIASING
    invocation = accept(program, InvocationId("ali"), composite.PRICED)
    (request,) = frontier(evaluate(program, invocation)).dispatch
    assert isinstance(request.request, composite.AliasedRequest)
    assert request.request.model_dump(by_alias=True) == {"order_ref": "o-7"}
    invocation = perform(program, intend(invocation, (request,)), request.identity, ALIASED_ANSWER)
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, composite.AliasedFact)
    assert result.goal.order.total.root == Decimal("50.00")
    assert result.goal.model_dump(by_alias=True)["the_order"]["id"] == "o-7"
