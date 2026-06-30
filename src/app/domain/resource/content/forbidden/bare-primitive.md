---
name: tca_forbidden_pattern_bare_primitive
description: The bare-primitive anti-pattern. A primitive field names a domain quantity while keeping none of its constraint. Read this while building a semantic scalar to see why the constraint scatters out of the type, and the frozen scalar that keeps it.
---

## Bare primitive

A primitive field names a domain quantity but keeps none of its constraint; the constraint then scatters into checks instead of living in the type.

The atomic domain value is a frozen `RootModel[P]` over one allowed primitive (`str`, `int`, `float`, `Decimal`, `bool`, `bytes`, `date`), carrying a `Field(...)` constraint, or a docstring stating why the open range is the domain fact. The field is typed as that scalar, never the primitive; a raw value passed where the scalar field stands constructs the scalar inside the composite's own call.

```python
class Account(BaseModel):
    email: str   # "email" is a claim the type doesn't keep: type the field as a frozen RootModel[str] scalar carrying the email constraint on its Field
```
