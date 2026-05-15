---
paths:
  - "**/domain/**/value.py"
---

# value.py — Value Objects

The second dependency layer. Composes scalars into richer proven structures.

**Shape:**
```python
class LineItem(BaseModel, frozen=True):
    sku: Sku
    unit_price: Money
    quantity: Quantity
```

**Contains:** `BaseModel` subclasses with `frozen=True` composing scalars from `type.py`.
**Imports from:** `type.py` in this context only. Nothing else from the program.
