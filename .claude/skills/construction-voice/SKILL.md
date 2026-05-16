---
name: construction-voice
description: "Rewrite procedural language into construction voice. Words prime code at the token level — procedural words in instructions produce procedural code regardless of architectural intent. This skill identifies infection vectors and rewrites as structural declarations."
license: MIT
compatibility: "Any TCA project or instruction set"
metadata:
  author: kylejtobin
  version: "2.0.0"
---

# Construction Voice

Words prime code at the token level, not the concept level. A procedural word in an instruction, plan, or doc produces procedural code — regardless of what the writer intended.

```
"Extract the domain scalars" → extraction function (reads and returns)
"The model contains domain scalars" → field declarations (construction proves containment)
```

Same intent. Different word. Different generated code.

## Activation Scope

This skill MUST fire:
- Before writing or editing any doc, rule, instruction, or plan
- When reviewing output and any word from the infection table appears
- When the user invokes `/construction-voice` or says "check the voice"

Do not wait to "notice" procedural drift. You will not notice — that is the failure this skill exists to prevent. Load preemptively when the output is language, not code.

## Infection Vectors

Each word activates a specific procedural generation pattern. The construction equivalent eliminates the pattern at the source.

| Infection word | Primes | Construction equivalent |
|---|---|---|
| extract | function that reads and returns | field declaration — the model CONTAINS it |
| check | if-statement, boolean return | `Field()` constraint — construction REJECTS invalid |
| validate | try/except, error branch | type construction — invalid state is UNREPRESENTABLE |
| handle | switch/case, dispatch | discriminated union — variant selection IS construction |
| process | pipeline, sequential steps | composed model — richer type from proven inputs |
| determine | conditional logic, branching | `@computed_field` — intrinsic fact OF the model |
| return | function output | type existence — the model IS the result |
| find / look for | search loop, filter | field type — if it constructs, it was found |
| store / save | write operation | event publishing — the event IS the record |
| calculate / compute | standalone function | `@cached_property` on the owning model |
| transform | mapper function | `model_validate` — construction IS transformation |
| call / invoke | procedure orchestration | construction cascade — `@cached_property` triggers `model_validate` |
| first / then / finally | sequential steps | simultaneous field declarations — no ordering exists |
| pass to / hand off | explicit data flow | field type on the receiving model — dependency is structural |

## Protocol

### 1. Scan

Identify every infection vector in the text. Mark each instance.

### 2. Identify what EXISTS

For each procedural phrase: what type or structure exists when the work is done? Not what the programmer does — what IS.

### 3. Rewrite as declarations

Every sentence declares what something IS, CONTAINS, or PROVES.

**Before:** "The classifier extracts the field name from the dict items, checks if the annotation is Optional, and passes the inner type to the next stage."

**After:** "`FieldSlot` reads `(name, FieldInfo)` tuples via `model_validator(mode='before')`. `AnnotationShape` is a discriminated union on `TypeAnnotation.kind` — Pydantic selects the variant during construction. The variant's `resolved_type` field IS the inner type."

**Before:** "First parse the source, then validate the file is in the domain directory, then construct the smell list."

**After:** "`FileContext` fields carry all proof obligations. `source` and `path` are stored. `tree` is a `@cached_property` — it exists because `source` parsed. `in_domain` is a `@cached_property` derived from `path`. `Smell` is constructed only when an invariant's `check` yields one."

**Before:** "The service processes incoming messages, determines the variant type, and routes to the appropriate handler."

**After:** "Incoming bytes are absorbed by `model_validate_json(raw_bytes)` against a discriminated union. Each variant contains its payload as typed fields. The variant IS the routing decision."

### 4. Verify: no temporal ordering survives

If "first," "then," "after," "before," "next," or "finally" remain in the rewritten text, one of two things is true:

- **Residual procedural frame** — rewrite again. The temporal word is carrying a procedural mental model that will infect code.
- **Irreducible seam** — name it explicitly as procedure and explain why construction cannot replace it. Temporal ordering that survives honest rewriting is diagnostic — it identifies genuine seams.

Both outcomes are useful. The skill succeeds either way: procedural language is eliminated, or an irreducible seam is surfaced and named.

## Output

The rewritten text. Every sentence declares what something IS, CONTAINS, or PROVES. No sentence describes what someone DOES, CHECKS, or HANDLES. Surviving temporal ordering is flagged with its justification.
