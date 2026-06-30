---
name: tca_forbidden_pattern_union_alias_built_wrong
description: The mis-built-union-alias anti-pattern. A union alias whose selection is not provable. Read this while building a union or ordered union to see the missing `Annotated`, discriminator, or ordered-union machinery, and the alias forms that make selection construct.
---

## Union alias built wrong

The choice is declared without making selection provable: no `Annotated`, variants that do not match the model, a missing discriminator, or for an ordered union a missing `union_mode="left_to_right"`, wrong variant order, or no `TypeAdapter` constructor. Selection then leans on inference.

Identity-carrying data renders `Annotated[A | B, Field(discriminator="kind")]`, each variant pinning its `kind` member, so the checker narrows through the discriminator. Foreign data expected to fail renders `Annotated[A | B, Field(union_mode="left_to_right")]` with variants in attempt order, the failure variant last, and a `TypeAdapter` constant named for the alias.

```python
SignalUnion = A | B   # no Annotated, no discriminator: SignalUnion = Annotated[A | B, Field(discriminator="kind")] with each variant pinning kind
```
