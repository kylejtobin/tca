---
paths:
  - "tca/**/*.py"
---

# domain concept files — the frozen typed core

The shapes here are derived from the Frozen model, Union, Collection, Derivation,
Boundary model, and Domain event constructs in `docs/type-construction-architecture.md`,
which is the authority. This is the generation target for a context's concept files.
`type.py` (scalars) and `value.py` (value objects) and the active model carry their own
rules; this rule covers the frozen models, unions, collections, derivations, boundary
models, and events.

## Frozen model

A frozen `BaseModel` (`frozen=True`, `extra="forbid"`) composing already-declared types as
fields into one proven product. Its existence is the certificate that every field's
constraint held together.

    class BookLevel(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        price: Price
        quantity: BookQuantity

Every field is a declared type: never a bare primitive (an unforged scalar), never a bare
collection of primitives (an unforged element), never a field derivable from the others (a
derivation, not stored state). Shared fields are composed by holding a declared type, never
by subclassing a domain type. A cross-field relation no single field constrains is part of
the composite proof: reparameterize so it collapses into a single-field constraint and a
derivation first; only when that distorts the model is an asserting `model_validator(mode=
"after")` that *only raises* the home, and it never re-checks a field's own constraint.

## Union

A closed `RootModel[A | B | C]` of two or more frozen-model variants, each a distinct
structure, and disjoint so no value satisfies two. No stored discriminator, no tag, no
routing function.

    class BookMessage(RootModel[BookSnapshot | BookUpdate], frozen=True):
        root: BookSnapshot | BookUpdate

The variants must be disjoint, proven by the drop-test in the disjointness skill and run on
the substrate rather than reasoned. Behavior is read off the selected variant by a
same-named derivation, never switched by a `match`; that derivation may return a value or a
typed effect description (a frozen model) that the active model emits by one uniform step,
the effect read off the variant and never picked by a branch.

## Collection

A frozen `RootModel[tuple[T, ...]]` whose element `T` is a declared type, when the sequence
is a domain thing in its own right (its own constraints or a derivation it implies). As a
plain field it is `tuple[T, ...]` on a frozen model. The element is never a bare primitive.

## Derivation

A fact a frozen model implies from its own already-proven fields, the only behavior a
frozen value has. `@cached_property`, or `@computed_field` over `@cached_property` when it
must cross the wire. Takes only `self`, returns a declared type, union, or proven model,
never a bare `bool`/`str`/`int`. Its body is a single returned expression: no statement
before the return, no nested helper, no `match`, no `and`/`or` selection. It composes a
constructed object from the typed fields and never unwraps them to primitives or flattens
them into a hand-formatted string.

## Boundary model

A frozen model that takes foreign-shaped data and produces domain truth in a single
construction: `Field(alias="foreign_name")` for renames, nested declared models for nested
structure, `model_validate_json` for serialized payloads.

    class CoinbaseLevel(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        price: Price = Field(alias="price_level")
        quantity: L2Quantity = Field(alias="new_quantity")

It never retains a foreign handle as a field (no `arbitrary_types_allowed`). Its one allowed
procedural crossing is a `mode="before"` validator that indexes a transport wrapper to reach
the payload; a before-validator that renames or computes, or a `mode="after"` validator that
routes to a variant, is procedure and is out — distinct shapes are a union selected by
structure.

## Domain event

A frozen model representing an established fact, projected by `model_dump_json` onto a
transport to cross a process boundary, and re-proven through a boundary model on the far
side. The type is the contract: services publish facts after proof, they do not call each
other.

## The breaks this file forbids
- A bare primitive or a bare collection of primitives as a field (escaped).
- A stored discriminator/`kind` tag, or an `if`/`elif`/`match` over a union (duplicated).
- A `bool` returned as a decision (fused outcomes). Use a union of typed result variants.
- A standalone function computing from a model's fields, or a stored derivable field
  (escaped derivation).
- A type minted to factor out recurring fields (vacuous). Compose the shared leaf.
- A mapper/adapter/DTO between foreign and domain (escaped). Use a boundary model.
- A foreign handle held on a boundary model. The live client's home is the active model.
