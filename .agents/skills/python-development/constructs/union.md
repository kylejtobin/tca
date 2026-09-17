---
type: Reference
description: How a closed algebraic sum represents alternatives with variant-specific facts. Read when one semantic axis has multiple valid shapes.
---

# Union

## Use

Use for one closed semantic axis whose alternatives carry different valid facts or behavior.

## Required Form

```python
class Filled(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    fill: Fill


class Refused(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    reason: RefusalReason


OrderOutcome = Filled | Refused
```

- Each variant is a frozen Pydantic model containing only facts valid for that case.
- Use refinement when every child remains substitutable for one parent without changing inherited behavior; use a union when alternatives own distinct facts or behavior.
- The alias is the union's single declared form.
- Put behavior that varies by case on each variant under the same typed derivation name, following the closed [transformation](transformation.md) algebra. These are separate variants, not overrides of an inherited semantic declaration.
- Consume that same-named derivation directly from the union value. Construction selects the variant; the consumer does not contain a second case-selection program.
- Add a `Literal` discriminator only when that identity is actual domain or interchange data.
- Use `TypeAdapter` when raw input must construct the bare alias.

## Do Not

- return `bool` when either answer carries facts
- add a discriminator solely to recover Python class identity
- combine independent axes in one union
- use `None`, `Optional`, or nullable fields; meaningful absence is a named constructed variant
- select variants in an unrelated route or interpreter
- catch construction failure and call it a refusal variant
- use `match`, `isinstance`, class or discriminator comparisons, ternaries, or dispatch dictionaries to choose domain behavior
