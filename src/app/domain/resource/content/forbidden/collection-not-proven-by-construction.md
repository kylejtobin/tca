---
name: tca_forbidden_pattern_collection_not_proven_by_construction
description: The unproven-collection anti-pattern. A non-`RootModel` sequence field is mutable and proves nothing. Read this while building a collection to see the frozen tuple form that proves it.
---

## Collection not proven by construction

The scalar failure for sequences: an aggregate that is not a frozen `RootModel[tuple[T, ...]]` is mutable and unproven, its contents guaranteed by nothing and free to change after the value is built.

A sequence that is its own domain thing is a frozen `RootModel[tuple[T, ...]]` whose element `T` is a declared type, carrying its bound on `Field(...)`, constructed whole in one expression. A sequence with no name, constraint, or derivation of its own is a plain `tuple[T, ...]` field on a model.

```python
class Trades(BaseModel):
    items: list[Trade]   # a frozen RootModel[tuple[Trade, ...]] proves the contents and forbids mutation after build
```
