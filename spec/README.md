# TCA Spec System

The planning artifacts that precede any code. The **TCA Spec System** is the *logic architecture layer* of a TCA project: the structural model of what is true, what makes it true, and where the proof lives. It is distinct from execution architecture (services, transports, persistence) and physical architecture (deployment topology). Most artifacts called "architecture" describe how components are wired or how quality attributes are met. This one describes the proof graph — load paths for guarantees, not for forces.

The spec is upstream of the type system: the type catalog, the `.claude/` rule files, and the domain models all derive from what is written here. Nothing downstream is sound if the spec is wrong.

## Artifacts

- **`01-foundation-spec.md`** — the template. A new project fills this out section by section.
- **`02-foundation-spec-refactor.md`** — the procedure for sharpening an existing spec when invariants have accumulated ad hoc.
- **`03-type-catalog-extraction-worksheet.md`** — the derivation from a completed spec to the type catalog the codebase contains.

## Schema

The spec has eight layers. Each derives from the one above. An entry that does not trace back through the hierarchy does not belong.

1. **Scope** — what the system IS, what it IS NOT, the constraints of its operating environment. Prevents downstream argument against the wrong frame.
2. **Strategy** — how the system achieves its objective. Stated in a form explicable without reference to technology.
3. **Conditions** — every real-world problem the system must handle. The exhaustive list of what can go right and what can go wrong inside the chosen scope.
4. **Proof Hierarchy Classification** — the proof mechanisms available and their relative strength: field constraint on a narrowed scalar, narrowed type as field on a composed model, derivation returning a typed result variant, impossible-composition validator, handler-gated absence. Classification precedes shape selection.
5. **Premises** — architectural axioms that govern every invariant. The non-negotiable assumptions all downstream design rests on.
6. **Configuration Models** — runtime parameters decomposed by owner and change cadence. Configuration is typed and validated at construction; this layer names what is parameterized versus constant.
7. **Domain Invariants** — what must be true, where it is enforced, how it is proven, which condition it addresses, why. Each invariant names its proof level from layer 4 and its condition from layer 3.
8. **Coverage** — verification that every condition has an invariant, every invariant traces to a condition, every invariant's proof level is the strongest the hierarchy admits.

## How to use it

**Top-down to build.** Fill Scope first. Derive Strategy from Scope. Exhaustively name Conditions inside Strategy's frame. Classify the proof mechanisms available. State the Premises that govern. Name what is configuration. Write the invariants. Close with Coverage.

**Bottom-up to validate.** Every line of generated code traces to an invariant; every invariant to a condition; every condition to the Strategy; the Strategy to the Scope. Coverage is the artifact that closes the loop.

The order is not stylistic. A condition discovered after the invariants are written is a sign the scope was too narrow — the spec restarts at the layer where the gap appeared. A premise added to justify an invariant is the same signal. A configuration parameter introduced mid-implementation belongs in layer 6, not in the code that consumes it.

## Lineage

The TCA Spec System is a synthesis. Its parts come from different traditions, and none of the major named methodologies do all of them at once.

- **Sectioned planning form** (Scope, IS-NOT, venue constraints, Strategy) — conventional product-spec lineage: IEEE 830 SRS, Arc42, Joel Spolsky's spec template.
- **Conditions and Coverage matrix** — safety-critical engineering. DO-178B (avionics), ISO 26262 (automotive), IEC 61508 (industrial). The "every condition has an invariant; every invariant traces to a condition" rule is the formal traceability matrix from those domains.
- **Premises as architectural axioms** — TLA+ assumptions, DDD core-domain hypotheses, Parnas-style module specifications. The placement between conditions and invariants (not above scope, not below invariants) is the unusual choice.
- **Proof Hierarchy Classification** — the distinctive piece. Synthesis of Design by Contract (Meyer), Parse-Don't-Validate (Alexis King), refinement calculus / Hoare logic, and Pydantic v2's construction-as-proof mechanic. The Level 1→4 ordering is a constructive-types reading of "where does proof live?" It does not appear as a named hierarchy in any single methodology.
- **Configuration Models** — 12-factor app + typed settings discipline (Pydantic Settings).
- **Domain Invariants with a named home** — Design by Contract + Parnas information hiding.

The combination is closest to what could be called *constructive specification* or *type-driven specification*: the form is requirements-engineering, the coverage discipline is safety-critical, the proof mechanism is constructive type theory, the substrate is Pydantic.

## Why this is feasible now

The artifacts the TCA Spec System asks for — exhaustive condition enumeration, every invariant classified by proof mechanism, full forward and backward traceability, every configuration parameter consumed by a named handler — have historically been affordable only to teams that could fund dedicated requirements engineers. Aerospace-grade traceability is the canonical example: a small fleet of specialists maintaining the matrix across years of system evolution.

The artifacts are no easier to write by hand today. What changed is the cost of maintaining them. An AI assistant can:

- propose the initial classification of an invariant onto the proof hierarchy and challenge weaker placements
- detect when a Level-3 validator is actually a Level-1 unforged or a decision in disguise
- rebuild the coverage matrix automatically as invariants and conditions evolve
- flag orphan invariants and uncovered conditions during edits, at the hook level
- enforce the upstream-downstream order (condition first, then invariant, then code) before generation begins

The human's role is judgment — does this condition belong, is this premise correct, is the venue described accurately, is this invariant at its strongest admissible level. The mechanical work — classification, matrix maintenance, drift detection, trace lookups — moves to the assistant.

The same shift makes TCA's type discipline feasible. Modeling every domain value as a narrowed scalar, every composed truth as a frozen model, every decision as a typed result variant is more code than the procedural equivalent. But the code is shape-regular, derivable, and verifiable — exactly the shape an AI assistant scaffolds well. The cost of declaring everything used to be the discipline's killer; declaration is now cheap.

The result is a **certainty upside** small teams could not previously reach: every guarantee in production traces through a documented proof mechanism back to a named condition the system was specified to handle. The matrix is closed. The drift surface is bounded. The cost of that closure used to be a specialist department.

## Output

A completed spec yields:

- An invariant list with proof-level annotations — the input to `03-type-catalog-extraction-worksheet.md`.
- A type catalog — every narrowed scalar, value object, composed model, discriminated union, and evaluation model the domain layer admits.
- Path-scoped rule files in `.claude/rules/` — the per-file shape definitions the hooks adjudicate against.

Nothing in the codebase exists without a path back to this directory.
