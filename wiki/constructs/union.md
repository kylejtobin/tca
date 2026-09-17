---
type: Construct
description: A closed sum of alternatives on one semantic axis, each carrying its own facts.
---

# Union

## Definition

One closed semantic axis whose alternatives carry different valid facts or behavior. Construction selects the variant; nothing after construction selects again.

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

- Each variant is a frozen model containing only the facts valid for that case.
- Refinement is for a child substitutable for one parent without changing inherited behavior; a union is for alternatives that own distinct facts or behavior. Is-a is an implication and either-or is a disjunction; one structure for both fuses them.
- The alias is the union's single declared form.
- Behavior that varies by case is a same-named derivation on each variant, following the closed [transformation](./transformation.md) algebra, consumed directly from the union value. The static checker requires every variant to define it.
- A `Literal` discriminator is added only when that identity is actual domain or interchange data. In memory the class proves identity and a pin duplicates it; on a wire the class is erased and identical-payload variants collapse, so where the value crosses a wire identity is data.
- `TypeAdapter` constructs the bare alias from raw input.

## Forbidden

- `bool` returned when either answer carries facts
- a discriminator added solely to recover Python class identity
- independent axes combined in one union
- `None`, `Optional`, or a nullable field; meaningful absence is a named constructed variant
- variants selected in an unrelated route or interpreter
- construction failure caught and called a refusal variant
- `match`, `isinstance`, class or discriminator comparisons, ternaries, or dispatch dictionaries choosing domain behavior
