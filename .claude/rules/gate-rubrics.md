---
paths:
  - "**/*"
---

# Gate Rubrics

## Reading Order

1. Classify mode: determine which layer of the program topology the edited file belongs to — `type.py` (scalar root), `value.py` (value objects), `domain/` model (frozen or active), `api.py` (domain contracts), `service/` (transport shim), `api/` route (edge), or `main.py` (composition root). The layer determines which evidence shapes apply most directly.
2. For each gate, answer the stated Question against the edit.
3. Classify against Allowed and Disallowed evidence.
4. If the edit matches an Approved Mechanism, the gate passes unless a specific Disallowed shape also applies.
5. If classification is ambiguous, emit the gate's Escalation Trigger.

---

## Type Integrity Gate

**Question**: Is every type well-formed — scalars own values, models are frozen (unfrozen only for the single active model of a bounded context whose live state evolves through model operations), unions are discriminated, constraints are declarative on fields?

**Allowed evidence**:
- `RootModel[base_type]` with `frozen=True` and constraints via `Field()`, defined in `type.py` — the scalar pattern
- `BaseModel` with `frozen=True`, `from_attributes=True`, fields typed as domain scalars — the composed model pattern
- `Annotated[A | B | C, Field(discriminator="field")]` — declared discriminated union with `Literal` discriminator on each variant
- `Field(gt=0)`, `Field(ge=0, le=1)`, `Field(min_length=1)` — constraints declared on the field itself, not in external validation
- `model_validator(mode="before")` that peels a transport envelope to reach the payload — wrapper absorption, not field-level work
- `model_validator(mode="after")` rejecting an *impossible variant composition* — composed fields whose individually-valid values cannot coexist as a meaningful state. E.g., on `StateTransition(current_state: NodeState, event: NodeEvent)` the validator rejects the cell `(Terminal, ChildAdded)` because a terminal node cannot accept children. Data integrity only. Never for business decisions, threshold comparisons, or "given these proven values, should the system act?" — those are derivations producing typed result variants on an Evaluation Model
- A single `BaseModel` without `frozen=True` as the active model of a bounded context — one per context, named for the domain concept it represents, state evolves through model operations
- Value objects in `value.py` composing scalars from `type.py` — the second layer of the dependency graph
- `config.py` using Pydantic `BaseSettings` — configuration is typed and validated at construction

**Disallowed evidence**:
- `BaseModel` without `frozen=True` that is not the single active model of a bounded context — unfrozen for convenience
- `model_validator` checking a constraint that `Field()` expresses declaratively — e.g., `if value <= 0: raise` when `Field(gt=0)` exists
- `model_validator(mode="after")` whose body reads multiple proven field values and raises based on a comparison against a configured threshold — that is a business decision encoded as construction failure. The decision belongs on an Evaluation Model as a derivation returning a typed result variant (e.g., `GateResult = GatePassed(intent) | GateRejected(reason)`). Construction succeeds; the consumer dispatches on the variant via Pydantic's discriminator. The only `model_validator(mode="after")` shape that survives doctrine review is the impossible-variant-composition shape named in Allowed evidence above
- `Union[A, B]` without a discriminator field — implicit type resolution instead of declared structural dispatch
- `Optional[X]` where absence represents a structurally distinct state with behavioral consequences — absence should be its own DU variant with its own fields
- `Enum` where each member carries different associated data — the data is invisible to the type system; a DU of models makes per-variant fields explicit
- Scalar defined outside `type.py` — born in the wrong place in the dependency graph
- Value object defined outside `value.py` — born in the wrong place in the dependency graph
- Multiple unfrozen models in the same context — only one active model per context
- Configuration as bare `os.environ` access, a settings dict, or untyped environment variable reads
- `@computed_field` + `@property` on a frozen model — recomputes every access instead of caching; use `@computed_field` + `@cached_property` which caches via the frozen bypass in Pydantic's `_setattr_handler`
- A stored field whose value is fully derivable from other stored fields on the same model — the derivation should be a `@computed_field` + `@cached_property`, with the upstream data as stored fields instead

**Approved mechanisms**:
- **Unfrozen model as active model:** A `BaseModel` without `frozen=True` is approved when it is the single active model of a bounded context. Named for the domain concept it represents. Exactly one per context. State evolves through model operations on the model itself, not external code setting attributes. A second unfrozen model in the same context is not approved.
- **`model_validator(mode="before")` for envelope unwrapping:** A before-validator accessing a wrapper key like `data["payload"]` or `data["events"][0]` is approved. It absorbs transport structure that field aliases cannot express. If renaming individual fields or coercing field values, `Field(alias=...)` or field-level constraints should do that work instead.
- **`Optional[ScalarType]` for informational absence:** `Optional[X]` is approved when absence is purely informational — no downstream logic branches on whether the value is present or absent. When presence vs absence drives different behavior, the cases should be DU variants.

**Escalation triggers**:
- Scalar vs value object boundary unclear → Developer consults the project's type catalog. Single base type with constraints = scalar. Composes multiple scalars = value object.
- `Optional` vs DU variant boundary unclear → Developer checks: does any `if x is not None` or `if x is None` appear in logic that decides what to do (not just display)? If yes, absence is behavioral → DU variant.

---

## Construction Carries Meaning Gate

**Question**: Does model construction, composition, and derivation do the work — not services, not adapters, not external computation, not coordinator scripts?

**Allowed evidence**:
- `@computed_field` + `@cached_property` on a frozen model deriving from its own proven fields — the TCA derivation stack: serializable, cached, uses the frozen bypass
- `@cached_property` alone on a model for internal derivations that do not need serialization — caches but excluded from `model_dump()`
- `@property` on a model computing a trivial intrinsic fact from its own fields — lightweight, uncached derivation
- `model_validate(proven_model)` crossing from foreign to domain truth — the lifting pattern
- `model_validate_json(raw_bytes)` at the live input edge, yielding the result — the capture pattern
- Composed model with proven models as fields — the richer semantic world as one proven object
- `@cached_property` that calls `model_validate` to trigger next construction — the cascade pattern
- `TypeAdapter(UnionType).validate_python(data)` for DU dispatch at a boundary
- `Field(alias="foreign_name")` translating foreign field names declaratively — the boundary model pattern
- Active model orchestrating through construction, derivation, and projection — domain logic living on the model
- `domain/context/api.py` contracts as domain-owned models that route files import

**Disallowed evidence**:
- A function that takes a model, reads its fields, computes a value, and returns the result — derivation that escaped the model
- A function that builds a dict of intermediate values before passing to model construction — preparation work smuggled into procedure
- A class that takes two models and produces a third by copying fields between them — a mapper by another name
- A service method that sequences multiple `model_validate` calls — a coordinator script replacing construction cascade via `@cached_property`
- `model_validator(mode="before")` renaming or transforming individual fields — translation work that `Field(alias=...)` handles declaratively
- A "helper function" or "utility" computing an intrinsic property of a model from that model's own fields — an escaped derivation
- A route file defining its own request/response models instead of importing contracts from `domain/context/api.py` — meaning escaped from domain ownership
- A service file containing computation, classification, derivation, or domain logic beyond binding transport to the active model — orchestration escaped
- A standalone function that could be a `@cached_property` on a composed model — construction replaced by procedure because the composed model was never created
- `json.loads()` followed by `model_validate()` when data arrives as raw bytes or str — `model_validate_json(raw_bytes)` absorbs JSON in a single Rust-level pass with no intermediate dict; the two-step parse creates untyped truth between steps

**Approved mechanisms**:
- **Irreducible seam procedure:** A function performing external I/O (REST call, websocket send/receive, database query, file read) and passing the result to `model_validate` is approved. The seam must be contained (one function), terminal (bridges INTO the construction graph, procedure does not spread beyond), and irreducible (no way to express the I/O as construction). The seam touches a live transport edge, positional data structure, or untyped external surface.
- **Test infrastructure:** Test files constructing models with literal values, building fixtures, or using dicts as input to `model_validate` for assertions are approved. Test code is infrastructure, not domain code. Gates apply to production source, not test files.
- **Transport setup in service connect:** A service's connect function performing transport-level setup (socket connection, authentication handshake, channel subscription) before binding to the active model is approved. The setup must be purely transport — if it makes domain decisions, classifies data, or computes domain values, it has escaped.

**Escalation triggers**:
- Seam boundary placement unclear → Developer consults the TCA document's irreducible seams section. The seam is irreducible only when it touches a live transport edge, positional data structure, or untyped external surface. If replaceable by `Field(alias=...)`, `model_validator(mode="before")`, or a composed model, it is not a seam.

---

## Program Shape Gate

**Question**: Does code live where it belongs — domain types in domain, services are thin transport shims, main.py composes, types flow domain toward edge?

**Allowed evidence**:
- `main.py` containing only dependency construction and injection — composition, nothing else
- `config.py` containing Pydantic `BaseSettings` models
- `api/context.py` as a route file importing contracts from `domain/context/api.py` — transport edge using domain-owned types
- `service/context.py` as a class with a single connect function binding transport to the active model, optionally passing a client — same boring shape everywhere
- `domain/context/type.py` containing scalars, importing nothing from the program — the dependency root
- `domain/context/value.py` containing value objects, importing only from `type.py` in its context — the second layer
- `domain/context/[domain_named].py` as the active model — one per context, named for what it represents
- `domain/context/api.py` containing contracts for routes — domain-owned boundary types
- `domain/context/[concept].py` as sub-context models named for domain concepts — files named for what they are
- Import direction within domain: `type.py` ← `value.py` ← frozen domain models ← active model
- Import direction across layers: domain ← service ← route ← main
- Cross-context imports between domain models — domains are primitives, forged to be combined

**Disallowed evidence**:
- A route or edge module defining a type that a domain module imports — type flow inverted
- A service file with domain logic beyond binding transport to the active model — the service grew fat
- `main.py` containing model definitions, domain logic, or computation — composition only
- A "shared types" or "common" module that both domain and edge import from — those types belong in domain
- A domain model importing from a transport, route, or infrastructure module — domain depends on nothing above it
- More than one active model (unfrozen model) per domain context — one convergence point per context
- A route file computing or transforming data instead of handing it to domain contracts — the route is doing work
- Scalars defined outside `type.py` or value objects defined outside `value.py` — types born in the wrong layer

**Approved mechanisms**:
- **Cross-context domain imports:** A domain model importing scalars, value objects, or frozen models from another context is approved. Domains are primitives, not sealed bounded contexts. The import must flow between peer domain modules — not from edge into domain or from domain into infrastructure.
- **Novel domain file names:** A file in `domain/context/` with a name not in the standard set (`type.py`, `value.py`, `api.py`, active model) is approved when the name describes a genuine domain concept. The test: does this name describe something the domain contains, or something the technology does?

**Escalation triggers**:
- Own file vs inline on active model unclear → Developer decides: if any other file in the context imports the model, it gets its own file. If only the active model uses it and it is small, it may live in the active model's file.
- Shared model ownership unclear → Developer decides: the model lives in the context closer to the authority root. When contexts are peers, it lives in the context whose domain concept it most directly represents.
