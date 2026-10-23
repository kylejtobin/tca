"""Demand is rooted in the goal and decisions precede their dependent effects (foundations §7.1
to §7.4; acceptance A1 to A5, A7).

The declarations are ``decisions``. The hypothesis under test is the one the first slice held:
a request whose premises are available and whose result the goal needs is justified. The first
experiments break it: the welcome desk's ping needs nothing but the applicant and the goal needs
it, yet the registrar may deny, and then the ping would have been performed for nothing. The
rule that repairs it is causal: while a premise of a conjunction is undecided, only the requests
that decide it are dispatched, with or without a fallback outcome. The later experiments bound
the repair: independent necessary work stays concurrent, two decisions are made together, and a
choice between two effects that nothing decides is reported, not guessed.
"""

import pytest

from type_construction.program import (
    AnsweredOtherwise,
    Blocked,
    Completed,
    Deferred,
    Frontier,
    InvocationId,
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
    """No fallback: the goal needs both, and the registrar may still deny."""
    program = decisions.ADMISSION
    invocation = accept(program, InvocationId("adm"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert requests(opening) == [decisions.CheckRequest]
    (deferred,) = opening.withheld
    assert isinstance(deferred, Deferred)
    assert isinstance(deferred.request, decisions.PingRequest)
    assert deferred.until == ("Granted.allowed",)

    invocation, _ = performing(program, invocation, ALLOWED)
    decided = frontier(evaluate(program, invocation))
    assert requests(decided) == [decisions.PingRequest]
    assert decided.withheld == ()
    assert decided.dispatch[0].identity == deferred.identity

    invocation, _ = performing(program, invocation, PINGED)
    assert isinstance(evaluate(program, invocation), Completed)


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
    assert [type(w) for w in opening.withheld] == [Unchosen]
    assert isinstance(opening.withheld[0].request, decisions.PingRequest)

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


def test_two_decisions_are_made_together() -> None:
    program = decisions.CLEARANCE
    invocation = accept(program, InvocationId("clr"), decisions.APPLICANT)
    opening = frontier(evaluate(program, invocation))
    assert sorted(requests(opening), key=lambda k: k.__name__) == [
        decisions.CheckRequest,
        decisions.ScreenRequest,
    ]
    invocation = intend(invocation, opening.dispatch)
    (check,) = [d for d in opening.dispatch if isinstance(d.request, decisions.CheckRequest)]
    (screen,) = [d for d in opening.dispatch if isinstance(d.request, decisions.ScreenRequest)]
    invocation = perform(program, invocation, screen.identity, FLAGGED)
    assert isinstance(evaluate(program, invocation), Blocked)
    invocation = perform(program, invocation, check.identity, ALLOWED)
    blocked = evaluate(program, invocation)
    assert isinstance(blocked, Blocked)
    assert [type(r) for r in blocked.reasons] == [AnsweredOtherwise]


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
    assert {type(w.request) for w in opening.withheld} == {
        decisions.MailRequest,
        decisions.TextRequest,
    }
    assert all(isinstance(w, Unchosen) for w in opening.withheld)
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
    (deferred,) = opening.withheld
    assert isinstance(deferred, Deferred)
    assert deferred.until == ("Endorsed.approved",)
    invocation = admit(
        program, invocation, delivered(decisions.COMMITTEE, "c-1", '{"applicant": "ada"}')
    )
    assert requests(frontier(evaluate(program, invocation))) == [decisions.PingRequest]


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
