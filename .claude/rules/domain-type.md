---
paths:
  - "**/domain/**/type.py"
---

# type.py — Scalars

The dependency root. Imports nothing from the program.

**Shape:**
```python
class Money(RootModel[Decimal], frozen=True):
    root: Decimal = Field(gt=0)

class Sku(RootModel[str], frozen=True):
    root: str = Field(min_length=1)
```

**Contains:** `RootModel` subclasses with `frozen=True` and `Field()` constraints. Each scalar owns a single value with identity and semantic distinction.
**Imports from:** Standard library and third-party only. Never from the program.
**Imported by:** Everything in this context and peer contexts.
