---
type: construct
---

# Semantic scalar

## Definition

A frozen `RootModel[P]` over one primitive or one closed value space, carrying a `Field(...)` constraint or a docstring stating why the open range is the domain fact. The atomic domain value: it references no domain type.

Allowed primitives: `str`, `int`, `float`, `Decimal`, `bool`, `bytes`, `date`. A closed vocabulary wraps a `StrEnum` or `Literal` value space — the enum is the value space, the role `gt=0` plays.

## Required form

```python
class Price(RootModel[Decimal], frozen=True):
    root: Decimal = Field(gt=0, decimal_places=8)


class Quantity(RootModel[Decimal], frozen=True):
    root: Decimal = Field(gt=0)


class OrderId(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class Side(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderSide(RootModel[Side], frozen=True):
    root: Side

    @property
    def opposite(self) -> "OrderSide":
        return OrderSide({Side.BUY: Side.SELL, Side.SELL: Side.BUY}[self.root])


class OrderNote(RootModel[str], frozen=True):
    """A trader's free-text note on an order. Unconstrained on purpose: any text, including empty, is a legal note."""

    root: str
```

A scalar derivation on a closed value space selects by data lookup, never by a ternary or a branch.

## Root discipline

A scalar constructs where its composite is proven: pass the raw value where the scalar field stands and it constructs inside the composite's own call. Pass the declared value onward. Read `.root` in exactly two settings: inside a derivation's one returned expression, where the bare value immediately feeds the construction the derivation returns, and where the program meets the wire — a client binding or a route reply. A bare `.root` value is consumed by that construction or client call, never assigned, stored, or passed onward.

## Sorting

- One axis, every member the same kind of thing → this construct.
- A member needing a field or behavior a sibling lacks → two axes → [union](union.md).
- A value composed of other values → [value object](value-object.md) or [concept model](concept-model.md).
- Program placement → lives in `domain/<context>/type.py`; see [topology](topology.md).

## Allowed

- `class X(RootModel[P], frozen=True)` over one allowed primitive with a `Field(...)` constraint stating the domain's bound
- `class X(RootModel[E], frozen=True)` over a `StrEnum` or `Literal` value space
- an unconstrained scalar whose docstring states why the open range is the domain fact
- a derivation on the scalar returning a declared type, selecting by data lookup on a closed space

## Forbidden

- a bare primitive used as a domain value
- string literals used as a closed vocabulary
- a standalone enum used as a field type
- an unconstrained `RootModel` without a stated openness
- a ternary or branch inside a scalar derivation
- a bare `.root` value assigned, stored, or passed onward
