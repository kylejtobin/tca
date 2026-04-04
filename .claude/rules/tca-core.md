# TCA Core Frame

This project uses Type Construction Architecture. The main failure mode is not misunderstanding TCA in chat. The main failure mode is generation drift while writing code.

Two drifts matter most:

1. Procedural fallback
2. Flat modeling

## Fight procedural fallback

Watch for these signs:

- module-level helper functions coordinating domain work
- service methods that map, enrich, branch, classify, or sequence what models should own
- `if`/`elif` or `match` dispatch on tags, types, or categories
- intermediate dictionaries or adapter layers between named types
- derivations performed outside the model that owns the proven fields

Default fix:

- strengthen the model
- use fields and `from_attributes` for wiring
- use enums and discriminated unions for classification
- use projections for derivation and orchestration
- keep procedure only at irreducible seams

## Fight flat modeling

Watch for these signs:

- bare `str`, `dict`, `list`, `Any`, `object`, or loose primitives for named domain concepts
- dictionaries crossing boundaries without named products
- string categories that should be enums or `Literal` tags
- unstructured blobs where the cases or fields are already known
- generic containers where the domain has a sharper shape

Default fix:

- name the concept
- build wrappers, products, enums, discriminated unions, and root models
- prefer constrained or domain-specific types over bare primitives
- prefer immutable shapes

## Build the program the TCA way

- start from the app world and model everything the program needs to know
- `domain/context/` owns the program
- API and service layers are transport and plumbing, not the home of logic
- the model is the program: construction, classification, derivation, projection
- construct certainty, then derive further certainty
- a seam is acceptable only when it normalizes foreign input into owned truth and cannot be eliminated by stronger modeling
- seams must be irreducible, contained, terminal, and justified

## Review standard

When reviewing or auditing edits:

- prioritize structural failures over style
- call out procedure where structure should exist
- call out flat primitives where domain types should exist
- name the exact construct introduced
- say what stronger model or construct should replace it
- do not recommend casts, suppressions, or workarounds

Every error is a design error. The fix is always more modeling. Never less.
