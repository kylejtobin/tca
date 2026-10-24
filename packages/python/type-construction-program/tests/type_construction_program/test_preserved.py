"""The conditional relationship survives the compositions a type goes through, dependency is
reasoned over occurrences, and a construction from nothing has every obligation a construction
from premises has (foundations §7.2, §7.3, §7.6, §8.1, §8.3; acceptance A3, A5, B1, C3, C4, C6,
E1; decisions 0003 laws 3 to 6, 0005, 0007).

The declarations are ``decisions`` and ``composite``. One conditional is declared directly, under a
business name, as a generic subclass, under ``Annotated`` metadata and with a premise of its own
beside it; each form waits, refuses and releases alike, with unrelated work concurrent, and the
value each constructs equals Pydantic's own. A conditional that leaves its demand open is refused,
never read as a product. A condition that may be established without the effect it governs is a
condition, and the same operation at two distinct occurrences is two; only a condition
established by the very occurrences the conditional governs is refused. A request occurrence is
one send: two answers the source may give are two propositions over it, so a condition
established through either answer is established through that one send, which is dispatched
once with both demands, and a result that is itself one of those answers orders nothing; the
same operation on another collection's elements is another occurrence, whichever way each is
answered. A relation over business constants is established or refuted from nothing exactly as
native construction under the same context judges it, and so is a root constant whose validator
reads that context.
"""

import pytest
from pydantic import ValidationError

from type_construction.program import (
    Activation,
    AnsweredOtherwise,
    Binding,
    Blocked,
    Built,
    Completed,
    Demand,
    Elements,
    Frontier,
    Indeterminate,
    InvocationId,
    Pending,
    Program,
    Refutation,
    Site,
    Unchosen,
    Unsolicited,
    When,
    accept,
    admit,
    evaluate,
    intend,
    perform,
)
from type_construction.world import Fact, Refusals

from . import composite, decisions
from .drive import delivered, frontier, performing

ALLOWED = '{"applicant": "ada"}'
DENIED = '{"applicant": "ada", "reason": "no vacancy"}'
PINGED = '{"applicant": "ada"}'
MAILED = '{"applicant": "ada"}'
APPROVED = '{"applicant": "ada"}'
REFUSED = '{"applicant": "ada", "reason": "unknown"}'
LINE_SHIPPED = '{"order_id": "o-7", "tracking": "1Z-%s"}'
CAPTURED = '{"order_id": "o-7", "amount": "%s"}'
SHIPPED = '{"order_id": "o-7", "tracking": "1Z"}'
CLEARED = '{"order_id": "o-7"}'
HELD = '{"order_id": "o-7", "reason": "recall"}'
PING_REQUEST = "type_construction_program.decisions.PingRequest"
SHIP_LINE = "type_construction_program.composite.ShipLine"
SCREEN_LINE = "type_construction_program.composite.ScreenLine"


def names(result: Frontier) -> list[str]:
    return sorted(type(d.request).__name__ for d in result.dispatch)


@pytest.mark.parametrize("goal", sorted(decisions.ADMISSIONS))
def test_the_conditional_relationship_is_the_same_in_every_form_the_type_takes(goal: str) -> None:
    """Direct, under a business name, generic, annotated, with a premise from the input beside
    it, or with the mail itself beside it: the ping waits for the allowance while the check and
    the mail, which the allowance does not govern, are dispatched together; a denial blocks with
    the ping never intended and the mail still intended; an allowance releases the ping under
    the allowance's occurrence, beside the mail still outstanding; and the goal holds the
    declared class, equal to native construction over the same evidence."""
    program = decisions.ADMISSIONS[goal]
    invocation = accept(program, InvocationId("frm"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert names(opening) == ["CheckRequest", "MailRequest"]
    assert opening.withheld == (
        Pending(
            premise=f"{goal}.pinged",
            condition=f"{goal}.pinged.condition",
            operations=(PING_REQUEST,),
        ),
    )
    assert all(d.activations == () for why in opening.derived for d in why.demands)
    (check,) = [d for d in opening.dispatch if isinstance(d.request, decisions.CheckRequest)]
    (mail,) = [d for d in opening.dispatch if isinstance(d.request, decisions.MailRequest)]

    denied = perform(program, intend(invocation, opening.dispatch), check.identity, DENIED)
    blocked = evaluate(program, denied)
    assert isinstance(blocked, Blocked)
    assert all(isinstance(r, AnsweredOtherwise) for r in blocked.reasons)
    assert set(denied.intents) == {check.identity, mail.identity}

    allowed = perform(program, intend(invocation, opening.dispatch), check.identity, ALLOWED)
    released = frontier(evaluate(program, allowed))
    assert names(released) == ["MailRequest", "PingRequest"]
    assert released.withheld == ()
    (ping,) = [d for d in released.dispatch if isinstance(d.request, decisions.PingRequest)]
    (allowance,) = allowed.evidence
    (demand,) = released.why(ping.identity).demands
    assert demand.consumer == f"{goal}.pinged.result"
    (activation,) = demand.activations
    assert activation.conditional == f"{goal}.pinged"
    assert activation.occurrence == Site(evidence=allowance.id)

    done = perform(program, intend(allowed, (ping,)), ping.identity, PINGED)
    done = perform(program, done, mail.identity, MAILED)
    result = evaluate(program, done)
    assert isinstance(result, Completed)
    pinged = getattr(result.goal, "pinged")  # noqa: B009  the goal's class varies
    assert getattr(pinged, "condition") == getattr(result.goal, "allowed")  # noqa: B009
    assert isinstance(getattr(pinged, "result"), decisions.Pinged)  # noqa: B009
    declared = type(result.goal).model_fields["pinged"].annotation
    assert isinstance(declared, type)
    assert issubclass(declared, When)
    (pinged_evidence,) = [e for e in done.evidence if isinstance(e.value, decisions.Pinged)]
    (mailed_evidence,) = [e for e in done.evidence if isinstance(e.value, decisions.Mailed)]
    given: dict[str, object] = {"condition": allowance.value, "result": pinged_evidence.value}
    if declared is decisions.NotedPing:
        given["applicant"] = decisions.APPLICANT.applicant
    if declared is decisions.PingAndMail:
        given["mailed"] = mailed_evidence.value
    native = declared.model_validate(given, context=Refusals(), by_name=True)  # pyright: ignore[reportUnknownVariableType]  the conditional's arguments are the test's parameter
    assert type(pinged) is declared
    assert pinged == native


def test_a_conditional_that_leaves_its_demand_open_is_refused_not_read_as_a_product() -> None:
    """A generic conditional left unparametrized, and the bare ``When``: what is demanded is not
    declared, so the program is refused naming the open parameter, rather than demanding the
    fields jointly as if nothing had been declared."""
    with pytest.raises(ValidationError) as refusal:
        Program(
            goal=decisions.Unparametrized,
            accepts=decisions.Admit,
            interactions=(decisions.CHECK, decisions.PING),
        )
    message = str(refusal.value)
    assert "Unparametrized.pinged" in message
    assert "Once leaves R open" in message

    class Bare(Fact):
        pinged: When  # pyright: ignore[reportMissingTypeArgument]  the open form under test

    with pytest.raises(ValidationError) as refusal:
        Program(goal=Bare, accepts=decisions.Admit, interactions=(decisions.CHECK, decisions.PING))
    assert "When leaves C, R open" in str(refusal.value)


def test_a_condition_with_an_independent_path_orders_the_effect_it_may_also_need() -> None:
    """Vouched for by the committee's approval or, refused, by the ping. Nothing is dispatched at
    first: the ping is one member's need and not the other's, so it is unchosen inside the
    condition and pending behind it, and the committee is awaited. An approval establishes the
    condition without the ping and releases it, under the vouching's occurrence. A refusal
    leaves the ping as the one way to be vouched for: it is dispatched by the condition's own
    demand, with no activation, and the completed goal holds that one ping at both places."""
    program = decisions.VOUCHING
    invocation = accept(program, InvocationId("vch"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert opening.dispatch == ()
    assert [type(a) for a in opening.awaiting] == [Unsolicited]
    (unchosen,) = [w for w in opening.withheld if isinstance(w, Unchosen)]
    assert isinstance(unchosen.request, decisions.PingRequest)
    assert unchosen.premise == "PingedWhenVouched.pinged.condition.via"
    assert unchosen.among == (decisions.Approved, decisions.Unapproved)
    assert [w for w in opening.withheld if isinstance(w, Pending)] == [
        Pending(
            premise="PingedWhenVouched.pinged",
            condition="PingedWhenVouched.pinged.condition",
            operations=(PING_REQUEST,),
        )
    ]
    assert invocation.intents == {}

    approved = admit(program, invocation, delivered(decisions.COMMITTEE, "c-1", APPROVED))
    released = frontier(evaluate(program, approved))
    (ping,) = released.dispatch
    assert isinstance(ping.request, decisions.PingRequest)
    assert released.withheld == ()
    (approval,) = approved.evidence
    assert released.why(ping.identity).demands == (
        Demand(
            consumer="PingedWhenVouched.pinged.result",
            activations=(
                Activation(
                    conditional="PingedWhenVouched.pinged",
                    condition="PingedWhenVouched.pinged.condition",
                    occurrence=Built(
                        kind="type_construction_program.decisions.Vouched",
                        parts=(("via", Site(evidence=approval.id)),),
                    ),
                ),
            ),
        ),
    )
    done = perform(program, intend(approved, (ping,)), ping.identity, PINGED)
    result = evaluate(program, done)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, decisions.PingedWhenVouched)
    assert isinstance(result.goal.pinged.condition.via, decisions.Approved)
    assert isinstance(result.goal.pinged.result, decisions.Pinged)

    refused = admit(program, invocation, delivered(decisions.COMMITTEE, "c-2", REFUSED))
    needed = frontier(evaluate(program, refused))
    (ping,) = needed.dispatch
    assert isinstance(ping.request, decisions.PingRequest)
    assert needed.why(ping.identity).demands == (
        Demand(consumer="PingedWhenVouched.pinged.condition.via.Unapproved.pinged"),
    )
    assert [type(w) for w in needed.withheld] == [Pending]
    done = perform(program, intend(refused, (ping,)), ping.identity, PINGED)
    result = evaluate(program, done)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, decisions.PingedWhenVouched)
    assert isinstance(result.goal.pinged.condition.via, decisions.Unapproved)
    assert result.goal.pinged.condition.via.pinged == result.goal.pinged.result
    assert isinstance(result.occurrence, Built)
    conditional = dict(result.occurrence.parts)["pinged"]
    assert isinstance(conditional, Built)
    condition = dict(conditional.parts)["condition"]
    assert isinstance(condition, Built)
    via = dict(condition.parts)["via"]
    assert isinstance(via, Built)
    assert dict(via.parts)["pinged"] == dict(conditional.parts)["result"]


def test_an_alternative_whose_members_both_hold_once_the_effect_is_done_is_indeterminate() -> None:
    """Observation for review: reached by the applicant or by the ping, with the applicant in the
    input. The condition is established at once through the applicant and releases the ping. Once
    the ping is there both members hold, and the declaration does not say which the condition is
    made of, so the goal is blocked as indeterminate: the evaluator does not choose a member by
    the order in which they came to hold. ``Vouched`` declares the same business with members
    one answer decides between, and completes."""
    program = decisions.REACHING
    invocation = accept(program, InvocationId("rch"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    (ping,) = opening.dispatch
    assert isinstance(ping.request, decisions.PingRequest)
    (demand,) = opening.why(ping.identity).demands
    (activation,) = demand.activations
    assert activation.occurrence == Built(
        kind="type_construction_program.decisions.Reached",
        parts=(("via", Site(evidence=0, path=("applicant",))),),
    )
    done = perform(program, intend(invocation, (ping,)), ping.identity, PINGED)
    blocked = evaluate(program, done)
    assert isinstance(blocked, Blocked)
    assert blocked.reasons == (
        Indeterminate(
            premise="PingedWhenReached.pinged.condition.via",
            members=(decisions.Applicant, decisions.Pinged),
        ),
    )


def test_one_operation_at_distinct_occurrences_on_both_sides_of_a_conditional_is_ordered() -> None:
    """The gifts shipped only once every cart line is. Shipping a line is one operation; the
    cart's lines and the gifts' are distinct occurrences of it, so the condition does not need
    what the conditional governs. The two cart shipments are dispatched and the gifts' is pending;
    both answered, the condition is established and the gift shipment released under it; the
    goal holds two shipments in the condition and one in the result."""
    program = composite.GIFTING
    invocation = accept(program, InvocationId("gft"), composite.ORDER)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.ShipLine] * 2
    assert {d.elements for d in opening.dispatch} == {
        (Site(evidence=0, path=("order", "cart", "lines", 0)),),
        (Site(evidence=0, path=("order", "cart", "lines", 1)),),
    }
    assert opening.withheld == (
        Pending(
            premise="GiftsAfterCart.gifts",
            condition="GiftsAfterCart.gifts.condition",
            operations=(SHIP_LINE,),
        ),
    )
    invocation = intend(invocation, opening.dispatch)
    for d in opening.dispatch:
        invocation = perform(program, invocation, d.identity, LINE_SHIPPED % d.elements[0].path[-1])
    released = frontier(evaluate(program, invocation))
    (gift,) = released.dispatch
    assert isinstance(gift.request, composite.ShipLine)
    assert gift.elements == (Site(evidence=0, path=("order", "gifts", "lines", 0)),)
    assert released.withheld == ()
    (demand,) = released.why(gift.identity).demands
    assert demand.consumer == "GiftsAfterCart.gifts.result[0].shipment"
    (activation,) = demand.activations
    assert activation.conditional == "GiftsAfterCart.gifts"
    assert isinstance(activation.occurrence, Built)
    assert activation.occurrence.kind.endswith(".CartDone")
    cart = dict(activation.occurrence.parts)["cart"]
    assert isinstance(cart, Elements)
    assert len(cart.of) == 2

    invocation = perform(program, intend(invocation, (gift,)), gift.identity, LINE_SHIPPED % "g")
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, composite.GiftsAfterCart)
    assert [done.shipment.tracking.root for done in result.goal.gifts.condition.cart] == [
        "1Z-0",
        "1Z-1",
    ]
    assert [done.shipment.tracking.root for done in result.goal.gifts.result] == ["1Z-g"]


def test_the_same_occurrences_on_both_sides_of_a_conditional_are_a_cycle_and_refused() -> None:
    """The cart shipped only once the cart is shipped: the condition is established by the very
    shipments the conditional would govern, so the program is refused at declaration, naming the
    conditional, the operation and both places."""
    with pytest.raises(ValidationError) as refusal:
        Program(
            goal=composite.CartAfterCart,
            accepts=composite.ProcessOrder,
            interactions=(composite.SHIP_LINE,),
            bound=(
                Binding(premise="cart.condition.cart", subject="order.cart.lines"),
                Binding(premise="cart.result", subject="order.cart.lines"),
            ),
        )
    message = str(refusal.value)
    assert "CartAfterCart.cart:" in message
    assert "ShipLine at CartAfterCart.cart.condition.cart.*.shipment" in message
    assert "CartAfterCart.cart.result.*.shipment" in message
    assert "orders nothing" in message


def test_two_answers_to_one_check_are_one_occurrence_and_either_establishes_the_condition() -> None:
    """The desk pinged once the registrar has ruled, allowed or denied. One check is dispatched,
    demanded by both members of the condition, and the ping is pending behind it. Either answer
    establishes the ruling and releases the ping, under the ruling's occurrence at that answer,
    and the goal holds the answer the registrar gave."""
    program = decisions.RULING
    invocation = accept(program, InvocationId("rul"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    (check,) = opening.dispatch
    assert isinstance(check.request, decisions.CheckRequest)
    assert sorted(d.consumer for d in opening.why(check.identity).demands) == [
        "PingedWhenRuled.pinged.condition.via.Allowed",
        "PingedWhenRuled.pinged.condition.via.Denied",
    ]
    assert all(d.activations == () for d in opening.why(check.identity).demands)
    assert opening.withheld == (
        Pending(
            premise="PingedWhenRuled.pinged",
            condition="PingedWhenRuled.pinged.condition",
            operations=(PING_REQUEST,),
        ),
    )
    for answer, member in ((ALLOWED, decisions.Allowed), (DENIED, decisions.Denied)):
        ruled = perform(program, intend(invocation, opening.dispatch), check.identity, answer)
        released = frontier(evaluate(program, ruled))
        (ping,) = released.dispatch
        assert isinstance(ping.request, decisions.PingRequest)
        assert released.withheld == ()
        (ruling,) = ruled.evidence
        assert isinstance(ruling.value, member)
        assert released.why(ping.identity).demands == (
            Demand(
                consumer="PingedWhenRuled.pinged.result",
                activations=(
                    Activation(
                        conditional="PingedWhenRuled.pinged",
                        condition="PingedWhenRuled.pinged.condition",
                        occurrence=Built(
                            kind="type_construction_program.decisions.Ruled",
                            parts=(("via", Site(evidence=ruling.id)),),
                        ),
                    ),
                ),
            ),
        )
        done = perform(program, intend(ruled, (ping,)), ping.identity, PINGED)
        result = evaluate(program, done)
        assert isinstance(result, Completed)
        assert isinstance(result.goal, decisions.PingedWhenRuled)
        assert isinstance(result.goal.pinged.condition.via, member)


def test_a_result_that_is_one_answer_to_the_check_its_condition_needs_is_refused() -> None:
    """The allowance demanded once the registrar has ruled: the ruling is established through
    either answer to the one check, and the allowance is that check's answer, so the conditional
    orders nothing. The program is refused naming the one request and every place that demands
    an answer to it."""
    with pytest.raises(ValidationError) as refusal:
        Program(
            goal=decisions.AllowedWhenRuled,
            accepts=decisions.Admit,
            interactions=(decisions.CHECK,),
        )
    message = str(refusal.value)
    assert "AllowedWhenRuled.allowed:" in message
    assert (
        "CheckRequest at AllowedWhenRuled.allowed.condition.via.Allowed and at"
        " AllowedWhenRuled.allowed.condition.via.Denied and at AllowedWhenRuled.allowed.result"
    ) in message
    assert "orders nothing" in message


def test_two_answers_per_subject_keep_distinct_subjects_distinct_occurrences() -> None:
    """The gifts screened only once every cart line is, cleared or held. One screening per cart
    line is dispatched, each demanded by both answers' premises, and the gifts' screening is
    pending. One line cleared and one held, the condition is established and the gift's
    screening released under it, demanded by both of its answers' premises; the goal holds each
    answer where it was given."""
    program = composite.SCREENING
    invocation = accept(program, InvocationId("scr"), composite.ORDER)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.ScreenLine] * 2
    by_line = {d.elements[0].path[-1]: d for d in opening.dispatch}
    assert set(by_line) == {0, 1}
    for index, dispatch in by_line.items():
        assert dispatch.elements == (Site(evidence=0, path=("order", "cart", "lines", index)),)
        assert sorted(d.consumer for d in opening.why(dispatch.identity).demands) == [
            f"GiftsAfterCartScreened.gifts.condition.cart[{index}].verdict.LineCleared",
            f"GiftsAfterCartScreened.gifts.condition.cart[{index}].verdict.LineHeld",
        ]
    assert opening.withheld == (
        Pending(
            premise="GiftsAfterCartScreened.gifts",
            condition="GiftsAfterCartScreened.gifts.condition",
            operations=(SCREEN_LINE,),
        ),
    )
    invocation = intend(invocation, opening.dispatch)
    invocation = perform(program, invocation, by_line[0].identity, CLEARED)
    invocation = perform(program, invocation, by_line[1].identity, HELD)
    released = frontier(evaluate(program, invocation))
    (gift,) = released.dispatch
    assert isinstance(gift.request, composite.ScreenLine)
    assert gift.elements == (Site(evidence=0, path=("order", "gifts", "lines", 0)),)
    assert released.withheld == ()
    demands = released.why(gift.identity).demands
    assert sorted(d.consumer for d in demands) == [
        "GiftsAfterCartScreened.gifts.result[0].verdict.LineCleared",
        "GiftsAfterCartScreened.gifts.result[0].verdict.LineHeld",
    ]
    for demand in demands:
        (activation,) = demand.activations
        assert activation.conditional == "GiftsAfterCartScreened.gifts"
        assert isinstance(activation.occurrence, Built)
        assert activation.occurrence.kind.endswith(".CartScreened")
        cart = dict(activation.occurrence.parts)["cart"]
        assert isinstance(cart, Elements)
        assert len(cart.of) == 2

    invocation = perform(program, intend(invocation, (gift,)), gift.identity, HELD)
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, composite.GiftsAfterCartScreened)
    assert [type(s.verdict) for s in result.goal.gifts.condition.cart] == [
        composite.LineCleared,
        composite.LineHeld,
    ]
    assert [type(s.verdict) for s in result.goal.gifts.result] == [composite.LineHeld]


def test_two_answers_per_subject_on_both_sides_of_a_conditional_are_a_cycle_and_refused() -> None:
    """The cart screened only once the cart is screened, cleared or held: whichever way each
    line is answered, the condition is established through the very screenings the conditional
    would govern, so the program is refused naming the one operation at every place an answer
    to it is demanded."""
    with pytest.raises(ValidationError) as refusal:
        Program(
            goal=composite.CartAfterCartScreened,
            accepts=composite.ProcessOrder,
            interactions=(composite.SCREEN_LINE,),
            bound=(
                Binding(premise="cart.condition.cart", subject="order.cart.lines"),
                Binding(premise="cart.result", subject="order.cart.lines"),
            ),
        )
    message = str(refusal.value)
    assert "CartAfterCartScreened.cart:" in message
    assert (
        "ScreenLine at CartAfterCartScreened.cart.condition.cart.*.verdict.LineCleared and at"
        " CartAfterCartScreened.cart.condition.cart.*.verdict.LineHeld and at"
        " CartAfterCartScreened.cart.result.*.verdict.LineCleared and at"
        " CartAfterCartScreened.cart.result.*.verdict.LineHeld"
    ) in message
    assert "orders nothing" in message


def test_a_relation_over_constants_is_judged_from_nothing_as_native_construction_judges_it() -> (
    None
):
    """Mailed when the fee is waived, texted when it is charged, both decided by relations over
    business constants with nothing to supply. Natively, under the refusal context, the waiver
    constructs and the charge is refuted, not malformed; the evaluator judges the same, so the
    charged member is no longer live and the mail is dispatched. As conditions, the waiver is
    established from nothing and releases the mail at once, and the charge refutes the text."""
    waived = decisions.Waived.model_validate({}, context=Refusals(), by_name=True)
    assert waived == decisions.Waived()
    refusals = Refusals()
    with pytest.raises(ValidationError) as refusal:
        decisions.Billed.model_validate({}, context=refusals, by_name=True)
    assert decisions.Billed.refuted(refusal.value, refusals)

    program = decisions.FEES
    invocation = accept(program, InvocationId("fee"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert names(opening) == ["MailRequest"]
    assert opening.withheld == ()
    invocation, _ = performing(program, invocation, MAILED)
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, decisions.NotifiedByFee)
    assert isinstance(result.goal.how, decisions.MailedFree)
    assert result.goal.how.waived == waived

    program = decisions.WAIVED_MAILING
    invocation = accept(program, InvocationId("wvd"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    (mail,) = opening.dispatch
    (demand,) = opening.why(mail.identity).demands
    (activation,) = demand.activations
    assert activation.occurrence == Built(kind="type_construction_program.decisions.Waived")
    invocation, _ = performing(program, invocation, MAILED)
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, decisions.MailedWhenWaived)
    assert result.goal.mailed.condition == waived

    program = decisions.BILLED_TEXTING
    invocation = accept(program, InvocationId("bld"), decisions.APPLICANT)
    blocked = evaluate(program, invocation)
    assert isinstance(blocked, Blocked)
    (reason,) = blocked.reasons
    assert isinstance(reason, Refutation)
    assert reason.kind is decisions.Billed
    assert reason.premise == "TextedWhenBilled.texted.condition"
    assert invocation.intents == {}


def test_a_root_constant_constructs_natively_under_the_context_its_validator_reads() -> None:
    """A business constant whose validator reads the construction's context, as the elements of
    the reviewer's context case do. Constructed from nothing by the evaluator it has that context,
    like every other construction; the ping beside it is dispatched, and the goal holds the
    constant equal to native construction of its default under the same context."""
    program = decisions.STAFFING
    invocation = accept(program, InvocationId("stf"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert names(opening) == ["PingRequest"]
    invocation, _ = performing(program, invocation, PINGED)
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, decisions.Staffed)
    native = decisions.Office.model_validate("front desk", context=Refusals())
    assert result.goal.office == native
    with pytest.raises(ValidationError, match="outside any context"):
        decisions.Office()


def test_a_condition_over_supplied_premises_equals_native_construction_over_the_evidence() -> None:
    """The declared relation inside the eligibility, over the capture and the order: the
    condition the evaluator constructs equals Pydantic's own construction over the admitted
    capture and the accepted order, and the short capture it refutes is the one native
    construction under the same context refutes."""
    program = composite.DECLARED_DISPATCHING
    invocation = accept(program, InvocationId("dcl"), composite.PRICED)
    exact, _ = performing(program, invocation, CAPTURED % "50")
    (ship,) = frontier(evaluate(program, exact)).dispatch
    done = perform(program, intend(exact, (ship,)), ship.identity, SHIPPED)
    result = evaluate(program, done)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, composite.DeclaredDispatched)
    (captured,) = [e for e in done.evidence if isinstance(e.value, composite.Captured)]
    assert isinstance(captured.value, composite.Captured)
    native = composite.DeclaredEligible.model_validate(
        {
            "order": composite.PRICED.order,
            "payment": captured.value,
            "matched": {"value": captured.value.amount, "bound": composite.PRICED.order.total},
        },
        context=Refusals(),
        by_name=True,
    )
    assert result.goal.shipment.condition == native

    short, _ = performing(program, invocation, CAPTURED % "20")
    blocked = evaluate(program, short)
    assert isinstance(blocked, Blocked)
    (reason,) = blocked.reasons
    assert isinstance(reason, Refutation)
    assert reason.kind is composite.Matches
    (captured,) = short.evidence
    assert isinstance(captured.value, composite.Captured)
    refusals = Refusals()
    with pytest.raises(ValidationError) as refusal:
        composite.Matches.model_validate(
            {"value": captured.value.amount, "bound": composite.PRICED.order.total},
            context=refusals,
            by_name=True,
        )
    assert composite.Matches.refuted(refusal.value, refusals)
    assert reason.refused == tuple(e["msg"] for e in refusal.value.errors())
