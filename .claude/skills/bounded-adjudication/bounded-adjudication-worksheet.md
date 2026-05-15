# Bounded Adjudication Worksheet

## Project Context [TEMPLATE]

**Project name:** (your project)
**What it builds:** (what it does)
**Primary language/framework:** Python 3.13+ / Pydantic v2
**Key architectural commitments:** Type Construction Architecture. Domain logic lives in model construction, not service layers. All models frozen. Construction is proof. Discriminated unions replace branching. Foreign boundaries get mirror models. Derivations belong on the model.
**Where does truth live in this project:** In the types. The project's specification documents define what the types must be. The TCA document defines how code must be written. The adjudication protects construction discipline — not the domain invariants themselves, but the guarantee that code edits let types carry meaning rather than smuggling procedure in.

---

## 1. Structural Invariants [CONFIRMED]

Shapes that are always wrong regardless of context. Not usually wrong. Always wrong.

| # | Invariant shape | Why it is always wrong |
|---|----------------|----------------------|
| 1 | Bare `str`, `int`, `float`, or `Decimal` as a model field type (not `Literal`, not `bool`) | A domain value without a scalar owner has no identity, no constraints, no semantic distinction. `price: Decimal` and `quantity: Decimal` are the same type. `Price` and `Quantity` are not. The TCA doc opens with this. |
| 2 | Function returning `dict` | Unowned truth flowing through the program. Data with shape is a model. |
| 3 | Function parameter typed as `dict` | Construction was skipped at the boundary. Raw data enters via `model_validate`, not dict-passing. |
| 4 | Class named `*Mapper`, `*Translator`, `*Converter`, `*Adapter`, `*Builder`, `*Factory`, `*Normalizer`, `*Presenter` | Each of these is a procedural layer the TCA doc explicitly replaces: `model_validate` is the translator, `Field(alias=...)` is the mapper, construction is the factory, `model_validator(mode="before")` is the normalizer, terminal model derivation is the presenter. |
| 5 | `if`/`elif` chain branching on a string or field value to select among known categories | Construction selects the variant. `Literal` field + discriminated union replaces the router. |
| 6 | `isinstance()` check inside a loop body over model types | A DU hiding inside iteration. Variants are a static property. Dispatch is structural, not conditional. |
| 7 | `type.py` importing from any other module in the program | `type.py` is the dependency root. Pure scalars. It imports nothing from the program. If it imports upward, the gravity of the entire dependency graph is broken. |
| 8 | `value.py` importing from anything other than `type.py` in its own context | `value.py` composes scalars. It is the second layer. It looks down to `type.py` only. Importing from domain models, active models, services, or other contexts breaks the layered dependency order. |
| 9 | A frozen domain model importing from the active model of its context | The active model converges everything — frozen models are its inputs. A frozen model depending on the active model inverts the dependency direction. |
| 10 | A file in `domain/` named for a technology pattern: `store.py`, `repository.py`, `handler.py`, `controller.py`, `crud.py`, `manager.py`, `processor.py`, `router.py` | The domain names its files. These names describe framework roles, not domain concepts. A `store.py` tells you about persistence technology. An `event.py` tells you what the domain contains. |
| 11 | A file in `domain/` named `utils.py`, `helpers.py`, `common.py`, or `misc.py` | Code without a domain identity. In TCA every piece of logic belongs to a domain concept. These names are admissions that the code has no owner. |

---

## 2. Axes of Judgment [CONFIRMED]

Each gate asks one question about one independent dimension of the work.

| # | Gate name | Question |
|---|----------|----------|
| 1 | Type Integrity | Is every type well-formed — scalars own values, models are frozen (unfrozen only for the single active_model of a bounded context whose live state evolves through model operations), unions are discriminated, constraints are declarative on fields? |
| 2 | Construction Carries Meaning | Does model construction, composition, and derivation do the work — not services, not adapters, not external computation, not coordinator scripts? |
| 3 | Program Shape | Does code live where it belongs — domain types in domain, services are thin transport shims, main.py composes, types flow domain toward edge? |

---

## 3. Evidence Shapes [CONFIRMED]

For each gate, the concrete observable shapes that constitute allowed and disallowed work.

### Gate: Type Integrity

**Allowed shapes:**
- `RootModel[base_type]` with `frozen=True` and constraints via `Field()`, defined in `type.py` — the scalar pattern
- `BaseModel` with `frozen=True`, `from_attributes=True`, fields typed as domain scalars — the composed model pattern
- `Annotated[A | B | C, Field(discriminator="field")]` — declared discriminated union with `Literal` discriminator on each variant
- `Field(gt=0)`, `Field(ge=0, le=1)`, `Field(min_length=1)` — constraints declared on the field itself, not in external validation
- `model_validator(mode="before")` that peels a transport envelope to reach the payload — wrapper absorption, not field-level work
- A single `BaseModel` without `frozen=True` as the active_model of a bounded context — one per context, named for the domain concept it represents, state evolves through model operations on that single object
- Value objects in `value.py` composing scalars from `type.py` — the second layer of the dependency graph
- `config.py` using Pydantic `BaseSettings` — configuration is typed and validated at construction

**Disallowed shapes:**
- `BaseModel` without `frozen=True` that is not the single active_model of a bounded context — unfrozen for convenience
- `model_validator` checking a constraint that `Field()` expresses declaratively — e.g., `if value <= 0: raise` when `Field(gt=0)` exists
- `Union[A, B]` without a discriminator field — implicit type resolution instead of declared structural dispatch
- `Optional[X]` where absence represents a structurally distinct state with behavioral consequences — absence should be its own DU variant with its own fields
- `Enum` where each member carries different associated data — the data is invisible to the type system; a DU of models makes per-variant fields explicit
- Scalar defined outside `type.py` — born in the wrong place in the dependency graph
- Value object defined outside `value.py` — born in the wrong place in the dependency graph
- Multiple unfrozen models in the same context — only one active_model per context
- Configuration as bare `os.environ` access, a settings dict, or untyped environment variable reads

### Gate: Construction Carries Meaning

**Allowed shapes:**
- `@cached_property` or `@computed_field` on a model deriving from its own proven fields — the derivation pattern
- `@property` on a model computing an intrinsic fact from its own fields — lightweight derivation
- `model_validate(proven_model)` crossing from foreign to domain truth — the lifting pattern
- `model_validate_json(raw_bytes)` at the live input edge, yielding the result — the capture pattern
- Composed model with proven models as fields — the richer semantic world as one proven object
- `@cached_property` that calls `model_validate` to trigger next construction — the cascade pattern
- `TypeAdapter(UnionType).validate_python(data)` for DU dispatch at a boundary
- `Field(alias="foreign_name")` translating foreign field names declaratively — the boundary model pattern
- Active model orchestrating through construction, derivation, and projection — domain logic living on the model, not around it
- `domain/context/api.py` contracts as domain-owned models that route files import

**Disallowed shapes:**
- A function that takes a model, reads its fields, computes a value, and returns the result — derivation that escaped the model it belongs to
- A function that builds a dict of intermediate values before passing to model construction — preparation work that is itself construction, smuggled into procedure
- A class that takes two models and produces a third by copying fields between them — a mapper that escaped the class-name fast-fail by using a different name
- A service method that sequences multiple `model_validate` calls — a coordinator script replacing construction cascade via `@cached_property`
- `model_validator(mode="before")` renaming or transforming individual fields — translation work that `Field(alias=...)` handles declaratively
- A "helper function" or "utility" computing an intrinsic property of a model from that model's own fields — an escaped derivation wearing a neutral name
- A route file defining its own request/response models instead of importing contracts from `domain/context/api.py` — meaning escaped from domain ownership
- A service file containing computation, classification, derivation, or domain logic beyond binding transport to the active model — orchestration escaped from where it belongs
- A standalone function that could be a `@cached_property` on a composed model — construction replaced by procedure because the composed model was never created

### Gate: Program Shape

**Allowed shapes:**
- `main.py` containing only dependency construction and injection — composition, nothing else
- `config.py` containing Pydantic `BaseSettings` models
- `api/context.py` as a route file importing contracts from `domain/context/api.py` — transport edge using domain-owned types
- `service/context.py` as a class with a single connect function binding transport to the active model, optionally passing a client — same boring shape everywhere
- `domain/context/type.py` containing scalars, importing nothing from the program — the dependency root
- `domain/context/value.py` containing value objects, importing only from `type.py` in its context — the second layer
- `domain/context/[domain_named].py` as the active model — one per context, named for what it represents in the domain
- `domain/context/api.py` containing contracts for routes — domain-owned boundary types
- `domain/context/[concept].py` as sub-context models named for domain concepts — files named for what they are, not what technology they use
- Import direction within domain: `type.py` ← `value.py` ← frozen domain models ← active model
- Import direction across layers: domain ← service ← route ← main
- Cross-context imports between domain models — domains are primitives, forged to be combined

**Disallowed shapes:**
- A route or edge module defining a type that a domain module imports — type flow inverted
- A service file with domain logic beyond binding transport to the active model — the service grew fat
- `main.py` containing model definitions, domain logic, or computation — composition only
- A "shared types" or "common" module that both domain and edge import from — those types belong in domain, edge imports from domain
- A domain model importing from a transport, route, or infrastructure module — the domain depends on nothing above it
- More than one active model (unfrozen model) per domain context — one convergence point per context
- A route file computing or transforming data instead of handing it to domain contracts — the route is doing work
- Scalars defined outside `type.py` or value objects defined outside `value.py` — types born in the wrong layer

---

## 4. Approved Mechanisms [CONFIRMED]

For each gate, the sanctioned ways to achieve goals that would otherwise appear suspicious.

### Gate: Type Integrity

**Mechanisms:**
- **Unfrozen model as active_model:** A `BaseModel` without `frozen=True` is approved when it is the single active model of a bounded context. It must be named for the domain concept it represents (not a technology name). There is exactly one per context. Its state evolves through model operations — fields change through construction and derivation on the model itself, not through external code reaching in and setting attributes. Any second unfrozen model in the same context is not approved.
- **`model_validator(mode="before")` for envelope unwrapping:** A before-validator that accesses a wrapper key like `data["payload"]` or `data["events"][0]` is approved. It is absorbing transport structure that cannot be expressed as a field alias because the target fields are nested inside a wrapper. If the validator is renaming individual fields or coercing field values, `Field(alias=...)` or field-level constraints should do that work instead.
- **`Optional[ScalarType]` for informational absence:** `Optional[X]` is approved when absence is purely informational — no downstream logic branches on whether the value is present or absent. When presence vs absence drives different behavior or represents structurally distinct states, the cases should be DU variants.

### Gate: Construction Carries Meaning

**Mechanisms:**
- **Irreducible seam procedure:** A function or method that performs external I/O (REST call, websocket send/receive, database query, file read) and passes the result to `model_validate` is approved. This is the irreducible seam — the single point where construction cannot reach because the outside world is involved. The seam must be contained (one function), terminal (it bridges INTO the construction graph, procedure does not spread beyond it), and irreducible (there is no way to express the I/O as construction).
- **Test infrastructure:** Test files constructing models with literal values, building test fixtures, or using dicts as input to `model_validate` for test assertions are approved. Test code is infrastructure, not domain code. The adjudication gates apply to production source, not test files.
- **Transport setup in service connect:** A service's connect function performing transport-level setup (socket connection, authentication handshake, channel subscription) before binding to the active model is approved. The setup must be purely about transport — if it makes domain decisions, classifies data, or computes domain values, it has escaped.

### Gate: Program Shape

**Mechanisms:**
- **Cross-context domain imports:** A domain model in one context importing scalars, value objects, or frozen models from another context is approved. Domains are primitives, not sealed bounded contexts. They are forged to be combined. The import must flow between peer domain modules — not from edge into domain or from domain into infrastructure.
- **Novel domain file names:** A file in `domain/context/` with a name not in the standard set (`type.py`, `value.py`, `api.py`, active model) is approved when the name describes a genuine domain concept. The test: does this name describe something the domain contains, or something the technology does?

---

## 5. Genuine Ambiguities [CONFIRMED]

Where evidence matching fails to resolve classification.

| # | Ambiguity | Owner |
|---|-----------|-------|
| 1 | **Scalar vs value object:** When is a constrained value a scalar in `type.py` vs a composed value object in `value.py`? If it wraps a single base type with constraints, it is a scalar. If it composes multiple scalars, it is a value object. The boundary is not always obvious. | Developer — consult the project's type catalog. |
| 2 | **Own file vs inline on active model:** When does a frozen domain model belong in its own `domain/context/[concept].py` file vs defined in the active model's file? | Developer — if any other file in the context imports the model, it gets its own file. If only the active model uses it and it is small, it may live in the active model's file. |
| 3 | **Shared model ownership:** When a model serves two contexts, which context owns it? Cross-domain composition is approved, but the model must be defined in one place. | Developer — the model lives in the context closer to the authority root (the one that other contexts depend on). When contexts are peers, the model lives in the context whose domain concept it most directly represents. |
| 4 | **Seam boundary placement:** Is a piece of procedure an irreducible seam or an escaped construction? The test is whether the procedure involves external I/O that construction cannot express. But some transformations feel like they require procedure when a composed model with the right fields would absorb them. | Developer — the seam is irreducible only when it touches a live transport edge, positional data structure, or untyped external surface. If the procedure can be replaced by a model with `Field(alias=...)`, `model_validator(mode="before")`, or a composed model, it is not a seam. |
| 5 | **Optional vs DU variant:** When is `Optional[X]` acceptable informational absence vs a case that should be a DU variant? The test is whether absence drives different behavior. But "drives different behavior" can be subtle — a field that is None might cause a downstream derivation to produce a different result without an explicit branch. | Developer — if any `if x is not None` or `if x is None` appears in logic that decides what to do (not just what to display), absence is behavioral and should be a DU variant. |

---

## 6. Authority Topology [CONFIRMED]

What is the declared truth against which work is measured?

**Authority root:** `type.py` in each domain context. Scalars are atomic truth — the vocabulary from which everything else is composed. They import nothing from the program. Every other layer builds upward from them.

**Ownership map:**

| Gate | Measured against |
|------|-----------------|
| Type Integrity | The TCA document defines what well-formed types look like — frozen models, owned scalars, declared DUs, declarative constraints. The project's type catalog defines what specific scalars and models must exist for this domain. `type.py` is the structural root within code. |
| Construction Carries Meaning | The TCA document's pattern pairs are the authority — each "Bad Procedural Pattern" / "TCA Pattern" section defines what construction replaces and what it looks like when construction carries the meaning. The irreducible seams section defines where procedure is legitimate. |
| Program Shape | The file structure rules define what each file is and what it may contain: `main.py` composes, `config.py` is Pydantic Settings, `service/context.py` binds transport, `api/context.py` routes using domain contracts, `domain/context/` owns all types with the layered import hierarchy `type.py` ← `value.py` ← domain models ← active model. The naming principle is: the domain names the files. |

**Import hierarchy as authority graph:**

```
type.py          (root — imports nothing from program)
  ↑
value.py         (imports only type.py in its context)
  ↑
domain models    (import type.py, value.py, peer context types)
  ↑
active model     (imports all of the above, one per context)
  ↑
api.py           (contracts — domain-owned, imported by routes)
  ↑
service/         (binds transport to active model)
  ↑
api/ routes      (imports contracts from domain/context/api.py)
  ↑
main.py          (composes everything, imports from all layers)
```

Each layer sees only downward. No layer imports from above it.

---

## Quality Gate [PASSED]

- [x] Every invariant is a concrete shape, not a principle
- [x] Every gate asks exactly one question
- [x] No gate overlaps with another gate
- [x] All gates together cover the work's dimensions
- [x] Every evidence shape is observable in an edit
- [x] Every approved mechanism is specific enough to match against
- [x] Every ambiguity names an owner
- [x] Authority topology is consistent with the gates

---

## Generation [COMPLETE]

**Generated artifacts:**

1. `settings.json` — Hooks configuration with:
   - `PreToolUse` prompt hook on `Edit|Write`: fast-fail invariant check (11 patterns)
   - `PostToolUse` agent hook on `Edit|Write`: three-gate adjudication referencing rubric

2. `rules/gate-rubrics.md` — Path-scoped rule (`**/*`) containing:
   - Reading order with layer classification
   - Type Integrity gate: 8 allowed, 9 disallowed, 3 approved mechanisms, 2 escalation triggers
   - Construction Carries Meaning gate: 10 allowed, 9 disallowed, 3 approved mechanisms, 1 escalation trigger
   - Program Shape gate: 12 allowed, 8 disallowed, 2 approved mechanisms, 2 escalation triggers
