---
name: proof-design
description: "Classify the invariant onto the three orthogonal proof hierarchies — A (data integrity), B (decision dispatch), C (external state) — before any model is written. `model_validator(mode=\"after\")` survives only as A.3 — impossible variant composition."
license: MIT
compatibility: "Any TCA project using Pydantic v2 frozen models"
metadata:
  author: kylejtobin
  version: "3.0.0"
---

# Proof Design

This skill IS the invariant's classification onto hierarchy A, B, or C — and the strongest-shape selection within the classified hierarchy. Its output is a field list with hierarchy annotations and proof-level selections. Not code. Not a plan. Not steps.

## The Rule

**No `model_validator(mode="after")` is admissible until A.1, A.2, B.1, B.2, and B.3 are demonstrated insufficient AND the invariant is structurally impossible-variant-composition.**

The default reach is `model_validator`. The training corpus carries that gravity. This skill exists because classification onto A/B/C precedes any validator selection. Classification first; shape selection second; validator only as A.3 — and only when the rejection target is an impossible composition of variant-and-event, never a threshold comparison in disguise.

## Activation Scope

This skill MUST fire:

- Before writing any model whose construction proves invariants.
- Before adding a `model_validator(mode="after")` to any model.
- Before writing a derivation whose return type is the decision's typed result variant.
- On `/proof-design` or "design the model".

A `model_validator(mode="after")` lacking a classification justification from this skill is unfinished code.

## The Three Orthogonal Hierarchies

Three independent questions. Three independent answers. Their conflation is the deepest failure mode in the codebase.

### A. Data integrity — "is this value well-formed?"

Construction's rejection surface for malformed values. The strongest shape an invariant admits is its home.

| Level | Shape |
|-------|-------|
| A.1 | `Field()` constraint on a narrowed `RootModel` scalar. Type existence IS proof. |
| A.2 | Narrowed type as field on a composed model. A.1's proof is carried into the parent through Pydantic's Rust validator at construction. |
| A.3 | `model_validator(mode="after")` rejecting an *impossible variant composition*. Rare. The documented case is `StateTransition(current_state, event)` rejecting the cell `(Terminal, ChildAdded)`. Never for thresholds, never for business decisions. |

A `model_validator` measuring one field against a constant is A.1 left unforged.
A `model_validator` comparing a proven field against a configured threshold is a *decision*, not an integrity check — its home is hierarchy B.

### B. Decision dispatch — "given proven measurements, what is the typed answer?"

Construction always succeeds. The answer is a typed result variant.

| Level | Shape |
|-------|-------|
| B.1 | `@cached_property` on an Evaluation Model returning a typed result variant (DU, typed tuple, proven model). Never `bool`, never `int`, never `str`-with-contextual-meaning. |
| B.2 | Smart enum method on a `StrEnum` class. The F-test passes — the signature is satisfied by the enum value plus proven scalars or proven value objects, never a composed model's `self`. |
| B.3 | Smart variant method on a frozen `BaseModel` DU member. Polymorphic dispatch through Pydantic's discriminator. The method body is total over the variant's valid input subset. |
| B.4 | Consumer dispatch via Pydantic DU narrowing. The variant itself IS the consumer's branch point — `match`/`case` over the DU, never `if`/`elif` re-branching on `.kind`. |

### C. External state — "is the prerequisite for attempting construction present?"

The handler's construction precondition. The model's *absence* is the proof.

- Connection alive.
- Scheduled cadence fired.
- Halt not active.
- Prerequisite event observed.

C is not a field. C is not a validator. The handler refuses to construct the model when the prerequisite is missing.

## Protocol

Three classification questions, in order. The first "yes" names the hierarchy.

**Question 1 — Hierarchy A.** "Does this rejection target a malformed value during construction?"

- Single value, static bound → A.1 (narrowed `RootModel` scalar with `Field()`).
- Composed model carrying A.1 types as fields → A.2.
- Composition of two proven variant-and-event fields where the cell is meaningless → A.3.

**Question 2 — Hierarchy B.** "Is this a decision the consumer dispatches on, given proven measurements?"

- Construction succeeds for every well-formed input set.
- Composed proven inputs → typed result variant on an Evaluation Model → B.1.
- F-test passes against an enum value → B.2.
- F-test passes against a variant value → B.3.
- Consumer's branch point is the discriminator itself → B.4.

**Question 3 — Hierarchy C.** "Is this the prerequisite for construction, not part of fields?"

- Handler gate. The evaluation model's absence carries the proof.

## The F-test (decision-dispatch boundary)

> Is the method's signature satisfied by the variant value plus proven scalars or proven value objects, with no reference to the composed model's `self`?

- **Yes** → B.2 (smart enum method) or B.3 (smart variant method). The variant carries the dispatch.
- **No** → B.1 (derivation on the composed Evaluation Model). The composed-model derivation may compose B.2 or B.3 for the variant-owned part.

The variant's signature contains no composed-model `self`. That is the boundary.

## Validator gate (A.3 only)

For a candidate `model_validator(mode="after")`, all four answers are required.

1. **Which two or more proven fields participate?** Name them. A single-field reference is A.1 left unforged.
2. **Why is each field's value individually valid in isolation?** Each field's type carries its own A.1/A.2 proof; the validator does not duplicate that work.
3. **Why does their composition represent a structurally impossible state, not a business threshold?** Impossible composition is a cell in a finite variant × variant grid — `(Terminal, ChildAdded)` cannot exist. A threshold comparison is a decision.
4. **Which of A.1 / A.2 / B.1 / B.2 / B.3 is demonstrated insufficient?** Name the shape and its insufficiency.

A missing or unconvincing answer means the validator's home is elsewhere — reclassify to B (most common case) or A.1 / A.2.

## Declare the field list

```
ModelName(BaseModel, frozen=True):
    field_a: NarrowedTypeA          # A.1 carries [invariant]
    field_b: NarrowedTypeB          # A.2 carries [invariant]

    @cached_property
    def result(self) -> ResultDU:   # B.1 carries [decision]
        ...

    # A.3 (rare): field_x × field_y — [why composition is structurally impossible]
    # C (external state): [prerequisite] — handler gate, not a field
```

No body. No validators except an A.3 admitted through the validator gate.

## Catalog obligations

- Each A.1 proof is a narrowed scalar entry in the project's type catalog — base type, constraint, invariant.
- Each B.1 derivation is a typed result variant catalog entry — DU members, discriminator field, per-variant fields.

## What This Prevents

- A `model_validator` written before the invariant's classification onto A, B, or C.
- A decision classified as a validator — validation-thinking-drift. Construction fails on valid measurements; the consumer never sees a typed result.
- `bool` fields as gates. The typed variant IS the gate; `bool` erases the discriminator and forces `if`-branching back into the consumer.
- Raw observation types as fields. A narrowed scalar carries the A.1 proof; a `float` field does not.
- External-state prerequisites declared as fields. C's proof is the model's absence at the handler's construction site.
- A.3 validators whose body is a threshold comparison in disguise. The rejection target is a meaningless variant × variant cell, not a "should the system act?" decision — that decision's home is B.1.
