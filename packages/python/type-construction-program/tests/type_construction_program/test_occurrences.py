"""A class is not an occurrence (foundations §4.1, §10.2; acceptance B1, B2, B3).

The declarations are ``lines`` and ``review``. The hypothesis under test is the simplest
identity for an occurrence: the class, or the evidence it was found in. Two lines of one order
break both: they are one class, they are in one piece of evidence, they may be equal in every
field, and the business intends two shipments. The identity that repairs it is the site: the
evidence and the path to the value, element index included. A constructed value's occurrence is
the occurrences of its premises, so a request built from a different line is a different
operation, and two facts built from the same line share one occurrence.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from type_construction.program import (
    Ambiguous,
    Built,
    Completed,
    Elements,
    InvocationId,
    Occurrence,
    Program,
    Refusal,
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
from type_construction.world import Fact, Value

from . import lines, review
from .drive import delivered, frontier

SHIPPED = '{"order_id": "o-9", "tracking": "1Z-%s"}'
CLOSE_REVIEW = '{"case_id": "case-3"}'


def approval(reviewer: str) -> str:
    return f'{{"case_id": "case-3", "reviewer": "{reviewer}"}}'


def cleared(sku: str) -> str:
    return f'{{"order_id": "o-9", "sku": "{sku}", "reviewer": "ren"}}'


def sites(occurrence: Occurrence) -> set[tuple[int, tuple[str | int, ...]]]:
    """Every site an occurrence is built from."""
    match occurrence:
        case Site(evidence=evidence, path=path):
            return {(evidence, path)}
        case Built(parts=parts):
            return {s for _, part in parts for s in sites(part)}
        case Elements(of=of):
            return {s for part in of for s in sites(part)}


def test_two_equal_lines_are_two_occurrences_and_two_intended_operations() -> None:
    program = lines.SHIPPING
    invocation = accept(program, InvocationId("inv"), lines.TWO_EQUAL)
    result = frontier(evaluate(program, invocation))
    first, second = result.dispatch
    assert first.request == second.request
    assert first.request.model_dump_json() == second.request.model_dump_json()
    assert first.identity != second.identity
    assert sites(first.identity.occurrence) == {(0, ("order", "id")), (0, ("order", "lines", 0))}
    assert sites(second.identity.occurrence) == {(0, ("order", "id")), (0, ("order", "lines", 1))}
    evidence_only = {
        (d.identity.operation, frozenset(e for e, _ in sites(d.identity.occurrence)))
        for d in result.dispatch
    }
    assert len(evidence_only) == 1
    assert len({d.identity for d in result.dispatch}) == 2


def test_each_result_binds_to_the_line_that_requested_it() -> None:
    program = lines.SHIPPING
    invocation = accept(program, InvocationId("inv"), lines.TWO_DISTINCT)
    proposed = frontier(evaluate(program, invocation))
    invocation = intend(invocation, proposed.dispatch)
    (for_b,) = [d for d in proposed.dispatch if d.request.model_dump()["line"]["sku"] == "B"]
    (for_a,) = [d for d in proposed.dispatch if d.request.model_dump()["line"]["sku"] == "A"]

    invocation = perform(program, invocation, for_b.identity, SHIPPED % "B")
    remaining = frontier(evaluate(program, invocation))
    assert [d.identity for d in remaining.dispatch] == [for_a.identity]
    assert remaining.dispatch[0].attempt == 1

    invocation = admit(
        program,
        invocation,
        delivered(lines.CARRIER, "wh-a", SHIPPED % "A", answers=for_a.identity),
    )
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, lines.AllShipped)
    by_sku = {done.line.sku.root: done.shipment.tracking.root for done in result.goal.lines}
    assert by_sku == {"A": "1Z-A", "B": "1Z-B"}


def test_a_result_for_a_per_line_receive_must_name_the_line_it_answers() -> None:
    program = lines.SHIPPING
    invocation = accept(program, InvocationId("inv"), lines.TWO_DISTINCT)
    invocation = intend(invocation, frontier(evaluate(program, invocation)).dispatch)
    with pytest.raises(Refusal) as refusal:
        admit(program, invocation, delivered(lines.CARRIER, "wh-?", SHIPPED % "X"))
    assert refusal.value.reason == Uncorrelated(received=lines.LineShipped, correlation=None)


def test_pure_construction_per_line_shares_each_lines_occurrence() -> None:
    program = lines.INVOICING
    invocation = accept(program, InvocationId("inv"), lines.TWO_DISTINCT)
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    goal = result.goal
    assert isinstance(goal, lines.Invoice)
    assert [p.total.root for p in goal.priced] == [Decimal("20.00"), Decimal("4.50")]
    assert goal.total.root == Decimal("24.50")
    assert all(p.total is t for p, t in zip(goal.priced, goal.total.of, strict=True))
    assert isinstance(result.occurrence, Built)
    parts = dict(result.occurrence.parts)
    assert isinstance(parts["priced"], Elements)
    assert [sites(p) for p in parts["priced"].of] == [
        {(0, (*at, *rest)) for rest in ((), ("price",), ("quantity",))}
        for at in (("order", "lines", 0), ("order", "lines", 1))
    ]


def test_two_equal_lines_are_priced_twice() -> None:
    program = lines.INVOICING
    invocation = accept(program, InvocationId("inv"), lines.TWO_EQUAL)
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, lines.Invoice)
    assert len(result.goal.priced) == 2
    assert result.goal.priced[0] == result.goal.priced[1]
    assert result.goal.priced[0] is not result.goal.priced[1]
    assert result.goal.total.root == Decimal("20.00")


def test_an_unsolicited_receive_correlates_to_one_element() -> None:
    program = lines.CLEARANCE
    invocation = accept(program, InvocationId("inv"), lines.TWO_DISTINCT)
    waiting = frontier(evaluate(program, invocation))
    assert waiting.dispatch == ()
    assert {a.element for a in waiting.awaiting if isinstance(a, Unsolicited)} == {
        Site(evidence=0, path=("order", "lines", 0)),
        Site(evidence=0, path=("order", "lines", 1)),
    }
    invocation = admit(program, invocation, delivered(lines.APPROVALS, "ap-b", cleared("B")))
    assert invocation.evidence[0].element == Site(evidence=0, path=("order", "lines", 1))
    still = frontier(evaluate(program, invocation))
    assert [a.element for a in still.awaiting if isinstance(a, Unsolicited)] == [
        Site(evidence=0, path=("order", "lines", 0))
    ]
    invocation = admit(program, invocation, delivered(lines.APPROVALS, "ap-a", cleared("A")))
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, lines.AllCleared)
    assert [c.approval.sku.root for c in result.goal.lines] == ["A", "B"]
    assert [c.line.sku.root for c in result.goal.lines] == ["A", "B"]


def test_equal_elements_make_an_element_correlation_ambiguous_not_guessed() -> None:
    program = lines.CLEARANCE
    invocation = accept(program, InvocationId("inv"), lines.TWO_EQUAL)
    with pytest.raises(Refusal) as refusal:
        admit(program, invocation, delivered(lines.APPROVALS, "ap-a", cleared("A")))
    reason = refusal.value.reason
    assert isinstance(reason, Ambiguous)
    assert reason.elements == (
        Site(evidence=0, path=("order", "lines", 0, "sku")),
        Site(evidence=0, path=("order", "lines", 1, "sku")),
    )


def test_work_per_element_of_a_source_proceeds_before_closure() -> None:
    program = review.GRATITUDE
    invocation = accept(program, InvocationId("rev"), review.CASE)
    opening = frontier(evaluate(program, invocation))
    assert opening.dispatch == ()

    invocation = admit(program, invocation, delivered(review.REVIEWERS, "a-1", approval("ren")))
    one = frontier(evaluate(program, invocation))
    (thank_ren,) = one.dispatch
    assert isinstance(thank_ren.request, review.ThankRequest)
    assert thank_ren.request.approval.reviewer == review.Reviewer("ren")
    assert sites(thank_ren.identity.occurrence) == {(invocation.evidence[0].id, ())}
    assert any(isinstance(a, Unclosed) and a.held == 1 for a in one.awaiting)
    invocation = intend(invocation, one.dispatch)
    invocation = perform(program, invocation, thank_ren.identity, approval("ren"))
    assert frontier(evaluate(program, invocation)).dispatch == ()

    invocation = admit(program, invocation, delivered(review.REVIEWERS, "a-2", approval("kai")))
    two = frontier(evaluate(program, invocation))
    (thank_kai,) = two.dispatch
    assert thank_kai.identity != thank_ren.identity
    invocation = intend(invocation, two.dispatch)
    invocation = perform(program, invocation, thank_kai.identity, approval("kai"))
    assert frontier(evaluate(program, invocation)).dispatch == ()

    invocation = admit(program, invocation, delivered(review.REVIEWERS, "c-1", CLOSE_REVIEW))
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, review.Acknowledged)
    assert [t.sent.reviewer.root for t in result.goal.thanks] == ["ren", "kai"]


def test_a_goal_that_varies_per_element_is_refused() -> None:
    with pytest.raises(ValidationError) as refusal:
        Program(goal=lines.LineDone, accepts=lines.ProcessOrder, interactions=(lines.LINE_SHIP,))
    message = str(refusal.value)
    assert "LineDone varies per element of ProcessOrder.order.lines.*" in message


def test_a_tuple_of_a_class_that_varies_over_nothing_is_refused() -> None:
    with pytest.raises(ValidationError) as refusal:
        Program(goal=review.Acknowledged, accepts=review.ReviewCase, interactions=(review.THANKS,))
    assert "no interaction declares a source" in str(refusal.value)

    class Orders(Fact):
        orders: tuple[lines.LinedOrder, ...]

    with pytest.raises(ValidationError) as refusal:
        Program(goal=Orders, accepts=lines.ProcessOrder)
    assert "there is one, not many" in str(refusal.value)


class Left(Value):
    sku: lines.Sku


class Right(Value):
    sku: lines.Sku


class Pairing(Value):
    lefts: tuple[Left, ...]
    rights: tuple[Right, ...]


class Cross(Fact):
    left: Left
    right: Right


class Crosses(Fact):
    all: tuple[Cross, ...]


def test_a_tuple_of_a_class_that_varies_over_two_collections_is_refused() -> None:
    """Zip or product is a business rule; the declaration does not state one, so neither is
    guessed."""
    with pytest.raises(ValidationError) as refusal:
        Program(goal=Crosses, accepts=Pairing)
    message = str(refusal.value)
    assert "each Cross varies over both Pairing.lefts.* and Pairing.rights.*" in message
