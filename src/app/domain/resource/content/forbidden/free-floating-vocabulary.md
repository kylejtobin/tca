---
name: tca_forbidden_pattern_free_floating_vocabulary
description: The free-floating-vocabulary anti-pattern. A raw `Literal[...]` or a standalone enum used as a field, where nothing single proves membership. Read this while building a semantic scalar to see the scalar that owns the value space.
---

## Free-floating vocabulary

A closed value-space with no scalar that owns it: a raw `Literal[...]` string used as a field, or a `StrEnum` used directly as a field type. Nothing single proves membership.

A closed vocabulary is a frozen `RootModel` over a `StrEnum` or `Literal` value space; the `StrEnum` is the value space, the role a `gt=0` plays for a number. The field is then typed as that scalar, which proves membership on construction.

```python
status: Literal["open", "filled", "canceled"]   # label bag, no owner: a StrEnum value space wrapped in a frozen RootModel scalar
ctx: BoundedContext                              # enum as field, no scalar: wrap BoundedContext in a frozen RootModel and type the field as that scalar
```
