"""What a judgement the evaluator cannot read justifies, and what native construction decides
(foundations §7.2, §7.3, §8.1, §8.2; acceptance A1 to A5, B1, B3; decisions 0003, 0005, 0006).

The declarations are ``composite``. The expected behaviour of each case is derived from the
business program alone, by taking both of what an unread validator might be, a condition or an
identity, and keeping only what holds either way: a request is dispatched only when it would be
dispatched under both readings, and waits otherwise. Where neither reading settles the order,
the evaluator reports what the declarations did not establish instead of choosing. The
equivalent formulation of each condition as a declared relation is exercised beside it, and
constructed results are compared with Pydantic's own construction over the same input.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from type_construction.program import (
    Blocked,
    Bounded,
    Built,
    Completed,
    Decided,
    Deferred,
    Elements,
    InvocationId,
    Malformed,
    Program,
    Refutation,
    Site,
    Undetermined,
    Unread,
    Unsolicited,
    accept,
    admit,
    evaluate,
    intend,
    perform,
)
from type_construction.program.declaration import early
from type_construction.program.evaluation import checked

from . import composite
from .drive import delivered, frontier

CAPTURED = '{"order_id": "o-7", "amount": "%s"}'
ORDER_APPROVAL = '{"order_id": "o-7", "reviewer": "%s"}'
ORDER_CLOSED = '{"order_id": "o-7"}'
VOUCHER = '{"order_id": "o-7", "reviewer": "ren"}'
QUOTE = '{"order_id": "o-7", "amount": "5.00"}'
PINGED = '{"order_id": "o-7"}'
SHIPPED = '{"order_id": "o-7", "tracking": "1Z"}'


def operations(blocked: Blocked) -> tuple[str, ...]:
    (reason,) = blocked.reasons
    assert isinstance(reason, Undetermined)
    return tuple(o.rsplit(".", 1)[-1] for o in reason.operations)


@pytest.mark.parametrize(
    ("program", "judged", "refusal", "established"),
    [
        (composite.DISPATCHING, composite.Eligible, Malformed, False),
        (composite.DECLARED_DISPATCHING, composite.Matches, Refutation, True),
    ],
)
def test_the_same_condition_as_a_validator_or_a_relation_withholds_and_releases_alike(
    program: Program, judged: type[object], refusal: type[object], *, established: bool
) -> None:
    """One business condition, the capture equals the total, written as a model validator and
    as a declared relation. The effects are the same either way: the capture is dispatched, the
    shipment waits, a short capture blocks with the shipment never dispatched, an exact one
    releases it. What differs is knowledge, not authority: the relation is a decision the
    evaluator reads, so the shipment's dependency is established and the refusal is a
    refutation; the validator is unread, so the dependency is reported unresolved and the
    refusal is a malformed construction."""
    invocation = accept(program, InvocationId("dsp"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.CaptureRequest]
    (deferred,) = opening.withheld
    assert isinstance(deferred, Deferred)
    assert isinstance(deferred.request, composite.ShipOrder)
    assert (deferred.unread == ()) is established
    assert all(isinstance(j, Decided) for j in deferred.behind) is established

    short = perform(
        program, intend(invocation, opening.dispatch), opening.dispatch[0].identity, CAPTURED % "20"
    )
    blocked = evaluate(program, short)
    assert isinstance(blocked, Blocked)
    (reason,) = blocked.reasons
    assert isinstance(reason, refusal)
    assert isinstance(reason, Malformed | Refutation)
    assert reason.kind is judged
    assert all(not isinstance(r, composite.ShipOrder) for r in short.intents.values())

    exact = perform(
        program, intend(invocation, opening.dispatch), opening.dispatch[0].identity, CAPTURED % "50"
    )
    (ship,) = frontier(evaluate(program, exact)).dispatch
    assert isinstance(ship.request, composite.ShipOrder)


def test_two_unread_judgements_each_needing_an_effect_block_naming_what_is_not_established() -> (
    None
):
    """Eligibility behind a model validator, resolved only by the capture; the desk's ping
    behind an opaque identity validator, resolved only by the ping. If both validators are
    conditions, both requests decide and go together; if the desk's is an identity, the ping
    depends on the eligibility and must wait; if the eligibility's is an identity, the capture
    must wait for the desk. The declarations do not say which, so nothing is dispatched and the
    evaluator names the two judgements and the two requests rather than guess."""
    program = composite.DOUBLING
    invocation = accept(program, InvocationId("dbl"), composite.PRICED)
    result = evaluate(program, invocation)
    assert isinstance(result, Blocked)
    (reason,) = result.reasons
    assert reason == Undetermined(
        judgements=(
            Unread(premise="Doubly.desk", kind=composite.CheckedPingDesk),
            Unread(premise="Doubly.eligible", kind=composite.Eligible),
        ),
        operations=(
            "type_construction_program.composite.CaptureRequest",
            "type_construction_program.composite.PingRequest",
        ),
    )
    assert invocation.intents == {}


def test_declaring_one_condition_readably_is_the_smallest_change_that_orders_the_other() -> None:
    """The same two constructions, with the eligibility's condition declared as a relation. The
    capture now feeds a decision the evaluator reads, so it is dispatched; the ping, behind an
    unread validator, would be a deciding request if that validator is a condition and a
    dependent one if it is not, so it waits for the readable decision and is reported
    unresolved. A refuted relation blocks with no ping; a satisfied one releases it."""
    program = composite.DOUBLING_DECLARED
    invocation = accept(program, InvocationId("dbd"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.CaptureRequest]
    (deferred,) = opening.withheld
    assert isinstance(deferred, Deferred)
    assert isinstance(deferred.request, composite.PingRequest)
    assert deferred.behind == (Decided(premise="DoublyDeclared.eligible.matched"),)
    assert deferred.unread == (
        Unread(premise="DoublyDeclared.desk", kind=composite.CheckedPingDesk),
    )

    short = perform(
        program, intend(invocation, opening.dispatch), opening.dispatch[0].identity, CAPTURED % "20"
    )
    blocked = evaluate(program, short)
    assert isinstance(blocked, Blocked)
    (reason,) = blocked.reasons
    assert isinstance(reason, Refutation)
    assert reason.kind is composite.Matches
    assert all(not isinstance(r, composite.PingRequest) for r in short.intents.values())

    exact = perform(
        program, intend(invocation, opening.dispatch), opening.dispatch[0].identity, CAPTURED % "50"
    )
    (ping,) = frontier(evaluate(program, exact)).dispatch
    assert isinstance(ping.request, composite.PingRequest)


def test_a_plain_wrapper_beside_an_unread_judgement_waits_for_it_as_unresolved() -> None:
    """The desk's ping in a plain fact beside the eligibility's validator: the ping decides
    nothing, so if the validator is a condition the ping must wait, and if it is an identity the
    ping could go. Less knowledge releases nothing: it waits, named as unresolved, and goes when
    the eligibility constructs."""
    program = composite.DOUBLING_PLAIN
    invocation = accept(program, InvocationId("dbp"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.CaptureRequest]
    (deferred,) = opening.withheld
    assert isinstance(deferred, Deferred)
    assert isinstance(deferred.request, composite.PingRequest)
    assert deferred.behind == (Unread(premise="DoublyPlain.eligible", kind=composite.Eligible),)
    assert deferred.unread == deferred.behind
    exact = perform(
        program, intend(invocation, opening.dispatch), opening.dispatch[0].identity, CAPTURED % "50"
    )
    (ping,) = frontier(evaluate(program, exact)).dispatch
    assert isinstance(ping.request, composite.PingRequest)
    short = perform(
        program, intend(invocation, opening.dispatch), opening.dispatch[0].identity, CAPTURED % "20"
    )
    blocked = evaluate(program, short)
    assert isinstance(blocked, Blocked)
    assert all(isinstance(r, Malformed) for r in blocked.reasons)
    assert all(not isinstance(r, composite.PingRequest) for r in short.intents.values())


def test_an_unread_judgement_a_delivery_resolves_is_waited_for_not_blocked() -> None:
    """The eligibility's capture beside a voucher behind an opaque identity validator, which a
    delivery supplies and nothing is sent for. The capture waits for the voucher's construction,
    unresolved: nothing is blocked, because the voucher's arrival resolves it with no effect.
    Once it is constructed the capture is dispatched."""
    program = composite.VOUCHED
    invocation = accept(program, InvocationId("vch"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert opening.dispatch == ()
    assert [type(a) for a in opening.awaiting] == [Unsolicited]
    (deferred,) = opening.withheld
    assert isinstance(deferred, Deferred)
    assert isinstance(deferred.request, composite.CaptureRequest)
    assert deferred.behind == (Unread(premise="Vouched.vouched", kind=composite.CheckedVoucher),)
    assert deferred.unread == (
        Unread(premise="Vouched.vouched", kind=composite.CheckedVoucher),
        Unread(premise="Vouched.eligible", kind=composite.Eligible),
    )
    vouched = admit(program, invocation, delivered(composite.REVIEWERS, "v-1", VOUCHER))
    (capture,) = frontier(evaluate(program, vouched)).dispatch
    assert capture.identity == deferred.identity


@pytest.mark.parametrize(
    ("program", "judged", "behind"),
    [
        (
            composite.SECONDING,
            composite.Seconded,
            (
                Bounded(premise="SecondedRelease.seconded.approvals"),
                Unread(premise="SecondedRelease.seconded.approvals", kind=composite.Seconded),
            ),
        ),
        (
            composite.PREFACING,
            composite.Prefaced,
            (
                Bounded(premise="PrefacedRelease.prefaced.approvals"),
                Unread(premise="PrefacedRelease.prefaced", kind=composite.Prefaced),
            ),
        ),
    ],
)
def test_a_validator_padding_before_a_length_check_is_judged_by_pydantic_alone(
    program: Program,
    judged: type[composite.Seconded | composite.Prefaced],
    behind: tuple[object, ...],
) -> None:
    """Native Pydantic accepts one approval: a before-validator at the field, or a model
    validator running before field validation, pads it to two before the length is checked.
    The evaluator makes no judgement of its own on that field, since the bare constraint would
    refuse what Pydantic accepts; the shipment waits behind the field's judgements, the fact
    constructs natively once the approvals close, and the shipment is released. The
    constructed result holds what Pydantic returned, two approvals; the history holds the one
    record admitted; and the construction witness names that one occurrence."""
    assert not early(judged, "approvals")
    invocation = accept(program, InvocationId("sec"), composite.PRICED)
    opening = frontier(evaluate(program, invocation))
    assert opening.dispatch == ()
    (deferred,) = opening.withheld
    assert isinstance(deferred, Deferred)
    assert isinstance(deferred.request, composite.ShipOrder)
    assert deferred.behind == behind

    one = admit(program, invocation, delivered(composite.REVIEWERS, "a-1", ORDER_APPROVAL % "ren"))
    closed = admit(program, one, delivered(composite.REVIEWERS, "c-1", ORDER_CLOSED))
    (ship,) = frontier(evaluate(program, closed)).dispatch
    assert isinstance(ship.request, composite.ShipOrder)
    (approval,) = [e for e in closed.evidence if isinstance(e.value, composite.OrderApproval)]
    native = judged.model_validate({"approvals": (approval.value,)}, by_name=True)
    assert len(native.approvals) == 2

    done = perform(program, intend(closed, (ship,)), ship.identity, SHIPPED)
    result = evaluate(program, done)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, composite.SecondedRelease | composite.PrefacedRelease)
    (padded,) = [v for v in vars(result.goal).values() if isinstance(v, judged)]
    assert padded == native
    assert [e.value for e in done.evidence if isinstance(e.value, composite.OrderApproval)] == [
        approval.value
    ]
    assert isinstance(result.occurrence, Built)
    (witness,) = [w for _, w in result.occurrence.parts if isinstance(w, Built) and w.parts]
    assert dict(witness.parts)["approvals"] == Elements(of=(Site(evidence=approval.id),))


def test_the_bare_constraint_refuses_what_pydantic_accepts_so_it_is_not_judged_early() -> None:
    """The counterexample itself: the field's constraint stripped of its before-validator
    refuses a lone approval that native construction accepts. ``early`` is false for the field,
    so the evaluator never makes that stripped judgement."""
    approval = composite.OrderApproval(
        order_id=composite.OrderId("o-7"), reviewer=composite.Reviewer("ren")
    )
    assert checked(composite.Seconded, "approvals", (approval,)) is not None
    assert len(composite.Seconded(approvals=(approval,)).approvals) == 2
    assert not early(composite.Seconded, "approvals")
    assert not early(composite.Prefaced, "approvals")
    assert composite.Prefaced.model_validate({"approvals": (approval,)}, by_name=True)
    assert checked(composite.Prefaced, "approvals", (approval,)) is not None
    assert not early(composite.Covered, "payment")
    assert early(composite.Catalogued, "quotes")
    assert early(composite.Endorsed, "approvals")


@pytest.mark.parametrize("count", [1, 2, 3])
def test_an_early_constraint_judgement_is_pydantics_own_verdict(count: int) -> None:
    """Where the field carries native constraints alone, the verdict made before construction
    equals the verdict native construction gives the field, for lengths under, at and over the
    bound."""
    quote = composite.Quote(order_id=composite.OrderId("o-7"), amount=composite.Paid(Decimal(5)))
    quotes = tuple(
        composite.Quoted(line=composite.line("tea", "w1"), quote=quote) for _ in range(count)
    )
    verdict = checked(composite.Catalogued, "quotes", quotes)
    pinged = composite.Pinged(order_id=composite.OrderId("o-7"))
    try:
        composite.Catalogued.model_validate(
            {"order": composite.ONE_LINE.order, "quotes": quotes, "pinged": pinged}, by_name=True
        )
    except ValidationError as refusal:
        assert verdict == tuple(e["msg"] for e in refusal.errors())
    else:
        assert verdict is None


def test_a_judgement_only_the_goals_construction_can_make_is_reported_not_guessed() -> None:
    """The padded length check on the goal's own field: the quote is dispatched, since it feeds
    the judgement; the ping waits. Once the quote is there the judgement still cannot be made
    before the goal constructs, and the goal needs the ping, so nothing can advance: the
    evaluator names the judgements and the request rather than run the bare constraint or
    dispatch the ping. The same declarations with the judgement at a construction boundary of
    its own progress: the fact constructs natively, padded, and the ping is released."""
    program = composite.SECONDED_CATALOGUING
    invocation = accept(program, InvocationId("scat"), composite.ONE_LINE)
    opening = frontier(evaluate(program, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.QuoteRequest]
    (deferred,) = opening.withheld
    assert isinstance(deferred, Deferred)
    assert isinstance(deferred.request, composite.PingRequest)
    assert deferred.until == ("SecondedCatalogue.quotes",)
    quoted = perform(
        program, intend(invocation, opening.dispatch), opening.dispatch[0].identity, QUOTE
    )
    blocked = evaluate(program, quoted)
    assert isinstance(blocked, Blocked)
    assert operations(blocked) == ("PingRequest",)
    (reason,) = blocked.reasons
    assert isinstance(reason, Undetermined)
    assert reason.judgements == (
        Bounded(premise="SecondedCatalogue.quotes"),
        Unread(premise="SecondedCatalogue.quotes", kind=composite.SecondedCatalogue),
    )
    assert all(not isinstance(r, composite.PingRequest) for r in quoted.intents.values())

    boundary = composite.SECONDED_CATALOGUING_VIA_FACT
    invocation = accept(boundary, InvocationId("scat-b"), composite.ONE_LINE)
    opening = frontier(evaluate(boundary, invocation))
    assert [type(d.request) for d in opening.dispatch] == [composite.QuoteRequest]
    assert [type(w.request) for w in opening.withheld] == [composite.PingRequest]
    quoted = perform(
        boundary, intend(invocation, opening.dispatch), opening.dispatch[0].identity, QUOTE
    )
    (ping,) = frontier(evaluate(boundary, quoted)).dispatch
    assert isinstance(ping.request, composite.PingRequest)
    done = perform(boundary, intend(quoted, (ping,)), ping.identity, PINGED)
    result = evaluate(boundary, done)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, composite.SecondedCatalogueViaFact)
    assert len(result.goal.quoted.quotes) == 2
    assert len([e for e in done.evidence if isinstance(e.value, composite.Quote)]) == 1


def test_an_opaque_identity_wrapper_is_reported_unresolved_where_a_plain_one_is_established() -> (
    None
):
    """Beside the quotes' constraint, the ping behind a plain wrapper waits as an established
    dependency; behind an opaque identity validator it waits the same, and the frontier says
    the dependency is unresolved, naming the validator it cannot read."""
    plain = composite.CATALOGUING_VIA_DESK
    opening = frontier(evaluate(plain, accept(plain, InvocationId("cat"), composite.REVIEW)))
    (deferred,) = opening.withheld
    assert isinstance(deferred, Deferred)
    assert deferred.behind == (Bounded(premise="CataloguedViaDesk.quotes"),)
    assert deferred.unread == ()

    checked_ = composite.CATALOGUING_VIA_CHECKED_DESK
    opening = frontier(evaluate(checked_, accept(checked_, InvocationId("cat"), composite.REVIEW)))
    (deferred,) = opening.withheld
    assert isinstance(deferred, Deferred)
    assert deferred.behind == (Bounded(premise="CataloguedViaCheckedDesk.quotes"),)
    assert deferred.unread == (
        Unread(premise="CataloguedViaCheckedDesk.desk", kind=composite.CheckedPingDesk),
    )
