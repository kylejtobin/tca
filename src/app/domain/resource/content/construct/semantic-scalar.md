---
name: tca_authorized_construct_semantic_scalar
description: Build a semantic scalar, the only legal shape for a single domain value. MUST be invoked before writing any domain value type. Replaces the forbidden forms; if a bare str, int, float, Decimal, bool, bytes, or date standing for a domain value, a vocabulary as string literals, or a standalone enum used as a field type is about to appear, stop and build the scalar instead.
---
# Semantic Scalar

## Definition

A frozen `RootModel[P]` over one primitive or one closed value space, carrying a `Field(...)` constraint or a docstring stating why the open range is the domain fact. The atomic domain value: it references no domain type.

## Required Form

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

The allowed primitives are `str`, `int`, `float`, `Decimal`, `bool`, `bytes`, and `date`. A closed vocabulary wraps a `StrEnum` or `Literal` value space; the `StrEnum` is the value space, the role `gt=0` plays. A scalar derivation on a closed value space selects by data lookup, never by a ternary or a branch.

## Sorting Rules

One axis, every member the same kind of thing: a scalar. A member needing a field or behavior a sibling lacks: two axes, a union. A value composed of other values: a value object or concept model.

## Replaced Forms

A bare primitive standing for a domain value holds its meaning in a variable name no downstream reader receives. A vocabulary scattered as string literals is unnamed and unproven. An unconstrained `RootModel[str]` with no docstring and no genuine name is a structure with no meaning.

## Construct-Specific Doctrine

A scalar constructs where its composite is proven: a raw value passed where the scalar field stands constructs it inside the composite's own call. Pass the declared value onward. `.root` is read in exactly two settings: inside a derivation's one returned expression, where the bare value immediately feeds the construction of the declared type the derivation returns, and where the program meets the wire, at a client binding or a route reply. A bare `.root` value is consumed by the construction or the client call that reads it, never assigned, stored, or passed onward.

## Allowed Patterns

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
- a bare `.root` value assigned, stored, or passed onward; `.root` is read only inside a derivation's returned construction, at a client binding, or at a route reply

## Halt Rule

Halt when a member of the value space needs a field or behavior a sibling lacks, or when a value has neither a statable constraint nor a statable openness. Report the row and the member or bound: the meaning is a union or is not yet understood, and the table is not finished.
