---
paths:
  - "tca/**/type.py"
---

# type.py — semantic scalars, the graph's leaves

The dependency root of a context: imports nothing from the program, and is imported by
everything in this context and its peers. The shape here is derived from the Semantic
scalar construct in `docs/type-construction-architecture.md`; that document is the
authority, this is the generation target for this one file.

A semantic scalar is a frozen `RootModel[P]` over one primitive (`str`, `int`, `float`,
`Decimal`, `bool`, `bytes`) or a closed value space named by a `StrEnum` or `Literal`,
carrying a `Field(...)` constraint or a domain-meaningful name that does real work, often
both. It is one shape varying along one axis, and that one-dimensionality is what
separates it from a union. Construction proves the constraint, so a value outside the
bound or outside the closed set has no representation. It carries no behavior but its
derivations.

A scalar with an open value space, a constraint over a primitive:

    class RoutingNumber(RootModel[str], frozen=True):
        root: str = Field(pattern=r"^\d{9}$")

A scalar whose value space is a closed named set: the `StrEnum` is the constraint, the
role `gt=0` plays. The vocabulary is named in one place and proven at construction, never
scattered as bare literals and never branched on:

    class CurrencyCode(StrEnum):
        USD = "USD"
        EUR = "EUR"
        GBP = "GBP"

    class Currency(RootModel[CurrencyCode], frozen=True):
        root: CurrencyCode

**Contains:** `RootModel` subclasses, `frozen=True`, each with a `Field()` constraint or
a genuine domain name. Nothing else: no methods beyond derivations, no validators, no
logic. The type's existence is its proof.

**Imports from:** standard library and third party only, never from the program.

**The breaks this file forbids** (each is one of the four):
- A bare primitive standing for a domain value, its meaning held in a variable name a
  reader downstream never receives (escaped). Forge the scalar.
- A closed vocabulary scattered as bare string literals, its value space unnamed and
  unproven (escaped, and fused once a member is branched on). Forge a scalar over a
  `StrEnum` value space.
- A `RootModel[str]` with neither a constraint nor a genuine domain name (vacuous,
  primitive laundering). It is not a scalar.
- A member that gets branched on: the dimensionality test has already fired, the
  vocabulary gained a second axis, and it is a union whose home is the concept file, not
  this one.
