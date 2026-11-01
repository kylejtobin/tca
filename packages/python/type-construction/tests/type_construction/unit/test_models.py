"""The value foundations keep their configuration-only contract.

Governing requirement: docs/architecture/DESIGN.md section 5.1. ``Model`` and ``Root[T]`` add
``validate_default=True`` and ``frozen=True`` to native construction and nothing else.
"""

import pytest
from pydantic import Field, ValidationError

from type_construction import Model, Root


class Quantity(Root[int]):
    """A named scalar with a native constraint."""

    root: int = Field(ge=1)


class Line(Model):
    """A product whose constituents exist together."""

    sku: str
    quantity: Quantity = Quantity(1)


def test_bases_declare_required_configuration() -> None:
    for base in (Model, Root):
        assert base.model_config.get("validate_default") is True
        assert base.model_config.get("frozen") is True


def test_product_and_root_construct_from_native_rules() -> None:
    line = Line(sku="A-1", quantity=Quantity(3))

    assert line.quantity.root == 3
    assert Line(sku="A-1").quantity == Quantity(1)


def test_constraints_reject_invalid_constituents_at_their_location() -> None:
    with pytest.raises(ValidationError) as excinfo:
        Line.model_validate({"sku": "A-1", "quantity": 0})

    assert [(error["loc"], error["type"]) for error in excinfo.value.errors()] == [
        (("quantity",), "greater_than_equal")
    ]


def test_invalid_default_fails_at_construction() -> None:
    class Misdeclared(Model):
        count: int = Field(default=0, ge=1)

    with pytest.raises(ValidationError) as excinfo:
        Misdeclared()

    assert [(error["loc"], error["type"]) for error in excinfo.value.errors()] == [
        (("count",), "greater_than_equal")
    ]


def test_established_values_reject_reassignment() -> None:
    line = Line(sku="A-1")

    with pytest.raises(ValidationError) as excinfo:
        line.sku = "B-2"

    assert excinfo.value.errors()[0]["type"] == "frozen_instance"
    assert hash(line) == hash(Line(sku="A-1"))
