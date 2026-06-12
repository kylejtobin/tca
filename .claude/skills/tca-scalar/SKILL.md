---
name: tca-scalar
description: Build a semantic scalar, the only legal shape for a single domain value. MUST be invoked before writing any domain value type. Replaces the forbidden forms; if a bare str/int/float/Decimal/bool standing for a domain value, a vocabulary as string literals, or a standalone enum used as a type is about to appear, stop and build the scalar instead.
---

# semantic scalar

A semantic scalar is a domain meaning given its own named type: a frozen `RootModel`
over one primitive or one closed value space, carrying the constraint that defines it.
A closed vocabulary is the same construct: the `StrEnum` is the value space, the role
`gt=0` plays.

    class InvariantName(RootModel[str], frozen=True):
        root: str = Field(min_length=1, pattern=r"^[A-Z][A-Za-z0-9_]*$")

    class PositiveLineNumber(RootModel[int], frozen=True):
        root: int = Field(ge=1)

    class Suit(StrEnum):
        HEARTS = "hearts"
        DIAMONDS = "diamonds"
        CLUBS = "clubs"
        SPADES = "spades"

    class CardSuit(RootModel[Suit], frozen=True):
        root: Suit

Every primitive in the closed set carries its bound the same way; money is the
canonical `Decimal`, and an unconstrained scalar is legal exactly when the name does
real work and the openness is itself the domain fact, stated:

    class Price(RootModel[Decimal], frozen=True):
        root: Decimal = Field(gt=0, decimal_places=8)

    class ObjectBytes(RootModel[bytes], frozen=True):
        """One stored object's payload, verbatim. Unconstrained on purpose: the store
        admits the empty object, and a bound here would refuse a legal state."""
        root: bytes

A scalar carries no behavior but its derivations, and a derivation on a closed space
selects by data, never by branching: a ternary in a derivation body is denied.

    class OrderSide(RootModel[Side], frozen=True):
        root: Side

        @cached_property
        def opposite(self) -> "OrderSide":
            return OrderSide({Side.BUY: Side.SELL, Side.SELL: Side.BUY}[self.root])

The contrast that fails the test, primitive laundering: `class Name(RootModel[str])`
with no constraint and no meaning beyond its field name is a structure with no
meaning. `ObjectBytes` survives the same shape because its docstring states the domain
fact its openness asserts.

One axis, every member the same kind of thing: scalar. A member needing a field or
behavior a sibling lacks: that is two axes, a union (`tca-union`).

A scalar is constructed where its composite is proven: a raw primitive passed where
the scalar field stands constructs it inside the composite's own proof, constraint and
all. Pass the declared value itself onward; unwrapping `.root` to re-feed a constructor
that accepts the value erases the name the type carries and restates the constructor's
work. `.root` is read at one kind of site only: projecting into a foreign call the
program does not own.

## The row

The spec row this card expands. `name` is the class, `primitive` is the
`RootModel[...]` parameter, `constraint` is the `Field(...)` argument list
verbatim. A closed vocabulary carries `value_space` (the `StrEnum` class) and
`members` (its values) instead of `primitive`. The gate holds the file to the row.

    {"construct": "scalar", "name": "PositiveLineNumber", "file": "type.py", "primitive": "int", "constraint": "ge=1"}
    {"construct": "scalar", "name": "CardSuit", "file": "type.py", "value_space": "Suit", "members": ["hearts", "diamonds", "clubs", "spades"]}

## Allowed patterns

- `class X(RootModel[P], frozen=True)` over one primitive (`str`, `int`, `float`,
  `Decimal`, `bool`, `bytes`, `date`) with a `Field(...)` constraint that states the
  domain's actual bound
- `class X(RootModel[E], frozen=True)` over a `StrEnum` or `Literal` value space
- a derivation on the scalar returning a declared type (`tca-derivation`)

Build exactly these patterns. Never invent an exception. If you cannot see how, the
modeling is incomplete or construction is not yet the pipeline: report the gap.
