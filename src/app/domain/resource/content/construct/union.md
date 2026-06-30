---
name: tca_authorized_construct_union
description: Build a union, the only legal shape for a choice among structures, in the graph and wherever identity-carrying raw data constructs one. MUST be invoked before modeling any set of kinds, any decision, any either/or, any status whose members carry payloads, and before any transport payload, stored fact, or re-entering published fact constructs a choice. Replaces the forbidden forms; if a match, an if/elif chain, or an isinstance ladder selecting by kind, a bool decision, a raw-string kind, an untagged union, a routing validator, or a RootModel wrapped around a union is about to appear, stop and build the union instead.
---
# Union

## Definition

A closed set of two or more frozen variants over one domain axis, the axis a `StrEnum`, each variant pinning exactly one member with a defaulted `kind: Literal[Axis.MEMBER]` field. The structural form of a choice: a decision with consequences is a union of result variants, and identity-carrying data constructs it through the discriminator on its alias.

## Required Form

```python
class OrderOutcomeKind(StrEnum):
    FILLED = "filled"
    REJECTED = "rejected"


class Filled(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[OrderOutcomeKind.FILLED] = OrderOutcomeKind.FILLED
    fill_price: Price
    filled_quantity: Quantity

    @property
    def headline(self) -> Headline:
        return Headline("order filled")


class Rejected(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[OrderOutcomeKind.REJECTED] = OrderOutcomeKind.REJECTED
    reason: RejectionReason

    @property
    def headline(self) -> Headline:
        return Headline("order rejected")


OrderOutcome = Annotated[Filled | Rejected, Field(discriminator="kind")]
```

The defaulted pin puts the identity in every serialization of the value. A fact that differs by variant is each variant's own same-named derivation, read from the union value: a consumer reads `outcome.headline`, and the static checker requires every variant to define `headline`.

Variants with identical payloads differ in nothing but identity, so identity is a field or it is nowhere:

```python
class HaltKind(StrEnum):
    HALTED = "halted"
    RESUMED = "resumed"


class Halted(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[HaltKind.HALTED] = HaltKind.HALTED
    at: Timestamp


class Resumed(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[HaltKind.RESUMED] = HaltKind.RESUMED
    at: Timestamp
```

A yes-or-no decision with consequences is a two-variant union, never `bool`, because each outcome carries its own facts:

```python
class ReviewKind(StrEnum):
    APPROVED = "approved"
    REFUSED = "refused"


class Approved(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ReviewKind.APPROVED] = ReviewKind.APPROVED
    terms: ApprovalTerms


class Refused(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ReviewKind.REFUSED] = ReviewKind.REFUSED
    reason: RefusalReason
```

## Sorting Rules

A uniform one-axis vocabulary, every member the same kind of thing, is a semantic scalar over a `StrEnum`; the moment a member needs a field or behavior a sibling lacks, it is this construct. Foreign data that carries no identity and is expected to fail constructs through the ordered union, never by discriminator. A single variant on its own is a concept model pinning a kind.

## Replaced Forms

A `match`, `if`/`elif` chain, or `isinstance` ladder over variants is selection re-implemented after construction already selected; what differs by variant is the variant's derivation. A `bool` decision fuses both outcomes and drops both payloads. A raw-string kind or an unpinned `kind: Axis` admits every member on every variant and identifies nothing. A `RootModel` wrapped around a union is a class created only to provide `model_validate` the alias already provides.

## Construct-Specific Doctrine

**The alias.** The discriminator is declared on the union's own alias: `Annotated[A | B, Field(discriminator="kind")]`, one alias, one name, everywhere. In the graph the annotation is inert and the checker narrows through it. Where identity-carrying raw data constructs the union, the alias is the constructor: as a field on a foreign or contract model, or through one module-level `TypeAdapter` named for the alias when the data arrives with no surrounding modeled structure. Discriminated construction fails on the claimed variant's own fields, never across all variants.

```python
OrderOutcomeConstructor = TypeAdapter(OrderOutcome)

outcome = OrderOutcomeConstructor.validate_json(transport_bytes)
```

**Probes.** Before building on a union, construct one variant and read the pin back:

```python
filled = Filled(fill_price=Price("101.50"), filled_quantity=Quantity("3"))
```

`filled.kind` is `OrderOutcomeKind.FILLED`, and `kind` appears in the serialized data. Before building on the alias, serialize a constructed variant and re-prove it: `OrderOutcomeConstructor.validate_json(filled.model_dump_json())` returns a `Filled`, because the identity was carried in the data. Never author a dict input object as a probe.

## Allowed Patterns

- one `StrEnum` axis declared beside the variants
- two or more frozen variants, each pinning exactly one member with `kind: Literal[Axis.MEMBER] = Axis.MEMBER`
- the alias `Annotated[A | B, Field(discriminator="kind")]` as the union's one rendered form
- the alias as a field's type, a derivation's return, or a verb parameter
- a same-named derivation on every variant for any fact that differs by variant
- one `TypeAdapter` named for the alias, only for bare arrivals

## Forbidden

- a raw-string kind or `kind: Axis` unpinned
- an untagged union selected by field shape
- `match`, `if`/`elif`, or `isinstance` over variants
- `bool` returned as a domain decision
- a `RootModel` class wrapped around a union
- a routing validator selecting a variant
- a hand-written dict input passed to discriminated construction

## Halt Rule

Halt when a variant cannot pin exactly one axis member, when a member sits outside the axis, or when the data that must construct the union carries no identity. Report the row and the variant or arrival: the axis is mis-factored or the arrival belongs to the ordered union, and the table is not finished.
