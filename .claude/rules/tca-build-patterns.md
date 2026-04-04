# TCA Build Patterns

Build in TCA by moving from vocabulary to proof graph, not from procedure to helper layers.

## Preferred construction moves

Reach for these moves before free procedure:

1. name domain scalars first with `RootModel` or focused `BaseModel`
2. let fields declare their own constraints with `Field(...)` and `Annotated`
3. mirror the foreign schema with aliases and boundary `BaseModel` fields
4. absorb outer wrappers on that same boundary with `model_validator(mode="before")` only when irreducible
5. capture live input and hand it to `model_validate` or `model_validate_json` immediately
6. lift foreign truth into owned domain truth with `model_validate`, aliases, and `from_attributes`
7. compose proven models into richer semantic worlds by owning them as fields
8. let one model read another model's declared surface with `from_attributes`
9. derive intrinsic facts on the model that owns the proof with `@computed_field`, `@cached_property`, or `@property`
10. declare cases instead of branching with enums, `Literal`, and `Field(discriminator=...)`
11. continue by shape when a case contains more of its own world through recursive products or discriminated unions
12. let proven construction trigger further proven construction through projection plus `model_validate`
13. render the final surface from owned truth with projection and declarative output models

## What to prefer

- domain wrappers and focused product types over bare primitives
- `Field(...)`, `Annotated`, aliases, constrained types, enums, `Literal`, and discriminated unions over helper code
- `from_attributes`, `model_validate`, and `model_validate_json` over adapter layers
- composition and projection over service logic
- `model_validator(mode="before")` or `mode="wrap"` only for irreducible seams, not as a generic normalization layer
- `model_validator(mode="after")` only for integrity that truly belongs after construction, not as a procedural backfill
- tiny seams that capture or normalize once, then get back to construction immediately

## What to remove

Flag these procedural substitutes:

- translators and mapper classes
- DTO reshaping layers
- branchy tag dispatch in services or helpers
- temporary dict payloads between named types
- inline derivations outside the model that owns the fields
- `field_validator` or `model_validator` used where `Field(...)`, aliases, `from_attributes`, discriminated unions, or projection should solve it
