# Pydantic Machinery for Type Construction Architecture

This document maps Pydantic v2's internal mechanisms to the TCA patterns they enable. Every mechanism here is load-bearing — it is the *implementation* of a TCA concept, not a convenience wrapper. If you do not know the precise behavior of these mechanisms, you will write procedural code that looks like TCA but computes differently.

---

## Frozen Models and `@cached_property`: The Construction Compute Engine

### The mechanism

Pydantic v2 frozen models raise `ValidationError` on attribute assignment. But `@cached_property` is explicitly exempted. In the Pydantic source (`_model_construction.py`), `_setattr_handler` checks `isinstance(attr, cached_property)` **before** calling `_check_frozen()`. The first access to a `@cached_property` writes the result to `__dict__` via `model.__dict__.__setitem__(name, val)`. Subsequent accesses return the cached value directly — the descriptor protocol finds it in `__dict__` and never calls `__get__` again.

The same bypass exists in `__delattr__`: deleting a `@cached_property` clears the cached value without triggering the frozen check, allowing recomputation on next access.

### What this means for TCA

A frozen model is a construction compute engine, not just a data container. Stored fields are sealed inputs — the proven facts from construction. `@cached_property` derivations are lazy materializations of intrinsic facts that were *determined* at construction even though their computation is deferred.

The write to `__dict__` is not mutation. The model's semantic state was fixed when it was constructed. The `@cached_property` write materializes what was already true.

### The correct decorator stack

```python
class TreeReport(BaseModel, frozen=True, from_attributes=True):
    reports: tuple[FieldReport, ...] = Field(alias="fields")

    @computed_field
    @cached_property
    def text(self) -> str:
        def _indent(report: FieldReport, depth: int) -> tuple[str, ...]:
            prefix = "  " * depth
            return (
                f"{prefix}{report.line}",
                *(line for child in report.children for line in _indent(child, depth + 1)),
            )
        return "\n".join(line for r in self.reports for line in _indent(r, 0))
```

`@computed_field` declares the derivation to Pydantic's serialization layer — it appears in `model_dump()`, `model_dump_json()`, and JSON Schema. `@cached_property` provides the caching and the frozen bypass. Together they make the derivation a first-class part of the model: proven, cached, serialized.

### What goes wrong without this

| Wrong pattern | What happens |
|:---|:---|
| `@computed_field` + `@property` | Recomputes on every access. No caching, no frozen bypass needed. Functionally different — the value is not materialized, it is recalculated. For expensive derivations (recursive tree walks, cascaded constructions), this changes performance characteristics and makes access-order-dependent timing visible. |
| Plain `@cached_property` without `@computed_field` | Caches correctly but is invisible to serialization. `model_dump()` excludes it. Events written to the store lose the derivation. The event store is the source of truth — if the derivation is not serialized, it does not exist in the truth. |
| Standalone function computing from model fields | The derivation escaped the model. It computes the same value but is not owned, not cached on the model, and not serialized with it. |

---

## `model_validate_json(raw_bytes)`: Pydantic IS the JSON Parser

### The mechanism

`model_validate_json(raw_bytes)` accepts `bytes` or `str` and deserializes JSON directly into the model. Pydantic delegates to its Rust core (`pydantic-core`) which handles JSON parsing and validation in a single pass. There is no intermediate Python dict.

### What this means for TCA

At every boundary where data arrives as JSON (websocket messages, REST responses, file reads), a single call absorbs the raw bytes:

```python
event = HookEvent.model_validate_json(raw_bytes)
```

No `json.loads()`. No intermediate dict. No dict-to-model conversion. The foreign boundary model with `Field(alias=...)` IS the complete adapter — it declares the field name translation, absorbs the foreign shape, and validates in one construction.

### What goes wrong without this

`json.loads()` + `model_validate()` is two passes: Python's JSON decoder produces a dict, then Pydantic validates the dict. The intermediate dict is untyped, unowned truth passing through the program. Every time you see `json.loads` followed by model construction, a parsing seam was introduced that `model_validate_json` eliminates.

---

## `Field(alias=...)`: Declarative Boundary Translation

### The mechanism

`Field(alias="foreign_name")` tells Pydantic to read the value from the aliased key during construction from dicts or JSON. The model's Python attribute name is the domain name. The alias is the foreign name. Pydantic resolves the mapping during validation — no renaming code, no dict comprehension, no adapter class.

With `model_validate_json`, aliases resolve during the Rust-level JSON parse. The foreign key name never appears as a Python string at runtime.

### What this means for TCA

Foreign boundary models (mirrors of external API shapes) use aliases to declare the field name translation:

```python
class FieldEntry(BaseModel, frozen=True, from_attributes=True):
    field_name: str
    shape: AnnotationShape = Field(alias="annotation")
    # 'shape' is the domain name; 'annotation' is the source attribute on FieldSlot
```

The domain names the field. The alias maps the foreign key. No mapper class, no renaming function, no intermediate dict with renamed keys. The translation is declared on the type and executed by construction.

---

## `from_attributes=True` and `model_validate`: The Lifting Pattern

### The mechanism

`ConfigDict(from_attributes=True)` tells Pydantic to use `getattr()` to read field values from the source object during `model_validate()`. This is significant: `getattr()` triggers Python's descriptor protocol. If the source model has `@property` or `@cached_property` derivations, they fire during the `getattr` call.

### What this means for TCA

A domain model can absorb another model's proven fields AND its derivations:

```python
class FieldEntry(BaseModel, frozen=True, from_attributes=True):
    field_name: str
    shape: AnnotationShape = Field(alias="annotation")
    # reads FieldSlot.annotation (the TypeAnnotation wrapper)
    # the DU is constructed from TypeAnnotation.kind, which is a @property

entry = FieldEntry.model_validate(field_slot)
```

`model_validate` reads `field_slot.annotation`, which is a `TypeAnnotation` wrapper. The `AnnotationShape` discriminated union routes on `TypeAnnotation.kind` — a `@property`. The property fires during `getattr`, the DU selects the variant, and construction continues. The descriptor protocol is the mechanism — properties on the source feed construction on the destination.

### What goes wrong without this

Without `from_attributes=True`, you either `model_dump()` the source — introducing an intermediate dict where owned truth temporarily becomes untyped keys — or you write a function that reads attributes and builds a dict, which is an escaped adapter. `model_validate(proven_model)` with `from_attributes=True` keeps the transfer model-to-model: no dict, no adapter, construction does the work.

---

## Discriminated Unions: O(1) Structural Dispatch

### The mechanism

`Annotated[A | B | C, Field(discriminator="status")]` with a `Literal` discriminator field on each variant creates O(1) dispatch. Pydantic reads the discriminator value, looks it up in a precomputed mapping, and validates against exactly one variant. No trial-and-error. No ordering dependency.

This is distinct from Pydantic's `union_mode='smart'` (default for untagged unions) which tries types in order — O(n), ordering-dependent, and ambiguity-prone.

### What this means for TCA

Classification is declared, not computed:

```python
OrderStatusEvent = Annotated[
    OrderAccepted | OrderFilled | OrderPartialFill | OrderCancelled | OrderFailed,
    Field(discriminator="status"),
]
```

The `Literal["accepted"]`, `Literal["filled"]`, etc. on each variant's `status` field is both the type-level classification AND the runtime dispatch key. Construction selects the variant. No `if/elif` chain examines the status string.

### The constraint

Every variant in a discriminated union must have the discriminator field typed as `Literal[value]`. The discriminator values must be unique across variants. If two variants share a discriminator value, Pydantic raises at schema-build time — the conflict is caught at import, not at runtime.

---

## Validator Ordering: The Construction Pipeline

### The mechanism

Pydantic v2's validation fires in a fixed order:

1. **`model_validator(mode='before')`** — receives raw input (dict, object, etc.) before any field validation. Can reshape, unwrap, or reject. Runs outermost-first if multiple are declared.
2. **Field validators** — fire in field definition order. `@field_validator(mode='before')` then coercion then `@field_validator(mode='after')` per field.
3. **`model_validator(mode='after')`** — receives the fully constructed model instance. All fields are validated and set. Can perform cross-field checks.
4. **`model_post_init`** — fires last. The model is fully constructed.

### What this means for TCA

`model_validator(mode='before')` is the envelope unwrapper — it peels transport wrappers to reach the payload before field validation starts. It operates on raw, untyped input.

`model_validator(mode='after')` can enforce cross-field invariants that no single field constraint expresses. The model is already constructed, so `self` is fully populated.

**Doctrinal scope.** The only `mode='after'` shape that survives doctrine review is *impossible variant composition* — composed fields whose individually-valid values cannot coexist as a meaningful state (e.g., `StateTransition(Terminal, ChildAdded)`). Threshold comparisons, configurable limits, "should the system act on this?" — those are business decisions, not data integrity. They belong on an Evaluation Model as a `@computed_field` + `@cached_property` returning a discriminated union (`GateResult = GatePassed | GateRejected`). Construction succeeds; the consumer dispatches on the variant. See `.claude/rules/gate-rubrics.md` and `.claude/skills/proof-design/SKILL.md` for the full classification.

Field validators should be rare in TCA. Most field-level constraints are declared via `Field()` — `gt=0`, `ge=0, le=1`, `min_length=1`. A field validator doing what `Field()` expresses is procedural validation replacing declarative constraint.

---

## `model_construct()`: The Unsafe Escape Hatch

### The mechanism

`model_construct()` creates a model instance with NO validation — no field validators, no model validators, no coercion, no constraint checking. It directly assigns values. The resulting object may violate every constraint the type declares.

### What this means for TCA

Avoid it. A model created via `model_construct()` is not proven. In TCA, "if the object exists, every constraint was satisfied" — but `model_construct()` breaks this guarantee. The object exists but nothing was checked.

The only legitimate use is performance-critical paths where data is already proven (e.g., reconstructing from a trusted store where the constraints were enforced on write). Even then, the proof guarantee is transferred, not eliminated — you must be certain the source is trustworthy.

---

## `model_copy(update=...)`: Copy Without Re-validation

### The mechanism

`model_copy(update={"field": new_value})` creates a shallow copy with updated fields. The update values are NOT re-validated — they bypass field validators and model validators. Constraints declared on the field are not checked for the update values.

### What this means for TCA

On frozen models, `model_copy(update=...)` is the controlled state transition mechanism. But the lack of re-validation means the caller must ensure the update values are already valid. For domain scalars (owned types with constraints), construct the scalar first, then pass it to `model_copy`:

```python
new_peak = Price(Decimal("68500.00"))  # construction proves the value
updated = position.model_copy(update={"trailing_stop_peak": new_peak})
```

Do not pass raw primitives to `model_copy` — they will not be coerced or validated.

---

## Frozen Model Hashing

### The mechanism

`frozen=True` generates `__hash__()` based on the model's stored fields. Computed fields (`@computed_field`) are NOT included in the hash. Two models with identical stored fields but different computed field implementations hash identically.

### What this means for TCA

Frozen models can be used as dict keys and in sets. The hash is stable because stored fields are immutable. But if you rely on computed fields for identity (which you shouldn't — identity lives in the proven facts), hash collisions are possible.

---

## `ConfigDict` Options That Matter

| Option | What it does | TCA relevance |
|:---|:---|:---|
| `frozen=True` | Immutable after construction. Generates `__hash__`. | Every TCA model except the single active model per context. |
| `from_attributes=True` | `model_validate` uses `getattr` on source objects. | Enables the lifting pattern — constructing domain models from foreign models. |
| `populate_by_name=True` | Fields can be set by both alias and Python name. | Useful when foreign boundary models need to be constructed from both JSON (alias) and Python code (name). |
| `strict=True` | Disables type coercion. `int` stays `int`, no silent `str → int`. | Consider for domain models where implicit coercion hides type confusion. |
| `revalidate_instances='never'` (default) | `model_validate` returns model instances as-is without re-validation. | An already-proven model passes through untouched. No redundant work. |
| `ser_json_inf_nan='constants'` | Serializes `Infinity`/`NaN` as JSON strings instead of raising. | Relevant for financial math where division edge cases can produce infinity. |

---

## Summary: The Mechanism-Pattern Map

| Pydantic mechanism | TCA pattern it enables |
|:---|:---|
| `@cached_property` frozen bypass | Lazy derivation on frozen proof objects |
| `@computed_field` + `@cached_property` | Serializable, cached derivation — the TCA decorator stack |
| `model_validate_json(raw_bytes)` | Single-pass JSON absorption at boundaries |
| `Field(alias=...)` | Declarative foreign field translation |
| `from_attributes=True` + `model_validate` | Cross-model truth lifting via descriptor protocol |
| `Literal` + `Field(discriminator=...)` | O(1) structural classification replacing `if/elif` |
| `model_validator(mode='before')` | Envelope unwrapping before field validation |
| `model_validator(mode='after')` | Cross-field invariant enforcement |
| `model_construct()` | Unsafe escape — breaks proof guarantee |
| `model_copy(update=...)` | Frozen state transition without re-validation |
| `frozen=True` + `__hash__` | Immutable, hashable proof objects |
