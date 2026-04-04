# TCA Review

When reviewing code, plans, or architecture, prioritize structural drift over style.

## Primary review questions

- where did semantics escape from the type tree?
- where is uncertainty still unmodeled?
- where is foreign shape leaking past the boundary?
- where did a seam become larger than irreducible?
- where did naming, field shape, or surface precision weaken the program?

## Dominant failure shapes

Look for real enterprise drift, not toy mistakes:

- services or helpers computing what models should derive
- adapters, converters, and translators between types that should wire directly
- tag branching that should be enum or discriminated union dispatch via `Literal` and `Field(discriminator=...)`
- temporary dict staging areas between named models
- `field_validator` or `model_validator(mode="before" | "wrap" | "after")` doing work that `Field(...)`, `Annotated`, aliases, `from_attributes`, or projection should own
- stringly statuses or flags where a possibility space should be typed

## Fix standard

Prefer these repairs:

- build the missing `RootModel` or focused `BaseModel`
- fix the ownership with aliases, `from_attributes`, or projection
- model the boundary with declarative fields and only the smallest justified validator seam
- tighten the semantic surface with domain names, `Literal`, enums, and discriminated unions

Do not recommend casts, suppressions, or weaker typing.
