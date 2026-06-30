---
name: tca_authorized_construct_concept_model
description: Build a concept model, the only legal shape for a full domain thing or domain fact. MUST be invoked before writing any composite domain class. Replaces the forbidden forms; if a dataclass, NamedTuple, TypedDict, dict-shaped value, a T | None field, a post-construction check, or a validator is about to appear, stop and build the concept model instead.
---
# Concept Model

## Definition

A frozen `BaseModel` composing declared types into one full domain thing or domain fact. The product type whose sum-type sibling is the union: the type is the concept, each field a relation to another concept.

## Required Form

```python
class Fill(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", from_attributes=True)
    order_id: OrderId
    account_id: AccountId
    fill_price: Price
    filled_quantity: Quantity


class Position(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[PositionKind.OPEN] = PositionKind.OPEN
    prior: PositionState
    fill: Fill

    @cached_property
    def exposure(self) -> Exposure:
        return Exposure(self.prior.exposure.root + self.fill.exposure.root)
```

Every field is a declared type: never a bare primitive, never `T | None`, and never a value derivable from other fields. A concept model that pins a `kind` is a union variant.

## Sorting Rules

A small identity-less composition of scalars, equal by value, is a value object. A single value is a semantic scalar. A choice among concept models is a union, and a concept model pinning one axis member is that union's variant. Another system's shape is a foreign model; this program's API shape is a contract model; mutable state is the consistency model.

## Replaced Forms

A dataclass, `NamedTuple`, `TypedDict`, or dict-shaped value carries the shape without the proof. A validator that asserts a relation is a check performed inside construction; the relation reparameterizes. A base class created only to share fields is a second structure for one meaning; the shared field is already shared as the leaf both models compose.

## Construct-Specific Doctrine

**Construction discipline.** A composite constructs whole in one call: constituents are proven by coercion inside it, never pre-constructed one at a time beside it. Keywords express the lift from a foreign result's attributes; `from_attributes` lifts a whole object; `model_validate_json` lifts serialized data. A dict assembled by hand and fed to `model_validate` where keywords express it is a mapper in miniature. A coalesce on the way in (`x or default`) manufactures a value nothing proved. A check after construction un-proves the value it guards.

**Absence.** "May be missing" is never a field. Absence that means something is a union variant named for what absence means, or separate models when absence changes the state shape. When constructing from foreign data, an omitted key resolves to a default that states what omission means, or a variant when omission means a different fact; bare `None` never crosses into the domain.

```python
class PositionKind(StrEnum):
    OPEN = "open"
    FLAT = "flat"


class Flat(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[PositionKind.FLAT] = PositionKind.FLAT

    @property
    def exposure(self) -> Exposure:
        return Exposure(Decimal("0"))


class QuoteSubscription(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    product: ProductId
    depth: BookDepth = BookDepth(50)
```

`Flat` is the account with no position, and it carries no position fields: absence changed the state shape, so absence is its own variant. `QuoteSubscription.depth` defaults to the venue default, so an omitted foreign key never enters as `None`.

## Allowed Patterns

- `class X(BaseModel)` with `model_config = ConfigDict(frozen=True, extra="forbid")`
- every field a declared type: a scalar, a value object, a collection element form, a concept model, or a union
- `from_attributes=True` in the config when the model lifts from objects
- a defaulted field whose default states what omission means
- derivations implying the model's facts
- the kind pin `kind: Literal[Axis.MEMBER] = Axis.MEMBER` when the row declares a variant

## Forbidden

- a bare primitive field
- a `T | None` field
- a stored field derivable from the others
- a validator that computes, normalizes, or asserts
- a `Present` or `Absent` wrapper
- subclassing a domain model for field reuse
- a constituent constructed in a separate statement beside its composite
- an unfrozen model that is not the consistency model

## Halt Rule

Halt when a field has no declared row, when a cross-field relation will not reparameterize into a constraint plus a derivation, or when an absence has no statable meaning. Report the row and the field or relation: the meaning is not yet modeled, and the table is not finished.
