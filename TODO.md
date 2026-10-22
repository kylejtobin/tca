# TODO

Not built, in order. The design for each is in `docs/decisions/`; the developer's side is `.agents/skills/tca-python-dev/SKILL.md`.

## Now
### Task 1: Establish the declaration-driven construction model - Done

### Task 2: Make computational results authoritative through native construction - Done

### Task 3: Runtime Construction and Execution Integrity - Not Done

Complete runtime construction using the occurrence model established in Task 1.

Ensure nested scopes, repeated occurrences, alternatives, and newly available evidence construct correctly without procedural source selection or duplicated dependency resolution.

Verify execution context, structured concurrency, cancellation, and connection lifecycles. Use standard Python primitives, including `TaskGroup`, `contextvars`, and `AsyncExitStack`, where they materially improve correctness or simplify the engine.

Preserve occurrence identity, provenance, diagnostics, and OpenTelemetry context throughout execution, including failure and cancellation.

**Outcome:** A deterministic, occurrence-driven runtime with correct execution and resource lifecycles.

### Task 4: Route-Local Proof and Construction Soundness - Not Done

Make symbolic proof and runtime construction agree on what can be constructed, from which premises, and under which conditions.

Proof must derive its conclusions from the same Pydantic declarations and binding semantics used by runtime. Preserve collection cardinality, alternatives, conditional evidence, and occurrence-specific dependencies.

Eliminate class-global assumptions, false ambiguities, invented evidence, and duplicated proof logic.

**Outcome:** Route-local proof accurately represents the construction possibilities and constraints of each route.

### Task 5: Occurrence-Bound Effect Authorization - Not Done

Ensure every executable effect is authorized by valid evidence belonging to the correct occurrence.

Use the occurrence identity and provenance established in Task 1 and the proof semantics verified in Task 4. Authorization must remain correct across repeated entities, conditional facts, mutually exclusive outcomes, and alternative construction paths.

Prevent unrelated, missing, or refuted evidence from authorizing an effect. Keep authorization declarative rather than introducing a procedural policy engine.

**Outcome:** Effects execute only when their actual premises establish the required authority.

### Task 6: Complete Declarative CLI Projection - Not Done

Derive the CLI from the program's Pydantic declarations without introducing a parallel input schema.

Support the relevant scalar, vocabulary, value, union, collection, optional, and nested structures. Preserve Pydantic validation, meaningful errors, and consistent Python, JSON, and CLI semantics.

Ensure computed values remain non-writable and execution-specific details remain properly separated from developer-facing inputs.

**Outcome:** A complete, type-driven CLI that faithfully exposes the program's declared interface.

### Task 7: End-to-End Verification and Engine Simplification - Not Done

Verify the complete framework across construction, proof, execution, effects, interfaces, and failure paths.

Test repeated and nested occurrences, conditional evidence, invalid inputs, computation, concurrency, cancellation, partial resource initialization, and cleanup.

Verify occurrence provenance, actionable diagnostics, OpenTelemetry trace continuity, and optional Logfire interoperability across ordinary Python execution and Pydantic validation.

Remove superseded abstractions, compatibility machinery, duplicate validation paths, dead code, and obsolete tests. Reconcile architecture documentation with the final design.

**Outcome:** A coherent, production-ready type-construction engine with one authoritative declarative model and minimal necessary machinery.

## Next

1. Bind the feature files with pytest-bdd, so every scenario in `packages/python/*/tests/features/*.feature` and `tests/features/smell_check.feature` runs as a test. Step definitions live in each package's `tests/`, one module per feature file, with a parametrized step for each sentence shape that repeats, such as "ValidationError is raised with type {type} at loc {loc}". Add `pytest-bdd` to the dev group. Order of work: `scalar.feature` and `kinds.feature`, which need only the world; the other world features and `smell_check.feature`; then `engine.feature`; then `cli.feature`.

## Later

1. The HTTP kind (0015, 0016, 0023, 0045): `Http`, `Keyed`, `Post`, `Get` with `perform(self)` sending through the `httpx.AsyncClient` held in `self.party`'s `PrivateAttr` and returning `hear(self, response.text)`; one FastAPI path operation per route with `Q` as the body and `answered.reply` as the response, served inside `opened`; the standard OpenTelemetry instrumentations for httpx and FastAPI. Its scenarios in the http package's `tests/features/`, with httpx's `MockTransport` as the party.

