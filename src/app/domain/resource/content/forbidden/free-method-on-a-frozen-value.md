---
name: tca_forbidden_pattern_free_method_on_a_frozen_value
description: The free-method anti-pattern. An undecorated method on a frozen value is procedure escaping where a derivation belongs. Read this while building a derivation to see the three decorators a derivation wears.
---

## Free method on a frozen value

A method on an immutable value that is not decorated `@property`, `@cached_property`, or `@computed_field` is procedure escaping where a modeled implied fact belongs.

A fact implied by a frozen value's already-proven fields is a derivation: it takes only `self`, its body is one returned expression, and it returns a declared type, model, or union. `@property` recomputes a cheap fact, `@cached_property` computes a costly or recursive one once, and `@computed_field` above `@cached_property` writes the fact into the contract's serialized shape.

```python
class SignalSnapshot(BaseModel, frozen=True):
    def momentum(self) -> Momentum: ...   # undecorated: a derivation decorated @property or @cached_property, body one returned expression
```
