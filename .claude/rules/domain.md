---
paths:
  - "**/domain/**"
---

# Domain — Where The Program Lives

Every file in `domain/` is named for a domain concept: `product.py`, `cart.py`, `order.py`, `promotion.py`. Never for a technology pattern: `store.py`, `repository.py`, `handler.py`, `controller.py`, `manager.py`, `utils.py`.

**Frozen domain models:**
```python
class CartSnapshot(BaseModel, frozen=True, from_attributes=True):
    subtotal: Money
    item_count: Quantity

    @cached_property
    def per_item_average(self) -> Money:
        # Derivation belongs on the model that owns the proven fields
```

All models are `frozen=True` except the single active model per context. The active model is named for its domain concept (`cart.py`, `checkout.py`), is the convergence point that composes all layers below it, and is the one place where unfrozen is earned — not granted for convenience.

Fields are domain scalars from `type.py`, not bare `str`, `int`, `float`, or `Decimal`. Derivations live on the model as `@cached_property`, `@computed_field`, or `@property`. Discriminated unions with `Literal` fields replace `if/elif` classification. `model_validate` replaces mapper/translator/adapter classes. Construction cascades via `@cached_property` calling `model_validate` replace coordinator services.

Types flow outward: domain defines, edge imports. Domain never imports from services, routes, or infrastructure.
