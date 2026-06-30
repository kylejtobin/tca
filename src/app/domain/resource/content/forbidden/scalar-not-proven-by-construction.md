---
name: tca_forbidden_pattern_scalar_not_proven_by_construction
description: The unproven-scalar anti-pattern. A scalar declared as a plain class proves nothing when built. Read this while building a semantic scalar to see the frozen `RootModel` that makes the invalid value unconstructable.
---

## Scalar not proven by construction

A semantic scalar declared as a plain class or typedef proves nothing when built. Only a frozen `RootModel` carrying its constraint on the `root` field makes the invalid value unconstructable.

The required form is `class X(RootModel[P], frozen=True)` over one allowed primitive, with the domain bound on `root`'s `Field(...)`, or a docstring stating why the open range is the domain fact when the value is unconstrained.

```python
class Price(BaseModel):
    value: Decimal   # vs RootModel[Decimal], frozen, root: Decimal = Field(gt=0): then a non-positive price cannot be constructed at all
```
