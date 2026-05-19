# CLAUDE.md

---

# THE PROTOCOL

The protocol is a graph. Files map to rules; triggers map to skills; every emitted construct admits to one of three forms or names a missing type. Edge traversal IS the precondition for code emission. Independent reasoning has no home — rule loading IS the reasoning.

## File → rule

- `tca/` (domain) → `.claude/rules/domain.md`
- `type.py` → `domain-type.md`
- `value.py` → `domain-value.md`
- foreign mirrors → `foreign.md`
- `*Evaluation` models → `evaluation-model.md`
- services → `service.md`
- `api.py` → `api.md`
- `main.py` → `main.md`
- semantic-surface types → `semantic-surface.md`
- gate adjudication → `gate-rubrics.md`

## Trigger → skill

- new shape needed → `shape-match`
- invariant classification needed → `proof-design`
- procedure reached for to bridge typed shapes → `forge-the-link`
- text drifting procedural → `construction-voice`

Doctrinal anchor: `docs/manifesto.md`, `docs/pydantic-machinery.md`, `docs/program-topology.md`, `docs/building-block-classifier.md`.

## The admissible set

Construction is the verb. Its kin are derivation (`@cached_property` / `@computed_field` returning a constructed value from a model's own fields) and projection (`model_dump_json()` / `model_dump()` emitting the constructed state). Declaration (class definitions and field type annotations) is construction's structural precondition. Every code element resolves to one of these.

The three runtime statement-level forms:

1. Construction — `Type(...)` or `Type.model_validate(...)`
2. Assignment of constructed result to field — `self.field = Type(...)`
3. `match`/`case` on a Pydantic-narrowed discriminated union

## Forbidden constructs name their missing types

| Construct | Missing type |
|---|---|
| For-loop with side effects | A model whose construction folds the iteration |
| `if`/`elif` on string/`Literal` | A discriminated union whose variants own the dispatch |
| Helper function | A `@cached_property` on the model whose fields it reads |
| Dict-building before construction | A composed model whose field types are proven |
| `*Mapper`/`*Translator`/`*Adapter` class | `model_validate(source)` with `from_attributes=True` |
| `model_validator(mode="after")` on a constant | A narrowed scalar with `Field(constraint)` |
| `model_validator(mode="after")` comparing to threshold | A `@cached_property` on an Evaluation Model returning a typed result variant |
| `@cached_property` returning `bool` | A discriminated union whose variant existence IS the answer |
| Bare `str`/`int`/`float`/`Decimal` as composed-model field | A forged scalar from `type.py` |
| `Optional[X]` where absence drives behavior | A discriminated union variant whose fields encode the absence |
| `json.loads` + `model_validate` | `model_validate_json(raw_bytes)` |
| `TypeAdapter(DU)` | A `RootModel[DU]` envelope |
| Consumer re-branching on `.kind` | `match`/`case` against the variants themselves |

The doctrine names every admissible decision. Invented decisions have no home. Requested scope IS the scope. Added scope has no home. The training corpus is procedural; this graph is its counterweight.

**Action IS construction. (Construction's kin: derivation and projection. Construction's precondition: declaration.) Procedure has no home.**

---

## StrEnum IS Literal

A `StrEnum` member IS a `Literal` value — `Literal[MyEnum.FOO]` resolves to `Literal["foo"]` because `StrEnum` values are strings. One declaration serves as enum member, discriminator value, and domain knowledge simultaneously. Restated enum knowledge has no home.

## Naming Conventions

Suffix anchors the semantic role and makes the dispatch chain readable.

| Suffix         | Role                                                                     | Examples (from the reference program) |
| -------------- | ------------------------------------------------------------------------ | ------------------------------------- |
| `*Result`      | decision outputs                                                         | —                                     |
| `*Decision`    | wrappers around action choices                                           | —                                     |
| `*Action`      | action variants downstream of a decision                                 | —                                     |
| `*State` (DU)  | discriminated union of state variants                                    | —                                     |
| `*Transition`  | composed `(state, event)` input model whose derivation yields next state | —                                     |
| `*Intent`      | outbound events to an external system                                    | —                                     |
| `*Event`       | inbound external events                                                  | —                                     |
| `*Evaluation`  | composed-input decision models                                           | —                                     |
| `*Annotation` (DU) | discriminated union of Python typing-form variants                   | `DirectAnnotation`, `UnionAnnotation`, `TupleAnnotation` |
| `*Block`       | discriminated union of classified-node variants                          | `RecordBlock`, `AlgebraBlock`, `LeafBlock`, `EffectBlock` |
| `*Report`      | projection shape over a classified tree                                  | `FieldReport`, `TreeReport`           |

The first eight rows are the paradigm-level conventions; the reference program's domain is type-tree classification and exemplifies the last three. Both sets travel together — a downstream TCA project inherits the eight and grows its own examples for the rest.

## Narrated steps have no home — declared structure IS the construction

```python
# WRONG: construction as orchestrated procedure
annotation = DirectAnnotation(form=raw_type)
slot = FieldSlot(name=field_name, annotation=annotation)
entry = FieldEntry(slot=slot, owner=cls)

# RIGHT: one construction site, field types as obligations
entry = FieldEntry(
    slot=FieldSlot(name=field_name, annotation=raw_type),
    owner=cls,
)
# DirectAnnotation and TypeAnnotation are Pydantic field-validation artifacts
```

## Compatibility hedging has no home

`_REMOVED_` markers, commented-out blocks, dead "kept for compatibility" scaffolding — none has a home in the domain layer. Backward-compatibility is not a constraint within domain. Replacement types are forged. Old shapes have no home alongside their replacements.

## What This Is

This repository develops and documents Type Construction Architecture. It is both a theory surface and a working enforcement environment — the quality bar is architectural, not just valid Python. `tca/building_block.py` is the reference program: a recursive Pydantic type-tree walker that classifies any `BaseModel`'s entire construction graph through one `model_validate` at the root, two self-classifying `RootModel` wrappers, two discriminated unions, demand-driven recursion, zero if-chains. `spec/` is the TCA Spec System — the logic-architecture layer from which every rule, type, and hook derives.

## Commands

```bash
just up dev             # bring up dev env
just down               # bring all envs down
just build dev          # rebuild dev services
just logs dev           # tail dev logs
just shell dev <svc>    # interactive shell in a service
just status             # health snapshot
uv run basedpyright     # static type check
uv run pytest           # run tests
```

Python 3.12+ / `uv` / Pydantic v2 / basedpyright / hatchling build system.

## Architecture (the WHY — shapes live in `.claude/rules/`)

**Type Construction Architecture.** Domain logic's home is model construction and derivation. Services are transport shims. Handlers are deterministic event projections. The type system IS the protocol.

**Spec-derived rules.** `spec/` is the logic architecture; `.claude/rules/`, `.claude/skills/`, and `.claude/scripts/smell.py` are its mechanical projections. A rule whose pattern is not covered by the spec has no home. Rule edits without spec coverage have no home.

**Reference program as proof.** `tca/building_block.py` IS the worked example of the cognitive mode. Edits to it must preserve the construction-graph shape — recursive `RootModel` self-classification, discriminated-union dispatch, derivation on frozen models. A change that introduces procedural orchestration into the reference program is a paradigm defect, not a refactor.

**Frozen models.** Every model is `frozen=True` except the single active model per bounded context. Construction is proof. Derivation's home is the model.

## Key Constraints

- Procedural language in instruction surfaces (`CLAUDE.md`, `.claude/rules/`, `.claude/skills/`, `spec/`) primes procedural code at the token level — text containing "extract," "check," "handle," "process," "manager," "processor," "repository" is infected and must be rewritten via `construction-voice`
- `model_validator(mode="after")` lacking an irreducibility justification from `proof-design` (A.3 — impossible-variant-composition only) has no home
- `TypeAdapter` and `json.loads` have no home in TCA domain code — the class IS the validator (`RootModel` / `RootModel[DU]` / `BaseModel`)
- Helper functions, mapper/translator/adapter classes, dict-building before construction — all name missing types; the fix is more modeling, never more procedure
- Rule edits without corresponding spec coverage have no home — the spec drives the rules, not the other way around

## When the shape is wrong

Imperfection in existing code is not deferrable work. The codebase admits no state where a known wrong shape persists alongside other work. Rule coverage of the pattern IS the precondition for the code edit, not its sequel. "Later" has no home.

## What Goes Where

- **This file** — the protocol, project identity, project-specific architecture and constraints.
- **`.claude/rules/`** — correct shapes per file type. Proof hierarchies, Evaluation Model template, smart-method patterns, semantic-surface doctrine, gate rubrics.
- **`.claude/skills/`** — invocable cognition: `shape-match`, `proof-design`, `construction-voice`, `forge-the-link`, `bounded-adjudication`.
- **`.claude/settings.json` hooks** — mechanical enforcement. Pre-edit fast-fail + post-edit `smell.py` + LLM gate adjudication.
- **`.claude/scripts/smell.py`** — deterministic post-edit fast-fail. No LLM judgment.
- **`spec/`** — TCA Spec System: scope, strategy, conditions, proof-hierarchy classification, premises, configuration models, domain invariants, coverage. The logic architecture layer.
- **`tca/building_block.py`** — the working reference program.
- **`docs/manifesto.md`** — TCA doctrine narrative.
- **`docs/pydantic-machinery.md`** — Pydantic internals load-bearing for TCA patterns.
- **`docs/program-topology.md`, `docs/build-patterns.md`, `docs/irreducible-seams.md`, `docs/roots-and-proof-obligations.md`, `docs/semantic-index-types.md`, `docs/building-block-classifier.md`** — supporting doctrine surfaces.
- **`.claude/CLAUDE.template.md`** — generic CLAUDE.md template for adapting this scaffold to another TCA project.
