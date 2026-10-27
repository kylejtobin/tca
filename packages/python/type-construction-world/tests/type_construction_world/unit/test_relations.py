"""Architecture §5 World: comparisons refuse with the reserved code only after their operands
validate; computations derive their result from validated operands and accept no substitute;
selections over a finite tuple hold for exactly their declared count."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Annotated

import pytest
from pydantic import Field, TypeAdapter, ValidationError

from type_construction.world import (
    REFUTED,
    AtLeast,
    AtMost,
    Between,
    Beyond,
    Equal,
    Only,
    Record,
    Scalar,
    Sum,
    Times,
    Value,
)
from type_construction.world.relations import Comparison


class Amount(Scalar[Decimal]):
    root: Decimal = Field(gt=0)


class Count(Scalar[int]):
    root: int = Field(gt=0)


class Threshold(Scalar[Decimal]):
    root: Decimal = Decimal(100)


class Rate(Scalar[Decimal]):
    root: Decimal = Decimal("0.9")


class Total(Times[Amount, Count]):
    """A line's total."""


class Reduced(Times[Total, Rate]):
    """A total at the rate."""


class Totals(Sum[Total]):
    """What several lines cost together."""


class Covers(AtLeast[Totals, Threshold]):
    """The totals reach the threshold."""


class Small(AtMost[Total, Threshold]):
    """A line is small."""


class Large(Beyond[Total, Threshold]):
    """A line is large."""


class Exact(Equal[Total, Threshold]):
    """A line is exactly the threshold."""


class Within(Between[Count, Count, Count]):
    """A count is within two others."""


class Single(Only[Amount]):
    """Exactly one amount."""


class Tag(Value):
    name: str


class Pair(Record):
    small: Small
    tag: Tag


def total(amount: str, count: int = 1) -> Total:
    return Total(left=Amount(Decimal(amount)), right=Count(count))


def error_types(failure: ValidationError) -> set[str]:
    return {e["type"] for e in failure.errors()}


@pytest.mark.parametrize(
    ("relation", "amount", "holds"),
    [
        (Small, "99.99", True),
        (Small, "100", True),
        (Small, "100.01", False),
        (Large, "100", False),
        (Large, "100.01", True),
        (Exact, "100", True),
        (Exact, "100.00", True),
        (Exact, "99.99", False),
    ],
)
def test_comparison_holds_or_refuses_exactly_at_its_declared_boundary(
    relation: type[Small | Large | Exact], amount: str, *, holds: bool
) -> None:
    operand = total(amount)

    if holds:
        value = relation(value=operand, bound=Threshold())
        assert value.value == operand
        assert value.bound == Threshold()
    else:
        with pytest.raises(ValidationError) as failure:
            relation(value=operand, bound=Threshold())
        assert [(e["type"], e["loc"]) for e in failure.value.errors()] == [(REFUTED, ())]


@pytest.mark.parametrize("total_amount,holds", [("98.99", False), ("99", True), ("150", True)])
def test_at_least_compares_a_computed_sum_with_a_scalar(*, total_amount: str, holds: bool) -> None:
    totals = Totals(of=(total("1"), total(total_amount)))

    if holds:
        assert Covers(value=totals, bound=Threshold()).value.root == Decimal(total_amount) + 1
    else:
        with pytest.raises(ValidationError) as failure:
            Covers(value=totals, bound=Threshold())
        assert error_types(failure.value) == {REFUTED}


@pytest.mark.parametrize("count,holds", [(1, False), (2, True), (3, True), (4, True), (5, False)])
def test_between_is_inclusive_at_both_bounds(*, count: int, holds: bool) -> None:
    if holds:
        assert Within(value=Count(count), lower=Count(2), upper=Count(4)).value == Count(count)
    else:
        with pytest.raises(ValidationError) as failure:
            Within(value=Count(count), lower=Count(2), upper=Count(4))
        assert error_types(failure.value) == {REFUTED}


@pytest.mark.parametrize(
    ("relation", "amount", "message"),
    [
        (Covers, "99", "Covers does not hold: 99 is not at least 100"),
        (Small, "101", "Small does not hold: 101 is not at most 100"),
        (Large, "100", "Large does not hold: 100 is not beyond 100"),
        (Exact, "99", "Exact does not hold: 99 is not 100"),
    ],
)
def test_a_refusal_states_in_the_relations_own_words_what_did_not_hold(
    relation: type[Covers | Small | Large | Exact], amount: str, message: str
) -> None:
    operand = Totals(of=(total(amount),)) if relation is Covers else total(amount)

    with pytest.raises(ValidationError) as failure:
        relation.model_validate({"value": operand, "bound": Threshold()})

    (error,) = failure.value.errors()
    assert (error["type"], error["msg"]) == (REFUTED, message)


def test_between_refusal_names_both_bounds() -> None:
    with pytest.raises(ValidationError) as failure:
        Within(value=Count(9), lower=Count(2), upper=Count(4))

    (error,) = failure.value.errors()
    assert error["msg"] == "Within does not hold: 9 is not within 2 and 4"


def test_the_comparison_base_cannot_be_constructed_even_through_validation() -> None:
    given = {"value": Amount(Decimal(1)), "bound": Threshold()}

    with pytest.raises(TypeError, match="abstract"):
        Comparison[Amount, Threshold].model_validate(given)


class Moment(Scalar[datetime]):
    """When something happened."""


class NotBefore(AtLeast[Moment, Moment]):
    """One moment is not before another."""


@pytest.mark.parametrize("later", [True, False], ids=["after-cutoff", "before-cutoff"])
def test_comparisons_hold_over_moments_as_over_quantities(*, later: bool) -> None:
    cutoff = Moment(datetime(2026, 1, 1, tzinfo=UTC))
    moment = Moment(datetime(2026, 1, 1 + int(later), tzinfo=UTC) - timedelta(hours=1 - later))

    if later:
        assert NotBefore(value=moment, bound=cutoff).value == moment
    else:
        with pytest.raises(ValidationError) as failure:
            NotBefore(value=moment, bound=cutoff)
        assert error_types(failure.value) == {REFUTED}


class Name(Scalar[str]):
    """A name, ordered as names are."""


class NotBeforeName(AtLeast[Name, Name]):
    """One name is not before another."""


@pytest.mark.parametrize(("name", "holds"), [("Bravo", True), ("Alpha", False)])
def test_comparisons_hold_over_names_in_their_native_order(*, name: str, holds: bool) -> None:
    if holds:
        assert NotBeforeName(value=Name(name), bound=Name("Bravo")).value == Name(name)
    else:
        with pytest.raises(ValidationError) as failure:
            NotBeforeName(value=Name(name), bound=Name("Bravo"))
        assert error_types(failure.value) == {REFUTED}


def test_a_malformed_operand_is_reported_as_itself_and_the_predicate_does_not_run() -> None:
    with pytest.raises(ValidationError) as failure:
        Small.model_validate({"value": {"left": Decimal(500), "right": 0}, "bound": Decimal(1)})

    assert [(e["type"], e["loc"]) for e in failure.value.errors()] == [
        ("greater_than", ("value", "right"))
    ]


def test_a_refusal_beside_a_malformed_sibling_keeps_both_errors_distinct() -> None:
    with pytest.raises(ValidationError) as failure:
        Pair.model_validate({"small": {"value": total("500"), "bound": Threshold()}, "tag": 1})

    assert {(e["type"], e["loc"]) for e in failure.value.errors()} == {
        (REFUTED, ("small",)),
        ("model_type", ("tag",)),
    }


def test_a_union_member_that_constructs_is_chosen_after_a_refused_candidate() -> None:
    class Either(Value):
        pick: Small | Large

    given = {"value": {"left": Decimal(500), "right": 1}, "bound": Decimal(100)}
    with pytest.raises(ValidationError) as first_candidate:
        Small.model_validate(given)

    chosen = Either.model_validate({"pick": given})

    assert error_types(first_candidate.value) == {REFUTED}
    assert chosen.pick == Large(value=total("500"), bound=Threshold())


def test_computation_derives_its_result_from_validated_operands() -> None:
    line = Total(left=Amount(Decimal("2.50")), right=Count(3))
    reduced = Reduced(left=line, right=Rate())
    totals = Totals(of=(line, Total(left=Amount(Decimal("4.00")), right=Count(2))))

    assert line.root == Decimal("7.50")
    assert reduced.root == Decimal("6.750")
    assert totals.root == Decimal("15.50")
    assert Totals(of=()).root == 0


@pytest.mark.parametrize("supplied", ["7.50", "999"], ids=["correct", "forged"])
def test_a_supplied_result_is_an_undeclared_field_whatever_its_value(supplied: str) -> None:
    with pytest.raises(ValidationError) as failure:
        Total.model_validate({"left": Decimal("2.50"), "right": 3, "root": Decimal(supplied)})

    assert error_types(failure.value) == {"extra_forbidden"}


@pytest.mark.parametrize("enclosing", [False, True], ids=["adapter", "holder"])
def test_a_copy_carrying_a_substituted_result_still_reports_the_derived_one(
    *, enclosing: bool
) -> None:
    line = Total(left=Amount(Decimal("2.50")), right=Count(3))
    forged = line.model_copy(update={"root": Decimal(999)})

    assert forged.root == Decimal("7.50")
    with pytest.raises(ValidationError) as failure:
        if enclosing:
            Totals(of=(forged,))
        else:
            TypeAdapter(Total).validate_python(forged)
    assert error_types(failure.value) == {"extra_forbidden"}


def test_a_computation_over_an_operand_without_a_measure_is_a_declaration_fault() -> None:
    class Wrong(Times[Tag, Count]):
        pass

    with pytest.raises(TypeError, match="Tag carries no measure"):
        Wrong(left=Tag(name="x"), right=Count(1))


@pytest.mark.parametrize("members", [(), ("1",), ("1", "2")], ids=["none", "one", "two"])
def test_only_holds_for_exactly_one_member_and_exposes_it(members: tuple[str, ...]) -> None:
    amounts = tuple(Amount(Decimal(m)) for m in members)

    if len(members) == 1:
        assert Single(of=amounts).chosen == Amount(Decimal(1))
    else:
        with pytest.raises(ValidationError) as failure:
            Single(of=amounts)
        assert [(e["type"], e["loc"]) for e in failure.value.errors()] == [(REFUTED, ())]


def test_relations_construct_the_same_value_from_json_and_python() -> None:
    from_json = Small.model_validate_json('{"value": {"left": "2.50", "right": 3}, "bound": "9"}')
    from_python = Small(value=total("2.50", 3), bound=Threshold(Decimal(9)))

    assert from_json == from_python
    assert TypeAdapter(Annotated[Small, Field()]).validate_python(from_json) == from_python
