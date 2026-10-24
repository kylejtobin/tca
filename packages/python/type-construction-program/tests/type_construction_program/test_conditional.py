"""Conditional demand, declared, and joint construction, undeclared (foundations §7.1 to §7.4,
§8.1, §8.2; acceptance A1 to A5, C1, C5, C6, D1; decisions 0003, 0005, 0006).

The declarations are ``composite`` and ``decisions``. The expected behaviour of each case is
derived from the business program alone: a product demands every field jointly and orders
nothing between them; ``When[C, R]`` demands ``R`` only once ``C`` is constructed through its own
complete native boundary. What the condition checks inside that boundary, a model validator, an
annotated validator, a declared relation, a native constraint, a padding before-validator, a
revalidated element reading the context, changes nothing about when the result is demanded, and
every constructed value equals Pydantic's own construction over the same values. The reviewer's
counterexamples against the rejected strategies are kept as the differentials they were: the
bare constraint refuses what native construction accepts, the stripped element refuses outside
its context, and the evaluator asks neither question.
"""

from decimal import Decimal
from typing import Annotated

import pytest
from pydantic import Field, TypeAdapter, ValidationError

from type_construction.program import (
    Activation,
    Blocked,
    Built,
    Completed,
    Demand,
    Elements,
    Frontier,
    InvocationId,
    Malformed,
    Pending,
    Program,
    Refutation,
    Site,
    Unchosen,
    Unsolicited,
    accept,
    admit,
    evaluate,
    intend,
    perform,
)
from type_construction.world import Refusals

from . import composite, decisions
from .drive import delivered, frontier, performing

CAPTURED = '{"order_id": "o-7", "amount": "%s"}'
ORDER_APPROVAL = '{"order_id": "o-7", "reviewer": "%s"}'
ORDER_CLOSED = '{"order_id": "o-7"}'
VOUCHER = '{"order_id": "o-7", "reviewer": "ren"}'
QUOTE = '{"order_id": "o-7", "amount": "5.00"}'
PINGED = '{"order_id": "o-7"}'
SHIPPED = '{"order_id": "o-7", "tracking": "1Z"}'
LINE_SHIPPED = '{"order_id": "o-7", "tracking": "1Z-%s"}'
ALLOWED = '{"applicant": "ada"}'
DENIED = '{"applicant": "ada", "reason": "no vacancy"}'
DESK_PINGED = '{"applicant": "ada"}'
MAILED = '{"applicant": "ada"}'
SHIP_ORDER = "type_construction_program.composite.ShipOrder"
PING_REQUEST = "type_construction_program.composite.PingRequest"


def names(result: Frontier) -> list[str]:
    return sorted(type(d.request).__name__ for d in result.dispatch)


@pytest.mark.parametrize(
    ("program", "judged", "refusing", "short"),
    [
        (composite.DISPATCHING, composite.Eligible, composite.Eligible, "20"),
        (composite.SETTLING, composite.Covered, composite.Covered, "0.00"),
        (composite.DECLARED_DISPATCHING, composite.DeclaredEligible, composite.Matches, "20"),
        (composite.FLAT_DECLARED_DISPATCHING, composite.Matches, composite.Matches, "20"),
    ],
)
def test_equivalent_formulations_of_one_condition_withhold_refuse_and_release_alike(
    program: Program, judged: type[object], refusing: type[object], short: str
) -> None:
    """One business condition on the capture, as a model validator, as an annotated validator,
    as a declared relation inside a fact, and as the relation itself; in every form the shipment
    is demanded only once the condition is constructed. The capture is dispatched, the shipment
    is pending, a refused condition blocks with the shipment never dispatched, an established one
    releases it with a derivation naming the condition's occurrence, and the goal holds the
    condition that justified the shipment. What differs is the kind of refusal, a declared
    relation's refutation or an ordinary validator's malformed construction, never the demand."""
    invocation = accept(program, InvocationId("cnd"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.CaptureRequest]
    (pending,) = opening.withheld
    assert isinstance(pending, Pending)
    assert pending.premise.endswith(".shipment")
    assert pending.condition == f"{pending.premise}.condition"
    assert pending.operations == (SHIP_ORDER,)
    (why,) = opening.derived
    assert why.revision == invocation.revision
    assert all(d.activations == () for d in why.demands)

    refused = perform(
        program,
        intend(invocation, opening.dispatch),
        opening.dispatch[0].identity,
        CAPTURED % short,
    )
    blocked = evaluate(program, refused)
    assert isinstance(blocked, Blocked)
    (reason,) = blocked.reasons
    assert isinstance(reason, Malformed | Refutation)
    assert isinstance(reason, Refutation) is issubclass(refusing, composite.Matches)
    assert reason.kind is refusing
    assert all(not isinstance(r, composite.ShipOrder) for r in refused.intents.values())

    exact = perform(
        program, intend(invocation, opening.dispatch), opening.dispatch[0].identity, CAPTURED % "50"
    )
    released = frontier(evaluate(program, exact))
    (ship,) = released.dispatch
    assert isinstance(ship.request, composite.ShipOrder)
    (demand,) = released.why(ship.identity).demands
    assert demand.consumer == f"{pending.premise}.result"
    (activation,) = demand.activations
    assert activation.conditional == pending.premise
    assert activation.condition == pending.condition
    assert isinstance(activation.occurrence, Built)
    assert activation.occurrence.kind.endswith(f".{judged.__name__}")

    done = perform(program, intend(exact, (ship,)), ship.identity, SHIPPED)
    result = evaluate(program, done)
    assert isinstance(result, Completed)
    shipment = getattr(result.goal, "shipment")  # noqa: B009  the goal's class varies
    assert isinstance(shipment.condition, judged)
    assert isinstance(shipment.result, composite.OrderShipped)
    assert shipment.result.tracking == composite.Tracking("1Z")
    assert isinstance(result.occurrence, Built)
    witness = dict(result.occurrence.parts)["shipment"]
    assert isinstance(witness, Built)
    assert dict(witness.parts)["condition"] == activation.occurrence


@pytest.mark.parametrize(
    ("program", "judged"),
    [
        (composite.JOINT_DISPATCHING, composite.Eligible),
        (composite.FLAT_DISPATCHING, composite.FlatDispatched),
    ],
)
def test_a_product_demands_jointly_and_a_validator_on_it_is_a_postcondition(
    program: Program, judged: type[object]
) -> None:
    """The amendment, stated as a test. The eligibility and the shipment held by one fact with
    nothing declared between them, nested or flattened: both requests are demanded at once, with
    no condition in force. A short capture then refuses the construction that holds the
    validator, after the shipment was performed, and the frontier never claimed otherwise. The
    two packagings have one frontier; the validator's placement grants and withholds nothing.
    Where the business means the shipment to wait, it declares ``When``, which the test above
    exercises on the same values."""
    invocation = accept(program, InvocationId("jnt"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert names(opening) == ["CaptureRequest", "ShipOrder"]
    assert opening.withheld == ()
    assert all(d.activations == () for why in opening.derived for d in why.demands)
    (capture,) = [d for d in opening.dispatch if isinstance(d.request, composite.CaptureRequest)]
    (ship,) = [d for d in opening.dispatch if isinstance(d.request, composite.ShipOrder)]

    short = intend(invocation, opening.dispatch)
    short = perform(program, short, ship.identity, SHIPPED)
    short = perform(program, short, capture.identity, CAPTURED % "20")
    blocked = evaluate(program, short)
    assert isinstance(blocked, Blocked)
    (reason,) = blocked.reasons
    assert isinstance(reason, Malformed)
    assert reason.kind is judged
    assert ship.identity in short.intents

    exact = intend(invocation, opening.dispatch)
    exact = perform(program, exact, ship.identity, SHIPPED)
    exact = perform(program, exact, capture.identity, CAPTURED % "50")
    assert isinstance(evaluate(program, exact), Completed)


def test_the_flattened_and_the_nested_plain_products_have_one_frontier() -> None:
    """The reviewer's counterexample against packaging as authority, under the amendment: the
    same validator nested in a fact and flattened onto the goal demand the same work, carry the
    same derivations, and withhold nothing. Visibility of the check changed nothing."""
    nested = composite.JOINT_DISPATCHING
    flat = composite.FLAT_DISPATCHING
    first = frontier(evaluate(nested, accept(nested, InvocationId("same"), composite.PRICED)))
    second = frontier(evaluate(flat, accept(flat, InvocationId("same"), composite.PRICED)))
    assert first.dispatch == second.dispatch
    assert first.withheld == second.withheld == ()
    assert {d.consumer.rsplit(".", 1)[-1] for w in first.derived for d in w.demands} == {
        "payment",
        "shipment",
    }
    assert {d.consumer.rsplit(".", 1)[-1] for w in second.derived for d in w.demands} == {
        "payment",
        "shipment",
    }


@pytest.mark.parametrize(
    "program", [composite.DOUBLING, composite.DOUBLING_DECLARED, composite.DOUBLING_PLAIN]
)
def test_two_constructions_with_nothing_declared_between_them_are_demanded_together(
    program: Program,
) -> None:
    """Eligibility behind a validator or a relation, the desk's ping plain or behind an opaque
    identity validator: nothing declared relates them, so the capture and the ping are demanded
    together in every form. No category of check orders anything."""
    invocation = accept(program, InvocationId("dbl"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert names(opening) == ["CaptureRequest", "PingRequest"]
    assert opening.withheld == ()


def test_a_delivery_beside_a_request_leaves_the_request_demanded() -> None:
    """The eligibility's capture beside a voucher behind an opaque identity validator, which a
    delivery supplies: the capture is dispatched and the voucher awaited, together."""
    program = composite.VOUCHED
    invocation = accept(program, InvocationId("vch"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert names(opening) == ["CaptureRequest"]
    assert [type(a) for a in opening.awaiting] == [Unsolicited]
    assert opening.withheld == ()
    vouched = admit(program, invocation, delivered(composite.REVIEWERS, "v-1", VOUCHER))
    assert frontier(evaluate(program, vouched)).dispatch == opening.dispatch


@pytest.mark.parametrize(
    ("program", "judged"),
    [(composite.SECONDING, composite.Seconded), (composite.PREFACING, composite.Prefaced)],
)
def test_a_validator_padding_before_a_length_check_is_judged_by_pydantic_alone(
    program: Program, judged: type[composite.Seconded | composite.Prefaced]
) -> None:
    """Native Pydantic accepts one approval: a before-validator at the field, or a model
    validator running before field validation, pads it to two before the length is checked. The
    shipment, demanded only once the approvals construct, is pending while the reviews are open;
    the condition constructs natively once they close, with one approval; the shipment is
    released, and its derivation names the padded construction. The goal holds what Pydantic
    returned, two approvals, equal to native construction over the same record; the history holds
    the one record admitted; and the witness names that one occurrence."""
    invocation = accept(program, InvocationId("sec"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert opening.dispatch == ()
    (pending,) = opening.withheld
    assert isinstance(pending, Pending)
    assert pending.operations == (SHIP_ORDER,)

    one = admit(program, invocation, delivered(composite.REVIEWERS, "a-1", ORDER_APPROVAL % "ren"))
    assert frontier(evaluate(program, one)).dispatch == ()
    closed = admit(program, one, delivered(composite.REVIEWERS, "c-1", ORDER_CLOSED))
    released = frontier(evaluate(program, closed))
    (ship,) = released.dispatch
    assert isinstance(ship.request, composite.ShipOrder)
    (approval,) = [e for e in closed.evidence if isinstance(e.value, composite.OrderApproval)]
    native = judged.model_validate({"approvals": (approval.value,)}, by_name=True)
    assert len(native.approvals) == 2
    (demand,) = released.why(ship.identity).demands
    (activation,) = demand.activations
    assert activation.occurrence == Built(
        kind=f"type_construction_program.composite.{judged.__name__}",
        parts=(("approvals", Elements(of=(Site(evidence=approval.id),))),),
    )

    done = perform(program, intend(closed, (ship,)), ship.identity, SHIPPED)
    result = evaluate(program, done)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, composite.SecondedRelease | composite.PrefacedRelease)
    assert result.goal.shipment.condition == native
    assert [e.value for e in done.evidence if isinstance(e.value, composite.OrderApproval)] == [
        approval.value
    ]


def test_the_bare_constraint_refuses_what_pydantic_accepts_and_the_evaluator_never_asks_it() -> (
    None
):
    """The reviewer's differential: the field's constraint stripped of its before-validator
    refuses a lone approval that native construction accepts. The evaluator has no judgement of
    its own on any field; the padded quotes on the goal, in a plain fact beside the ping, and as
    the ping's condition each construct natively from one quote and complete with two."""
    approval = composite.OrderApproval(
        order_id=composite.OrderId("o-7"), reviewer=composite.Reviewer("ren")
    )
    stripped: TypeAdapter[tuple[composite.OrderApproval, ...]] = TypeAdapter(
        Annotated[tuple[composite.OrderApproval, ...], Field(min_length=2)]
    )
    with pytest.raises(ValidationError):
        stripped.validate_python((approval,), strict=True)
    assert len(composite.Seconded(approvals=(approval,)).approvals) == 2
    assert composite.Prefaced.model_validate({"approvals": (approval,)}, by_name=True)

    for program in (composite.SECONDED_CATALOGUING, composite.SECONDED_CATALOGUING_VIA_FACT):
        invocation = accept(program, InvocationId("scat"), composite.ONE_LINE)
        opening = frontier(evaluate(program, invocation))
        assert names(opening) == ["PingRequest", "QuoteRequest"]
        invocation = intend(invocation, opening.dispatch)
        for d in opening.dispatch:
            answer = PINGED if isinstance(d.request, composite.PingRequest) else QUOTE
            invocation = perform(program, invocation, d.identity, answer)
        result = evaluate(program, invocation)
        assert isinstance(result, Completed)
        if isinstance(result.goal, composite.SecondedCatalogue):
            padded = result.goal.quotes
        else:
            assert isinstance(result.goal, composite.SecondedCatalogueViaFact)
            padded = result.goal.quoted.quotes
        assert len(padded) == 2
        assert len([e for e in invocation.evidence if isinstance(e.value, composite.Quote)]) == 1

    gated = composite.SECONDED_CATALOGUING_WHEN_QUOTED
    invocation = accept(gated, InvocationId("scat-g"), composite.ONE_LINE)
    opening = frontier(evaluate(gated, invocation))
    assert names(opening) == ["QuoteRequest"]
    quoted = perform(
        gated, intend(invocation, opening.dispatch), opening.dispatch[0].identity, QUOTE
    )
    (ping,) = frontier(evaluate(gated, quoted)).dispatch
    assert isinstance(ping.request, composite.PingRequest)
    done = perform(gated, intend(quoted, (ping,)), ping.identity, PINGED)
    result = evaluate(gated, done)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, composite.SecondedCatalogueWhenQuoted)
    assert len(result.goal.pinged.condition.quotes) == 2
    assert len([e for e in done.evidence if isinstance(e.value, composite.Quote)]) == 1


@pytest.mark.parametrize(
    ("holder", "name", "element"),
    [
        (composite.Notes, "notes", composite.Noted),
        (composite.Stamps, "stamps", composite.Stamped),
    ],
)
def test_a_revalidated_element_reading_the_context_refuses_outside_it(
    holder: type[composite.Notes | composite.Stamps],
    name: str,
    element: type[composite.Noted | composite.Stamped],
) -> None:
    """The reviewer's differential: Pydantic's own construction of the holder revalidates each
    element with the context the construction carries, and accepts; the field's annotation alone
    runs the element's validator with no context and refuses, whether that validator wraps the
    element's class or sits on one of its fields. The evaluator constructs only the holder, with
    the context construction has; the programs below show it."""
    one = element.model_validate({"reviewer": composite.Reviewer("ren")}, context={})
    native = holder.model_validate({name: (one,)}, context=Refusals(), by_name=True)
    assert getattr(native, name) == (one,)
    stripped: TypeAdapter[tuple[object, ...]] = TypeAdapter(
        Annotated[tuple[element, ...], Field(min_length=1)]  # pyright: ignore[reportInvalidTypeForm]
    )
    with pytest.raises(ValidationError, match="outside any context"):
        stripped.validate_python((one,), strict=True)


@pytest.mark.parametrize("program", [composite.NOTING, composite.FLAT_NOTING])
def test_notes_beside_the_shipment_are_joint_and_construct_natively_with_their_context(
    program: Program,
) -> None:
    """The context case as a business program: an order with one note, revalidated with a
    context-reading validator wherever it is held, beside the shipment, at a boundary of its own
    or on the goal's own field. Both are joint: the shipment is dispatched at once, and the goal
    constructs natively once it is answered, equal to Pydantic's own construction over the same
    values, with the context the evaluator carries reaching every revalidated note."""
    invocation = accept(program, InvocationId("note"), composite.TAKEN)
    opening = frontier(evaluate(program, invocation))
    (ship,) = opening.dispatch
    assert isinstance(ship.request, composite.ShipOrder)
    assert opening.withheld == ()
    done = perform(program, intend(invocation, (ship,)), ship.identity, SHIPPED)
    result = evaluate(program, done)
    assert isinstance(result, Completed)
    (shipped,) = done.evidence
    if isinstance(result.goal, composite.Noting):
        native = composite.Notes.model_validate(
            {"notes": composite.TAKEN.notes}, context=Refusals(), by_name=True
        )
        assert result.goal.noted == native
    else:
        assert isinstance(result.goal, composite.FlatNoting)
        native = composite.FlatNoting.model_validate(
            {"notes": composite.TAKEN.notes, "shipment": shipped.value},
            context=Refusals(),
            by_name=True,
        )
        assert result.goal == native


def test_notes_as_the_shipments_condition_are_established_from_the_input_at_once() -> None:
    """The notes as the condition of the shipment: they are in the input, so the condition
    constructs at once, natively, and the shipment is dispatched with that construction as what
    activated it."""
    program = composite.NOTED_SHIPPING
    invocation = accept(program, InvocationId("noted"), composite.TAKEN)
    opening = frontier(evaluate(program, invocation))
    (ship,) = opening.dispatch
    assert opening.withheld == ()
    (demand,) = opening.why(ship.identity).demands
    (activation,) = demand.activations
    assert activation.occurrence == Built(
        kind="type_construction_program.composite.Notes",
        parts=(("notes", Elements(of=(Site(evidence=0, path=("notes", 0)),))),),
    )
    done = perform(program, intend(invocation, (ship,)), ship.identity, SHIPPED)
    result = evaluate(program, done)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, composite.ShippedWhenNoted)
    assert result.goal.shipment.condition.notes == composite.TAKEN.notes


def test_the_conditional_is_one_more_native_boundary_and_equals_pydantics_own_construction() -> (
    None
):
    """A note revalidated wherever it is held, counting its validations. Accepted, it has crossed
    one boundary. The conditional holding it as its condition is a second, constructed natively,
    so the completed goal's note counts two, exactly as Pydantic's own construction of the goal
    over the same values does; the history's note still counts one. A conditional assembled
    without validation would count one and differ from the native oracle."""
    program = composite.COUNTED_SHIPPING
    assert composite.COUNTED.note.passes == 1
    invocation = accept(program, InvocationId("cnt"), composite.COUNTED)
    (ship,) = frontier(evaluate(program, invocation)).dispatch
    done = perform(program, intend(invocation, (ship,)), ship.identity, SHIPPED)
    result = evaluate(program, done)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, composite.ShippedWhenCounted)
    (shipped,) = done.evidence
    assert isinstance(done.input, composite.CountedOrder)
    native = composite.ShippedWhenCounted.model_validate(
        {"shipment": {"condition": done.input.note, "result": shipped.value}},
        context=Refusals(),
        by_name=True,
    )
    assert result.goal == native
    assert result.goal.shipment.condition.passes == 2
    assert done.input.note.passes == 1
    assert invocation.input == composite.COUNTED


def test_one_operation_demanded_jointly_and_conditionally_keeps_its_paths_apart() -> None:
    """The ping demanded directly by the goal and again once the registrar allows. It is one
    operation, dispatched once, and while the allowance is open its derivation names the direct
    demand alone: the conditional path does not exist yet, and sharing the construction does not
    lend it the other path's standing. Once allowed, the same unanswered ping is demanded by
    both, and its derivation names both, the second with the allowance that activated it. The
    completed goal holds one ping at both places."""
    program = decisions.SHARING
    invocation = accept(program, InvocationId("shr"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    (ping,) = [d for d in opening.dispatch if isinstance(d.request, decisions.PingRequest)]
    (check,) = [d for d in opening.dispatch if isinstance(d.request, decisions.CheckRequest)]
    assert opening.why(ping.identity).demands == (Demand(consumer="Shared.direct"),)
    assert opening.why(check.identity).demands == (Demand(consumer="Shared.later.condition"),)
    assert opening.withheld == (
        Pending(
            premise="Shared.later",
            condition="Shared.later.condition",
            operations=("type_construction_program.decisions.PingRequest",),
        ),
    )

    allowed = perform(program, intend(invocation, opening.dispatch), check.identity, ALLOWED)
    again = frontier(evaluate(program, allowed))
    (same,) = again.dispatch
    assert same.identity == ping.identity
    (evidence,) = allowed.evidence
    assert again.why(ping.identity).demands == (
        Demand(consumer="Shared.direct"),
        Demand(
            consumer="Shared.later.result",
            activations=(
                Activation(
                    conditional="Shared.later",
                    condition="Shared.later.condition",
                    occurrence=Site(evidence=evidence.id),
                ),
            ),
        ),
    )
    assert again.withheld == ()

    done = perform(program, allowed, ping.identity, DESK_PINGED)
    result = evaluate(program, done)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, decisions.Shared)
    assert result.goal.later.result == result.goal.direct
    assert isinstance(result.occurrence, Built)
    parts = dict(result.occurrence.parts)
    later = parts["later"]
    assert isinstance(later, Built)
    assert dict(later.parts)["result"] == parts["direct"]


def test_the_order_the_two_demands_are_declared_in_changes_nothing() -> None:
    """``Shared`` with its fields reversed: the conditional path constructs the ping first once
    allowed, and the direct demand meets it second. The direct demand still carries no
    activation, and the conditional one carries the allowance: sharing a construction lends
    neither path the other's conditions, in either order."""
    program = decisions.SHARING_REVERSED
    invocation = accept(program, InvocationId("rev"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    (ping,) = [d for d in opening.dispatch if isinstance(d.request, decisions.PingRequest)]
    (check,) = [d for d in opening.dispatch if isinstance(d.request, decisions.CheckRequest)]
    assert opening.why(ping.identity).demands == (Demand(consumer="SharedReversed.direct"),)
    allowed = perform(program, intend(invocation, opening.dispatch), check.identity, ALLOWED)
    again = frontier(evaluate(program, allowed))
    (evidence,) = allowed.evidence
    assert set(again.why(ping.identity).demands) == {
        Demand(consumer="SharedReversed.direct"),
        Demand(
            consumer="SharedReversed.later.result",
            activations=(
                Activation(
                    conditional="SharedReversed.later",
                    condition="SharedReversed.later.condition",
                    occurrence=Site(evidence=evidence.id),
                ),
            ),
        ),
    }


def test_one_conditional_held_at_two_places_is_one_construction_demanded_twice() -> None:
    """The same conditional ping in a fact held twice by the goal: the check is dispatched once,
    demanded by both places' conditions; the ping is pending at both places; once allowed the
    ping is dispatched once, demanded from both places under the one allowance; and the goal
    holds one ping at both."""
    program = decisions.TWICE
    invocation = accept(program, InvocationId("twc"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    (check,) = opening.dispatch
    assert opening.why(check.identity).demands == (
        Demand(consumer="Twice.one.pinged.condition"),
        Demand(consumer="Twice.two.pinged.condition"),
    )
    assert [w.premise for w in opening.withheld if isinstance(w, Pending)] == [
        "Twice.one.pinged",
        "Twice.two.pinged",
    ]
    allowed = perform(program, intend(invocation, opening.dispatch), check.identity, ALLOWED)
    pinging = frontier(evaluate(program, allowed))
    (ping,) = pinging.dispatch
    assert [
        (d.consumer, [a.conditional for a in d.activations])
        for d in pinging.why(ping.identity).demands
    ] == [
        ("Twice.one.pinged.result", ["Twice.one.pinged"]),
        ("Twice.two.pinged.result", ["Twice.two.pinged"]),
    ]
    assert pinging.withheld == ()
    done = perform(program, intend(allowed, (ping,)), ping.identity, DESK_PINGED)
    result = evaluate(program, done)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, decisions.Twice)
    assert result.goal.one == result.goal.two
    assert isinstance(result.occurrence, Built)
    parts = dict(result.occurrence.parts)
    assert parts["one"] == parts["two"]


def test_a_result_sharing_a_receive_with_its_condition_gates_only_what_the_condition_lacks() -> (
    None
):
    """The paid shipment demanded once the order is eligible, where both the condition and the
    result hold the capture. The capture is demanded by the condition and dispatched; the
    conditional gates the shipment alone, and says so; once eligible, the shipment is released
    and the result holds the very capture the condition holds."""
    program = composite.DISPATCHING_WITH_PAYMENT
    invocation = accept(program, InvocationId("pay"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.CaptureRequest]
    assert opening.withheld == (
        Pending(
            premise="DispatchedWithPayment.shipment",
            condition="DispatchedWithPayment.shipment.condition",
            operations=(SHIP_ORDER,),
        ),
    )
    exact, capture = performing(program, invocation, CAPTURED % "50")
    (ship,) = frontier(evaluate(program, exact)).dispatch
    assert isinstance(ship.request, composite.ShipOrder)
    done = perform(program, intend(exact, (ship,)), ship.identity, SHIPPED)
    result = evaluate(program, done)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, composite.DispatchedWithPayment)
    assert result.goal.shipment.result.payment == result.goal.shipment.condition.payment
    assert isinstance(result.occurrence, Built)
    shipment = dict(result.occurrence.parts)["shipment"]
    assert isinstance(shipment, Built)
    condition, paid = dict(shipment.parts)["condition"], dict(shipment.parts)["result"]
    assert isinstance(condition, Built)
    assert isinstance(paid, Built)
    assert dict(condition.parts)["payment"] == dict(paid.parts)["payment"]
    assert exact.evidence[0].answers == capture.identity


def test_a_chain_of_conditions_is_established_one_at_a_time() -> None:
    """The mail demanded once the ping is there, the ping once the allowance is: the check is
    dispatched first with both effects pending; the allowance releases the ping under one
    activation; the ping releases the mail under two, outermost first."""
    program = decisions.CHAINING
    invocation = accept(program, InvocationId("chn"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [decisions.CheckRequest]
    assert opening.withheld == (
        Pending(
            premise="Chained.mailed",
            condition="Chained.mailed.condition",
            operations=(
                "type_construction_program.decisions.MailRequest",
                "type_construction_program.decisions.PingRequest",
            ),
        ),
    )
    invocation, _ = performing(program, invocation, ALLOWED)
    pinging = frontier(evaluate(program, invocation))
    (ping,) = pinging.dispatch
    assert isinstance(ping.request, decisions.PingRequest)
    (demand,) = pinging.why(ping.identity).demands
    assert demand.consumer == "Chained.mailed.result.condition"
    assert [a.conditional for a in demand.activations] == ["Chained.mailed"]
    assert pinging.withheld == (
        Pending(
            premise="Chained.mailed.result",
            condition="Chained.mailed.result.condition",
            operations=("type_construction_program.decisions.MailRequest",),
        ),
    )
    invocation, _ = performing(program, invocation, DESK_PINGED)
    mailing = frontier(evaluate(program, invocation))
    (mail,) = mailing.dispatch
    assert isinstance(mail.request, decisions.MailRequest)
    (demand,) = mailing.why(mail.identity).demands
    assert demand.consumer == "Chained.mailed.result.result"
    assert [a.conditional for a in demand.activations] == [
        "Chained.mailed",
        "Chained.mailed.result",
    ]
    assert mailing.withheld == ()
    invocation, _ = performing(program, invocation, MAILED)
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, decisions.Chained)
    assert isinstance(result.goal.mailed.result.result, decisions.Mailed)


def test_a_conditional_inside_an_alternative_pings_only_on_the_branch_it_governs() -> None:
    """The desk pinged once allowed, or the applicant rejected. Both members need the check, so
    it is dispatched; the ping is pending the allowance. A denial refutes the conditional member
    and completes the rejection with the ping never dispatched; an allowance refutes the
    rejection and releases the ping."""
    program = decisions.EITHER
    invocation = accept(program, InvocationId("eth"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [decisions.CheckRequest]
    assert [type(w) for w in opening.withheld] == [Pending]
    assert not any(isinstance(w, Unchosen) for w in opening.withheld)

    denied, check = performing(program, invocation, DENIED)
    result = evaluate(program, denied)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, decisions.Either)
    assert isinstance(result.goal.outcome, decisions.Rejected)
    assert set(denied.intents) == {check.identity}

    allowed, _ = performing(program, invocation, ALLOWED)
    (ping,) = frontier(evaluate(program, allowed)).dispatch
    assert isinstance(ping.request, decisions.PingRequest)
    done = perform(program, intend(allowed, (ping,)), ping.identity, DESK_PINGED)
    result = evaluate(program, done)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, decisions.Either)
    assert not isinstance(result.goal.outcome, decisions.Rejected)
    assert isinstance(result.goal.outcome.result, decisions.Pinged)


def test_a_condition_established_only_by_the_effect_it_gates_is_refused_at_declaration() -> None:
    """A validator that needs the shipment's result is a postcondition, not prior authorization.
    Declared as the shipment's condition, it would be established only by the shipment itself,
    so the conditional orders nothing; the program is refused, naming the conditional, the
    operation and where the condition and the result demand it. The evaluator does not validate
    part of the condition to escape this."""
    with pytest.raises(ValidationError) as refusal:
        Program(
            goal=composite.Circular,
            accepts=composite.FulfillOrder,
            interactions=(composite.CAPTURE, composite.SHIP_ORDER),
        )
    message = str(refusal.value)
    assert "Circular.shipment:" in message
    assert "every request the result demands is one the condition is established through" in message
    assert "ShipOrder at Circular.shipment.condition.shipment and at Circular.shipment.result" in (
        message
    )
    assert "orders nothing" in message
    assert "postcondition" in message

    with pytest.raises(ValidationError) as refusal:
        Program(goal=decisions.Vacuous, accepts=decisions.Admit, interactions=(decisions.PING,))
    message = str(refusal.value)
    assert "Vacuous.pinged:" in message
    assert "PingRequest at Vacuous.pinged.condition.pinged and at Vacuous.pinged.result" in message


def test_a_condition_per_element_releases_each_elements_effect_on_its_own() -> None:
    """Every line shipped only once it is quoted. Three quotes are dispatched and three shipments
    are pending, one per line; the first line's quote releases that line's shipment alone, with
    the line's quote as what activated it, while the others stay pending; every line quoted and
    shipped completes the goal with each shipment under its own line."""
    program = composite.QUOTED_SHIPPING
    invocation = accept(program, InvocationId("qsh"), composite.REVIEW)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.QuoteRequest] * 3
    assert [w.premise for w in opening.withheld if isinstance(w, Pending)] == [
        f"QuotedShipments.lines[{i}].shipment" for i in range(3)
    ]
    quotes = {d.elements[0].path[-1]: d for d in opening.dispatch}
    invocation = intend(invocation, opening.dispatch)
    invocation = perform(program, invocation, quotes[0].identity, QUOTE)
    first = frontier(evaluate(program, invocation))
    assert names(first) == ["QuoteRequest", "QuoteRequest", "ShipLine"]
    (ship,) = [d for d in first.dispatch if isinstance(d.request, composite.ShipLine)]
    assert ship.elements == (Site(evidence=0, path=("order", "lines", 0)),)
    assert [w.premise for w in first.withheld if isinstance(w, Pending)] == [
        "QuotedShipments.lines[1].shipment",
        "QuotedShipments.lines[2].shipment",
    ]
    (demand,) = first.why(ship.identity).demands
    (activation,) = demand.activations
    assert activation.conditional == "QuotedShipments.lines[0].shipment"
    assert isinstance(activation.occurrence, Built)
    assert activation.occurrence.kind.endswith(".LineQuoted")
    assert dict(activation.occurrence.parts)["line"] == Site(evidence=0, path=("order", "lines", 0))

    invocation = perform(program, intend(invocation, (ship,)), ship.identity, LINE_SHIPPED % "0")
    for index in (1, 2):
        invocation = perform(program, invocation, quotes[index].identity, QUOTE)
    rest = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in rest.dispatch] == [composite.ShipLine] * 2
    invocation = intend(invocation, rest.dispatch)
    for d in rest.dispatch:
        invocation = perform(program, invocation, d.identity, LINE_SHIPPED % d.elements[0].path[-1])
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, composite.QuotedShipments)
    assert [line.shipment.result.tracking.root for line in result.goal.lines] == [
        "1Z-0",
        "1Z-1",
        "1Z-2",
    ]
    assert [line.shipment.condition.line for line in result.goal.lines] == list(
        composite.REVIEW.order.lines
    )


def test_a_frontier_carries_one_derivation_per_request_and_no_other() -> None:
    program = decisions.WELCOME
    opening = frontier(evaluate(program, accept(program, InvocationId("wel"), decisions.APPLICANT)))
    assert [d.identity for d in opening.derived] == [d.identity for d in opening.dispatch]
    with pytest.raises(ValidationError):
        Frontier(dispatch=opening.dispatch, derived=())
    with pytest.raises(ValidationError):
        Frontier(dispatch=opening.dispatch[:1], derived=opening.derived)
    with pytest.raises(KeyError):
        opening.why(opening.dispatch[0].identity.model_copy(update={"operation": "none"}))


def test_short_capture_in_the_declared_form_blocks_before_any_shipment() -> None:
    """The declared form, driven to its refusal: with the condition's construction refused the
    conditional is refused, the goal is blocked, and the shipment was never intended. The
    Decimal the condition refused is the one admitted."""
    program = composite.DISPATCHING
    invocation = accept(program, InvocationId("dsp"), composite.PRICED)
    invocation, capture = performing(program, invocation, CAPTURED % "20")
    blocked = evaluate(program, invocation)
    assert isinstance(blocked, Blocked)
    (reason,) = blocked.reasons
    assert isinstance(reason, Malformed)
    assert reason.kind is composite.Eligible
    assert reason.premise == "Dispatched.shipment.condition"
    assert set(invocation.intents) == {capture.identity}
    (captured,) = invocation.evidence
    assert isinstance(captured.value, composite.Captured)
    assert captured.value.amount.root == Decimal("20")
