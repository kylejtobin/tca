"""The invariants where the features interact (foundations §4.1, §7.2, §8.2, §9.1, §9.4; acceptance
A3, B1 to B5, D1, N4, N6, N12).

The declarations are ``composite``. Each experiment combines what the earlier modules test one at
a time, and each names what it establishes and no more. Independent review found the defects the
first two experiments regress: a delivery identity shared across sources was one claim, and a
request class demanded under two collections was compiled once. The conditional cases hold the
business requirement each reviewer counterexample assumed, declared with ``When``; the plain
cases beside them are joint construction, where nothing is withheld.
"""

from decimal import Decimal

import pytest

from type_construction.program import (
    Ambiguous,
    Blocked,
    Closed,
    Completed,
    Dispatch,
    Impure,
    InvocationId,
    Malformed,
    Pending,
    Program,
    Refusal,
    Refutation,
    Site,
    Unclosed,
    Uncorrelated,
    Unsolicited,
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
ORDER_APPROVAL = '{"order_id": "o-7", "reviewer": "%s"}'
QUOTE = '{"order_id": "o-7", "amount": "%s"}'
ORDER_CLOSED = '{"order_id": "o-7"}'
PINGED = '{"order_id": "o-7"}'
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
    assert isinstance(reason, Refutation)
    assert reason.premise == "AllDecided.lines[0].approval"


def test_an_ordinary_validator_over_delayed_evidence_defers_the_dependent_effect() -> None:
    """The capture has one declared answer and no declared relation; only a model validator may
    refuse the fact. The shipment, which needs nothing but the order, must still wait, because
    the business declared it demanded only once the eligibility is established."""
    program = composite.DISPATCHING
    invocation = accept(program, InvocationId("dsp"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.CaptureRequest]
    (pending,) = opening.withheld
    assert pending == Pending(
        premise="Dispatched.shipment",
        condition="Dispatched.shipment.condition",
        operations=("type_construction_program.composite.ShipOrder",),
    )

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


def test_the_declared_relationship_makes_the_shipment_wait_for_eligibility() -> None:
    """A separate contract, not a repair of the one above: here the business means the shipment
    to require eligibility universally, so eligibility is a premise of the shipment request, an
    action's own requirement (foundations §7.4). The shipment then waits for the eligibility as
    for any premise, nothing is withheld, a refusing validator blocks with the shipment never
    dispatched, and a passing one releases it."""
    program = composite.GUARDED_DISPATCHING
    invocation = accept(program, InvocationId("gdsp"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.CaptureRequest]
    assert opening.withheld == ()

    short = perform(
        program,
        intend(invocation, opening.dispatch),
        opening.dispatch[0].identity,
        CAPTURED % "20.00",
    )
    blocked = evaluate(program, short)
    assert isinstance(blocked, Blocked)
    assert all(isinstance(r, Malformed) and r.kind is composite.Eligible for r in blocked.reasons)
    assert all(not isinstance(r, composite.GuardedShipOrder) for r in short.intents.values())

    exact = perform(
        program,
        intend(invocation, opening.dispatch),
        opening.dispatch[0].identity,
        CAPTURED % "50.00",
    )
    (ship,) = frontier(evaluate(program, exact)).dispatch
    assert isinstance(ship.request, composite.GuardedShipOrder)
    assert ship.request.eligible.payment.amount.root == Decimal("50.00")


def test_a_native_field_constraint_over_an_unclosed_source_defers_the_dependent_effect() -> None:
    """Regression: a fact with ``Field(min_length=2)`` and no declared selection was taken to
    construct, and the shipment the business declared to wait for it was dispatched before the
    reviews closed. The constraint is judged natively, at the fact's own boundary, once the
    reviews close."""
    program = composite.RELEASING
    invocation = accept(program, InvocationId("rel"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert opening.dispatch == ()
    assert {type(a) for a in opening.awaiting} == {Unsolicited, Unclosed}
    (pending,) = opening.withheld
    assert isinstance(pending, Pending)
    assert pending.condition == "Released.shipment.condition"
    assert pending.operations == ("type_construction_program.composite.ShipOrder",)

    one = admit(program, invocation, delivered(composite.REVIEWERS, "a-1", ORDER_APPROVAL % "ren"))
    assert frontier(evaluate(program, one)).dispatch == ()
    closed_short = admit(program, one, delivered(composite.REVIEWERS, "c-1", ORDER_CLOSED))
    blocked = evaluate(program, closed_short)
    assert isinstance(blocked, Blocked)
    (reason,) = blocked.reasons
    assert isinstance(reason, Malformed)
    assert reason.kind is composite.Endorsed
    assert closed_short.intents == {}

    two = admit(program, one, delivered(composite.REVIEWERS, "a-2", ORDER_APPROVAL % "kai"))
    closed_enough = admit(program, two, delivered(composite.REVIEWERS, "c-1", ORDER_CLOSED))
    assert [type(d.request) for d in frontier(evaluate(program, closed_enough)).dispatch] == [
        composite.ShipOrder
    ]


def test_an_annotated_after_validator_over_delayed_evidence_defers_the_dependent_effect() -> None:
    program = composite.SETTLING
    invocation = accept(program, InvocationId("set"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.CaptureRequest]
    (pending,) = opening.withheld
    assert isinstance(pending, Pending)
    assert pending.condition == "Settled.shipment.condition"
    assert pending.operations == ("type_construction_program.composite.ShipOrder",)
    invocation = intend(invocation, opening.dispatch)
    nothing = perform(program, invocation, opening.dispatch[0].identity, CAPTURED % "0.00")
    blocked = evaluate(program, nothing)
    assert isinstance(blocked, Blocked)
    (reason,) = blocked.reasons
    assert isinstance(reason, Malformed)
    assert reason.kind is composite.Covered
    assert all(not isinstance(r, composite.ShipOrder) for r in nothing.intents.values())
    some = perform(program, invocation, opening.dispatch[0].identity, CAPTURED % "50.00")
    assert [type(d.request) for d in frontier(evaluate(program, some)).dispatch] == [
        composite.ShipOrder
    ]


def test_a_constant_whose_default_its_constraint_refuses_blocks_with_a_structured_reason() -> None:
    """Regression: a default-only class was constructed outside the validated path, and its
    refused default escaped as an exception."""
    program = composite.FLAWED
    invocation = accept(program, InvocationId("flw"), composite.PRICED)
    result = evaluate(program, invocation)
    assert isinstance(result, Blocked)
    (reason,) = result.reasons
    assert isinstance(reason, Malformed)
    assert reason.kind is composite.BadLimit
    assert reason.premise == "Flawed.limit"


def test_a_constraint_on_the_goals_own_field_refuses_the_goal_and_orders_nothing() -> None:
    """Reviewer counterexample, under the amended contract: a minimum length on the goal's own
    field keeps its obligation at that field, refusing the goal with fewer quotes, natively, when
    the goal constructs. It orders nothing: nothing in ``Catalogued`` says the ping waits for the
    quotes, so the ping is demanded jointly with them. With one line the goal is refused after
    the ping was performed, which is the program as declared."""
    program = composite.CATALOGUING
    invocation = accept(program, InvocationId("cat"), composite.REVIEW)
    opening = frontier(evaluate(program, invocation))
    assert sorted(type(d.request).__name__ for d in opening.dispatch) == [
        "PingRequest",
        "QuoteRequest",
        "QuoteRequest",
        "QuoteRequest",
    ]
    assert opening.withheld == ()
    invocation = intend(invocation, opening.dispatch)
    for d in opening.dispatch:
        answer = PINGED if isinstance(d.request, composite.PingRequest) else QUOTE % "5.00"
        invocation = perform(program, invocation, d.identity, answer)
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, composite.Catalogued)
    assert len(result.goal.quotes) == 3

    short = accept(program, InvocationId("cat-1"), composite.ONE_LINE)
    opening = frontier(evaluate(program, short))
    assert sorted(type(d.request).__name__ for d in opening.dispatch) == [
        "PingRequest",
        "QuoteRequest",
    ]
    short = intend(short, opening.dispatch)
    for d in opening.dispatch:
        answer = PINGED if isinstance(d.request, composite.PingRequest) else QUOTE % "5.00"
        short = perform(program, short, d.identity, answer)
    blocked = evaluate(program, short)
    assert isinstance(blocked, Blocked)
    (reason,) = blocked.reasons
    assert isinstance(reason, Malformed)
    assert reason.kind is composite.Catalogued
    assert any(isinstance(r, composite.PingRequest) for r in short.intents.values())


def test_the_declared_condition_on_the_quotes_gates_the_ping() -> None:
    """The business requirement the counterexample above assumed, declared: the quotes at a
    boundary of their own, and the ping demanded only once that boundary constructs. The quotes
    are dispatched, the ping is pending; with one line the quotes' fact is refused and the ping
    was never dispatched; with three the ping is released."""
    program = composite.CATALOGUING_WHEN_QUOTED
    invocation = accept(program, InvocationId("cat"), composite.REVIEW)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.QuoteRequest] * 3
    (pending,) = opening.withheld
    assert pending == Pending(
        premise="CataloguedWhenQuoted.pinged",
        condition="CataloguedWhenQuoted.pinged.condition",
        operations=("type_construction_program.composite.PingRequest",),
    )
    invocation = intend(invocation, opening.dispatch)
    for d in opening.dispatch:
        invocation = perform(program, invocation, d.identity, QUOTE % "5.00")
    assert [type(d.request) for d in frontier(evaluate(program, invocation)).dispatch] == [
        composite.PingRequest
    ]

    short = accept(program, InvocationId("cat-1"), composite.ONE_LINE)
    opening = frontier(evaluate(program, short))
    assert [type(d.request) for d in opening.dispatch] == [composite.QuoteRequest]
    short = perform(
        program, intend(short, opening.dispatch), opening.dispatch[0].identity, QUOTE % "5.00"
    )
    blocked = evaluate(program, short)
    assert isinstance(blocked, Blocked)
    (reason,) = blocked.reasons
    assert isinstance(reason, Malformed)
    assert reason.kind is composite.Quotes
    assert all(not isinstance(r, composite.PingRequest) for r in short.intents.values())


@pytest.mark.parametrize(
    ("program", "goal"),
    [
        (composite.CATALOGUING_WHEN_QUOTED_VIA_DESK, "CataloguedWhenQuotedViaDesk"),
        (composite.CATALOGUING_WHEN_QUOTED_VIA_CHECKED_DESK, "CataloguedWhenQuotedViaCheckedDesk"),
        (composite.CATALOGUING_VIA_GATED_DESK, "CataloguedViaGatedDesk"),
    ],
)
def test_an_opaque_validator_on_a_wrapper_releases_nothing_a_constraint_withholds(
    program: Program, goal: str
) -> None:
    """Under the declared condition, the ping behind a plain wrapper waits for the quotes; behind
    an opaque identity validator it must wait the same; with the conditional itself wrapped in a
    plain fact it waits the same. Packaging changes what the paths are called and nothing about
    what is demanded."""
    invocation = accept(program, InvocationId("cat"), composite.REVIEW)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.QuoteRequest] * 3
    (pending,) = opening.withheld
    assert isinstance(pending, Pending)
    assert pending.premise.startswith(f"{goal}.")
    assert pending.operations == ("type_construction_program.composite.PingRequest",)
    invocation = intend(invocation, opening.dispatch)
    for d in opening.dispatch:
        invocation = perform(program, invocation, d.identity, QUOTE % "5.00")
    assert [type(d.request) for d in frontier(evaluate(program, invocation)).dispatch] == [
        composite.PingRequest
    ]


@pytest.mark.parametrize(
    "program",
    [composite.CATALOGUING, composite.CATALOGUING_VIA_DESK, composite.CATALOGUING_VIA_CHECKED_DESK],
)
def test_a_plain_product_has_one_frontier_however_the_ping_is_packaged(program: Program) -> None:
    """Without a declared condition, the ping beside the quotes is demanded jointly with them,
    whether it sits on the goal, in a plain fact, or behind an opaque identity validator.
    Packaging grants nothing and withholds nothing."""
    invocation = accept(program, InvocationId("cat"), composite.REVIEW)
    opening = frontier(evaluate(program, invocation))
    assert sorted(type(d.request).__name__ for d in opening.dispatch) == [
        "PingRequest",
        "QuoteRequest",
        "QuoteRequest",
        "QuoteRequest",
    ]
    assert opening.withheld == ()
    assert all(all(d.activations == () for d in why.demands) for why in opening.derived)


def test_a_validator_that_alters_its_premise_does_not_alter_the_history() -> None:
    """Regression: a construction ran a validator on the history's own object and changed it."""
    program = composite.PADDING
    invocation = accept(program, InvocationId("pad"), composite.TALLY)
    result = evaluate(program, invocation)
    assert invocation.input == composite.TALLY
    assert isinstance(invocation.input, composite.Count)
    assert invocation.input.tally.counts == [1, 1]
    assert isinstance(result, Blocked)
    assert result.reasons == (Impure(evidence=(0,)),)


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
