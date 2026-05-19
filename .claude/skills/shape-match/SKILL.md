---
name: shape-match
description: "The correct TCA shape as the generation target before code exists — file classification, Evaluation Model template, smart-method patterns (B.2, B.3), and Pydantic decorator stack discipline loaded into working context."
license: MIT
compatibility: "Any TCA project with .claude/rules/ shape definitions"
metadata:
  author: kylejtobin
  version: "3.0.0"
---

# Shape Match

The skill IS the correct TCA shape loaded as the generation target. Training data's mass is procedural Python — services, mappers, dict-builders, if/elif routers. Without an explicit shape in working context, generation follows training gravity. The correct shape is the immediate reference, not a remembered principle.

Hooks are the *post-edit* gate. The shape loaded here is the *pre-edit* target. The two are complementary: the shape is what generation aims at; the hook is what survives if it misses.

## Activation Scope

This skill MUST fire:

- Before writing any file in `domain/`.
- Before writing any new model class anywhere.
- Before writing an Evaluation Model derivation (any `@cached_property` on a `*Evaluation` model).
- Before writing a smart enum method (B.2 — a method on a `StrEnum` or `Enum` class).
- Before writing a smart variant method (B.3 — a method on a frozen `BaseModel` member of a discriminated union).
- When the user invokes `/shape-match` or says "check shapes".

Domain code is where training pulls hardest. In typical Python, domain logic is procedural code that uses models. In TCA, domain logic IS model construction and derivation. Without this skill loaded, generation follows the typical-Python path.

## Protocol

### 1. Classify the file

The file's classification IS the shape's selector.

| File | What it IS |
|---|---|
| `type.py` | Scalars. `RootModel[base]` + `frozen=True` + `Field()`. Imports nothing from the project. No methods, no validators, no logic. |
| `value.py` | Value objects. `BaseModel` + `frozen=True` composing scalars from `type.py`. |
| domain `[concept].py` (wire-serializing) | Frozen domain model whose instances serialize to a wire surface. `frozen=True` + `from_attributes=True`. Fields are domain scalars / value objects / frozen models. Derivations are `@computed_field` + `@cached_property`. |
| domain `[concept].py` (non-serializing) | Frozen domain model whose derivations are in-process facts. `frozen=True`. Derivations are `@cached_property` alone — excluded from `model_dump()`. |
| domain `[concept]_evaluation.py` or `*Evaluation` class | Evaluation Model. `frozen=True`. Composed proven inputs. `@cached_property` derivations whose return type is a typed result variant. Zero decision-validators. Internal — not a wire shape. |
| domain active model | Single unfrozen `BaseModel` per bounded context. State evolves through model operations. One per context. `-> None` mutation methods admissible here and only here. |
| `api.py` in domain | Route contracts. Frozen request/response models. Domain-owned. |
| `service/*.py` | Transport shim. One class, one connect. Binds transport to the active model. Zero domain logic. |
| `api/*.py` | Route file. Contracts imported from `domain/context/api.py`. Defines nothing. Computes nothing. |
| `main.py` | Composition root. Observability bridge, single-expression config construction, transport connect, services bound, keep-alive primitive, drain on shutdown. No domain logic. No multi-line config assembly. No `os.environ` reads. |

### 2. Load the rule

If `.claude/rules/` contains a path-scoped rule matching the file, that rule is part of the loaded shape. The rule specifies what the file CONTAINS, what it IMPORTS FROM, and what has no home in it. The rule is the file's local shape; this skill is the global shape; both apply.

### 3. Generate against the shape

The loaded shape is the generation target. Each construct's match against the shape is the precondition for its existence in the file.

#### Scalars (`type.py`)

- Every type is `RootModel[X]` with `frozen=True`.
- Every field has a `Field()` constraint.
- The file's imports are stdlib and third-party only — nothing from the project.
- No methods, no validators, no logic. The type's existence is its proof.

#### Frozen domain models (wire-serializing and non-serializing)

- Fields are domain scalars, value objects, or other frozen models. Bare primitives (`str`, `int`, `float`, `Decimal`) have no home as field types. Collections of bare primitives (`list[str]`, `tuple[int, ...]`, `set[str]`, `dict[str, str]`) have no home as field types either — narrow the element type.
- Derivations are `@computed_field` + `@cached_property` for wire shapes.
- Derivations are `@cached_property` alone for internal facts that stay in-process — derivation results excluded from `model_dump()`.
- `model_validator(mode="after")` is admissible only as an A.3 impossible-variant-composition shape — `/proof-design` precedes its existence. A validator referencing one field against a constant is an A.1 left unforged. A validator comparing a proven field against a configured threshold is decision logic in the wrong shape — its home is hierarchy B.

#### Evaluation Models (`*Evaluation`)

- `frozen=True`.
- Fields are composed proven inputs — proven scalars, value objects, frozen models, configuration models, projections.
- Derivations are `@cached_property` alone (no `@computed_field`). Evaluation Models are internal; the wire shape is the *intent* or *event* the derivation yields on its own frozen model.
- Each derivation's return type is a typed result variant: a discriminated union (`GateResult = GatePassed | GateRejected`), a typed tuple, or a proven model. `bool`, `int`, and `str`-with-contextual-meaning are not admissible return shapes.
- Zero decision-validators. Construction succeeds for every well-formed input set.
- The body of each derivation is variant construction. The derivation may compose B.2 (smart enum methods) or B.3 (smart variant methods) for the variant-owned part — the F-test names the boundary.

```python
class FileEvaluation(BaseModel, frozen=True):
    context: FileContext
    invariants: tuple[Invariant, ...]
    config: AnalysisConfig

    @cached_property
    def result(self) -> EvaluationResult:
        ...
```

#### Smart enum methods (B.2)

A definition on a `StrEnum` (or `Enum`) class. The F-test is the membership criterion.

- The signature is satisfied by the enum self plus proven scalars or proven value objects. A composed-model `self` (an `*Evaluation`, `*Transition`, `*Decision`) in the signature is an F-test violation — the derivation's home is the composed model (B.1), not the enum.
- The return type is a typed result variant. Primitives have no home as the return shape.
- The body's reference frame is the enum value plus the proven inputs in the signature.

```python
class NodeKind(StrEnum):
    LEAF = "leaf"
    BRANCH = "branch"

    def child_count(self, node: ASTNode) -> ChildCount:
        return ChildCount(len(node.children)) if self is NodeKind.BRANCH else ChildCount(0)
```

#### Smart variant methods (B.3)

A definition on a frozen `BaseModel` member of a discriminated union. Polymorphic dispatch is Pydantic's discriminator narrowing the type at the variant boundary.

- The variant is a frozen `BaseModel` carrying its own fields and its own discriminator `Literal`.
- The F-test is the membership criterion. The signature admits proven DU inputs or proven value objects; a composed-model `self` is not admissible.
- The return type is a typed result variant.
- The method body is total over the variant's valid input subset.

```python
class LeafNode(BaseModel, frozen=True):
    kind: Literal["leaf"] = "leaf"
    value: ProvenScalar

    def apply(self, event: NodeEvent) -> NodeState:
        ...
```

#### Active models

- Single unfrozen `BaseModel` per bounded context. Named for the domain concept.
- `-> None` mutation methods admissible here. State evolves through model operations on the model itself.
- Construction takes proven dependencies and frozen registries — not runtime lists of primitives. The active model's existence proves the enumeration was complete.

#### Services

- One class. One connect function. Transport setup only.
- Zero domain logic. Zero computation. Zero classification. Zero derivation.

#### Routes

- Contracts imported from `domain/context/api.py`.
- No model definitions. No computation.

#### `main.py`

- Composition root, nothing else.
- Observability bridge installed (loop exception handler forwarded to logger).
- Each config root constructed in one expression via `BaseSettings`. No `os.environ` reads. No multi-line config assembly. No procedural defaults.
- Transport connect — one call.
- Services bound — each `.connect()` returns the active model it produced.
- Keep-alive primitive — `await event.wait()`, `await asyncio.gather(*tasks)`, or a documented irreducible-seam polling loop bridging a third-party SDK.
- Drain on shutdown in `finally`.

### 4. Post-generation verification

The shape is the precondition for the file's contents. Every construct is matched against the shape as a closing audit.

| Check | If violated |
|---|---|
| Field typed as bare `str` / `int` / `float` / `Decimal`? | A domain scalar from `type.py` is the correct field type. |
| Field typed as `list[str]` / `tuple[int, ...]` / `set[str]` / `dict[str, str]`? | Narrow the element type; the collection wrapper carries its own invariant if any. |
| Function parameter typed as `list[str]` / similar collection-of-primitives? | Same as above — narrow the element type, forge a registry construct if the collection has identity. |
| Derivation in a standalone function? | The derivation's home is `@computed_field` + `@cached_property` (wire) or `@cached_property` alone (internal) on the owning model. |
| `model_validator(mode="after")` on a single-field condition? | A narrowed scalar with `Field()` carries the proof; `/proof-design` precedes. |
| `model_validator(mode="after")` comparing fields against a threshold? | A decision in the wrong shape. Its home is a `@cached_property` returning a typed result variant on an Evaluation Model. |
| `@computed_field` + `@property` on a frozen model? | `@cached_property` is required — the frozen bypass in `_setattr_handler` is the cache path. |
| Evaluation Model with `@computed_field` + `@cached_property`? | Evaluation Models are internal — `@cached_property` alone is correct. The wire shape is the produced intent/event on its own frozen model. |
| `@cached_property` returning `bool`? | A `bool` return shape erases the variant's discriminator. Forge the typed result variant; the variant's existence carries the answer. |
| Enum method with a composed-decision-model parameter (`*Evaluation` / `*Transition` / `*Decision`)? | F-test violation — the derivation's home is the composed model (B.1) composing the enum value (B.2). |
| Consumer re-branching on `.kind`? | Pydantic's discriminator has already narrowed the type. `match`/`case` against the variants is the consumer's branch point. |
| `json.loads` anywhere in domain code? | `model_validate_json(raw_bytes)` absorbs JSON in a single Rust-level pass. `json.loads` produces an untyped intermediate dict with no home. |
| `TypeAdapter(...)` anywhere in domain code? | The TCA shape is a frozen `RootModel` envelope — `class Envelope(RootModel[T], frozen=True): root: T`. The class IS the validator. |
| External address (subject, channel, topic, key prefix, endpoint) as a `str` or `list[str]`? | Contract-surface erasure. Forge the typed address construct and a registry that enumerates the set. |
| Active model receiving a runtime `list` of primitive identifiers? | Construction-erases-the-domain. The active model's signature takes a frozen registry construct; construction proves the enumeration was complete. |
| `main.py` reading `os.environ` or assembling config across multiple lines? | The config layer was never forged. `BaseSettings` binds env vars at the model; `main.py` constructs each config root in one expression. |
| Import direction reversed? | Domain toward edge — never the reverse. |
| File named for a technology pattern? | The file's name is the domain concept it represents. |
| Service containing domain logic? | The home of domain logic is a model derivation or the active model. |

## Training Gravity — Know What Pulls

These are the patterns training generates by default. Each has a TCA shape that occupies its slot entirely. Awareness of the pull is the first defense.

| Training default | TCA shape | Why training wins without this skill |
|---|---|---|
| Service class with methods | Frozen model with `@cached_property` derivations | Most Python "domain logic" lives in services. |
| Function computing from model fields | `@computed_field` + `@cached_property` on the model | Functions are the default unit of work. |
| Dict-building before construction | Composed model with proven field types | Dicts are Python's universal intermediate. |
| `if`/`elif` on a string field | Discriminated union with `Literal` discriminators per variant | String matching is ubiquitous in training. |
| Mapper class between models | `model_validate(source, from_attributes=True)` | Mapper / adapter is a standard enterprise pattern. |
| Utility module of helpers | Derivations on their owning models | `utils.py` exists in nearly every Python project. |
| Validator checking a constant bound | Narrowed scalar with `Field(gt=X)` | Validators are the "obvious" Pydantic tool. |
| `@property` on a frozen model | `@computed_field` + `@cached_property` | `@property` is the Python default. |
| Validator comparing fields to a threshold | `@cached_property` on an Evaluation Model returning a typed result variant | Threshold-as-validator is the default decision shape in training. |
| `bool` field gating downstream behavior | DU variant whose existence IS the gate | Booleans are the default flag shape. |
| `if`/`elif` re-branching on a DU's `.kind` | `match`/`case` against the variants, or a smart variant method (B.3) | Re-branching is the default consumer pattern. |
| Enum method taking the composed model | Derivation on the composed model composing the enum value (B.1 composing B.2) | "Methods take context" is the OOP default; the F-test names the inversion. |
| `list[str]` of identifiers as input | Typed scalar list, or a frozen registry construct | Strings are the universal opaque identifier in training. |
| `main.py` reading `os.environ` directly | `BaseSettings` model constructed once | Top-level env access is the canonical training shape. |
