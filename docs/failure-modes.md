# Failure Modes

Every failure in a TCA program is a design error. The fix is always more modeling — never less. Never suppress, never work around, never move things to make the linter shut up. Every error tells you where the design is weak. The fix is always to strengthen the design: build the type, fix the ownership, model the boundary.

---

## How To Read A Failure

Failures are evidence about weak design, not annoyances to suppress. The first question is always: what is this failure telling me about the model, the ownership, or the boundary?

- If basedpyright says "cycle detected" — a module is returning types it doesn't own. Fix the responsibility so the dependency is one-way.
- If basedpyright says "Any" — there's a missing model at a boundary. Build the model that shapes that boundary.
- If basedpyright says "reportUnhashable" — the type is incomplete. Complete the type.
- If basedpyright says "reportCallInDefaultInitializer" — the annotation is wrong. Fix the annotation.
- If construction fails — the type declared more than the input could satisfy, or the input carried something the type did not expect.

The diagnostic stance is: what is the weakest part of the design, and how does better modeling fix it?

---

## Construction Failures

These are failures where the construction machine cannot uphold its own guarantees.

**Circular construction.** `RecursionError` during `model_validate`. Model A has a field of type B, and B has a field of type A. The fix: make one side lazy via `@cached_property`, introduce a reference/ID type, or decompose the domain differently.

**`from_attributes` name mismatch.** Unexpected default value or `ValidationError` on a required field. The source object's attribute name does not match the target model's field name. The fix: check attribute names or use `Field(alias=...)`.

**Missing discriminator.** Wrong variant selected or confusing multi-error `ValidationError`. A union without `Field(discriminator=...)` tries each variant in declaration order. The fix: always declare `Field(discriminator="tag_field")` on unions.

**Bare mutable collections on frozen models.** Proof decays silently — list contents mutated after construction. `list` and `dict` are mutable behind the frozen surface. The fix: `tuple[X, ...]` for sequences. Domain-typed frozen models for mappings.

---

## Purity Failures

These are failures where proof has been contaminated by time, state, or side effects smuggled into the machine.

**Validator that mutates.** Different results on repeated access. `@cached_property` diverges from fields. A validator modifies the input dict or external state instead of returning new values. The fix: validators must return new values, never mutate inputs.

**I/O inside construction.** Testing requires mocks. Proof depends on database state. A validator performs I/O. The fix: push I/O to the boundary — pre-fetch into an index, pass via validation context, let the validator translate, not fetch.

**Impure property consumed by `from_attributes`.** A property participating in construction performs I/O, reads global state, or triggers unbounded computation. The fix: properties consumed by `from_attributes` must be pure functions of the object's own frozen fields.

---

## Ownership Failures

These are failures where the program's semantics live in the wrong place — outside the type tree that should own them.

**Service logic that should be a projection.** A service method computes something that depends only on a model's own fields. That computation is a wiring defect. The fix: move the derivation onto the model as a `@computed_field`, `@cached_property`, or `@property`.

**Branching that should be dispatch.** An `if/elif` chain or `match/case` block selects behavior based on a tag or type. A discriminated union would route the same selection during construction. The fix: declare variants with `Literal` tags and let the DU dispatch.

**Procedure where a model should exist.** A function assembles, transforms, or enriches data that could be expressed as a model with fields, aliases, and projections. The fix: build the model. The function was a missing type.

**Route handler with domain logic.** A route handler interprets, enriches, or computes instead of delegating to context-owned contracts. The fix: move the logic into the domain context. The handler should be pure transport delegation.

---

## Translation Failures

These are failures where a boundary was modeled twice instead of once, or where an unnecessary translation layer introduces information loss.

**Adapter that should collapse.** An adapter, converter, or mapping function exists between two models that could wire directly via `from_attributes` and aliases. The fix: declare the wiring on the target model and remove the adapter.

**Context reinjected through the wrong surface.** Already-modeled context is pasted as prompt text or reassembled as a dict when it should be carried as a structured object. The fix: choose the compilation surface that preserves the context's semantic structure. See [Semantic Index Types](semantic-index-types.md).

---

## Semantic Surface Failures

These are failures where the program is structurally valid but semantically weak — the names, descriptions, or exposure surfaces are not precise enough for the consumer.

**Weak names.** A field named `level` when `churn_risk_tier` would instruct the consumer more precisely. The structural output may be valid, but the semantic output diverges from intent. The fix: name with domain precision.

**Missing descriptions.** A field with real degrees of freedom (not a `Literal` constant) lacks a `Field(description=...)`. The consumer must guess. The fix: add a description that says what the type annotation does not already say, grounded in what the value tells the consumer.

**Wrong compilation surface.** A schema is exposed via prompt text when a tool definition would better separate it from conversational context, or vice versa. The fix: choose the exposure regime that matches the architectural intent.

---

## The Modeling Fix

Every category above points toward the same repair strategy:

1. **Build the missing type.** The function was a type. The adapter was a missing alias. The branch was a missing DU.
2. **Fix the ownership.** The derivation belongs on the machine. The contract belongs in the context. The logic belongs in the domain.
3. **Model the boundary.** The seam needs a bridge model. The bare primitive needs a domain type. The untyped surface needs a construction entry point.
4. **Tighten the semantic surface.** The name needs domain precision. The description needs to resolve ambiguity. The compilation surface needs to match the consumer.

The fix is always more modeling. Never less.
