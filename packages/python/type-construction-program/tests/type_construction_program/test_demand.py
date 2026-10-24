"""Demand is rooted in the goal and decisions precede the effects declared to depend on them
(foundations §7.1 to §7.4; acceptance A1 to A5, A7).

The declarations are ``decisions``. The welcome desk's ping needs nothing but the applicant; the
registrar may deny. Where the business declares the ping demanded only once the registrar
allows, the ping waits for that decision, with or without a fallback outcome, and a denial
never pings. Where it declares both jointly, both are asked at once, and a denial leaves the
applicant pinged and not admitted: that is the program as declared, not a defect. The other
experiments bound the rule: independent necessary work stays concurrent, two decisions are made
together, a choice between two effects that nothing decides is reported, not guessed, and
every request dispatched carries the derivation that demanded it.
"""

import pytest

from type_construction.program import (
    AnsweredOtherwise,
    Blocked,
    Built,
    Completed,
    Demand,
    Frontier,
    InvocationId,
    Pending,
    Program,
    Site,
    Unchosen,
    Undecidable,
    Unsolicited,
    accept,
    admit,
    evaluate,
    intend,
    perform,
)

from . import decisions, fulfillment
from .drive import delivered, frontier, performing

ALLOWED = '{"applicant": "ada"}'
DENIED = '{"applicant": "ada", "reason": "no vacancy"}'
PINGED = '{"applicant": "ada"}'
MAILED = '{"applicant": "ada"}'
TEXTED = '{"applicant": "ada"}'
CLEAR = '{"applicant": "ada"}'
FLAGGED = '{"applicant": "ada", "reason": "sanctions"}'


def rated(rating: str) -> str:
    return f'{{"applicant": "ada", "rating": "{rating}"}}'


def requests(result: Frontier) -> list[type[object]]:
    return [type(d.request) for d in result.dispatch]


def test_a_constructible_demanded_request_waits_for_the_decision_it_depends_on() -> None:
    """No fallback: the goal needs both, the registrar may still deny, and the business declared
    the ping demanded only once the registrar allows."""
    program = decisions.ADMISSION
    invocation = accept(program, InvocationId("adm"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert requests(opening) == [decisions.CheckRequest]
    (pending,) = opening.withheld
    assert pending == Pending(
        premise="Granted.pinged",
        condition="Granted.pinged.condition",
        operations=("type_construction_program.decisions.PingRequest",),
    )

    invocation, check = performing(program, invocation, ALLOWED)
    decided = frontier(evaluate(program, invocation))
    assert requests(decided) == [decisions.PingRequest]
    assert decided.withheld == ()
    (why,) = decided.derived
    (demand,) = why.demands
    assert demand.consumer == "Granted.pinged.result"
    (activation,) = demand.activations
    assert activation.conditional == "Granted.pinged"
    assert activation.occurrence == Site(evidence=invocation.evidence[0].id)
    assert invocation.evidence[0].answers == check.identity

    invocation, _ = performing(program, invocation, PINGED)
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, decisions.Granted)
    assert result.goal.pinged.condition == result.goal.allowed
    assert isinstance(result.goal.pinged.result, decisions.Pinged)


def test_a_plain_product_demands_the_ping_jointly_with_the_check() -> None:
    """The amendment, stated: allowed and pinged with nothing declared between them is joint
    construction. Both are asked at once, and a denial leaves the applicant pinged and the goal
    blocked. Where the business means the ping to wait, it declares so; see the test above."""
    program = decisions.JOINT_ADMISSION
    invocation = accept(program, InvocationId("jnt"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert sorted(requests(opening), key=lambda k: k.__name__) == [
        decisions.CheckRequest,
        decisions.PingRequest,
    ]
    assert opening.withheld == ()
    assert [d.demands for d in opening.derived] == [
        (Demand(consumer="Jointly.allowed"),),
        (Demand(consumer="Jointly.pinged"),),
    ]
    invocation = intend(invocation, opening.dispatch)
    (check,) = [d for d in opening.dispatch if isinstance(d.request, decisions.CheckRequest)]
    (ping,) = [d for d in opening.dispatch if isinstance(d.request, decisions.PingRequest)]
    invocation = perform(program, invocation, ping.identity, PINGED)
    invocation = perform(program, invocation, check.identity, DENIED)
    result = evaluate(program, invocation)
    assert isinstance(result, Blocked)
    assert [type(r) for r in result.reasons] == [AnsweredOtherwise]
    assert set(invocation.intents) == {check.identity, ping.identity}


@pytest.mark.parametrize(
    ("program", "goal"),
    [
        (decisions.ADMISSION_VIA_DESK, "GrantedViaDesk"),
        (decisions.ADMISSION_VIA_CHECKED_DESK, "GrantedViaCheckedDesk"),
        (decisions.ADMISSION_VIA_ENCLOSED, "GrantedViaEnclosed"),
    ],
)
def test_a_request_behind_a_wrapper_or_an_opaque_validator_still_waits_for_the_decision(
    program: Program, goal: str
) -> None:
    """Regression: with every construction counted as undecided, the plain wrapper's request was
    taken for evidence-gathering and dispatched beside the registrar's check. Under the declared
    condition, the ping in a plain wrapper, behind an opaque identity validator, or with the
    conditional itself wrapped, waits the same and is released the same."""
    invocation = accept(program, InvocationId("adm"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert requests(opening) == [decisions.CheckRequest]
    (pending,) = opening.withheld
    assert isinstance(pending, Pending)
    assert pending.premise.startswith(f"{goal}.")
    assert pending.operations == ("type_construction_program.decisions.PingRequest",)
    invocation, _ = performing(program, invocation, ALLOWED)
    assert requests(frontier(evaluate(program, invocation))) == [decisions.PingRequest]


def test_a_denial_blocks_and_the_dependent_request_was_never_dispatched() -> None:
    program = decisions.ADMISSION
    invocation = accept(program, InvocationId("adm"), decisions.APPLICANT)
    invocation, check = performing(program, invocation, DENIED)
    result = evaluate(program, invocation)
    assert isinstance(result, Blocked)
    (reason,) = result.reasons
    assert isinstance(reason, AnsweredOtherwise)
    assert (reason.expected, reason.answered) == (decisions.Allowed, decisions.Denied)
    assert set(invocation.intents) == {check.identity}


def test_with_a_fallback_the_branch_not_taken_performs_no_effect() -> None:
    program = decisions.DECISION
    invocation = accept(program, InvocationId("dec"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert requests(opening) == [decisions.CheckRequest]
    (pending,) = opening.withheld
    assert isinstance(pending, Pending)
    assert pending.operations == ("type_construction_program.decisions.PingRequest",)

    invocation, check = performing(program, invocation, DENIED)
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, decisions.Decision)
    assert isinstance(result.goal.outcome, decisions.Rejected)
    assert set(invocation.intents) == {check.identity}

    allowed = accept(program, InvocationId("dec-2"), decisions.APPLICANT)
    allowed, _ = performing(program, allowed, ALLOWED)
    assert requests(frontier(evaluate(program, allowed))) == [decisions.PingRequest]


def test_two_necessary_requests_nothing_can_refute_are_dispatched_together() -> None:
    program = decisions.WELCOME
    invocation = accept(program, InvocationId("wel"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert sorted(requests(opening), key=lambda k: k.__name__) == [
        decisions.MailRequest,
        decisions.PingRequest,
    ]
    assert opening.withheld == ()
    assert all(d.activations == () for why in opening.derived for d in why.demands)


def test_two_decisions_are_made_together() -> None:
    program = decisions.CLEARANCE
    invocation = accept(program, InvocationId("clr"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert sorted(requests(opening), key=lambda k: k.__name__) == [
        decisions.CheckRequest,
        decisions.ScreenRequest,
    ]
    assert {why.demands for why in opening.derived} == {
        (Demand(consumer="Cleared.allowed"),),
        (Demand(consumer="Cleared.clear"),),
    }
    invocation = intend(invocation, opening.dispatch)
    (check,) = [d for d in opening.dispatch if isinstance(d.request, decisions.CheckRequest)]
    (screen,) = [d for d in opening.dispatch if isinstance(d.request, decisions.ScreenRequest)]
    invocation = perform(program, invocation, screen.identity, FLAGGED)
    assert isinstance(evaluate(program, invocation), Blocked)
    invocation = perform(program, invocation, check.identity, ALLOWED)
    blocked = evaluate(program, invocation)
    assert isinstance(blocked, Blocked)
    assert [type(r) for r in blocked.reasons] == [AnsweredOtherwise]


def test_each_request_carries_every_path_that_demands_it_through_the_facts_above() -> None:
    """Two decisions inside one fact, and a mail demanded once that fact is constructed. The
    check is demanded by the registrar's premise and the screen by the screening's, each at its
    own path, once as the goal's premise and once as the mail's condition; the mail is pending
    until both are made, and then carries the fact's occurrence as what activated it."""
    program = decisions.PROCESSING
    invocation = accept(program, InvocationId("prc"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    (check,) = [d for d in opening.dispatch if isinstance(d.request, decisions.CheckRequest)]
    (screen,) = [d for d in opening.dispatch if isinstance(d.request, decisions.ScreenRequest)]
    assert opening.why(check.identity).demands == (
        Demand(consumer="Processed.cleared.allowed"),
        Demand(consumer="Processed.mailed.condition.allowed"),
    )
    assert opening.why(screen.identity).demands == (
        Demand(consumer="Processed.cleared.clear"),
        Demand(consumer="Processed.mailed.condition.clear"),
    )
    (mail,) = opening.withheld
    assert mail == Pending(
        premise="Processed.mailed",
        condition="Processed.mailed.condition",
        operations=("type_construction_program.decisions.MailRequest",),
    )
    invocation = intend(invocation, opening.dispatch)
    invocation = perform(program, invocation, check.identity, ALLOWED)
    assert requests(frontier(evaluate(program, invocation))) == [decisions.ScreenRequest]
    invocation = perform(program, invocation, screen.identity, CLEAR)
    released = frontier(evaluate(program, invocation))
    (mailing,) = released.dispatch
    assert isinstance(mailing.request, decisions.MailRequest)
    (demand,) = released.why(mailing.identity).demands
    (activation,) = demand.activations
    assert activation.condition == "Processed.mailed.condition"
    allowed, clear = invocation.evidence
    assert activation.occurrence == Built(
        kind="type_construction_program.decisions.Cleared",
        parts=(("allowed", Site(evidence=allowed.id)), ("clear", Site(evidence=clear.id))),
    )


def test_a_choice_between_two_effects_nothing_decides_is_not_guessed() -> None:
    program = decisions.NOTIFICATION
    invocation = accept(program, InvocationId("not"), decisions.APPLICANT)
    result = evaluate(program, invocation)
    assert isinstance(result, Blocked)
    (reason,) = result.reasons
    assert isinstance(reason, Undecidable)
    assert reason.premise == "Notified.how"
    assert reason.members == (decisions.ByMail, decisions.ByText)
    assert reason.operations == (
        "type_construction_program.decisions.MailRequest",
        "type_construction_program.decisions.TextRequest",
    )
    assert invocation.intents == {}


@pytest.mark.parametrize(
    ("rating", "sent"), [("5", decisions.MailRequest), ("50", decisions.TextRequest)]
)
def test_the_same_choice_decided_by_a_rating_performs_the_one_the_rating_picks(
    rating: str, sent: type[object]
) -> None:
    program = decisions.RATED_NOTIFICATION
    invocation = accept(program, InvocationId("rated"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert requests(opening) == [decisions.RateRequest]
    assert all(isinstance(w, Unchosen) for w in opening.withheld)
    assert {type(w.request) for w in opening.withheld if isinstance(w, Unchosen)} == {
        decisions.MailRequest,
        decisions.TextRequest,
    }
    invocation, _ = performing(program, invocation, rated(rating))
    decided = frontier(evaluate(program, invocation))
    assert requests(decided) == [sent]
    assert decided.withheld == ()


def test_a_consumer_added_cannot_weaken_what_the_request_requires() -> None:
    program = decisions.HANDLING
    invocation = accept(program, InvocationId("han"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert requests(opening) == [decisions.CheckRequest]
    assert opening.withheld == ()
    invocation, check = performing(program, invocation, DENIED)
    result = evaluate(program, invocation)
    assert isinstance(result, Blocked)
    assert all(isinstance(r, AnsweredOtherwise) for r in result.reasons)
    assert set(invocation.intents) == {check.identity}


def test_a_deciding_request_that_needs_another_result_has_that_result_obtained_first() -> None:
    """In this case deferral does not stall: the ping is needed to decide, so it is dispatched,
    though the goal needs it only alongside the allowance."""
    program = decisions.VETTING
    invocation = accept(program, InvocationId("vet"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert requests(opening) == [decisions.PingRequest]
    assert opening.withheld == ()
    invocation, _ = performing(program, invocation, PINGED)
    assert requests(frontier(evaluate(program, invocation))) == [decisions.VettedCheckRequest]
    invocation, _ = performing(program, invocation, ALLOWED)
    assert isinstance(evaluate(program, invocation), Completed)


def test_a_decision_nothing_is_sent_for_still_defers_the_request_that_depends_on_it() -> None:
    program = decisions.ENDORSEMENT
    invocation = accept(program, InvocationId("end"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert opening.dispatch == ()
    assert [type(a) for a in opening.awaiting] == [Unsolicited]
    (pending,) = opening.withheld
    assert isinstance(pending, Pending)
    assert pending.condition == "Endorsed.pinged.condition"
    invocation = admit(
        program, invocation, delivered(decisions.COMMITTEE, "c-1", '{"applicant": "ada"}')
    )
    assert requests(frontier(evaluate(program, invocation))) == [decisions.PingRequest]


def test_an_alternative_one_member_of_which_nothing_can_refuse_withholds_nothing_beside_it() -> (
    None
):
    """Granted or withdrawn: the registrar may deny the grant, but the withdrawal needs nothing
    and nothing can refuse it, so the alternative as a whole cannot be refused and the mail
    beside it does not depend on the registrar's decision. The mail is dispatched. Inside the
    alternative the grant's requests stay unchosen, as beside any passive alternative."""
    program = decisions.RESOLUTION
    invocation = accept(program, InvocationId("res"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert requests(opening) == [decisions.MailRequest]
    (unchosen,) = [w for w in opening.withheld if isinstance(w, Unchosen)]
    assert isinstance(unchosen.request, decisions.CheckRequest)
    (pending,) = [w for w in opening.withheld if isinstance(w, Pending)]
    assert pending.operations == ("type_construction_program.decisions.PingRequest",)
    assert [type(a) for a in opening.awaiting] == [Unsolicited]


def test_a_passive_alternative_beside_the_charge_leaves_the_charge_unchosen() -> None:
    """Recorded as a limit, not a resolution. Shipped and refused both need the charge; cancelled
    needs nothing but a delivery that may never come. The declarations do not say the charge is
    attempted while a cancellation may still arrive, and shipping cannot be established as the
    outcome while one may: that needs a boundary on the cancellation (foundations §9.4), which
    nothing here declares. So the charge is withheld as unchosen and the invocation waits."""
    program = fulfillment.RACING
    invocation = accept(program, InvocationId("race"), fulfillment.ORDER)
    opening = frontier(evaluate(program, invocation))
    assert opening.dispatch == ()
    assert {a.receives for a in opening.awaiting if isinstance(a, Unsolicited)} == {
        (fulfillment.Approved,),
        (fulfillment.Cancellation,),
    }
    (unchosen,) = opening.withheld
    assert isinstance(unchosen, Unchosen)
    assert isinstance(unchosen.request, fulfillment.ChargeRequest)
    assert unchosen.among == (fulfillment.Shipped, fulfillment.Refused, fulfillment.Cancelled)


def test_a_justified_effect_stays_in_the_history_when_later_work_blocks() -> None:
    program = decisions.CLEARANCE
    invocation = accept(program, InvocationId("clr"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    invocation = intend(invocation, opening.dispatch)
    (check,) = [d for d in opening.dispatch if isinstance(d.request, decisions.CheckRequest)]
    (screen,) = [d for d in opening.dispatch if isinstance(d.request, decisions.ScreenRequest)]
    invocation = perform(program, invocation, check.identity, ALLOWED)
    invocation = perform(program, invocation, screen.identity, FLAGGED)
    assert isinstance(evaluate(program, invocation), Blocked)
    assert set(invocation.intents) == {check.identity, screen.identity}
    assert [type(e.value) for e in invocation.evidence] == [decisions.Allowed, decisions.Flagged]
    assert len(invocation.attempts(check.identity)) == 1
