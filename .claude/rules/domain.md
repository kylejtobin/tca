---
paths:
  - "**/domain/**"
---

# Domain — Where The Program Lives

Every file in `domain/` is named for a domain concept: `product.py`, `order.py`, `inventory.py`, `customer.py`. Never for a technology pattern: `store.py`, `repository.py`, `handler.py`, `controller.py`, `manager.py`, `utils.py`.

**Frozen domain models:**
```python
class Smell(BaseModel, frozen=True):
    invariant_name: InvariantName
    message: Message
    location: SourceLocation

    @cached_property
    def rendered(self) -> str:
        return f"{self.invariant_name.root}: {self.message.root} ({self.location.qualified})"
```

All models are `frozen=True` except the single active model per context. The active model is named for its domain concept (`catalog.py`, `cart.py`), is the convergence point that composes all layers below it, and is the one place where unfrozen is earned — not granted for convenience.

**The TCA decorator stack** for derivations that must serialize: `@computed_field` + `@cached_property`. `@computed_field` makes it visible to `model_dump()`/`model_dump_json()`. `@cached_property` caches the result and uses Pydantic's frozen bypass to write to `__dict__`. Never `@computed_field` + `@property` on frozen models — that recomputes every access.

Fields are domain scalars from `type.py`, not bare `str`, `int`, `float`, or `Decimal`. Discriminated unions with `Literal` fields replace `if/elif` classification. `model_validate` replaces mapper/translator/adapter classes. `model_validate_json(raw_bytes)` absorbs foreign JSON in a single pass — no `json.loads()`. Construction cascades via `@cached_property` calling `model_validate` replace coordinator services.

Types flow outward: domain defines, edge imports. Domain never imports from services, routes, or infrastructure.
