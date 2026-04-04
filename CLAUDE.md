# Claude Instructions

This file is intentionally modular.

Treat it as the always-on charter for a TCA project. The reusable scaffold is not this file alone. It is this file plus the minimal `.claude/` package.

## Universal TCA Frame

The main failure mode is not misunderstanding TCA in chat. The main failure mode is generation drift while producing code.

Do not trust momentary confidence over this frame. Extended generation drifts toward default training. The reusable Claude scaffold exists to force repeated self-correction before, during, and after that drift.

The universal defaults are:

- the type system is the semantic layer
- the model is the program
- construction is proof
- derivation extends proof
- unknown outcomes should become typed possibility spaces, not procedural control state
- procedure belongs only at irreducible seams that capture, normalize, trigger, or resume construction

When in doubt:

- model more
- name the concept
- strengthen the type
- prefer `RootModel` and focused `BaseModel` over bare primitives
- prefer `Field(...)`, `Annotated`, aliases, `Literal`, and `Field(discriminator=...)` before validators or free procedure
- prefer `model_validate`, `model_validate_json`, and `from_attributes` for staged lifting and wiring
- prefer `@computed_field`, `@cached_property`, and `@property` for intrinsic derivation
- use `model_validator(mode="before")` or `mode="wrap"` only at irreducible boundaries; use `mode="after"` or `field_validator` only when the proof cannot be carried more declaratively
- keep effects small, terminal, and justified

Do not solve design weakness with casts, suppressions, ignores, generic containers, semantic controllers, or stringly control state.

Every error is a design error. The fix is always more modeling. Never less.

## Project Identity

This repository develops and documents Type Construction Architecture.

The goal here is not only to explain TCA, but to build examples, docs, and agent architecture that actually preserve TCA during generation. This repo is therefore both:

- a theory surface
- a working anti-drift environment for building in that theory

When working here, assume the quality bar is architectural. Good output is not merely valid Python or coherent prose. Good output strengthens TCA as a programming paradigm and resists the patterns that usually weaken it.

## Optional Local Reading Pointers

These are optional deepening surfaces for this repository. They are not required for the reusable scaffold to behave correctly:

- `README.md` for the front door and build path
- `docs/manifesto.md` for the why
- `docs/overview.md` for the spec map
- `docs/irreducible-seams.md` for where procedure belongs
- `tca/building_block.py` for a concrete TCA program

## Use The Shared Frame

Do not duplicate the TCA reasoning frame into every prompt or workflow surface.

This repository uses a rules-first, hook-driven Claude architecture:

- `.claude/rules/` carries the shared cognitive frame
- `.claude/settings.json` runs prompt-time reminders, edit audits, and stop-time self-reflection hooks
- `.claude/skills/` holds a few real Claude skills for reusable TCA workflows
- `.claude/README.md` explains the scaffold itself

Treat those files as the primary operational surface for keeping Claude aligned during generation. The hooks are not optional optimization. They are part of the safety system.

## Reuse / Adaptation Instructions

If this setup is copied into another TCA repository:

1. copy `CLAUDE.md`
2. copy the minimal `.claude/` directory with it
3. rewrite `Project Identity`
4. replace `Local Reading Pointers` with that repo's theory and example surfaces
5. keep the universal anti-drift frame unless the target repo has a stronger proven alternative
6. add or sharpen project-specific rules only when the new repo has a sharper known drift than the default set

The point of this file is to keep the always-on frame compact, reusable, and anti-drift. The point of the accompanying `.claude/` package is to help Claude actually stay in that mode while generating.
