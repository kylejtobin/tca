"""ADR D-003 and D-004, architecture §§2, 5: a computation's result follows from its validated
operands alone. Arithmetic runs under the world's own fully specified decimal policy, never
the ambient ``decimal`` context, so identical declared operands give identical results at
construction, on later access, in nested composition and on native reconstruction, whatever
the surrounding configuration; a result the policy cannot represent exactly is a fault, never
a rounded value."""

from collections.abc import Callable, Iterator
from decimal import (
    ROUND_DOWN,
    ROUND_HALF_EVEN,
    ROUND_UP,
    Context,
    Decimal,
    DivisionByZero,
    FloatOperation,
    Inexact,
    InvalidOperation,
    Overflow,
    Rounded,
    Underflow,
    getcontext,
    localcontext,
)
from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

from type_construction.world import (
    REFUTED,
    AtLeast,
    AtMost,
    Between,
    Beyond,
    Equal,
    Scalar,
    Sum,
    Times,
    arithmetic,
    comparison,
)


class Amount(Scalar[Decimal]):
    root: Decimal


class Count(Scalar[int]):
    root: int


class Total(Times[Amount, Count]):
    """A line's total."""


class Totals(Sum[Total]):
    """What the lines cost together."""


class Units(Sum[Count]):
    """How many units in all."""


class Covers(AtLeast[Totals, Amount]):
    """The totals reach an amount."""


EXACT_TOTAL = Decimal("7.65")
"""2.55 times 3, as arithmetic gives it: the independent expectation of every case below."""


def line() -> Total:
    return Total(left=Amount(Decimal("2.55")), right=Count(3))


@pytest.fixture
def coarse_ambient_context() -> Any:
    """An ambient context under which 2.55 times 3 would round to 7.6: two digits, rounding
    away from zero, and no trap on the inexact result."""
    with localcontext() as ambient:
        ambient.prec = 2
        ambient.rounding = ROUND_UP
        ambient.traps[Inexact] = False
        yield ambient


def snapshot(context: Context) -> tuple[Any, ...]:
    """Everything a caller configures on a context, and every flag it has raised."""
    return (
        context.prec,
        context.rounding,
        context.Emin,
        context.Emax,
        context.capitals,
        context.clamp,
        dict(context.flags),
        dict(context.traps),
    )


def coarse(context: Context) -> None:
    context.prec = 2
    context.rounding = ROUND_UP


def narrow(context: Context) -> None:
    context.Emax = 5
    context.Emin = -5


def untrapped(context: Context) -> None:
    for signal in context.traps:
        context.traps[signal] = False


def flagged(context: Context) -> None:
    context.flags[Rounded] = True
    context.flags[Inexact] = True


def truncating(context: Context) -> None:
    context.prec = 3
    context.rounding = ROUND_DOWN
    context.traps[Inexact] = False


AMBIENTS: dict[str, Callable[[Context], None]] = {
    "coarse-precision-rounding-up": coarse,
    "narrow-exponent-range": narrow,
    "every-trap-disabled": untrapped,
    "flags-already-raised": flagged,
    "truncating-untrapped": truncating,
}


@pytest.fixture(params=list(AMBIENTS), ids=list(AMBIENTS))
def ambient(request: pytest.FixtureRequest) -> Iterator[Context]:
    """One way a caller may have configured the ambient context."""
    with localcontext() as context:
        AMBIENTS[request.param](context)
        yield context


class Big(Sum[Amount]):
    """A sum the narrow ambient range could not hold."""


def test_results_and_failure_categories_are_stable_whatever_the_ambient_setting(
    ambient: Context,
) -> None:
    before = snapshot(ambient)
    constructed = line()
    composed = Totals(of=(constructed, constructed))
    big = Big(of=(Amount(Decimal("1E+6")), Amount(Decimal("1E+6"))))

    revalidated = TypeAdapter(Total).validate_python(constructed)
    from_json = Total.model_validate_json('{"left": "2.55", "right": 3}')
    twenty_digits = Amount(Decimal("1.2345678901234567890"))
    with pytest.raises(Inexact):
        Times[Amount, Amount](left=twenty_digits, right=twenty_digits)
    with pytest.raises(ValidationError) as refusal:
        Covers(value=composed, bound=Amount(Decimal("15.31")))

    assert constructed.root == revalidated.root == from_json.root == EXACT_TOTAL
    assert composed.root == Decimal("15.30")
    assert big.root == Decimal("2E+6")
    assert {e["type"] for e in refusal.value.errors()} == {REFUTED}
    assert snapshot(ambient) == before


def test_a_result_constructed_before_the_ambient_context_changes_holds_under_it() -> None:
    constructed = line()
    totals = Totals(of=(constructed, constructed))

    with localcontext() as ambient:
        ambient.prec = 2
        ambient.rounding = ROUND_UP
        ambient.traps[Inexact] = False
        accessed = constructed.root
        composed = totals.root
        revalidated = TypeAdapter(Total).validate_python(constructed)
        from_json = Total.model_validate_json('{"left": "2.55", "right": 3}')
        fresh = line()

    assert accessed == EXACT_TOTAL
    assert composed == Decimal("15.30")
    assert revalidated == from_json == fresh == constructed
    assert revalidated.root == from_json.root == fresh.root == EXACT_TOTAL


def test_a_result_is_exact_when_constructed_under_a_coarse_ambient_context(
    coarse_ambient_context: Any,
) -> None:
    constructed = line()

    assert constructed.root == EXACT_TOTAL
    assert getcontext().prec == 2


def test_nested_composition_is_exact_under_a_coarse_ambient_context(
    coarse_ambient_context: Any,
) -> None:
    totals = Totals(of=(line(), line()))
    covered = Covers(value=totals, bound=Amount(Decimal("15.30")))

    assert totals.root == Decimal("15.30")
    assert covered.value.root == Decimal("15.30")


def test_native_reconstruction_under_a_coarse_ambient_context_gives_the_same_value(
    coarse_ambient_context: Any,
) -> None:
    constructed = line()

    revalidated = TypeAdapter(Total).validate_python(constructed)
    from_json = Total.model_validate_json('{"left": "2.55", "right": 3}')

    assert revalidated == constructed
    assert revalidated.root == from_json.root == EXACT_TOTAL


def test_identical_operands_give_equal_and_identically_hashed_results() -> None:
    first, second = line(), line()
    with localcontext() as ambient:
        ambient.prec = 2
        ambient.traps[Inexact] = False
        third = line()

    assert first == second == third
    assert hash(first) == hash(second) == hash(third)
    assert first.root == second.root == third.root == EXACT_TOTAL


def test_a_refusal_boundary_is_judged_on_exact_arithmetic(coarse_ambient_context: Any) -> None:
    totals = Totals(of=(line(),))

    with pytest.raises(ValidationError) as failure:
        Covers(value=totals, bound=Amount(Decimal("7.651")))
    assert {e["type"] for e in failure.value.errors()} == {REFUTED}
    assert Covers(value=totals, bound=Amount(Decimal("7.65"))).value.root == EXACT_TOTAL


@pytest.mark.parametrize(
    ("members", "expected"),
    [((), 0), ((7,), 7), ((2, 3, 10**30), 10**30 + 5)],
    ids=["empty", "singleton", "many"],
)
def test_integer_sums_are_exact_integers_whatever_the_member_count(
    members: tuple[int, ...], expected: int
) -> None:
    units = Units(of=tuple(Count(m) for m in members))

    assert units.root == expected
    assert isinstance(units.root, int)


@pytest.mark.parametrize(
    ("members", "expected"),
    [(("2.55",), Decimal("2.55")), (("0.1", "0.2"), Decimal("0.3"))],
    ids=["singleton", "many"],
)
def test_decimal_sums_are_exact_whatever_the_member_count(
    members: tuple[str, ...], expected: Decimal
) -> None:
    class Amounts(Sum[Amount]):
        pass

    amounts = Amounts(of=tuple(Amount(Decimal(m)) for m in members))

    assert amounts.root == expected


class Loose(Scalar[Any]):
    """A scalar whose root is whatever was given: the way an inexact measure reaches a sum."""

    root: Any


class LooseSum(Sum[Loose]):
    pass


@pytest.mark.parametrize("member", [2.5, True, "7"], ids=["float", "bool", "str"])
@pytest.mark.parametrize("count", [1, 2], ids=["singleton", "many"])
def test_a_sum_over_an_inexact_member_is_a_declaration_fault_at_any_count(
    member: object, count: int
) -> None:
    with pytest.raises(TypeError, match="exact"):
        LooseSum(of=tuple(Loose(member) for _ in range(count)))


@pytest.mark.parametrize(
    ("members", "signal"),
    [(("1E+7000",), Overflow), (("1E+34", "1"), Inexact)],
    ids=["singleton-overflow", "many-inexact"],
)
def test_a_sum_the_policy_cannot_hold_is_a_fault_at_any_count(
    members: tuple[str, ...], signal: type[ArithmeticError]
) -> None:
    class Amounts(Sum[Amount]):
        pass

    with pytest.raises(signal):
        Amounts(of=tuple(Amount(Decimal(m)) for m in members))


class Product(Times[Amount, Amount]):
    pass


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ("1234567890123456789012345678901234", "1", Decimal("1234567890123456789012345678901234")),
        ("1E+6144", "1", Decimal("1E+6144")),
        ("1E-6143", "1E-33", Decimal("1E-6176")),
        ("-0", "3", Decimal("-0")),
        ("0", "-3", Decimal("-0")),
    ],
    ids=["34-digits-exact", "largest-exponent", "smallest-exponent", "neg-zero-sign", "zero-sign"],
)
def test_a_product_at_the_policys_edge_is_exact(left: str, right: str, expected: Decimal) -> None:
    product = Product(left=Amount(Decimal(left)), right=Amount(Decimal(right)))

    assert isinstance(product.root, Decimal)
    assert product.root == expected
    assert product.root.is_signed() == expected.is_signed()


@pytest.mark.parametrize(
    ("left", "right", "signal"),
    [
        ("12345678901234567890123456789012345", "1", Inexact),
        ("1E+6144", "10", Overflow),
        ("1E-6143", "1E-34", Underflow),
    ],
    ids=["35-digits", "beyond-largest-exponent", "below-smallest-exponent"],
)
def test_a_product_beyond_the_policys_edge_is_a_fault(
    left: str, right: str, signal: type[ArithmeticError]
) -> None:
    with pytest.raises(signal):
        Product(left=Amount(Decimal(left)), right=Amount(Decimal(right)))


class Amounts(Sum[Amount]):
    pass


@pytest.mark.parametrize(
    ("members", "expected"),
    [
        (("1E+33", "1", "-1E+33"), Decimal(1)),
        (("0.1", "0.2", "-0.3"), Decimal("0.0")),
        (("-0.0",), Decimal("0.0")),
        (("-0.0", "-0.0"), Decimal("0.0")),
    ],
    ids=["large-then-cancelled", "tenths-cancelled", "neg-zero-alone", "neg-zeros"],
)
def test_cancellation_and_signed_zero_in_a_sum_follow_the_policy(
    members: tuple[str, ...], expected: Decimal
) -> None:
    """A sum starts from the integer zero, so under half-even rounding a negative zero added
    to it is a positive zero: the sign of zero is the policy's, not the members'."""
    total = Amounts(of=tuple(Amount(Decimal(m)) for m in members))

    assert isinstance(total.root, Decimal)
    assert total.root == expected
    assert total.root.is_signed() == expected.is_signed()


def test_a_sum_that_would_lose_a_member_to_precision_is_a_fault_not_a_silent_loss() -> None:
    with pytest.raises(Inexact):
        Amounts(of=(Amount(Decimal("1E+34")), Amount(Decimal(1)), Amount(Decimal("-1E+34"))))


class Mixed(Sum[Loose]):
    pass


class Scaled(Times[Count, Amount]):
    pass


def test_integer_and_decimal_operands_mix_into_an_exact_decimal() -> None:
    mixed = Mixed(of=(Loose(3), Loose(Decimal("0.5")), Loose(2)))
    scaled = Scaled(left=Count(3), right=Amount(Decimal("2.55")))

    assert mixed.root == Decimal("5.5")
    assert isinstance(mixed.root, Decimal)
    assert scaled.root == EXACT_TOTAL
    assert isinstance(scaled.root, Decimal)


def test_signed_zero_compares_as_zero() -> None:
    class Reaches0(AtLeast[Amount, Amount]):
        pass

    class Is(Equal[Amount, Amount]):
        pass

    assert Reaches0(value=Amount(Decimal("-0")), bound=Amount(Decimal(0))).value.root == 0
    assert Is(value=Amount(Decimal("-0.0")), bound=Amount(Decimal("0.00"))).value.root == 0


def test_the_policy_is_decimal128_with_every_inexact_signal_trapped() -> None:
    policy = arithmetic()

    assert (policy.prec, policy.rounding, policy.Emin, policy.Emax, policy.clamp) == (
        34,
        ROUND_HALF_EVEN,
        -6143,
        6144,
        1,
    )
    assert all(
        policy.traps[signal]
        for signal in (
            Inexact,
            InvalidOperation,
            DivisionByZero,
            Overflow,
            Underflow,
            FloatOperation,
        )
    )
    assert not any(policy.flags.values())


def test_the_policy_cannot_be_changed_through_a_handed_out_context() -> None:
    handed_out = arithmetic()
    handed_out.prec = 2
    handed_out.traps[Inexact] = False

    assert arithmetic().prec == 34
    assert line().root == EXACT_TOTAL


def test_a_result_the_policy_cannot_hold_exactly_is_a_fault_not_a_rounded_value() -> None:
    twenty_digits = Amount(Decimal("1.2345678901234567890"))

    with pytest.raises(Inexact):
        Times[Amount, Amount](left=twenty_digits, right=twenty_digits)
    with pytest.raises(Overflow):
        Times[Amount, Amount](left=Amount(Decimal("1E+6000")), right=Amount(Decimal("1E+6000")))


@pytest.mark.parametrize("operand", [2.5, True], ids=["float", "bool"])
def test_an_operand_outside_the_exact_policy_is_a_declaration_fault(operand: object) -> None:
    with pytest.raises(TypeError, match="exact"):
        Times[Loose, Count](left=Loose(operand), right=Count(1))


class Reaches(AtLeast[Amount, Loose]):
    pass


class Stays(AtMost[Amount, Loose]):
    pass


class Exceeds(Beyond[Amount, Loose]):
    pass


class Matches(Equal[Amount, Loose]):
    pass


class Inside(Between[Amount, Loose, Loose]):
    pass


@pytest.mark.parametrize(
    "trap_floats", [True, False], ids=["ambient-traps-floats", "ambient-allows"]
)
@pytest.mark.parametrize(
    ("relation", "amount", "holds"),
    [
        (Reaches, "2", True),
        (Reaches, "1", False),
        (Stays, "1", True),
        (Stays, "2", False),
        (Exceeds, "2", True),
        (Exceeds, "1.5", False),
        (Matches, "1.5", True),
        (Matches, "2", False),
    ],
)
def test_a_decimal_against_a_float_is_judged_the_same_whatever_the_ambient_traps(
    *,
    trap_floats: bool,
    relation: type[Reaches | Stays | Exceeds | Matches],
    amount: str,
    holds: bool,
) -> None:
    given = {"value": Amount(Decimal(amount)), "bound": Loose(1.5)}

    with localcontext() as ambient:
        ambient.traps[FloatOperation] = trap_floats
        if holds:
            assert relation.model_validate(given).value.root == Decimal(amount)
        else:
            with pytest.raises(ValidationError) as failure:
                relation.model_validate(given)
            assert {e["type"] for e in failure.value.errors()} == {REFUTED}


@pytest.mark.parametrize(
    "trap_floats", [True, False], ids=["ambient-traps-floats", "ambient-allows"]
)
@pytest.mark.parametrize(("amount", "holds"), [("1.5", True), ("3", False)])
def test_between_against_floats_is_judged_the_same_whatever_the_ambient_traps(
    *, trap_floats: bool, amount: str, holds: bool
) -> None:
    given = {"value": Amount(Decimal(amount)), "lower": Loose(1.0), "upper": Loose(2.0)}

    with localcontext() as ambient:
        ambient.traps[FloatOperation] = trap_floats
        if holds:
            assert Inside.model_validate(given).value.root == Decimal(amount)
        else:
            with pytest.raises(ValidationError) as failure:
                Inside.model_validate(given)
            assert {e["type"] for e in failure.value.errors()} == {REFUTED}


def test_the_comparison_policy_is_fully_specified_and_allows_floats() -> None:
    policy = comparison()

    assert (policy.prec, policy.rounding, policy.Emin, policy.Emax) == (
        34,
        ROUND_HALF_EVEN,
        -6143,
        6144,
    )
    assert not policy.traps[FloatOperation]
    assert policy.traps[InvalidOperation]
    assert not any(policy.flags.values())


def test_an_undefined_comparison_is_a_fault_not_a_refusal() -> None:
    with pytest.raises(InvalidOperation):
        Reaches(value=Amount(Decimal(1)), bound=Loose(float("nan")))
