---
paths:
  - "tca/**/value.py"
---

# value.py — value objects

A value object is a frozen `BaseModel` (`frozen=True`, `extra="forbid"`) composing scalars
from this context's `type.py` (and other value objects) into a small proven product that is
itself a domain thing. Derived from the Frozen model construct in
`docs/type-construction-architecture.md`: the value object in `value.py` and the full domain
model in a concept file are the same construct at different depths of composition, not two
kinds of thing. `value.py` holds the shallow ones, composed directly from the leaves.

    class BookLevel(BaseModel):
        model_config = ConfigDict(frozen=True, extra="forbid")
        price: Price
        quantity: BookQuantity

**Imports from:** `type.py` in this context, and value objects from peer contexts.
**Contains:** frozen `BaseModel` composites of declared types only.

**The breaks this file forbids:**
- A bare primitive field where a scalar from `type.py` belongs (escaped).
- A stored field derivable from the others (escaped derivation).
- Subclassing a domain type to share fields (use composition of the shared leaf).
