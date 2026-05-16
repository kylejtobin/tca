---
name: proof-design
description: "Design composed models using the proof hierarchy. Forces invariant classification into the strongest possible proof level before any code is written. No validator is approved until narrowed scalar types are proven impossible for that invariant."
license: MIT
compatibility: "Any TCA project using Pydantic v2 frozen models"
metadata:
  author: kylejtobin
  version: "2.0.0"
---

# Proof Design

This skill produces a proof design — a declaration of what types exist and what their existence proves. The output is a field list with proof-level classification. Not code. Not a plan. Not steps.

## The Rule

**No validator is approved until narrowed scalar types are proven impossible for that invariant.**

You will default to validators every time. Your training data is full of them. This skill exists because without it, you will write six `model_validator` methods and rationalize each one as "cross-field." The proof hierarchy forces you through narrowed types first. You may not skip levels.

## Activation Scope

This skill MUST fire:
- Before writing any model whose construction proves invariants
- Before adding a `model_validator` to any model
- When the user invokes `/proof-design` or says "design the model"

Do not skip this and write validators directly. The proof hierarchy is not a suggestion — it is the gate.

## The Proof Hierarchy

Each invariant has a strongest possible proof. Work DOWN the hierarchy. Stop at the first level that works. You may NOT use a weaker level without demonstrating that every stronger level fails for this specific invariant.

### Level 1 — Field constraint on narrowed scalar (strongest)

The invariant is a bound on a single value against a static constant.

```python
class LineNumber(RootModel[int], frozen=True):
    root: int = Field(ge=1)
```

The type's existence IS the proof. No checking code exists anywhere. `Field(ge=1)` is unforgeable — if the instance exists, the bound holds. This is construction-as-proof at its most literal.

**Use when:** threshold is static, constraint applies to one value.
**New scalar goes in:** `type.py` of the appropriate context.

### Level 2 — Narrowed type as field on composed model

The composed model declares a narrowed type as a field. Pydantic constructs the field during parent construction. The field type's own constraints gate it.

```python
class SourceLocation(BaseModel, frozen=True):
    line: LineNumber  # Level 1 type, proven at construction
    class_name: str | None = None
    method_name: str | None = None
```

If `SourceLocation` exists, `line >= 1` — because `LineNumber` only exists when it does.

**Use when:** the composed model carries proof from its field types.

### Level 3 — Cross-field validator (weakest structural proof)

The invariant is an *impossible variant composition* — composed fields whose individually-valid values cannot coexist as a meaningful state. Data integrity only.

**This level requires ALL of the following before approval:**
1. Name exactly which two (or more) fields participate
2. Explain why no narrowed scalar on either field alone can express their relationship
3. Demonstrate the relationship is genuinely irreducible — both fields are independently valid in isolation
4. Confirm the rejection is structural impossibility, not a business decision

Irreducible example (illustrative — not a type in this repo):
- `StateTransition(current_state: NodeState, event: NodeEvent)` rejects `(Terminal, ChildAdded)` because a terminal node cannot accept children. Each field is a valid enum on its own; the *cell* is the invariant.

**NOT irreducible — these are Level 1 in disguise:**
- `if self.line.root < 1: raise` — that is `LineNumber(Field(ge=1))`
- `if self.name == "": raise` — that is `InvariantName(Field(min_length=1))`
- `if depth + width > 0` — both are `PositiveCount(Field(gt=0))`; the sum is positive because each is positive
- Any validator checking one field against a constant

**NOT a validator at all — these are derivations returning a result DU:**
- `if self.score < threshold or self.elapsed > limit: raise` — that is a business decision encoded as construction failure. Construction must succeed; the decision belongs on an Evaluation Model as `@computed_field` + `@cached_property` returning a discriminated union: `EvaluationResult = Accepted(reason: AcceptanceCause) | Rejected(reason: RejectionCause)`. The consumer dispatches on the variant.
- Any threshold comparison framed as "given these proven values, should the system act?" — that's not data integrity, it's an evaluation. The model carries the evaluation as a typed result; it does not refuse to exist when the answer is no.

**Parallel data is not Level 3 — it is a composition smell:**
- `len(names) == len(types) == len(defaults)` is three tuple fields that should be one tuple of `FieldDecl(name, type, default)` value objects. The "invariant" disappears when the composition is correct.

### Level 4 — Handler gating (external state)

The invariant is external state no field on this model represents. The handler's decision to attempt construction IS the proof.

Examples: connection alive, halt not active, no pending cancel. These are NOT fields on the model. The model's existence proves the handler confirmed external state before attempting construction.

## Protocol

### 1. Enumerate invariants

List every invariant the model's construction must prove. For each:
- What it asserts (the condition)
- Which fields or values participate
- Whether thresholds are static or dynamic

### 2. Classify — strongest level first, no skipping

For each invariant, test levels in order. Stop at the first that works.

**Level 1 test:** Is this a bound on one value against a static constant? → Narrowed scalar with `Field()`. Done. Do not continue.

**Level 2 test:** Is this carried by a narrowed field type on the composed model? → Field type declaration. Done.

**Level 3 test:** Name two specific fields. Explain why neither field's type alone carries the proof. Confirm both are independently valid. Confirm the failure case is *structural impossibility* (a state cell that cannot mean anything), not a business judgment about whether to act. → Approved cross-field validator. Document the irreducibility.

**Dynamic threshold is not Level 3.** If the threshold comes from another field or configuration and the comparison answers "should the system act on this?", that is a business decision, not data integrity. Construction must succeed; the decision is a `@computed_field` + `@cached_property` returning a discriminated union (`GateResult = GatePassed | GateRejected`) on an Evaluation Model. The consumer dispatches on the variant. Validators do not encode decisions.

**Level 4 test:** Is this external state? → Handler gates. Not a field.

### 3. Declare the field list

```
ModelName(BaseModel, frozen=True):
    field_a: NarrowedTypeA          # Level 1 — proves [invariant]
    field_b: NarrowedTypeB          # Level 2 — proves [invariant]
    # Level 3 (irreducible): field_x × field_y — [why irreducible]
    # Level 4: [external state] — handler gates, not a field
```

No code body. No validators yet — only after Level 3 invariants are identified and approved.

### 4. Catalog new narrowed scalars

Each Level 1 proof requires a narrowed scalar:

```python
class ScalarName(RootModel[base_type], frozen=True):
    root: base_type = Field(constraint)
```

These are observations parsed into types carrying structural proof — the "parse, don't validate" principle in Pydantic.

### 5. Validator gate

For each Level 3 invariant, answer ALL three:
1. Which two+ fields does it reference?
2. Why can't a narrowed scalar on either field replace it?
3. Is the relationship genuinely irreducible?

**If any answer is missing or unconvincing, the validator is not approved.** Reclassify to Level 1 or 2. Do not proceed to code with an unapproved validator.

## What This Prevents

- Writing `model_validator` before considering narrowed types (the default failure)
- Rationalizing single-field checks as "cross-field" (the escape hatch)
- Carrying `bool` fields as gates — the TYPE is the gate, not a boolean
- Using raw observation types as fields instead of proven narrowed types
- Putting handler-level state (halt, connection) as fields on domain models
