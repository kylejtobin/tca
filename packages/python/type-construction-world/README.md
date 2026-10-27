# type-construction-world

TCA's reusable business-value vocabulary: native Pydantic scalars, values, records, and facts,
with computations, comparisons, and finite selections. World has no dependency on the engine
and makes no claim about where a value was observed or which work should run.

## Model and construct

```python
from decimal import Decimal

from pydantic import Field
from type_construction.world import AtMost, Scalar, Times


class Price(Scalar[Decimal]):
    root: Decimal = Field(ge=0)


class Quantity(Scalar[int]):
    root: int = Field(gt=0)


class LineTotal(Times[Price, Quantity]):
    pass


class WithinBudget(AtMost[LineTotal, Price]):
    pass


total = LineTotal(left=Price(Decimal("2.55")), right=Quantity(3))
approved = WithinBudget(value=total, bound=Price(Decimal("10.00")))

assert total.root == Decimal("7.65")
assert approved.value.root == Decimal("7.65")
```

Relations retain their validated operands. A computed result is derived from those operands;
callers cannot supply a replacement result. `Only[T]` selects exactly one member of a finite
tuple; zero or multiple members refuse.

## Arithmetic and construction outcomes

`Times` and `Sum` accept integer and Decimal measures. Integer arithmetic is exact Python
arithmetic. Decimal operations use a fresh, fully specified decimal128 context: 34 digits,
`Emin=-6143`, `Emax=6144`, clamp enabled, and half-even rounding. Inexact, invalid,
division-by-zero, overflow, underflow, and float-operation signals are trapped. Results that
cannot be represented exactly under this policy raise arithmetic exceptions instead of
silently rounding. Empty sums return integer zero; singleton sums apply the same policy as
larger sums. Float and boolean arithmetic operands raise `TypeError`.

Comparisons preserve native ordering, including Decimal/float, datetime, and string
comparisons. Their explicit local context disables the float-operation trap and retains the
invalid-operation trap. Computations and comparisons leave the caller's Decimal context alone.

- A satisfied condition constructs its relation value.
- A condition that does not hold produces a Pydantic `ValidationError` containing
  `tca_refuted` at the failing relation's location.
- Malformed operands produce native validation errors, not condition refusals.
- Programming faults and trapped arithmetic errors escape as exceptions, not refusals.

Models use frozen, strict native construction and revalidate supplied instances. Supported
collection declarations use tuples and frozen sets. Frozen wrappers do not make mutable
contents immutable; the engine's declaration and ownership checks enforce its ingress contract.

See the [architecture](../../../docs/TCA_ARCHITECTURAL_FOUNDATIONS.md) and
[decision register](../../../docs/ADR.md) for the complete contracts.
