"""A condition is established through its whole declaration before anything it governs is
dispatched (foundations §7.2, §7.3, §8.2; acceptance A3, A5, C4; decisions 0003 laws 1, 3 and 6,
0005, 0007).

The declarations are ``composite``. One condition over an order's lines is declared as a class of
its own and as metadata on the conditional's argument: a length constraint, an after-validator on
the tuple, an after-validator on the class that holds it, a normalization before the constraint.
Each refuses what native construction of the conditional refuses, with the same errors, before
anything is dispatched; each releases what native construction accepts beside a ping it does not
govern, under the candidate's occurrence; and the value each constructs equals Pydantic's own over
the same premises. The named class and the metadata are one condition and refuse with one message.
A conditional that checks its condition with a validator of its own class is refused at
declaration, since that check would run after the shipment.
"""

from typing import cast

import pytest
from pydantic import BaseModel, ValidationError

from type_construction.program import (
    Blocked,
    Built,
    Completed,
    Demand,
    Elements,
    Frontier,
    InvocationId,
    Malformed,
    Occurrence,
    Program,
    Site,
    When,
    accept,
    evaluate,
    intend,
    perform,
)
from type_construction.program.declaration import boundary
from type_construction.world import Refusals

from . import composite
from .drive import frontier

SHIPPED = '{"order_id": "o-7", "tracking": "1Z"}'
PINGED = '{"order_id": "o-7"}'
RECORD = composite.OrderShipped(
    order_id=composite.OrderId("o-7"), tracking=composite.Tracking("1Z")
)


def names(result: Frontier) -> list[str]:
    return sorted(type(d.request).__name__ for d in result.dispatch)


def conditional(goal: str) -> type[BaseModel]:
    """The conditional class the goal declares its shipment with."""
    declared = composite.LINED_SHIPPING[goal].goal.model_fields["shipment"].annotation
    assert isinstance(declared, type)
    kind = cast("type[BaseModel]", declared)
    assert issubclass(declared, When)
    return kind


def candidate(goal: str, given: composite.ReviewLines) -> object:
    """What the condition is established from, as the business holds it: the lines, the order,
    or the class of lines, constructed natively."""
    if goal == "ShippedWhenLined":
        return composite.Lines.model_validate(
            {"lines": given.order.lines}, context=Refusals(), by_name=True
        )
    if goal == "ShippedWhenOrderConsolidated":
        return given.order
    return given.order.lines


def lines(given: composite.ReviewLines) -> Elements:
    return Elements(
        of=tuple(
            Site(evidence=0, path=("order", "lines", i)) for i in range(len(given.order.lines))
        )
    )


def occurrence(goal: str, given: composite.ReviewLines) -> Occurrence:
    """The occurrence the condition is established at: where its candidate came from."""
    if goal == "ShippedWhenLined":
        return Built(
            kind="type_construction_program.composite.Lines", parts=(("lines", lines(given)),)
        )
    if goal == "ShippedWhenOrderConsolidated":
        return Site(evidence=0, path=("order",))
    return lines(given)


REFUSING = [
    ("ShippedWhenLined", composite.ONE_LINE),
    ("ShippedWhenTwoLines", composite.ONE_LINE),
    ("ShippedWhenConsolidated", composite.REVIEW),
    ("ShippedWhenOrderConsolidated", composite.REVIEW),
]
"""Each declaration with an order its condition refuses."""

ACCEPTING = [
    ("ShippedWhenLined", composite.REVIEW),
    ("ShippedWhenTwoLines", composite.REVIEW),
    ("ShippedWhenConsolidated", composite.TWO_LINES),
    ("ShippedWhenOrderConsolidated", composite.TWO_LINES),
    ("ShippedWhenSecondedLines", composite.ONE_LINE),
    ("ShippedWhenSecondedLines", composite.REVIEW),
]
"""Each declaration with an order its condition accepts, the normalizing one with a lone line it
doubles and with three it leaves."""


@pytest.mark.parametrize(("goal", "given"), REFUSING)
def test_what_the_condition_declaration_refuses_is_refused_before_anything_is_dispatched(
    goal: str, given: composite.ReviewLines
) -> None:
    """One line under a length constraint, lines from two warehouses under an after-validator on
    the tuple or on the order: native construction of the conditional refuses the condition, and
    the evaluator refuses it at the condition's premise with the same errors, before the shipment
    or anything else is dispatched. Nothing is ever intended."""
    program = composite.LINED_SHIPPING[goal]
    invocation = accept(program, InvocationId("rfs"), given)
    blocked = evaluate(program, invocation)
    assert isinstance(blocked, Blocked)
    (reason,) = blocked.reasons
    assert isinstance(reason, Malformed)
    assert reason.premise == f"{goal}.shipment.condition"
    assert invocation.intents == {}

    if goal == "ShippedWhenLined":
        assert reason.kind is composite.Lines
        with pytest.raises(ValidationError) as refusal:
            candidate(goal, given)
        assert reason.errors == tuple(e["msg"] for e in refusal.value.errors())
        return
    declared = conditional(goal)
    assert reason.kind is declared
    with pytest.raises(ValidationError) as refusal:
        declared.model_validate(
            {"condition": candidate(goal, given), "result": RECORD},
            context=Refusals(),
            by_name=True,
        )
    assert [e["loc"][0] for e in refusal.value.errors()] == ["condition"]
    assert reason.errors == tuple(e["msg"] for e in refusal.value.errors())


def test_the_named_class_and_the_metadata_are_one_condition_and_refuse_alike() -> None:
    """The length constraint inside a class of its own and on the conditional's argument: one
    line is refused at the condition's premise in both, with the one message Pydantic gives
    for it, and in neither is anything dispatched."""
    refusals: list[Malformed] = []
    for goal in ("ShippedWhenLined", "ShippedWhenTwoLines"):
        program = composite.LINED_SHIPPING[goal]
        invocation = accept(program, InvocationId("one"), composite.ONE_LINE)
        blocked = evaluate(program, invocation)
        assert isinstance(blocked, Blocked)
        (reason,) = blocked.reasons
        assert isinstance(reason, Malformed)
        assert reason.premise == f"{goal}.shipment.condition"
        assert invocation.intents == {}
        refusals.append(reason)
    named, metadata = refusals
    assert named.errors == metadata.errors
    assert named.kind is composite.Lines
    assert metadata.kind is conditional("ShippedWhenTwoLines")


@pytest.mark.parametrize(("goal", "given"), ACCEPTING)
def test_what_the_condition_declaration_accepts_releases_the_shipment_beside_the_ping(
    goal: str, given: composite.ReviewLines
) -> None:
    """An order the condition accepts, as declared: the condition is established from the input
    at once, so the shipment is dispatched beside the ping, which the condition never governed,
    with an activation at the candidate's occurrence and none on the ping. Both answered, the goal
    holds the conditional equal to native construction over the same premises: where the
    declaration doubles a lone line before counting, the goal holds two lines from one."""
    program = composite.LINED_SHIPPING[goal]
    invocation = accept(program, InvocationId("rls"), given)
    opening = frontier(evaluate(program, invocation))
    assert names(opening) == ["PingRequest", "ShipOrder"]
    assert opening.withheld == ()
    (ship,) = [d for d in opening.dispatch if isinstance(d.request, composite.ShipOrder)]
    (ping,) = [d for d in opening.dispatch if isinstance(d.request, composite.PingRequest)]
    (demand,) = opening.why(ship.identity).demands
    assert demand.consumer == f"{goal}.shipment.result"
    (activation,) = demand.activations
    assert activation.conditional == f"{goal}.shipment"
    assert activation.condition == f"{goal}.shipment.condition"
    assert activation.occurrence == occurrence(goal, given)
    assert opening.why(ping.identity).demands == (Demand(consumer=f"{goal}.pinged"),)

    done = perform(program, intend(invocation, opening.dispatch), ship.identity, SHIPPED)
    done = perform(program, done, ping.identity, PINGED)
    result = evaluate(program, done)
    assert isinstance(result, Completed)
    shipment = getattr(result.goal, "shipment")  # noqa: B009  the goal's class varies
    (shipped,) = [e for e in done.evidence if isinstance(e.value, composite.OrderShipped)]
    declared = conditional(goal)
    native = declared.model_validate(
        {"condition": candidate(goal, given), "result": shipped.value},
        context=Refusals(),
        by_name=True,
    )
    assert type(shipment) is declared
    assert shipment == native
    if goal == "ShippedWhenSecondedLines":
        condition = getattr(shipment, "condition")  # noqa: B009
        assert isinstance(condition, tuple)
        assert len(cast("tuple[object, ...]", condition)) == max(2, len(given.order.lines))


def test_the_condition_is_judged_under_the_conditionals_own_configuration() -> None:
    """The boundary a condition is established through is the conditional's declaration of its
    field, under the conditional's configuration: strict, so a list of lines is not a tuple of
    lines there, exactly as the conditional itself refuses it, while the tuple it accepts is
    accepted and returned as it would hold it."""
    declared = conditional("ShippedWhenTwoLines")
    given = composite.REVIEW.order.lines
    judged = boundary(declared, "condition")
    assert judged.validate_python(given, context=Refusals()) == given
    with pytest.raises(ValidationError) as at_boundary:
        judged.validate_python(list(given), context=Refusals())
    with pytest.raises(ValidationError) as natively:
        declared.model_validate(
            {"condition": list(given), "result": RECORD}, context=Refusals(), by_name=True
        )
    assert [e["type"] for e in at_boundary.value.errors()] == ["tuple_type"]
    assert [e["type"] for e in natively.value.errors()] == ["tuple_type"]


def test_a_conditional_that_validates_its_condition_with_a_decorator_is_refused() -> None:
    """A validator declared on the conditional's class for its condition runs when the class
    constructs, after the shipment it was meant to govern. The program refuses the declaration,
    naming the class and the validator and where the check belongs; the same check as metadata
    on the condition is accepted and governs the shipment."""
    with pytest.raises(ValidationError) as refusal:
        Program(
            goal=composite.ShippedWhenValidated,
            accepts=composite.ReviewLines,
            interactions=(composite.SHIP_ORDER, composite.PING),
        )
    message = str(refusal.value)
    assert "ShippedWhenValidated.shipment: ConsolidatedShipment validates its condition" in message
    assert "_consolidated" in message
    assert "condition's class or as Annotated metadata" in message
    assert composite.LINED_SHIPPING["ShippedWhenOrderConsolidated"].graph.gated
