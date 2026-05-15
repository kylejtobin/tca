# Claude Instructions

This file plus the `.claude/` directory form the reusable scaffold for any TCA project.

The hooks and rules enforce TCA structurally through a closed evidence vocabulary. This file carries what evidence matching alone cannot: the judgment defaults that resolve ambiguity when the gates escalate.

## Project Identity

This repository develops and documents Type Construction Architecture.

It is both a theory surface and a working enforcement environment. The quality bar is architectural — good output strengthens TCA as a programming paradigm, not just produces valid Python.

## When The Gates Escalate

The hooks and gate rubrics handle clear cases structurally. When classification is ambiguous, these defaults resolve it:

- the type system is the semantic layer — the model is the program
- construction is proof — derivation extends proof
- unknown outcomes are typed possibility spaces, not procedural control state
- procedure belongs only at irreducible seams
- every error is a design error — the fix is always more modeling, never less

When choosing between constructs:

- `RootModel` and focused `BaseModel` over bare primitives
- `Field(...)`, `Annotated`, aliases, `Literal`, `Field(discriminator=...)` before validators or free procedure
- `model_validate`, `model_validate_json`, `from_attributes` for staged lifting and wiring
- `@computed_field`, `@cached_property`, `@property` for intrinsic derivation
- `model_validator(mode="before")` or `mode="wrap"` only at irreducible boundaries
- `mode="after"` or `field_validator` only when proof cannot be carried declaratively

Do not solve design weakness with casts, suppressions, ignores, generic containers, or stringly control state.

## The Scaffold

The `.claude/` directory enforces TCA through evidence matching, not cognitive framing:

- **Gate rubrics** (`.claude/rules/gate-rubrics.md`): three gates — Type Integrity, Construction Carries Meaning, Program Shape — each with allowed shapes, disallowed shapes, approved mechanisms, and escalation triggers
- **Path-scoped rules** (`.claude/rules/`): six rules scoped to program layers (`type.py`, `value.py`, `domain/`, `api/`, `service/`, `main.py`)
- **Hooks** (`.claude/settings.json`): five hooks forming a pipeline — `UserPromptSubmit` loads the evidence vocabulary, `PreToolUse` fast-fails against 11 invariants, `PostToolUse` adjudicates against gate rubrics, `Stop` and `SubagentStop` check output for disallowed shapes
- **Bounded adjudication** (`.claude/skills/bounded-adjudication/`): the skill that generated the gates, rubrics, and hooks through a structured worksheet

The hooks are the enforcement system. They are not optional.

## Local Reading Pointers

- `README.md` — front door
- `docs/build-patterns.md` — 13 before/after build patterns
- `docs/program-topology.md` — where each file belongs
- `docs/manifesto.md` — the why
- `docs/overview.md` — spec map
- `docs/irreducible-seams.md` — where procedure belongs
- `tca/building_block.py` — a concrete TCA program

## Reuse

To adapt this scaffold to another TCA project:

1. Copy `CLAUDE.md` and the `.claude/` directory
2. Rewrite `Project Identity`
3. Replace `Local Reading Pointers` with the new repo's surfaces
4. Run the bounded adjudication skill to generate domain-specific evidence shapes, gates, and hooks
