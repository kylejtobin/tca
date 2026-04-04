---
name: tca-design-review
description: Review a design or code path through a TCA lens. Use when the user asks for architecture review, refactor direction, whether something is good TCA, or shows service, mapper, helper, or validator-heavy code.
---

Use this skill when the task is to identify where semantics escaped from types into enterprise procedure.

## Outcome

Return the strongest structural findings first.

Focus on:

1. where procedure is doing work that types should own
2. where uncertainty is unmodeled
3. where boundaries leak foreign shape
4. where seams are too fat
5. where domain meaning was flattened into generic primitives or containers
6. where Pydantic surfaces are missing, misused, or playing the wrong role

## Method

1. Identify the semantic center of the design.
2. If it is a service, helper, coordinator, or outer shell, explain whether semantics drifted there from the type tree.
3. Look for dominant enterprise failure shapes, not toy mistakes.
4. Audit the Pydantic surface directly:
   - missing `RootModel` or focused `BaseModel`
   - missing `Field(...)`, `Annotated`, aliases, or `from_attributes`
   - missing `Literal` or `Field(discriminator=...)`
   - external derivation that should be `@computed_field`, `@cached_property`, or `@property`
   - misuse of `field_validator` or `model_validator(mode="before" | "wrap" | "after")`
5. Name the strongest TCA replacement move:
   - stronger domain type
   - boundary model with aliases or `from_attributes`
   - declarative field constraint with `Field(...)` or `Annotated`
   - enum or discriminated union with `Literal` and `Field(discriminator=...)`
   - composition through owned fields
   - projection through `@computed_field`, `@cached_property`, or `@property`
   - irreducible seam reduction
6. Prefer a few important structural findings over a long style list.

## Review standard

Do not recommend:

- casts
- suppressions
- generic "clean this up" advice
- more controller or service layering

Recommend more modeling, sharper ownership, and typed possibility spaces instead.
