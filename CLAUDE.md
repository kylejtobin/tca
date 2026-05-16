# CLAUDE.md

**Do not simulate execution — declare what exists.**

## Construction Engine Mode

You think in types, not steps. A type's existence is its proof. A field declaration is a proof obligation. One construction call resolves the entire proof graph.

**You do NOT orchestrate construction. You DECLARE fields. If you catch yourself writing "first... then... finally..." about construction, you are thinking in procedure and the code will follow.**

**You do NOT validate and discard. You PARSE into narrower types. If you catch yourself writing a model_validator that checks one field against a constant, a narrowed scalar with Field() carries that proof structurally. Forge the type.**

When confused: "What type, if it existed, would make this problem structurally impossible?" Forge that type.

When ambiguous, these defaults resolve it:
- the type system is the semantic layer — the model is the program
- construction is proof — derivation extends proof
- unknown outcomes are typed possibility spaces, not procedural control state
- procedure belongs only at irreducible seams
- every error is a design error — the fix is always more modeling, never less

When choosing between constructs:
- `RootModel` and focused `BaseModel` over bare primitives
- `Field(...)`, `Annotated`, aliases, `Literal`, `Field(discriminator=...)` before validators or free procedure
- `model_validate`, `model_validate_json`, `from_attributes` for staged lifting and wiring
- `@computed_field` + `@cached_property` for intrinsic derivation on frozen models
- `model_validator(mode="before")` or `mode="wrap"` only at irreducible boundaries
- `mode="after"` or `field_validator` only when proof cannot be carried declaratively

## Proof Hierarchy

Every invariant has a strongest proof. Use it. Never reach for a weaker level.

| Level | Shape | When |
|-------|-------|------|
| 1. Field constraint | `Field(gt=2.0)` on `RootModel` | Static bound. Type existence IS proof. |
| 2. Narrowed type construction | `LineNumber(raw_value)` | Lifting observation → proven type. Pydantic Rust validator does the work. |
| 3. Cross-field validator | `model_validator(mode="after")` | Composed fields whose values are *structurally impossible together* — e.g., `StateTransition(Terminal, ChildAdded)`. NOT business thresholds (those are derivations returning a result DU like `GateResult = GatePassed \| GateRejected`). Must name which fields and why levels 1-2 fail. |
| 4. Handler gating | Model's absence | External state (halt, connection). Not a field — existence is proof. |

A validator referencing one field against a constant is a level-1 proof you failed to forge.

## Wrong → Right

**Validator that should be a narrowed type:**
```python
# WRONG: validating what Field() can prove
@model_validator(mode="after")
def _check_line(self) -> Self:
    if self.line < 1:
        raise ValueError("line must be positive")
    return self

# RIGHT: narrowed scalar carries the proof
class LineNumber(RootModel[int], frozen=True):
    root: int = Field(ge=1)
# Smell takes LineNumber as field type — construction proves it
```

**Narrating steps vs declaring structure:**
```python
# WRONG: orchestrating construction as procedure
line = LineNumber(node.lineno)
location = SourceLocation(line=line, class_name=cls.name)
smell = Smell(invariant_name="X", message="...", location=location)

# RIGHT: one construction call, field types carry obligations
smell = Smell(
    invariant_name="X",
    message="...",
    location=SourceLocation(line=node.lineno, class_name=cls.name),
)
# Pydantic constructs LineNumber inside SourceLocation during field validation
```

**Escaped derivation vs model-owned:**
```python
# WRONG: function computing what belongs on the model
def render_smell(name: str, message: str, location: SourceLocation) -> str:
    return f"{name}: {message} ({location.qualified})"

# RIGHT: derivation lives on the model
class Smell(BaseModel, frozen=True):
    invariant_name: str
    message: str
    location: SourceLocation

    @cached_property
    def rendered(self) -> str:
        return f"{self.invariant_name}: {self.message} ({self.location.qualified})"
```

## Failure Modes and Their Cures

**Validator-first.** Your instinct is `model_validator`. A `model_validator` without an irreducibility justification from `/proof-design` is unfinished code. `/proof-design` IS how invariants are classified into the proof hierarchy. Every validator names its two irreducible fields or it does not exist.

**Procedural drift.** Your training corpus is 99% procedure. Code without `/shape-match` drifts toward training defaults. `/shape-match` IS the correct TCA shape loaded as generation target. Domain code matches the shape in `.claude/rules/`, not the shape in training data.

**Language infection.** Procedural words produce procedural code. Text containing "extract," "check," "handle," "process" is infected. `/construction-voice` IS the structural rewrite — declarations of what types ARE, what files CONTAIN, what existence PROVES. Infected text does not ship.

## What This Is

This repository develops and documents Type Construction Architecture.

It is both a theory surface and a working enforcement environment. The quality bar is architectural — good output strengthens TCA as a programming paradigm, not just produces valid Python.

Python 3.12+ / Pydantic v2 / basedpyright.

`tca/building_block.py` is the reference program — a recursive Pydantic type tree walker that classifies any BaseModel's entire construction graph. One `model_validate` at the root fires the cascade. Two self-classifying wrappers, two discriminated unions, demand-driven recursion, zero if-chains. Study it before writing TCA code.

## When Architecture Must Be Wrong

If you find ANY imperfection in existing code — stop all work. Fix it NOW. Do not queue. Do not defer. Do not say "we could do this later." Fix rules first (verify they catch the pattern), then fix code.

## What Goes Where

- **This file** — cognitive mode, proof hierarchy, failure modes. Shapes how you think.
- **`.claude/rules/`** — correct shapes per file type. What each file IS and CONTAINS.
- **`.claude/scripts/smell.py`** — deterministic post-edit fast-fail. No LLM judgment. Catches: `type.py` importing from project, `value.py` importing from non-`type.py`, technology-named files in `domain/`, dumping-ground filenames in `domain/`, `@computed_field` + `@property` on frozen models, `json.loads` + `model_validate`, mutables inside `@cached_property`/`@computed_field`, `try`/`except` in domain models, void `-> None` methods on domain models, `@staticmethod`/`@classmethod` on domain models, multi-value `Literal[str]` (use StrEnum), domain imports from `service`/`api`, parallel tuple fields, private methods on domain models. Each smell is named for the invariant class that fired it.
- **`.claude/settings.json` hooks** — pipeline: LLM pre-edit fast-fail on diff-visible patterns → `smell.py` post-edit on full file → LLM agent gate adjudication.
- **`.claude/skills/`** — `/proof-design`, `/shape-match`, `/construction-voice`, `/bounded-adjudication`.
- **`docs/`** — manifesto, pydantic machinery, build patterns, program topology, irreducible seams.
- **`tca/building_block.py`** — the working reference program.

## Reuse

To adapt this scaffold to another TCA project:

1. Copy `CLAUDE.md` and the `.claude/` directory
2. Rewrite `What This Is` with project identity, commands, and domain constraints
3. Replace reading pointers with the new repo's surfaces
4. Run `/bounded-adjudication` to generate domain-specific evidence shapes
