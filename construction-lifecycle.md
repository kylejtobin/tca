# The Construction Lifecycle

## The Complete Active Computation Model

The construction machine has five phases. Each produces or extends the proven,
self-aware object. Field declaration is passive — labeled positions in a
product type. The five phases are where computation happens.

One hook — `model_post_init` — fires after construction but is not a
construction phase. It reacts to the object's existence rather than
producing it. It is documented separately below.

This document describes each phase with pure construction patterns. Every code
example follows the same principles as building_block.py: shape over procedure,
`from_attributes=True` for model-to-model wiring, discriminated unions for
dispatch, and `model_validate` as the sole entry point.

---

## The Pipeline

Data flows through a fixed sequence of phases. Each phase has a precise role.
The ordering is Pydantic's own construction pipeline — we are naming what
already exists.

```
raw data arrives
  → Phase 1: Boundary Transform      (model_validator mode="before", Field(alias=...))
    → Phase 2: Sealed Boundary        (model_validator mode="wrap")
      → Phase 3: Field Construction   (Pydantic parses labeled positions, from_attributes reads)
        → Phase 4: Proof Obligation   (model_validator mode="after")
          → proven, frozen object exists
            → Phase 5: Derived Projection   (computed_field / cached_property, on access)

  After construction:
    → Construction Effect             (model_post_init — reacts to existence, not part of construction)
```

Every phase is optional. A minimal frozen product type uses none of them —
field construction alone produces a valid immutable value. Each phase adds a
specific capability when needed. Most models use only field construction and
maybe one or two phases.

---

## Phase 1: Boundary Transform

**Pydantic hooks**: `@model_validator(mode="before")`, `Field(alias=...)`

**What it is**: Pre-construction reshaping. Operates on raw input and maps it
into the form the constructor accepts. Runs before any field parsing.

**There are two forms**:

**Alias (pure — no code)**: `Field(alias=...)` renames an input attribute to a
domain field name. This is the purest form of Translation — a declaration, not
a function. Pydantic reads the aliased name from the input and maps it to your
field. No validator needed.

```python
class FieldEntry(BaseModel, frozen=True, from_attributes=True):
    # Pydantic reads .annotation from the input object,
    # constructs AnnotationShape from it, stores as shape.
    # One declaration. No code.
    shape: AnnotationShape = Field(alias="annotation")
```

**Before validator (irreducible minimum)**: When the input shape can't be
bridged by alias alone — like pairing a dict key with its value — a before
validator does the minimum reshaping. Type the parameter precisely so the
linter helps you.

```python
class FieldSlot(BaseModel, frozen=True, from_attributes=True, populate_by_name=True):
    field_name: str = Field(alias="name")
    annotation: TypeAnnotation

    @model_validator(mode="before")
    @classmethod
    def _from_tuple(cls, data: tuple[str, FieldInfo]) -> dict[str, object]:
        # dict.items() produces (key, value) tuples.
        # Tuples have positions, not names. This is the ONE place
        # where we bridge position → name. Everything else is construction.
        return {"field_name": data[0], "annotation": data[1].annotation}
```

**Contract**: Output must be dict-like or attribute-bearing. Must not construct models — that is Phase 3's job. A before validator that calls `Model(...)` is doing construction work outside the construction machine.

**When to use alias**: Always try alias first. An input object with an
attribute named differently than a field is bridged by alias with zero code.

**When to use before validator**: When the input shape is fundamentally
different from the model shape (positional → named, nested → flat,
multi-source → single object). Keep it minimal. Type the parameter.

---

## Phase 2: Sealed Boundary

**Pydantic hook**: `@model_validator(mode="wrap")`

**What it is**: Construction interceptor. Receives raw input AND the inner
constructor as a handler. Controls whether and how construction proceeds.
Maximum control over the construction pipeline.

**Two uses**:

**Sealing base types**: Only concrete variants construct, never the abstract
base. The wrap validator intercepts before field construction — no wasted work
parsing fields for a type that shouldn't exist.

```python
class Logic(BaseModel, frozen=True, from_attributes=True):
    @model_validator(mode="wrap")
    @classmethod
    def _seal(cls, data: object, handler: Callable[..., Logic]) -> Logic:
        result = handler(data)
        if type(result) is Logic:
            raise TypeError("Construct Rule(...) or Judgment(...) directly")
        return result
```

**Reshaping with handler callback**: When a before validator would cause
recursion (returning an instance re-triggers the validator), wrap gives you
the handler to call exactly once. This is how ModelTree bridges `dict.items()`
into the cascade without infinite loops.

```python
class ModelTree(BaseModel, frozen=True, from_attributes=True, populate_by_name=True):
    fields: tuple[ClassifiedNode, ...] = Field(alias="fields")

    @model_validator(mode="wrap")
    @classmethod
    def _reshape(cls, data: type[BaseModel], handler: Callable[..., ModelTree]) -> ModelTree:
        # Wrap, not before. Calling ModelTree(...) inside a before validator
        # re-triggers the validator → infinite recursion.
        # handler() calls Pydantic's normal validation exactly once.
        return handler({
            "fields": tuple(
                FieldSlot.model_validate(item)
                for item in data.model_fields.items()
            )
        })
```

**Contract**: The handler must be called exactly once or not at all. Wrap must not re-enter construction except through the handler. If the handler is not called, no object is produced — the wrap validator has vetoed construction.

**When to use**: Sealing abstract bases. Reshaping input when before would
recurse. Any case where you need to control WHETHER construction happens,
not just transform the input.

---

## Phase 3: Field Construction

**Pydantic mechanism**: Type annotations + `from_attributes=True`

**What it is**: Pydantic reads the model's field declarations and constructs
each field from the input data. This is the core of nested construction —
each field type IS a construction instruction. Pydantic descends the tree.

This is NOT a hook you write. It's what Pydantic does automatically when
your field types and `from_attributes=True` are set up correctly. Your job
is to declare the right field types so Pydantic can do the work.

**The key mechanisms**:

**from_attributes=True**: Pydantic reads attributes from the input object by
name — matching your field names (or aliases) to the input's attributes.
Properties count. This is how models read from other models.

```python
class ClassifiedNode(FieldEntry, frozen=True, from_attributes=True):
    # When Pydantic constructs a ClassifiedNode from a FieldSlot:
    #   field_name ← reads FieldSlot.field_name (attribute)
    #   shape ← reads FieldSlot.annotation (via alias), constructs AnnotationShape
    # No code. The field declarations ARE the wiring.
    pass
```

**Type coercion**: Pydantic coerces input values to match field types.
Pass a raw annotation object where TypeAnnotation is expected — Pydantic
wraps it. Pass a dict where a BaseModel is expected — Pydantic constructs it.

```python
class FieldSlot(BaseModel, frozen=True, from_attributes=True):
    annotation: TypeAnnotation  # raw annotation → TypeAnnotation automatically
```

**Discriminated union routing**: When a field is a discriminated union,
Pydantic reads the tag field and routes to the correct variant. The
variant's stored fields ARE the answer — no computation needed.

```python
# TypeAnnotation exposes .kind as a property.
# Pydantic reads .kind via from_attributes, routes the DU.
# DirectAnnotation has nullable=Literal[False], collection=Literal[False].
# OptionalAnnotation has nullable=Literal[True].
# The SHAPE is the answer. Dispatch replaces computation.
AnnotationShape = Annotated[
    DirectAnnotation | OptionalAnnotation | TupleAnnotation | AliasAnnotation,
    Field(discriminator="kind"),
]
```

**Contract**: No user code runs during field construction except properties read by `from_attributes`. Those properties must be pure and terminating — they are participating in construction and must be as trustworthy as stored fields. Construction is structural: Pydantic does the work, you declare the shape.

**When to focus here**: Always. Field construction is where 90% of the work
happens. Construction that isn't working points to a missing intermediary
model, a smarter alias, or a discriminated union — not a validator.

---

## Phase 4: Proof Obligation

**Pydantic hook**: `@model_validator(mode="after")`

**What it is**: Cross-field invariant gate. Receives the fully-constructed
value with all fields set. Returns `Self` or rejects. A constructor that
returns proves the invariant holds.

**The core principle**: Construction that succeeds IS the proof that all
invariants hold. The existence of the value proves its validity. No separate
"validation step" — construction IS validation.

```python
class Organization(Resource, frozen=True, from_attributes=True):
    @model_validator(mode="after")
    def _validate(self) -> Self:
        # Organization(...) constructing proves every typed reference resolves.
        # The proof is the existence of the object.
        errors = self._detect_collisions() + self._detect_unresolved()
        if errors:
            raise OrganizationInvalidError(errors)
        return self
```

**Contract**: May only reject (raise) or return `Self`. Must be total and side-effect free — no I/O, no external state, no ambient dependencies. A proof obligation that reads a database or checks a global flag has smuggled a dependency into the proof.

**When to use**: Cross-field invariants that field types alone cannot express.
Reference resolution (field A's value must exist in collection B). Mutual
exclusion. Graph integrity. A single field type that can express the
constraint is always a stronger proof — it fires at field construction,
not after.

---

## Phase 5: Derived Projection

**Pydantic hooks**: `@computed_field` + `@cached_property`, or bare `@cached_property`

**What it is**: Pure function of frozen fields. Computed once on first access,
then cached. Not computed at construction time — materialized on demand.

**The core principle**: A derived projection is referentially transparent. The
frozen product's fields never change, so the projection is a pure function
with a stable result. It is a view of the product, not stored state.

**Two forms**:

**`@computed_field` + `@cached_property`** — derived, cached, AND serialized.
Appears in `model_dump()` and JSON output. Use when the projection is part of
the model's public contract.

```python
class FieldReport(BaseModel, frozen=True, from_attributes=True):
    field_name: str
    block: Block
    nullable: bool
    collection: bool

    @computed_field
    @cached_property
    def line(self) -> str:
        # Derived from stored fields. Computed once. Cached. Serializable.
        # This IS the rendering — no format_output() function needed.
        return f"{self.field_name}: {self.block.value} ..."
```

**Bare `@cached_property`** — derived and cached, but NOT serialized. Use for
in-memory projections like indexes that are expensive to recompute but
shouldn't appear in JSON output.

```python
class Organization(Resource, frozen=True, from_attributes=True):
    @cached_property
    def _team_index(self) -> TeamIndex:
        # Derived projection — O(1) typed retrieval.
        # Not serialized — the canonical state is the collection, not the index.
        return TeamIndex.model_validate(self.teams)
```

Note: the index projection constructs a typed model (`TeamIndex`), not a raw
dict. Even projections are models. A bare dict is unproven data.

**`@property` (no caching)** — for trivial derivations where caching adds no
value. Delegation properties that read from a nested model fall here.

```python
class FieldEntry(BaseModel, frozen=True, from_attributes=True):
    shape: AnnotationShape = Field(alias="annotation")

    @property
    def nullable(self) -> bool:
        # Trivial delegation. No caching needed. from_attributes reads this.
        return self.shape.nullable
```

**Contract**: Must be referentially transparent. Caching is observationally irrelevant — a `@cached_property` and an equivalent `@property` must produce the same value. If a projection appears in `model_dump()` (via `@computed_field`), it is part of the model's public API and should be versioned accordingly.

**When to use**: Any derivation from a model's own fields. Calling code that
computes something from a model's fields is a wiring bug — that computation
belongs ON the model as a projection.

---

## Construction Effect: `model_post_init`

**Pydantic hook**: `model_post_init(self, __context: object) -> None`

`model_post_init` is not a construction phase. By the time it fires, the
object is frozen and proven. It does not make the object more proven or more
self-aware. It makes the **world** different — registration, indexing,
notification. Projection extends the object. Effect extends the world.

This is why building_block.py's `Block` enum includes EFFECT as a distinct
building block: a type with `model_post_init` is structurally different from
a plain record. But the difference is in what the type *causes*, not in how
it *constructs*.

```python
class Resource(BaseModel, frozen=True, from_attributes=True):
    _registry_ctx: ClassVar[ContextVar[list[Resource]]]

    def model_post_init(self, __context: object) -> None:
        self._registry_ctx.get().append(self)
```

Construction IS registration. The resource exists, so register it. But the
registration is not part of producing the proven object — it is a consequence
of the proven object existing.

**Contract**: May mutate external state. Must not mutate the model — the object is frozen by the time `model_post_init` fires. Must not be used to "fix" invalid objects — if the object needs fixing, the construction pipeline is incomplete.

**When to use**: Auto-registration on construction. Any side effect that should
happen exactly once when a value is constructed.

---

## Completeness

| Need | Phase |
|------|-------|
| Rename/reshape input declaratively | Phase 1: Boundary Transform (alias) |
| Reshape input when alias can't bridge | Phase 1: Boundary Transform (before) |
| Control whether construction happens | Phase 2: Sealed Boundary (wrap) |
| Construct fields from input automatically | Phase 3: Field Construction (types + from_attributes) |
| Prove cross-field invariants hold | Phase 4: Proof Obligation (after) |
| Derive a view from frozen fields | Phase 5: Derived Projection (computed_field) |
| React to successful construction | Construction Effect (post_init) |

Five phases produce the proven, self-aware object. One hook reacts to its
existence. Field declaration handles the passive structure. There is no
"run arbitrary code on a model instance" capability. Every active computation
falls into one of these categories.

**Computation migrates toward earlier phases.** Prefer earlier phases because earlier phases are more compositional, more testable, and reduce semantic surface area. A problem solved by shape (Phase 1 + 3) requires no code. A problem solved by a validator (Phase 4) requires code that must be total and pure. A problem solved by an effect (post_init) requires code that interacts with the world. Each step right adds complexity and reduces the guarantees you can make. The priority order:
1. **Field types + aliases** (Phase 1 + 3) — shape alone, no code
2. **Discriminated unions** (Phase 3) — dispatch without branching
3. **`@property` / `@computed_field`** (Phase 5) — derivation from stored fields
4. **`mode="after"` validator** (Phase 4) — cross-field proofs
5. **`mode="before"` validator** (Phase 1) — irreducible reshaping
6. **`mode="wrap"` validator** (Phase 2) — sealing or recursion avoidance
7. **`model_post_init`** — side effects (not a construction phase)

Reaching for 5–7 first is a signal to stop and ask: can a better shape solve it?
