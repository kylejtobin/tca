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

**Active-model state-mutation methods are public, return `None`, and mutate fields directly.** No private helpers — no `def _foo` underscore-prefixed methods anywhere on a domain model. Private methods are the procedural escape hatch and have no home in TCA. State mutation methods on the active model (`apply(event) -> None`, `absorb(raw_bytes) -> None`, `seed(snapshot) -> None`) directly assign to `self.field` to evolve state. The "frozen models are pure" rule is exempted only on the active model file (detected by an unfrozen `BaseModel` declaration). Frozen models in the same context never carry `-> None` methods.

If a state mutation requires raw-input transformation before field validation, a `model_validator(mode="before")` on the relevant frozen model is the correct shape — not a method on the active model and not a free function. In practice this is rare; foreign-key renames are handled by `Field(alias=...)` on foreign models, not by before-validators.

**Active models are constructed from frozen registries, not runtime lists.** An active model that operates over a finite set of domain values (subjects, channels, instruments, rule identifiers, file globs) receives the enumeration as a frozen registry construct. The active model's signature is `Model(deps..., registry: FrozenRegistry)`. Construction proves the enumeration was complete at the time of binding. A list of opaque string identifiers crossing into an active model's signature is *construction-erases-the-domain* — forge the registry construct.

**The TCA decorator stack** for derivations that must serialize: `@computed_field` + `@cached_property`. `@computed_field` makes it visible to `model_dump()`/`model_dump_json()`. `@cached_property` caches the result and uses Pydantic's frozen bypass to write to `__dict__`. Never `@computed_field` + `@property` on frozen models — that recomputes every access.

**Evaluation Models** (`*Evaluation` suffix) use `@cached_property` alone — no `@computed_field`. They are internal compute substrate, not wire shapes. The wire shape is the *intent* or *event* the derivation yields on its own frozen model. See `.claude/rules/evaluation-model.md`.

Fields are domain scalars from `type.py`, not bare `str`, `int`, `float`, or `Decimal`. Collections of bare primitives — lists of strings, tuples of integers, sets of strings, mappings keyed and valued by primitives — have no home as field types or function parameters either; narrow the element type. Discriminated unions with `Literal` fields replace `if/elif` classification. `model_validate` replaces mapper/translator/adapter classes. `model_validate_json(raw_bytes)` absorbs foreign JSON in a single pass — no `json.loads()`, no `TypeAdapter`. Construction cascades via `@cached_property` calling `model_validate` replace coordinator services.

Types flow outward: domain defines, edge imports. Domain never imports from services, routes, or infrastructure.
