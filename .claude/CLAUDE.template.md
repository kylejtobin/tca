# CLAUDE.md — Template

A generic CLAUDE.md for a TCA project. Replace every `{{PLACEHOLDER}}`. Sections marked *(project-specific)* require domain content; everything else is paradigm-level and copies through unchanged.

---

# THE PROTOCOL

The protocol is a graph. Files map to rules; triggers map to skills; every emitted construct admits to one of three forms or names a missing type. Edge traversal IS the precondition for code emission. Independent reasoning has no home — rule loading IS the reasoning.

## File → rule

{{FILE_RULE_MAP}}

<!--
  *(project-specific)*. One row per `<path or pattern>` → `<rule filename in .claude/rules/>`.
  Example rows (copy/edit as needed):
    - `domain/`             → `.claude/rules/domain.md`
    - `type.py`             → `domain-type.md`
    - `value.py`            → `domain-value.md`
    - foreign mirrors       → `foreign.md`
    - `*Evaluation` models  → `evaluation-model.md`
    - services              → `service.md`
    - `api.py`              → `api.md`
    - `main.py`             → `main.md`
    - semantic-surface types→ `semantic-surface.md`
    - gate adjudication     → `gate-rubrics.md`
-->

## Trigger → skill

- new shape needed → `shape-match`
- invariant classification needed → `proof-design`
- procedure reached for to bridge typed shapes → `forge-the-link`
- text drifting procedural → `construction-voice`

Doctrinal anchor: {{DOCTRINAL_ANCHORS}}

<!--
  *(project-specific)*. Comma-separated pointers to TCA doctrine surfaces in this repo,
  e.g. `docs/type-construction-architecture.md`, `docs/pydantic-machinery.md`.
-->

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

| Suffix         | Role                                                                     | Examples                          |
| -------------- | ------------------------------------------------------------------------ | --------------------------------- |
| `*Result`      | decision outputs                                                         | {{EXAMPLES_RESULT}}               |
| `*Decision`    | wrappers around action choices                                           | {{EXAMPLES_DECISION}}             |
| `*Action`      | action variants downstream of a decision                                 | {{EXAMPLES_ACTION}}               |
| `*State` (DU)  | discriminated union of state variants                                    | {{EXAMPLES_STATE}}                |
| `*Transition`  | composed `(state, event)` input model whose derivation yields next state | {{EXAMPLES_TRANSITION}}           |
| `*Intent`      | outbound events to {{OUTBOUND_TARGET}}                                   | {{EXAMPLES_INTENT}}               |
| `*Event`       | inbound {{INBOUND_SOURCE}} events                                        | {{EXAMPLES_EVENT}}                |
| `*Evaluation`  | composed-input decision models                                           | {{EXAMPLES_EVALUATION}}           |

<!--
  *(project-specific)*. Fill examples from real domain types. If a row has no
  domain example yet, leave the placeholder rather than fabricating one.
  `{{OUTBOUND_TARGET}}` / `{{INBOUND_SOURCE}}` name the external system the
  domain talks to (e.g. "device", "peer service", "upstream system").
-->

## Narrated steps have no home — declared structure IS the construction

```python
# WRONG: construction as orchestrated procedure
{{WRONG_NARRATED_STEPS}}

# RIGHT: one construction site, field types as obligations
{{RIGHT_DECLARED_STRUCTURE}}
# {{NESTED_CONSTRUCTION_NOTE}}
```

<!--
  *(project-specific)*. Two snippets drawn from real domain types showing the
  same shape — explicit intermediate construction vs. one composed construction
  site where Pydantic's field validation does the nested forging.
-->

## Compatibility hedging has no home

`_REMOVED_` markers, commented-out blocks, dead "kept for compatibility" scaffolding — none has a home in the domain layer. Backward-compatibility is not a constraint within domain. Replacement types are forged. Old shapes have no home alongside their replacements.

## What This Is

{{PROJECT_PURPOSE}}

<!--
  *(project-specific)*. 1–3 sentences. What the project does, the bounded
  context, the external systems it integrates with, the operational stance.
-->

## Commands

```bash
{{COMMANDS_BLOCK}}
```

{{TOOLCHAIN_LINE}}

<!--
  *(project-specific)*. Real shell commands the operator/agent uses. Below
  the block, one line naming the toolchain — e.g.
  "Python 3.13+ / `uv` / Pydantic v2 / FastAPI / hatchling build system."
-->

## Architecture (the WHY — shapes live in `.claude/rules/`)

**Type Construction Architecture.** Domain logic's home is model construction and derivation. Services are transport shims. Handlers are deterministic event projections. The type system IS the protocol.

{{DOMAIN_AXIOMS}}

<!--
  *(project-specific)*. One short paragraph per load-bearing domain axiom.
  Each paragraph leads with a **Bolded Phrase.** naming the axiom, then states
  what it means and what it forbids. Two to four axioms is typical.

  An axiom is load-bearing if violating it would silently corrupt the domain —
  not a style preference. State the truth source, the projection rule, and what
  is *not* overridable. The frozen-models axiom below is paradigm-level and
  copies through to every TCA project unchanged.

  **Frozen models.** Every model is `frozen=True` except the single active model
  per bounded context. Construction is proof. Derivation's home is the model.
-->

## Key Constraints

{{KEY_CONSTRAINTS}}

<!--
  *(project-specific)*. Bulleted list. Each bullet states a forbidden construct
  or a hard rule, optionally followed by parenthesised spec/invariant tags
  from this project's spec system. State the construct first, then the
  positive replacement, then the tags.
-->

## When the shape is wrong

Imperfection in existing code is not deferrable work. The codebase admits no state where a known wrong shape persists alongside other work. Rule coverage of the pattern IS the precondition for the code edit, not its sequel. "Later" has no home.

## What Goes Where

- **This file** — the protocol, project identity, project-specific architecture and constraints.
- **`.claude/rules/`** — correct shapes per file type. Proof hierarchies, Evaluation Model template, smart-method patterns, semantic-surface doctrine, gate rubrics.
- **`.claude/skills/`** — invocable cognition: `shape-match`, `proof-design`, `construction-voice`, `forge-the-link`, `bounded-adjudication`.
- **`.claude/settings.json` hooks** — mechanical enforcement. Pre-edit fast-fail + post-edit gate.
{{EXTRA_LOCATIONS}}

<!--
  *(project-specific)*. Additional pointers — type catalog JSON, doctrine
  narrative, internals notes, reference program, spec system, etc. Each line
  is a bullet of the form:
    - **`path/to/thing`** — one-line description.
-->
