---
paths:
  - "**/domain/foreign/**"
---

# foreign — Boundary Mirror Models

Foreign models mirror the shapes that external systems emit and accept — REST responses, websocket frames, message payloads, file formats. They are the proven absorption surface — what raw bytes become before they lift into domain truth.

**Shape:**
```python
class ExternalEditUpdate(BaseModel, frozen=True):
    edit_id: EditId = Field(alias="id")
    target_path: FilePath = Field(alias="path")
    occurred_at: EventTimestamp = Field(alias="ts")
```

**Contains:** Frozen `BaseModel` subclasses mirroring foreign shapes. Each foreign model uses `Field(alias="foreign_key")` for every key whose foreign name differs from the domain-aligned attribute name. Discriminated unions for multi-channel envelopes use `Annotated[A | B | C, Field(discriminator="...")]` with the foreign discriminator field's name.

**Imports from:** Domain scalars from `**/domain/<context>/type.py` and value objects from `**/domain/<context>/value.py`. Standard library, third-party. Never from `service/`, `api/`, or layers above the domain.

**Imported by:** The active model's absorption method — the only place `model_validate_json(raw_bytes)` is called on a foreign-model class. The active model's startup-seeding code is the only place foreign REST response models are constructed.

**Directory shape:**
- One external system per subdirectory. `**/domain/foreign/<system_a>/`, `**/domain/foreign/<system_b>/`, etc.
- One file per channel, endpoint, or message family within a subdirectory.

**Hard rules:**
- `Field(alias=...)` translation lives ONLY here. Domain models never carry foreign aliases.
- Foreign models lift INTO domain types via `model_validate(foreign_instance)` with `from_attributes=True` on the domain side. The lift happens ONLY in the active model.
- No frozen domain event carries a foreign-model field. The projection from active model to frozen domain event drops foreign shape entirely.
- `model_validate_json(raw_bytes)` is the only JSON-absorption call. `json.loads` followed by `model_validate` has no home here or anywhere else in the codebase.
- One external system per subdirectory. One file per channel within a subdirectory.
- `TypeAdapter` has no home. The TCA shape for "absorb bytes into a discriminated variant" is a frozen `RootModel[DU]` envelope.
