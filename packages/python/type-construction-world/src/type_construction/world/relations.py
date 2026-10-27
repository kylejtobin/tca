"""Reusable relations over values: comparisons that must hold, computations derived from their
operands, and selections among a finite tuple.

Each is a generic ``Record`` whose fields are its operands. A subclass names the relation for
the business (``Covers(AtLeast[Paid, Total])``) and the operands are bound where it is used.
Operands are validated natively first; the predicate or derivation runs in an after-validator
over validated operands only, so a malformed operand is an ordinary validation error and a
condition that does not hold is a refusal that states, in the relation's own words, what did
not hold. A computation's result is a property derived from its operands: it is not a field,
so no caller can supply it, and a copy carrying a substituted result is reconstructed from its
operands wherever it is revalidated.

Comparisons hold between any measures that order natively: quantities, moments, names. The
predicate is judged under the world's own comparison policy, ``comparison()``, never the
caller's context, so a decimal against a float compares the same wherever it is constructed.
Arithmetic is exact and follows from the operands alone. Integers combine as Python integers.
Decimals, and integers combined with them, are computed under the world's own policy,
``arithmetic()``: IEEE 754 decimal128 (34 digits, exponents from -6143 to 6144, clamped,
half-even rounding specified for completeness), with every signal that would make a result
inexact or undefined trapped, so a result is either exact or a fault and never a rounded
value. The ambient ``decimal`` context is never read, so a result is the same at
construction, on later access, in nested composition and on native reconstruction, whatever
the caller has configured. A float or a boolean carries no exact measure and is a
declaration fault.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import (
    ROUND_HALF_EVEN,
    Context,
    Decimal,
    DivisionByZero,
    FloatOperation,
    Inexact,
    InvalidOperation,
    Overflow,
    Underflow,
    localcontext,
)
from typing import Any, ClassVar, LiteralString, Self

from pydantic import model_validator

from .base import Record, measure
from .refusal import refuse

__all__ = [
    "AtLeast",
    "AtMost",
    "Between",
    "Beyond",
    "Equal",
    "Only",
    "Sum",
    "Times",
    "arithmetic",
    "comparison",
]


def arithmetic() -> Context:
    """The world's arithmetic policy, as a fresh context each time so that no handed-out
    context can change it: decimal128 precision and exponent range, clamped, half-even
    rounding, no flags raised, and the inexact, invalid, division-by-zero, overflow,
    underflow and float-operation signals trapped."""
    return Context(
        prec=34,
        rounding=ROUND_HALF_EVEN,
        Emin=-6143,
        Emax=6144,
        capitals=1,
        clamp=1,
        flags=[],
        traps=[Inexact, InvalidOperation, DivisionByZero, Overflow, Underflow, FloatOperation],
    )


def comparison() -> Context:
    """The world's comparison policy, a fresh context each time: the arithmetic policy's
    precision and range, with the float-operation signal untrapped so that a decimal compares
    natively with a float, and the invalid-operation signal trapped so that a comparison that
    is undefined, against a float that is not a number, is a fault and not a refusal."""
    policy = arithmetic()
    policy.traps[FloatOperation] = False
    return policy


def exact(quantity: Any) -> int | Decimal:
    """A measure the policy computes exactly: an integer or a decimal. Anything else, a float
    or a boolean among them, is a declaration fault."""
    if isinstance(quantity, bool) or not isinstance(quantity, int | Decimal):
        msg = f"{type(quantity).__name__} is not an exact measure: arithmetic takes int or Decimal"
        raise TypeError(msg)
    return quantity


def multiply(left: Any, right: Any) -> int | Decimal:
    """The exact product of two measures under the policy."""
    one, other = exact(left), exact(right)
    if isinstance(one, int) and isinstance(other, int):
        return one * other
    return arithmetic().multiply(one, other)


def add(left: Any, right: Any) -> int | Decimal:
    """The exact sum of two measures under the policy."""
    one, other = exact(left), exact(right)
    if isinstance(one, int) and isinstance(other, int):
        return one + other
    return arithmetic().add(one, other)


class Comparison[V, B](Record, ABC):
    """A value compared with a bound. A subclass states the predicate over the two measures
    and, as ``refused``, how to say that it did not hold; the base cannot be constructed."""

    value: V
    bound: B

    refused: ClassVar[LiteralString]
    """How the refusal reads, with ``{value}`` and ``{bound}`` in it."""

    @abstractmethod
    def holds(self, value: Any, bound: Any) -> bool:
        """Whether the comparison holds between the two measures."""

    @model_validator(mode="after")
    def compared(self) -> Self:
        """The predicate, over operands Pydantic has already validated."""
        value, bound = measure(self.value), measure(self.bound)
        with localcontext(comparison()):
            held = self.holds(value, bound)
        if not held:
            refuse(
                "{relation} does not hold: " + self.refused,
                relation=type(self).__name__,
                value=value,
                bound=bound,
            )
        return self


class AtLeast[V, B](Comparison[V, B]):
    """The value is at least the bound."""

    refused = "{value} is not at least {bound}"

    def holds(self, value: Any, bound: Any) -> bool:
        return bool(value >= bound)


class AtMost[V, B](Comparison[V, B]):
    """The value is at most the bound."""

    refused = "{value} is not at most {bound}"

    def holds(self, value: Any, bound: Any) -> bool:
        return bool(value <= bound)


class Beyond[V, B](Comparison[V, B]):
    """The value is beyond the bound: strictly greater."""

    refused = "{value} is not beyond {bound}"

    def holds(self, value: Any, bound: Any) -> bool:
        return bool(value > bound)


class Equal[V, B](Comparison[V, B]):
    """The value is the bound."""

    refused = "{value} is not {bound}"

    def holds(self, value: Any, bound: Any) -> bool:
        return bool(value == bound)


class Between[V, L, U](Record):
    """The value is within the lower and upper bounds, inclusive."""

    value: V
    lower: L
    upper: U

    @model_validator(mode="after")
    def within(self) -> Self:
        """The predicate, over operands Pydantic has already validated."""
        value, lower, upper = measure(self.value), measure(self.lower), measure(self.upper)
        with localcontext(comparison()):
            held = bool(lower <= value <= upper)
        if not held:
            refuse(
                "{relation} does not hold: {value} is not within {lower} and {upper}",
                relation=type(self).__name__,
                value=value,
                lower=lower,
                upper=upper,
            )
        return self


class Times[L, R](Record):
    """The product of two measures."""

    left: L
    right: R

    @property
    def root(self) -> int | Decimal:
        """The derived product."""
        return multiply(measure(self.left), measure(self.right))

    @model_validator(mode="after")
    def derived(self) -> Self:
        """Derive once at construction, so a fault surfaces where the value is made."""
        _ = self.root
        return self


class Sum[T](Record):
    """The sum of the measures of a tuple of operands; the integer zero when there are none."""

    of: tuple[T, ...]

    @property
    def root(self) -> int | Decimal:
        """The derived sum: the integer zero, then every member added under the policy, so
        a single member is judged exactly as one among many."""
        total: int | Decimal = 0
        for each in self.of:
            total = add(total, measure(each))
        return total

    @model_validator(mode="after")
    def derived(self) -> Self:
        """Derive once at construction, so a fault surfaces where the value is made."""
        _ = self.root
        return self


class Only[T](Record):
    """Exactly one member: the selection holds when the tuple has one member, which is then
    ``chosen``. None or several is a refusal, not an absence."""

    of: tuple[T, ...]

    @property
    def chosen(self) -> T:
        """The one member."""
        return self.of[0]

    @model_validator(mode="after")
    def selected(self) -> Self:
        """The predicate, over members Pydantic has already validated."""
        if len(self.of) != 1:
            refuse(
                "{relation} does not hold: {count} members, not one",
                relation=type(self).__name__,
                count=len(self.of),
            )
        return self
