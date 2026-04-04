---
name: tca-slice-modeling
description: Model one real program slice in a TCA way. Use when the user asks how to structure a feature, context, stateful path, or complex interaction.
---

Use this skill when the problem is broad enough that you need to cut one clear semantic slice and model it properly.

## Outcome

Produce a model-first slice, not a framework-first design.

Name:

1. foreign systems
2. owned domain truths
3. representable outcome states
4. proof obligations / likely roots
5. irreducible seams
6. the thinnest typed path through the slice

Express that slice in Pydantic terms:

1. `RootModel` or focused `BaseModel` for owned concepts
2. `Literal`, enums, and discriminated unions for declared cases
3. `from_attributes`, aliases, `model_validate`, or `model_validate_json` for staged lifting
4. `@computed_field`, `@cached_property`, or `@property` for intrinsic derivation
5. `model_validator(mode="before" | "wrap")` only when the seam is truly irreducible

## Method

1. Start from one real slice, not the whole platform.
2. Ask:
   - what must be true?
   - what can happen next?
   - which outcomes are already known cases even if the result is not yet known?
3. Model those outcomes as typed possibility space.
4. Name the foreign contracts and boundary models.
5. Shrink procedure to seams that only capture, normalize, trigger, or resume proof.
6. Only after the world is modeled, place routes, thin services, or runtime shells around it.

## Review standard

Do not let the answer drift into:

- procedural coordination as the semantic center
- dict or flag based state handling
- vague control language without typed states
- validators used as a generic escape hatch instead of declarative fields, declared cases, or justified seam logic
