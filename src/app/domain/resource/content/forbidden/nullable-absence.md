---
name: tca_forbidden_pattern_nullable_absence
description: The nullable-absence anti-pattern. A `T | None` field fuses absence into a slot and names neither state. Read this while building a concept model or union to see the variant or split that carries absence as a fact.
---

## Nullable absence

A `T | None` field models absence as a slot modifier instead of a state. "Missing" is a real fact about which world the value is in, and fusing it into one field forces every reader to branch and names neither state.

"May be missing" is never a field. Absence that means something is a union variant named for what absence means, or separate models when absence changes the state shape. When constructing from foreign data, an omitted key resolves to a default that states what omission means, or a variant when omission means a different fact; bare `None` never crosses into the domain.

```python
class Order(BaseModel):
    settled_at: datetime | None   # two states crammed into one field: split into a Settled variant carrying the timestamp and an Unsettled variant carrying none
```
