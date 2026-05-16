# Foundational Program Design: Refactor Strategy

A process for reducing accidental complexity in a logical architecture while preserving all essential coverage. Use this after a foundational spec (Scope, Strategy, Conditions, Premises, Domain Invariants) has been validated green: every condition has invariants, every invariant traces to conditions, every invariant has a home.

The goal is: all the complexity you need, nothing you don't. Make things as simple as possible, but no simpler.

---

## Step 1: Tag by Shape

Read every invariant. Ignore the specific nouns (which handler, which event, which entity). Ask: what is the structural pattern this proposition expresses?

Common shapes:

- **Gate:** Check X before publishing Y. If X fails, Y does not publish.  
- **Lifecycle:** Monitor a thing, detect when it's no longer appropriate, cancel/replace it, handle outcomes.  
- **Schema:** The event model enforces a constraint at construction. Invalid data cannot enter the stream.  
- **Delegation:** Decision X is made by actor Y, not hardcoded.  
- **Circuit breaker:** Stop flow when integrity breaks, resume when restored.  
- **Reconciliation:** When internal state may have diverged from external reality, query external, publish discovered state.  
- **Threshold:** Measure X, require persistence over a window, then act.  
- **Independence:** Handler X makes decisions without input from handler Y. Y cannot override.  
- **Valuation:** Use metric X (not metric Y) for a specific calculation.  
- **Suppression:** Suppress behavior Z during condition W.

Tag each invariant with its shape. Use whatever labels fit your domain. The labels above are starting points, not a taxonomy.

**Template:**

{invariant-name}: {shape}. {one-sentence summary ignoring specific nouns}

---

## Step 2: Group by Shape

Collect invariants with the same shape tag. These are your candidate clusters.

Clusters with one member have no refactoring opportunity. Move on.

Clusters with two or more members are candidates for collapsing or principle extraction.

---

## Step 3: Write Candidate Abstractions

For each multi-member cluster, write the general proposition that all members are instances of.

**Template:**

Candidate: {general proposition}

Members: {invariant-name-A}, {invariant-name-B}, ...

---

## Step 4: Test Coverage

Walk the candidate against every condition its members currently govern.

For each condition, ask: does the general proposition still cover this condition? Is any condition left without an invariant if the specific members are replaced by the general form?

If any condition loses coverage, the abstraction leaks. Stop.

**Template:**

Candidate: {general proposition}

Condition {X}: covered by {which clause of the general form}

Condition {Y}: covered by {which clause of the general form}

Condition {Z}: NOT COVERED \- abstraction leaks

---

## Step 5: Test Precision

Walk the candidate against the premises, specifically the one that says every invariant must have a home (a specific handler, a specific input, a specific output).

Ask: can the general proposition still name a specific handler? Or has it become a floating decree that no single handler enforces?

If it can name a handler: precision holds. If it spans multiple handlers with different inputs: precision is lost.

**Template:**

Candidate: {general proposition}

Home: {handler} on {input} refusing {output}

Precision: HOLDS / LOST (because {reason})

---

## Step 6: Decide

Three outcomes per candidate:

**Collapse:** Coverage holds AND precision holds. Replace the specific members with the general proposition. Fewer invariants, same guarantees, less surface area for contradiction.

**Extract as Named Principle:** Coverage holds BUT precision is lost (or the specific members have distinct rationales worth preserving individually). Keep the specific invariants. Add a named principle that identifies them as instances of the same pattern. This doesn't reduce count but reveals structure and makes future invariants easier to validate ("is this just another instance of the X principle?").

**Abandon:** Coverage leaks. The abstraction is wrong. Keep the specific invariants as they are.

---

## Step 7: Rebuild and Validate

Write the refactored invariant list. Renumber. Rebuild the validation matrix.

Confirm green:

- [ ] Every condition has at least one invariant  
- [ ] Every invariant traces to at least one condition  
- [ ] Every invariant names its home handler  
- [ ] Every invariant is grounded in the premises  
- [ ] No invariant has become a floating decree  
- [ ] Named principles reference their member invariants correctly

If all boxes check, the refactor preserved all essential complexity and removed only accidental complexity.

If any box fails, the refactor introduced a gap. Revert and try again.

---

## When to Stop

Stop when no cluster has more than one member, or when every remaining cluster fails the precision test. At that point, each invariant is genuinely unique in both shape and home. Further compression would lose precision or coverage. The architecture is at its simplest correct form.  
