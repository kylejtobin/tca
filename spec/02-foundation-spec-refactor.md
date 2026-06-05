# Foundational Program Design: Refactor Strategy

A procedure for reducing accidental complexity in a validated spec while preserving all
essential coverage. As simple as possible, no simpler. Use it after a foundation spec
(Scope, Strategy, Conditions, Construct Classification, Premises, Configuration Models,
Domain Invariants, Coverage) has been validated green: every condition has invariants,
every invariant traces to a condition and names its carrying construct, every invariant
has a home, every config parameter is consumed.

The goal is: all the complexity you need, nothing you don't. Make things as simple as
possible, but no simpler. Refactor operates on two axes — **shape** (multiple invariants
collapsing to one general proposition) and **construct fit** (each invariant carried by
its strongest, most-structural construct, so the illegal state is unconstructable rather
than rejected after the fact). Both axes are tested before the refactor is declared done.

---

## Step 1: Tag by Shape

Read every invariant. Ignore the specific nouns (which construct, which event, which
entity). Ask: what is the structural pattern this proposition expresses?

Common shapes:

- **Decision:** Measure or compose X, and the outcome forks. The fork is not "X passes /
  X fails" — both outcomes construct. One variant carries the acted-on result, one
  carries the withheld result; nothing "fails," a different variant lands.
- **Lifecycle:** A thing passes through a closed set of states, each its own variant;
  the transition is a new construction, never a mutation of the old one.
- **Schema:** A frozen model enforces a constraint at construction. Invalid data has no
  representation and cannot enter the stream.
- **Delegation:** The result of a computation is implied by the construct that owns the
  inputs — the derivation on model X implies its result; no outside actor recomputes it.
- **Circuit breaker:** The live world's readiness is a precondition the active model
  holds; it constructs the fact only when the world is ready, and stands down otherwise.
- **Reconciliation:** When in-process truth may have diverged from external reality, the
  active model queries the world and constructs the discovered fact anew.
- **Threshold:** Measure X, require persistence over a window, then the outcome forks
  into result variants.
- **Independence:** The derivation on model X implies its result from X's own fields;
  no second construct can reach in and override what construction already settled.
- **Valuation:** A specific scalar (not another) is the input to a specific derivation.
- **Suppression:** During condition W, the decision lands the withheld variant; the
  suppression is a variant of the result union, not a flag checked at the edge.

Tag each invariant with its shape. Use whatever labels fit your domain. The labels above
are domain-flavored starting points, not a taxonomy.

**Template:**

{invariant-name}: {shape}. {one-sentence summary ignoring specific nouns}

---

## Step 2: Group by Shape

Collect invariants with the same shape tag. These are your candidate clusters.

Clusters with one member have no refactoring opportunity. Move on.

Clusters with two or more members are candidates for collapsing or principle extraction.

---

## Step 3: Write Candidate Abstractions

For each multi-member cluster, write the general proposition that all members are
instances of.

**Template:**

Candidate: {general proposition}

Members: {invariant-name-A}, {invariant-name-B}, ...

---

## Step 4: Test Coverage

Walk the candidate against every condition its members currently govern.

For each condition, ask: does the general proposition still cover this condition? Is any
condition left without an invariant if the specific members are replaced by the general
form?

If any condition loses coverage, the abstraction leaks. Stop.

**Template:**

Candidate: {general proposition}

Condition {X}: covered by {which clause of the general form}

Condition {Y}: covered by {which clause of the general form}

Condition {Z}: NOT COVERED \- abstraction leaks

---

## Step 5: Test Precision

Walk the candidate against the premises, specifically the one that says every invariant
must have a home (a named construct, a specific input, a specific output).

Ask: can the general proposition still name the construct that carries it — the frozen
model whose derivation implies it, or the active model that constructs the fact? Or has
it become a floating decree that no single construct carries?

If it can name a construct: precision holds. If it spans multiple constructs with
different inputs: precision is lost.

**Template:**

Candidate: {general proposition}

Home: {construct} on {input} constructing or refusing to construct {output}

Precision: HOLDS / LOST (because {reason})

---

## Step 6: Test Construct Fit

A refactor is not complete if an invariant is carried by a weaker, less-structural
construct than the strongest one it admits. For each invariant — collapsed candidates
and untouched survivors alike — reclassify against the closed construct set in the
Construct Classification of the foundation spec. There is one proof, construction, and
the only question is shape-fit: which construct *is* this, pushed as far toward the
structural as it will go, so the illegal state is unconstructable rather than rejected.

Ask: is this invariant carried by the most structural construct it admits?

- **A cross-field or after-the-fact validator — there is no validator.** An invariant
  written as a check that two or more fields agree is asserting that some compositions
  are impossible. An impossible composition is a **union** of the legal variants: the
  legal cells are the variants, the impossible cell is unconstructable because no variant
  matches. Forge the union; the validator does not exist.
- **A field-vs-constant check is a scalar constraint.** An invariant that pins one field
  against a fixed bound is a narrowed scalar. Forge the scalar; its existence is the
  proof, and no check runs anywhere.
- **A field-vs-threshold comparison is a decision.** Comparing fields against a configured
  threshold is not an integrity check; it is a **decision**, carried by a **derivation
  returning a union** of typed result variants. Both outcomes construct; the consumer
  reads the selected variant's own derivation. There is no `bool` and no `match`.
- **A world-edge gate hiding a decision is a derivation returning a union.** A gate that
  carries a check expressible as a typed result variant has buried a decision inside an
  external-state prerequisite. Split it: the decision becomes a derivation returning a
  union, and the genuinely-external part lives on the **active model**, which constructs
  the fact only when the live world is ready. The active model's only obligation is the
  world-edge part; the decision is structural.
- **A free function computing from fields is a derivation.** A configured value compared
  at runtime by a standalone function is a derivation whose home was never named. Forge
  the **derivation** on the frozen model that owns the fields.

This step is orthogonal to shape collapse. An invariant can pass coverage and precision
and still be carried by a weaker construct than it admits.

**Template:**

Invariant: {invariant-name}

Current construct: {construct}

Strongest admissible construct: {construct, with reasoning if different from current}

Action: {keep as-is / forge narrower scalar / forge the union / forge the derivation
returning a union / move the world-edge part to the active model}

If every invariant is carried by its strongest admissible construct after this step, no
escaped meaning remains. If any could move to a more structural construct, the refactor
is incomplete.

---

## Step 7: Decide

Three outcomes per candidate:

**Collapse:** Coverage holds AND precision holds. Replace the specific members with the
general proposition. Fewer invariants, same guarantees, less surface area for
contradiction.

**Extract as Named Principle:** Coverage holds BUT precision is lost (or the specific
members have distinct rationales worth preserving individually). Keep the specific
invariants. Add a named principle that identifies them as instances of the same pattern.
This doesn't reduce count but reveals structure and makes future invariants easier to
validate ("is this just another instance of the X principle?").

**Abandon:** Coverage leaks. The abstraction is wrong. Keep the specific invariants as
they are.

---

## Step 8: Rebuild and Validate

Write the refactored invariant list. Renumber. Rebuild the Coverage matrices from the
Coverage section of the foundation spec: conditions → invariants, and invariants →
conditions and carrying construct.

Confirm green:

- [ ] Every condition has at least one invariant
- [ ] Every invariant traces to at least one condition
- [ ] Every invariant names its carrying construct from the closed construct set
- [ ] Every invariant is carried by its strongest admissible construct (Step 6 closed for
      every entry)
- [ ] Every invariant names its home construct (the active model, route, boundary model,
      or a derivation on a frozen model)
- [ ] Every invariant is grounded in the premises
- [ ] Every config parameter from the Configuration Models section is still consumed by a
      construct (the active model, or a frozen model)
- [ ] No invariant has become a floating decree
- [ ] Named principles reference their member invariants correctly

If all boxes check, the refactor preserved all essential complexity and removed only
accidental complexity.

If any box fails, the refactor introduced a gap. Revert and try again.

---

## When to Stop

Stop when no cluster has more than one member or every remaining cluster fails the
precision test, AND every invariant is carried by its strongest admissible construct. At
that point, each invariant is genuinely unique in shape, in its home construct, and in
the construct that proves it. No escaped meaning remains. Further compression would lose
precision, coverage, or construct fit. The architecture is at its simplest correct form.
