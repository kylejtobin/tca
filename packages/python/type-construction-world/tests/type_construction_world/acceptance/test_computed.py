"""Product §4; architecture §5 world: native business computations and relations.

Public example spelling remains provisional. Expected arithmetic and refusal semantics
come from the architecture, not the removed computation implementation.
"""

from decimal import Decimal

import pytest
from pydantic import TypeAdapter, ValidationError

from .computed import Lines, LineTotal, Quantity, Rate, Reduced, Small, Threshold, UnitPrice


def test_computation_composes_and_revalidates_natively() -> None:
    first = LineTotal(left=UnitPrice(Decimal("2.50")), right=Quantity(3))
    second = LineTotal(left=UnitPrice(Decimal("4.00")), right=Quantity(2))

    total = Lines(of=(first, second))
    reduced = Reduced(left=first, right=Rate(Decimal("0.9")))

    assert first.root == Decimal("7.50")
    assert total.root == Decimal("15.50")
    assert reduced.root == Decimal("6.750")
    assert TypeAdapter(LineTotal).validate_python(first) == first
    assert TypeAdapter(Lines).validate_python(total) == total


@pytest.mark.parametrize(
    "given", [Decimal("7.50"), Decimal("999")], ids=["correct-supplied-result", "forged-result"]
)
def test_callers_cannot_supply_a_computed_result(given: Decimal) -> None:
    with pytest.raises(ValidationError):
        LineTotal.model_validate({"left": Decimal("2.50"), "right": 3, "root": given})


@pytest.mark.parametrize("nested", [False, True], ids=["direct-boundary", "enclosing-boundary"])
def test_forged_instance_cannot_publish_a_substituted_computation(*, nested: bool) -> None:
    valid = LineTotal(left=UnitPrice(Decimal("2.50")), right=Quantity(3))
    forged = valid.model_copy(update={"root": Decimal("999")})

    # Native reconstruction can reject forged storage or derive the correct result.
    # Neither boundary may publish the substituted value.
    try:
        restored = Lines(of=(forged,)) if nested else TypeAdapter(LineTotal).validate_python(forged)
    except ValidationError as failure:
        assert failure.errors()
        assert all(e["type"] != "tca_refuted" for e in failure.errors())
    else:
        assert restored.root == Decimal("7.50")


@pytest.mark.parametrize("quantity", [0, -1, "3"], ids=["zero", "negative", "wrong-python-type"])
def test_invalid_operands_are_not_business_refusals(quantity: object) -> None:
    with pytest.raises(ValidationError) as failure:
        LineTotal.model_validate({"left": Decimal("2.50"), "right": quantity})

    assert failure.value.errors()
    assert all(e["type"] != "tca_refuted" for e in failure.value.errors())


@pytest.mark.parametrize("price,allowed", [("99.99", True), ("100", True), ("100.01", False)])
def test_comparison_boundary_uses_native_structured_refusal(*, price: str, allowed: bool) -> None:
    amount = LineTotal(left=UnitPrice(Decimal(price)), right=Quantity(1))

    if allowed:
        value = Small(value=amount, bound=Threshold())
        assert value.value.root == Decimal(price)
        assert value.bound.root == Decimal(100)
    else:
        with pytest.raises(ValidationError) as failure:
            Small(value=amount, bound=Threshold())
        assert {e["type"] for e in failure.value.errors()} == {"tca_refuted"}


def test_json_and_python_modes_construct_the_same_value() -> None:
    from_json = LineTotal.model_validate_json('{"left":"2.50","right":3}')
    from_python = LineTotal(left=UnitPrice(Decimal("2.50")), right=Quantity(3))

    assert from_json == from_python
    assert from_json.root == Decimal("7.50")
