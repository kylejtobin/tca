---
name: tca_required_reference_jargon
description: The TCA construct vocabulary, the closed set of approved constructs and the definition of each. MUST be consulted whenever naming, classifying, or referencing a construct, and before introducing any architectural term. Replaces improvised vocabulary; if a term is about to be used for a structure not defined here, stop and use the defined construct name or report a missing construct.
---

# TCA jargon

The approved constructs, each defined once. A structure that fits none of these is a missing-construct report, never a new term.

## binding

The class whose `connect` method binds transport clients to the consistency model. Its entire meaning is the binding it performs: it owns no domain type, holds no domain logic, and makes no domain decision.

## collection

A frozen `RootModel[tuple[T, ...]]` whose element `T` is a declared type, for a sequence that is itself a domain thing with its own name, constraint, or derivation; or a frozen `RootModel[dict[K, V]]` over a declared key `K` and value `V`, for a namespace whose key-uniqueness is the domain fact. A sequence with no meaning of its own is a `tuple[T, ...]` field on a model, not a collection.

## composition root

The program entrypoint. It constructs config, instantiates concrete clients, passes them to bindings, constructs the consistency model, and registers or invokes routes. It holds no domain logic and defines no domain model.

## concept model

A frozen `BaseModel` composing declared types into one full domain thing or domain fact. The product type whose sum-type sibling is the union: the type is the concept, each field a relation to another concept.

## config

A frozen `BaseSettings` model, the only structure that reads environment values. Every field is a declared scalar or secret type, and it is constructed once by the composition root and injected.

## consistency model

The single unfrozen `BaseModel` of a context, the one node where live clients and mutable state converge. Every state it holds is a proven fact, and state evolution is a field re-pointing to a newer proven value.

## contract model

A frozen `BaseModel` of this program's own API request or reply, composed of declared types in this program's vocabulary. No alias to another system's key appears on it.

## derivation

A fact that is a pure function of a frozen value's already-proven fields, written on the model that owns them. It takes only `self`, its body is one returned expression, and it returns a declared type, model, or union. The same fields yield the same fact every time, because the value they compose never changes.

## foreign model

A frozen `BaseModel` of another system's data shape, named for the other system's thing: its aliases hold that system's keys, and its fields are this program's domain meanings. It exists only when the foreign shape differs from the domain shape, and it carries every field the program uses from the foreign data.

## ordered union

`Annotated[A | B, Field(union_mode="left_to_right")]` over variants in attempt order, for foreign data that carries no identity and is expected sometimes to fail or to say no. The stronger construction is attempted first, the failure variant is last and composes from the input itself, and construction selects the case.

## route

The function at transport ingress. It constructs a contract model or foreign model from raw transport data, unwraps transport wrapper structure, dispatches the value the verb consumes, and serializes the reply. It defines no types and computes no domain fact.

## semantic scalar

A frozen `RootModel[P]` over one primitive or one closed value space, carrying a `Field(...)` constraint or a docstring stating why the open range is the domain fact. The atomic domain value: it references no domain type.

## union

A closed set of two or more frozen variants over one domain axis, the axis a `StrEnum`, each variant pinning exactly one member with a defaulted `kind: Literal[Axis.MEMBER]` field. The structural form of a choice: a decision with consequences is a union of result variants, and identity-carrying data constructs it through the discriminator on its alias.

## value object

A frozen `BaseModel` composing scalars into a small value with no identity, equal by value: a measurement, a description, an amount. The composition layer between the semantic scalar and the concept model.

## verb

A state-transition method on the consistency model. Its parameter is the innermost constructed value it consumes; its body contains at most one construction statement, with constituents constructing inside that call; it may capture a foreign reply before the construction, re-point a state field to the constructed fact, and emit the constructed fact through a client field.

## existing (not a construct)

A reference to a type that already exists, built in an earlier pass, defined in another context, or given. It carries the name and the file where the type already lives, builds nothing, and expands to no source. It is the reference device that lets a row name a type the current pass does not build, never a sixteenth construct.
