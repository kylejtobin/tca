"""A computed field is a consequence of its operands: construction computes it, its type admits
or refuses it, and nothing given for it is accepted, in Python or in JSON, nested or not."""

from decimal import Decimal
from typing import Literal

import pytest
from pydantic import ValidationError

from type_construction.world import (
    COMPUTED,
    REFUTED,
    Comparison,
    Computation,
    Derived,
    Measure,
    Relation,
    Scalar,
    Times,
)

from .computed import (
    Allowed,
    Exact,
    Large,
    Line,
    Lines,
    LineTotal,
    Order,
    Priced,
    Quantity,
    Rate,
    Reduced,
    Small,
    Threshold,
    UnitPrice,
)

TOTAL = LineTotal(left=UnitPrice(Decimal("2.50")), right=Quantity(3))
"""A line's total, computed: 7.50."""


def refusals(refusal: ValidationError) -> list[tuple[str, tuple[int | str, ...], object]]:
    """Each error's type, location and input."""
    return [(e["type"], e["loc"], e["input"]) for e in refusal.errors()]


def test_an_omitted_root_is_computed_from_the_validated_operands() -> None:
    assert TOTAL.root == Decimal("7.50")
    assert Reduced(left=TOTAL, right=Rate()).root == Decimal("6.750")
    assert Lines(of=(TOTAL, TOTAL)).root == Decimal("15.00")
    assert Lines(of=()).root == Decimal(0)
    assert Small(value=TOTAL, bound=Threshold()).ordering == -1
    assert Allowed(value=Quantity(3), lower=Quantity(1), upper=Quantity(3)).above == 0


@pytest.mark.parametrize(
    "given",
    [Decimal("7.50"), Decimal(99), 7.5, "7.50", None, Quantity(7)],
    ids=["equal", "wrong", "float", "text", "none", "scalar"],
)
def test_a_root_given_in_python_is_refused_whatever_it_is(given: object) -> None:
    with pytest.raises(ValidationError) as refusal:
        LineTotal.model_validate(
            {"left": UnitPrice(Decimal("2.50")), "right": Quantity(3), "root": given}
        )
    assert refusals(refusal.value) == [("computed", ("root",), given)]
    assert (
        refusal.value.errors()[0]["msg"] == "root is computed from left and right and never given"
    )


@pytest.mark.parametrize("given", [-1, 0, 1], ids=["admitted", "equal", "refused"])
def test_an_ordering_given_in_python_is_refused_admitted_or_not(given: int) -> None:
    with pytest.raises(ValidationError) as refusal:
        Small.model_validate({"value": TOTAL, "bound": Threshold(), "ordering": given})
    assert refusals(refusal.value) == [("computed", ("ordering",), given)]


def test_json_omits_the_root_and_it_is_computed_or_gives_it_and_is_refused() -> None:
    assert LineTotal.model_validate_json('{"left": "2.50", "right": 3}').root == Decimal("7.50")
    with pytest.raises(ValidationError) as refusal:
        LineTotal.model_validate_json('{"left": "2.50", "right": 3, "root": "7.50"}')
    assert refusals(refusal.value) == [("computed", ("root",), "7.50")]
    with pytest.raises(ValidationError) as refusal:
        Small.model_validate_json(
            '{"value": {"left": "2.50", "right": 3}, "bound": "100", "ordering": -1}'
        )
    assert refusals(refusal.value) == [("computed", ("ordering",), -1)]


def test_the_computed_result_is_admitted_or_refused_by_the_fields_type() -> None:
    assert (
        Large(
            value=LineTotal(left=UnitPrice(Decimal(50)), right=Quantity(3)), bound=Threshold()
        ).ordering
        == 1
    )
    with pytest.raises(ValidationError) as refusal:
        Large(value=TOTAL, bound=Threshold())
    assert refusals(refusal.value) == [(REFUTED, ("ordering",), COMPUTED)]
    assert refusal.value.errors()[0]["msg"] == "value < bound"
    assert refusal.value.errors()[0].get("ctx") == {
        "left": "value",
        "right": "bound",
        "left_class": "LineTotal",
        "right_class": "Threshold",
        "sign": "<",
        "ordering": -1,
    }
    with pytest.raises(ValidationError) as refusal:
        Exact(value=TOTAL, bound=Threshold())
    assert refusals(refusal.value) == [(REFUTED, ("ordering",), COMPUTED)]
    with pytest.raises(ValidationError) as refusal:
        Allowed(value=Quantity(11), lower=Quantity(1), upper=Quantity(10))
    assert refusals(refusal.value) == [(REFUTED, ("above",), COMPUTED)]
    assert refusal.value.errors()[0]["msg"] == "value > upper"
    with pytest.raises(ValidationError) as refusal:
        Allowed.model_validate_json('{"value": 1, "lower": 2, "upper": 10}')
    assert refusals(refusal.value) == [(REFUTED, ("below",), COMPUTED)]
    assert refusal.value.errors()[0]["msg"] == "lower > value"


def test_a_nested_root_cannot_be_given_at_any_depth_or_in_any_element() -> None:
    with pytest.raises(ValidationError) as refusal:
        Priced.model_validate_json(
            '{"total": {"left": "2.50", "right": 3, "root": "7.50"},'
            ' "small": {"value": {"left": "2.50", "right": 3}, "bound": "100"}}'
        )
    assert refusals(refusal.value) == [("computed", ("total", "root"), "7.50")]
    with pytest.raises(ValidationError) as refusal:
        Lines.model_validate(
            {
                "of": (
                    {"left": Decimal("2.50"), "right": 3},
                    {"left": Decimal(1), "right": 1, "root": Decimal(1)},
                )
            }
        )
    assert refusals(refusal.value) == [
        ("computed", ("of", 1, "root"), Decimal(1)),
        ("uncomputed", ("root",), COMPUTED),
    ]
    with pytest.raises(ValidationError) as refusal:
        Priced.model_validate(
            {"total": TOTAL, "small": {"value": TOTAL, "bound": Threshold(), "ordering": -1}}
        )
    assert refusals(refusal.value) == [("computed", ("small", "ordering"), -1)]


def test_a_root_whose_operand_did_not_construct_is_uncomputed_beside_the_operands_error() -> None:
    with pytest.raises(ValidationError) as refusal:
        LineTotal.model_validate_json('{"left": "0", "right": 3}')
    assert [(e["type"], e["loc"]) for e in refusal.value.errors()] == [
        ("greater_than", ("left",)),
        ("uncomputed", ("root",)),
    ]
    assert refusal.value.errors()[1]["msg"] == "root is computed from left, which did not construct"


def test_a_computed_field_is_not_required_and_is_excluded_from_the_dump() -> None:
    assert [name for name, f in LineTotal.model_fields.items() if f.is_required()] == [
        "left",
        "right",
    ]
    assert LineTotal.model_fields["root"].default is COMPUTED
    assert TOTAL.model_dump() == {"left": Decimal("2.50"), "right": 3}
    assert TOTAL.model_dump_json() == '{"left":"2.50","right":3}'
    assert Small(value=TOTAL, bound=Threshold()).model_dump() == {
        "value": {"left": Decimal("2.50"), "right": 3},
        "bound": Decimal(100),
    }


def test_the_sentinel_itself_given_is_nothing_given() -> None:
    assert LineTotal(
        left=UnitPrice(Decimal("2.50")), right=Quantity(3), root=COMPUTED
    ).root == Decimal("7.50")


def test_a_validated_instance_is_frozen_and_only_a_copy_with_an_update_leaves_the_boundary() -> (
    None
):
    with pytest.raises(ValidationError) as refusal:
        TOTAL.root = Decimal(1)
    assert refusals(refusal.value) == [("frozen_instance", ("root",), Decimal(1))]
    assert TOTAL.root == Decimal("7.50")
    assert LineTotal.model_validate(TOTAL.model_dump()).root == TOTAL.root
    copied = TOTAL.model_copy(update={"root": Decimal(1)})
    assert copied.root == Decimal(1)
    assert LineTotal.model_validate(copied.model_dump()).root == Decimal("7.50")


def test_a_computed_field_declares_its_computation_once_in_its_annotation() -> None:
    (derived,) = [m for m in LineTotal.model_fields["root"].metadata if isinstance(m, Computation)]
    assert isinstance(derived, Derived)
    assert derived.operands == ("left", "right")
    (summed,) = [m for m in Lines.model_fields["root"].metadata if isinstance(m, Computation)]
    assert isinstance(summed, Derived)
    assert summed.operands == ("of",)
    (compared,) = [m for m in Small.model_fields["ordering"].metadata if isinstance(m, Computation)]
    assert isinstance(compared, Comparison)
    assert compared == Comparison(("value", "bound"))
    assert (compared.left, compared.right) == ("value", "bound")
    assert Small.model_fields["ordering"].annotation == Literal[-1, 0]
    below, above = (
        next(m for m in Allowed.model_fields[name].metadata if isinstance(m, Computation))
        for name in ("below", "above")
    )
    assert (below, above) == (Comparison(("lower", "value")), Comparison(("value", "upper")))
    assert not any(
        isinstance(m, Computation)
        for cls in (Measure, Relation, Scalar, Line)
        for f in cls.model_fields.values()
        for m in f.metadata
    )
    assert Times.model_fields["root"].default is COMPUTED


def test_a_computed_value_is_not_a_request_input() -> None:
    assert Order.model_validate_json('{"lines": [{"price": "2.50", "quantity": 3}]}').lines[
        0
    ] == Line(price=UnitPrice(Decimal("2.50")), quantity=Quantity(3))
    with pytest.raises(ValidationError) as refusal:
        Order.model_validate_json('{"lines": [{"price": "2.50", "quantity": 3, "root": "7.50"}]}')
    assert refusals(refusal.value) == [("extra_forbidden", ("lines", 0, "root"), "7.50")]
