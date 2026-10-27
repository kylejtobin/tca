"""Architecture §5 World refusal protocol and §8 construction outcomes: a refused condition is
a ``PydanticCustomError`` of the reserved type, carried by Pydantic at the refusing location,
and nothing else carries that type."""

from decimal import Decimal
from typing import Self

import pytest
from pydantic import ValidationError, model_validator
from pydantic_core import PydanticCustomError

from type_construction.world import REFUTED, Record, Scalar, refuse


class Amount(Scalar[Decimal]):
    root: Decimal


class Positive(Record):
    amount: Amount

    @model_validator(mode="after")
    def held(self) -> Self:
        if self.amount.root <= 0:
            refuse("{amount} is not positive", amount=self.amount.root)
        return self


class Holder(Record):
    positive: Positive
    label: str


def test_refuse_raises_the_reserved_error_type_with_the_rendered_condition() -> None:
    with pytest.raises(PydanticCustomError) as raised:
        refuse("{amount} is not positive", amount=Decimal(-1))

    assert raised.value.type == REFUTED == "tca_refuted"
    assert raised.value.message() == "-1 is not positive"


def test_a_refused_condition_is_reported_at_its_own_location_with_the_reserved_type() -> None:
    with pytest.raises(ValidationError) as failure:
        Holder.model_validate({"positive": {"amount": Decimal(-1)}, "label": "x"})

    assert [(e["type"], e["loc"]) for e in failure.value.errors()] == [(REFUTED, ("positive",))]


def test_a_malformed_sibling_is_reported_beside_the_refusal_with_its_own_type() -> None:
    with pytest.raises(ValidationError) as failure:
        Holder.model_validate({"positive": {"amount": Decimal(-1)}, "label": 5})

    assert {(e["type"], e["loc"]) for e in failure.value.errors()} == {
        (REFUTED, ("positive",)),
        ("string_type", ("label",)),
    }


def test_a_malformed_operand_prevents_the_predicate_and_is_not_a_refusal() -> None:
    with pytest.raises(ValidationError) as failure:
        Positive.model_validate({"amount": "-1"})

    (error,) = failure.value.errors()
    assert error["loc"] == ("amount",)
    assert error["type"] != REFUTED


def test_a_condition_that_holds_constructs_the_value() -> None:
    assert Positive(amount=Amount(Decimal(1))).amount.root == Decimal(1)
