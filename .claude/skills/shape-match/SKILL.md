---
name: shape-match
description: "Load the correct TCA shape before generating code. Hooks catch violations after writing — this skill prevents them by loading the generation target before you start. Counteracts training gravity toward procedural Python."
license: MIT
compatibility: "Any TCA project with .claude/rules/ shape definitions"
metadata:
  author: kylejtobin
  version: "2.0.0"
---

# Shape Match

Hooks catch violations after you write. This skill prevents them by loading the correct shape before you start.

Training data is 99% procedural Python — services, mappers, dict-builders, if/elif routers. Without an explicit counter-target loaded into working context, generation follows training gravity. The correct TCA shape must be the immediate reference, not a remembered principle.

## Activation Scope

This skill MUST fire:
- Before writing any file in `domain/`
- Before writing any new model class anywhere
- When the user invokes `/shape-match` or says "check shapes"

Domain code is where training pulls hardest. In typical Python, domain logic is procedural code that uses models. In TCA, domain logic IS model construction. Without this skill loaded, you will generate typical Python.

## Protocol

### 1. Classify the file

| File | What it IS |
|---|---|
| `type.py` | Scalars. `RootModel[base]` + `frozen=True` + `Field()`. Imports nothing from project. |
| `value.py` | Value objects. `BaseModel` + `frozen=True` composing scalars from `type.py`. |
| domain `[concept].py` | Frozen model. `frozen=True` + `from_attributes=True`. Fields are domain scalars. Derivations are `@computed_field` + `@cached_property`. |
| domain active model | Single unfrozen `BaseModel` per context. State evolves through model operations. One per context. |
| `api.py` in domain | Route contracts. Frozen request/response models. Domain-owned. |
| `service/*.py` | Transport shim. One class, one connect. Binds transport to active model. Zero domain logic. |
| `api/*.py` | Route file. Imports contracts from `domain/context/api.py`. Defines nothing. Computes nothing. |
| `main.py` | Composition root. Builds dependencies. No domain logic. |

### 2. Load the rule

If `.claude/rules/` contains a rule for this file type, read it now. The rule specifies what the file CONTAINS, what it IMPORTS FROM, and what it MUST NOT contain.

If no rule exists, the shape is the classification above.

### 3. Generate against the shape — not against training

Hold the loaded shape as the generation target. For each construct, verify it matches BEFORE writing:

**Scalars (`type.py`):**
- Every type is `RootModel[X]` with `frozen=True`
- Every field has `Field()` constraints
- No imports from the program — stdlib and third-party only
- No methods, no validators, no logic

**Frozen domain models:**
- Fields are domain scalars — never bare `str`, `int`, `float`, `Decimal`
- Derivations are `@computed_field` + `@cached_property` — never standalone functions
- Validators are `model_validator(mode="after")` for irreducible cross-field invariants ONLY — invoke `/proof-design` first

**Composed/gate models:**
- Fields are PROVEN types (narrowed scalars) — not raw observations
- Construction of the model IS the proof that invariants hold
- `@cached_property` derivations produce domain events/intents
- No boolean gate fields — the field TYPE is the gate

**Services:**
- One class. One connect function. Transport setup only.
- No domain logic. No computation. No classification. No derivation.

**Routes:**
- Import contracts from `domain/context/api.py`
- No model definitions. No computation.

### 4. Post-generation verification

After writing, check every construct against the shape:

| Check | If violated |
|---|---|
| Field typed as bare `str`/`int`/`float`/`Decimal`? | Use a domain scalar from `type.py` |
| Derivation in a standalone function? | Move to `@computed_field` + `@cached_property` on the model |
| Validator on a single-field condition? | Replace with narrowed scalar + `Field()` — invoke `/proof-design` |
| `@computed_field` + `@property` on frozen model? | Use `@cached_property` |
| `json.loads()` + `model_validate()`? | Use `model_validate_json(raw_bytes)` |
| Import direction reversed? | Domain toward edge, never the reverse |
| File named for a technology pattern? | Rename for the domain concept |
| Service containing domain logic? | Move to a model derivation or the active model |

## Training Gravity — Know What Pulls

These are the patterns your training data will generate by default. Each has a TCA shape that replaces it entirely. Knowing the pull is the first defense.

| Training default | TCA shape | Why training wins without this skill |
|---|---|---|
| Service class with methods | Frozen model with `@cached_property` | Most Python "domain logic" lives in services |
| Function computing from model fields | `@computed_field` on the model | Functions are the default unit of work |
| Dict-building before construction | Composed model with proven field types | Dicts are Python's universal intermediate |
| if/elif on a string field | `Field(discriminator=...)` on a union | String matching is ubiquitous in training |
| Mapper class between models | `model_validate(source, from_attributes=True)` | Mapper/adapter is a standard enterprise pattern |
| Utility module of helpers | Derivations on their owning models | `utils.py` exists in nearly every Python project |
| Validator checking a constant bound | Narrowed scalar with `Field(gt=X)` | Validators are the "obvious" Pydantic tool |
| `@property` on frozen model | `@computed_field` + `@cached_property` | `@property` is the Python default |
