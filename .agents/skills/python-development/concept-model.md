---
type: construct
---

# Concept model

## Definition

A frozen `BaseModel` composing declared types into one full domain thing or domain fact. The product type whose sum-type sibling is the union: the type is the concept, each field a relation to another concept.

## Required form

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

Every field is a declared type: never a bare primitive, never `T | None`, never a value derivable from other fields. A concept model that pins a `kind` is a [union](union.md) variant.

## Construction discipline

- A composite constructs whole in one call: constituents are proven by coercion inside it, never pre-constructed one at a time beside it.
- Keywords express the lift from a foreign result's attributes; `from_attributes` lifts a whole object; `model_validate_json` lifts serialized data.
- A hand-assembled dict fed to `model_validate` where keywords express it is a mapper in miniature.
- A coalesce on the way in (`x or default`) manufactures a value nothing proved.
- A check after construction un-proves the value it guards.

## Absence

- "May be missing" is never a field.
- Absence that means something is a [union](union.md) variant named for what absence means, or separate models when absence changes the state shape.
- An omitted foreign key resolves to a default that states what omission means, or a variant when omission means a different fact.
- Bare `None` never crosses into the domain.

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

`Flat` is the account with no position and carries no position fields: absence changed the state shape, so absence is its own variant. `QuoteSubscription.depth` defaults to the venue default, so an omitted foreign key never enters as `None`.

## Sorting

- A full domain thing or fact → this construct.
- A small identity-less composition of scalars, equal by value → [value object](value-object.md).
- A single value → [semantic scalar](semantic-scalar.md).
- A choice among concept models → [union](union.md); a concept model pinning one axis member is that union's variant.
- Another system's shape → [foreign model](foreign-model.md).
- Program placement → lives in `domain/<context>/[concept].py`; see [topology](topology.md).
- This program's API shape → [contract model](contract-model.md).
- Mutable state → [consistency model](consistency-model.md).

## Allowed

- `class X(BaseModel)` with `model_config = ConfigDict(frozen=True, extra="forbid")`
- `class Kind(Parent)` when the child is a kind of that concept model
- every field a declared type: a scalar, a value object, a collection element form, a concept model, or a union
- `from_attributes=True` in the config when the model lifts from objects
- a defaulted field whose default states what omission means
- derivations implying the model's facts
- the kind pin `kind: Literal[Axis.MEMBER] = Axis.MEMBER` when the row declares a variant

## Forbidden

- a bare primitive field
- a `T | None` field
- a stored field derivable from the others
- a validator that computes, normalizes, or asserts — a cross-field relation reparameterizes into one constrained field plus a derivation
- a `Present` or `Absent` wrapper
- subclassing a domain model for field reuse — the shared field is already shared as the leaf both models compose
- a constituent constructed in a separate statement beside its composite
- an unfrozen model that is not the consistency model
- a dataclass, `NamedTuple`, `TypedDict`, or dict-shaped value carrying the shape without the proof
