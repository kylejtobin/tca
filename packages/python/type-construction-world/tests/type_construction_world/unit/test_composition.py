"""ADR D-004, D-005, D-008 and D-030; architecture §§5, 8: computations, comparisons and
selections compose into one nested record whose construction is bounded and reproducible, and
whose failures keep their categories apart: a refused condition at its own location, malformed
input as itself, a union resolved by the alternative that constructs, and a programmer fault
escaping as the exception it is."""

from decimal import Decimal
from typing import Any, Self

import pytest
from pydantic import Field, TypeAdapter, ValidationError, model_validator

from type_construction.world import (
    REFUTED,
    AtLeast,
    AtMost,
    Beyond,
    Only,
    Record,
    Scalar,
    Sum,
    Times,
    Value,
)


class Price(Scalar[Decimal]):
    root: Decimal = Field(gt=0)


class Quantity(Scalar[int]):
    root: int = Field(gt=0)


class Budget(Scalar[Decimal]):
    root: Decimal = Decimal(100)


class Line(Times[Price, Quantity]):
    """What one line costs."""


class Lines(Sum[Line]):
    """What the lines cost together."""


class WithinBudget(AtMost[Lines, Budget]):
    """The lines cost at most the budget."""


class OverBudget(Beyond[Lines, Budget]):
    """The lines cost more than the budget."""


class Chosen(Only[Line]):
    """Exactly one line was chosen."""


class Floor(Scalar[Decimal]):
    root: Decimal = Decimal(1)


class Worthwhile(AtLeast[Line, Floor]):
    """The chosen line is worth at least the floor."""


class Order(Record):
    """Lines, their total judged against the budget either way, one chosen line, and the rule
    that the chosen line is worthwhile."""

    lines: Lines
    budget: WithinBudget | OverBudget
    chosen: Chosen
    worthwhile: Worthwhile


class Audited(Value):
    """An order with a rule whose implementation is broken."""

    order: Order

    @model_validator(mode="after")
    def audited(self) -> Self:
        msg = "the audit service is down"
        raise RuntimeError(msg)


def line(price: str, quantity: int = 1) -> Line:
    return Line(left=Price(Decimal(price)), right=Quantity(quantity))


def order(prices: tuple[str, ...], chosen: str = "2.50") -> dict[str, Any]:
    lines = Lines(of=tuple(line(p) for p in prices))
    return {
        "lines": lines,
        "budget": {"value": lines, "bound": Budget()},
        "chosen": {"of": (line(chosen),)},
        "worthwhile": {"value": line(chosen), "bound": Floor()},
    }


def error_types(failure: ValidationError) -> set[tuple[str, tuple[int | str, ...]]]:
    return {(e["type"], e["loc"]) for e in failure.errors()}


def test_a_nested_record_constructs_once_and_reproducibly_from_the_same_operands() -> None:
    given = order(("2.50", "4.00"))

    first = Order.model_validate(given)
    second = Order.model_validate(given)
    revalidated = TypeAdapter(Order).validate_python(first)

    assert first == second == revalidated
    assert hash(first) == hash(second)
    assert first.lines.root == Decimal("6.50")
    assert isinstance(first.budget, WithinBudget)
    assert first.chosen.chosen == line("2.50")
    assert first.worthwhile.value.root == Decimal("2.50")


def test_the_union_is_resolved_by_the_alternative_that_holds_after_the_other_refuses() -> None:
    given = order(("60", "50"))

    with pytest.raises(ValidationError) as first_candidate:
        WithinBudget.model_validate(given["budget"])
    constructed = Order.model_validate(given)

    assert error_types(first_candidate.value) == {(REFUTED, ())}
    assert isinstance(constructed.budget, OverBudget)
    assert constructed.budget.value.root == Decimal(110)


def test_a_refused_selection_is_reported_at_its_own_location_and_nothing_else_is_blamed() -> None:
    given = order(("2.50",))
    given["chosen"] = {"of": (line("2.50"), line("3.00"))}

    with pytest.raises(ValidationError) as failure:
        Order.model_validate(given)

    assert error_types(failure.value) == {(REFUTED, ("chosen",))}


def test_two_refusals_in_one_record_are_both_reported_and_both_refusals() -> None:
    given = order(("2.50",), chosen="0.50")
    given["chosen"] = {"of": ()}

    with pytest.raises(ValidationError) as failure:
        Order.model_validate(given)

    assert error_types(failure.value) == {(REFUTED, ("chosen",)), (REFUTED, ("worthwhile",))}


def test_malformed_input_beside_a_refusal_keeps_its_own_type_and_location() -> None:
    given = order(("2.50",))
    given["chosen"] = {"of": ()}
    given["worthwhile"] = {"value": {"left": Decimal(0), "right": 1}, "bound": Floor()}

    with pytest.raises(ValidationError) as failure:
        Order.model_validate(given)

    assert error_types(failure.value) == {
        (REFUTED, ("chosen",)),
        ("greater_than", ("worthwhile", "value", "left")),
    }


def test_a_programmer_fault_inside_a_nested_rule_escapes_as_itself() -> None:
    given = {"order": order(("2.50",))}

    with pytest.raises(RuntimeError, match="audit service"):
        Audited.model_validate(given)


def test_the_same_record_constructs_from_json_as_from_python() -> None:
    from_python = Order.model_validate(order(("2.50", "4.00")))
    from_json = Order.model_validate_json(
        '{"lines": {"of": [{"left": "2.50", "right": 1}, {"left": "4.00", "right": 1}]},'
        ' "budget": {"value": {"of": [{"left": "2.50", "right": 1}, {"left": "4.00", "right": 1}]},'
        ' "bound": "100"},'
        ' "chosen": {"of": [{"left": "2.50", "right": 1}]},'
        ' "worthwhile": {"value": {"left": "2.50", "right": 1}, "bound": "1"}}'
    )

    assert from_json == from_python
