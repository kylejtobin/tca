"""Architecture §5 World and §8 native construction: the base vocabulary constructs strictly at
its complete boundary, is immutable afterwards, is revalidated wherever it is supplied, and
carries nothing the declaration did not name."""

from decimal import Decimal
from typing import Annotated

import pytest
from pydantic import Field, StringConstraints, TypeAdapter, ValidationError

from type_construction.world import REFUTED, Fact, Measured, Record, Scalar, Value, measure


class Amount(Scalar[Decimal]):
    root: Decimal = Field(gt=0)


class Count(Scalar[int]):
    root: int


class Limit(Scalar[Decimal]):
    root: Decimal = Decimal(30)


class Code(Scalar[str]):
    root: Annotated[str, StringConstraints(pattern=r"^C-[0-9]+$")]


class Line(Value):
    amount: Amount
    count: Count


class Reported(Fact):
    code: Code = Field(alias="line_code")
    amount: Amount


class Holder(Record):
    line: Line
    label: str


def error_types(failure: ValidationError) -> set[str]:
    return {e["type"] for e in failure.errors()}


def test_scalar_constructs_the_declared_native_type_in_python_and_json_modes() -> None:
    from_python = Amount(Decimal("2.50"))
    from_json = Amount.model_validate_json('"2.50"')

    assert from_python.root == Decimal("2.50")
    assert from_json == from_python
    assert isinstance(from_json.root, Decimal)


@pytest.mark.parametrize(
    "given", [2.5, "2.50", 3], ids=["float-for-decimal", "str-for-decimal", "int-for-decimal"]
)
def test_scalar_in_python_mode_refuses_coercible_but_wrong_types_without_refusal(
    given: object,
) -> None:
    with pytest.raises(ValidationError) as failure:
        Amount.model_validate(given)

    assert failure.value.errors()
    assert REFUTED not in error_types(failure.value)


def test_scalar_metadata_is_applied_and_is_not_a_refusal() -> None:
    with pytest.raises(ValidationError) as failure:
        Amount(Decimal(0))

    assert error_types(failure.value) == {"greater_than"}


def test_scalar_default_root_applies_on_omission_and_yields_to_a_supplied_root() -> None:
    assert Limit().root == Decimal(30)
    assert Limit(Decimal(5)).root == Decimal(5)


def test_scalar_is_frozen_hashable_and_equal_by_root() -> None:
    one, same = Amount(Decimal(1)), Amount(Decimal(1))

    with pytest.raises(ValidationError):
        one.root = Decimal(2)  # type: ignore[misc]
    assert one == same
    assert hash(one) == hash(same)
    assert one != Count(1)


def test_value_forbids_undeclared_fields_and_is_frozen() -> None:
    line = Line(amount=Amount(Decimal(1)), count=Count(2))

    with pytest.raises(ValidationError) as failure:
        Line.model_validate({"amount": Decimal(1), "count": 2, "note": "x"})
    with pytest.raises(ValidationError):
        line.count = Count(3)  # type: ignore[misc]

    assert error_types(failure.value) == {"extra_forbidden"}


def test_value_revalidates_a_supplied_instance_at_the_consuming_boundary() -> None:
    line = Line(amount=Amount(Decimal(1)), count=Count(2))
    forged = line.model_copy(update={"count": "two"})

    with pytest.raises(ValidationError) as failure:
        Holder(line=forged, label="x")

    assert ("line", "count") in {e["loc"][:2] for e in failure.value.errors()}
    assert REFUTED not in error_types(failure.value)


def test_a_scalar_instance_is_revalidated_by_the_holder_that_receives_it() -> None:
    forged = Count(2).model_copy(update={"root": "two"})

    with pytest.raises(ValidationError) as failure:
        Line(amount=Amount(Decimal(1)), count=forged)

    (error,) = failure.value.errors()
    assert error["loc"] == ("count",)
    assert error["type"] != REFUTED


def test_measured_is_what_carries_a_root() -> None:
    assert isinstance(Amount(Decimal(1)), Measured)
    assert not isinstance(Line(amount=Amount(Decimal(1)), count=Count(1)), Measured)


def test_fact_reads_the_sources_names_and_constructs_the_same_value_from_json() -> None:
    from_python = Reported(line_code=Code("C-1"), amount=Amount(Decimal(5)))
    from_json = Reported.model_validate_json('{"line_code": "C-1", "amount": "5"}')

    assert from_json == from_python
    assert from_python.code == Code("C-1")


def test_fact_by_name_is_an_explicit_choice_of_the_constructing_boundary() -> None:
    by_alias = TypeAdapter(Reported).validate_python({"line_code": "C-1", "amount": Decimal(5)})
    by_name = TypeAdapter(Reported).validate_python(
        {"code": "C-1", "amount": Decimal(5)}, by_name=True, by_alias=False
    )

    assert by_alias == by_name


def test_measure_reads_a_root_and_names_the_operand_that_has_none() -> None:
    assert measure(Amount(Decimal(3))) == Decimal(3)

    with pytest.raises(TypeError, match="Line carries no measure"):
        measure(Line(amount=Amount(Decimal(1)), count=Count(1)))
