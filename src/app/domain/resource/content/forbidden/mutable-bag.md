---
name: tca_forbidden_pattern_mutable_bag
description: The mutable-bag anti-pattern. A bare `list`/`set`/`dict` field, an unconstrained container that proves nothing. Read this while building a collection to see the frozen collection that does.
---

## Mutable bag

A bare `list`, `set`, or `dict` field is unproven and mutable: nothing guarantees its contents are valid, and it can change after the value is built.

A sequence that is itself a domain thing, with its own name, constraint, or derivation, is a frozen `RootModel[tuple[T, ...]]`, constructed whole in one expression. A namespace whose key-uniqueness is the domain fact is a frozen `RootModel[dict[K, V]]` paired with a query model returning a found-or-missing union. A sequence with no meaning of its own is a `tuple[T, ...]` field on the model, not a bare container.

```python
class Book(BaseModel):
    bids: list[Level]   # not a constructed Collection: a frozen RootModel[tuple[Level, ...]] whose contents are proven and cannot change after build
```
