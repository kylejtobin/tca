# 0005. Native construction is authoritative

**Status:** binding reviewer decision, 2026-10-24. Governs value semantics throughout outcomes 1–7. Requires [0003](0003-construction-evidence-and-justified-execution.md) for justified execution and [0006](0006-evidence-ownership-and-derivation.md) for evidence integrity. Acceptance remains governed by [0004](0004-review-authority-and-outcome-evidence.md).

## Problem and decision

The interpreter in `8aed218` removes callbacks from a field, submits the remaining constraint to TypeAdapter, and calls that the same judgement as native construction. It rejects a tuple that Pydantic accepts after a before-validator normalizes it. Calling the right library on altered semantics creates a second business program.

Pydantic owns concrete value construction: native composition, normalization, constraints, validators, defaults, aliases and serialization. Python annotations, generics, unions, tuples and Annotated metadata remain the business modeling language. Reusable TCA computational primitives participate in that native machinery; they do not create an alternative validation path.

The construction boundary must preserve the original relevant schema, configuration, context, order and input mode. Model APIs and TypeAdapter are used for their supported roles. Internal field dictionaries use native field-name validation without alias reinterpretation; external admission uses its declared mode and aliases. Preserve omitted input versus explicit null versus defaults. Default-only construction has the same failure-classification obligations as other construction.

## What this decision does not authorize

- Pydantic acceptance does not establish source authority, causal demand, action eligibility, occurrence identity or replay safety. Those are distinct obligations.
- Core-schema inspection may support bounded inference; it does not authorize a replacement validator. Reading only annotations or decorator registries does not capture the whole construction.
- A partial judgement is valid only when the omitted operations cannot change that particular conclusion. If normalization, callbacks, defaults, context or configuration may affect it, keep the conclusion unknown and retain the native construction boundary.
- Do not run arbitrary field validators early with invented partial model context. Native field order can matter.
- Do not use unvalidated model construction or copy-update operations to bypass failed business validation. Trusted restoration requires its own demonstrated contract; it is not a general exception.
- A callback's opacity does not prove either a causal dependency or independence. Apply 0003; no dispatch follows merely from inability to inspect it.

## Falsification and required evidence

Compare the interpreter with direct native construction under the same declared mode and premises. Exercise before/after/plain/wrap validators, normalization before constraints, model context, defaults, aliases and returned transformations. Compare actual values and failure categories, not just whether both calls return.

A valid before-normalization case must not become malformed because the analyzer tested a stripped fragment. Equivalent predicate formulations must not gain execution authority by becoming less analyzable. Negative cases must retain their valid progress counterparts.

The ownership allocation is decided; the supported inference fragment is not frozen. New inference rules require evidence of soundness. Unsupported inference stays unknown rather than silently narrowing Pydantic's supported business semantics.

## References

[Pydantic architecture](https://docs.pydantic.dev/latest/internals/architecture/) and [validators](https://docs.pydantic.dev/latest/concepts/validators/) describe the native machinery. Exact compatibility is exercised against the lockfile; the reviewed environment uses Pydantic 2.13.5 and pydantic-core 2.46.5.
