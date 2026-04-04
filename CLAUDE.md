# Claude Instructions

This file is intentionally modular.

Most of it should be reusable across TCA projects. The section that should change most from repo to repo is `Project Identity`.

## Project Identity

This repository develops and documents Type Construction Architecture.

The goal here is not only to explain TCA, but to build examples, docs, and agent architecture that actually preserve TCA during generation. This repo is therefore both:

- a theory surface
- a working anti-drift environment for building in that theory

When working here, assume the quality bar is architectural. Good output is not merely valid Python or coherent prose. Good output strengthens TCA as a programming paradigm and resists the patterns that usually weaken it.

## Core Drift Warning

The main failure mode is not misunderstanding TCA in chat. The main failure mode is generation drift while producing code.

Two drifts matter most:

1. procedural fallback
2. flat modeling

Procedural fallback means helper functions, service logic, mapping layers, branching code, and free procedure appearing where stronger structure should have carried the work.

Flat modeling means collapsing named domain meaning into `str`, `dict`, `Any`, `object`, loose primitives, and other generic shapes where sharper domain types should exist.

## Default Response

When in doubt:

- model more
- name the concept
- strengthen the type
- use wiring, dispatch, and projection instead of free procedure
- keep procedure only at irreducible seams

Do not solve design weakness with casts, suppressions, ignores, or generic containers.

Every error is a design error. The fix is always more modeling. Never less.

## Build In TCA Mode

Use these defaults unless the domain proves otherwise:

- the model is the program
- construction is proof
- frozen models carry certainty
- `domain/context/` is the home of the program
- API and service layers are transport and plumbing
- derivation belongs on the model that owns the proven fields
- discriminated unions replace branching on tags or categories
- named products replace anonymous dictionaries
- enums, wrappers, and constrained types replace bare primitives for named concepts

## Use The Shared Frame

Do not duplicate the TCA reasoning frame into every prompt or workflow surface.

This repository uses a rules-first, hook-driven Claude architecture:

- `.claude/rules/` carries the shared cognitive frame
- `.claude/settings.json` runs edit audits after generation
- `.claude/README.md` explains the Claude architecture itself

Treat those files as the primary operational surface for keeping Claude aligned during generation.
The reusable scaffold is not this file alone. It is this file plus the minimal `.claude/` package.

## Read Next

If you need deeper grounding while working:

- `docs/manifesto.md` for the why
- `docs/overview.md` for the front door to the theory
- `docs/irreducible-seams.md` for where procedure belongs
- `tca/building_block.py` for a concrete TCA program

## Reuse Pattern

If this setup is copied into another TCA repository:

- copy `CLAUDE.md`
- copy the minimal `.claude/` directory with it
- rewrite `Project Identity`
- keep the drift warning unless the target repo has a sharper known failure mode
- keep the default response unless the target repo has stronger local discipline
- update the reading pointers to that repo's theory and example surfaces

The point of this file is to keep the always-on frame compact, reusable, and anti-drift. The point of the accompanying `.claude/` directory is to help Claude actually stay in that mode while generating.
