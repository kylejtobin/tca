---
type: Reference
description: Construction is the proof; there is no validation stage, and the dependency graph determines order.
---

# Construction Rules

## Proof

A semantic value exists only after its Pydantic constructor has established every declared field and invariant. Construction failure means no value of that type exists. A domain refusal is a constructed union variant, never a `ValidationError` reinterpreted as a result.

## Required Form

- Construct the outer meaning once; raw nested input constructs every constituent, and an existing immutable model instance is accepted as prior construction proof.
- Type every semantic field as a declared construct or its declared `StrEnum`, `Literal`, `SecretStr`, union-alias, or tuple substrate form.
- Use the exact configuration assigned to the construct category on [substrate-claims](./substrate-claims.md).
- Use recursively immutable constituents: frozen models, tuples, and frozen scalar roots.
- Give every default a declared omission meaning and validate it.
- Represent meaningful absence with a named constructed union variant, never `None`, `Optional`, or `T | None`. A default supplies a complete value only when omission means that value; it is not an absence sentinel.
- Construct a new complete fact from existing facts; never mutate, patch, partially copy, or maintain a replaceable current-state slot for a completed value.

## Construction, Not Validation

There is no program-owned validation stage or validator construct. Pydantic's constructor establishes the declared shape through field constraints, nested construction, unions, and structural reparameterization. Its API spelling `model_validate` does not introduce a second architectural operation.

Model the independent facts and derive their consequences. A bid and a nonnegative spread determine an ask; storing an independent ask and then checking its ordering creates the wrong representation. A program-owned custom validator, including a rejecting one, does not repair that representation and is not admitted: a validator body is procedure, so an invariant held there is the escaped break even though construction enforces it. An invariant with no structural form is a reported construction gap, never free code. Acyclicity of a hierarchy is structural when the hierarchy is nested rather than stored as an edge list, because a frozen value cannot contain itself.

## Forbidden

- `model_construct`, `PrivateAttr`, undeclared instance state, `object.__setattr__`, or overriding any inherited semantic declaration
- `model_copy(update=...)`
- `Any`, `JsonValue`, `Json`, `SkipValidation`, untyped dictionaries, or mutable containers on semantic edges
- checking an invariant again after its type constructed
- storing raw, partial, failed, or foreign input past its boundary
- constructing a constituent in a separate structure when the outer annotation owns that edge
- storing a value derivable from authoritative fields
- semantic `None`, `Optional`, nullable unions, or sentinel defaults
- domain branching or orchestration hidden inside a model method or property
- program-owned `field_validator`, `model_validator`, `BeforeValidator`, `AfterValidator`, `WrapValidator`, or `PlainValidator`
- custom `__init__`, `model_post_init`, or schema hooks used to perform domain work during construction
- free domain functions, mutable consistency holders, or a runner sequencing constructions; the only admitted free function is the one-expression framework callback at the [composition-root site](./composition-root.md)
- a test that restates a constraint the type already carries; construction is the proof, and a second statement of the same constraint is the duplicated break
