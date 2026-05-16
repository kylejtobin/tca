---
paths:
  - "**/domain/**/value.py"
---

# value.py — Value Objects

The second dependency layer. Composes scalars into richer proven structures.

**Shape:**
```python
class SourceLocation(BaseModel, frozen=True):
    line: LineNumber
    class_name: ClassName | None = None
    method_name: MethodName | None = None
```

**Contains:** `BaseModel` subclasses with `frozen=True` composing scalars from `type.py`.
**Imports from:** `type.py` in this context only. Nothing else from the program.
