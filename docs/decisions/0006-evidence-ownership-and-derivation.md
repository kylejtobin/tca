# 0006. Evidence ownership is distinct from construction and value equality

**Status:** binding reviewer decision, 2026-10-24. Governs occurrence semantics in outcome 1, pure evaluation in outcome 2 and durable recovery thereafter. Requires [0003](0003-construction-evidence-and-justified-execution.md), [0005](0005-native-construction-is-authoritative.md) and reviewer acceptance under [0004](0004-review-authority-and-outcome-evidence.md).

## Problem and decision

Native validation can transform or replace supplied values and can run again on existing model instances. Python references can share mutable objects. A validated value is therefore neither an immutable historical observation nor proof that an output field retains its input's identity.

Admission establishes an evidence occurrence with its declared origin and relationship. Evaluation must preserve that admitted history. Construction produces an actual returned result with a witness of the versioned construction and the labeled evidence occurrences supplied to it. An output field is a projection of that result; it is not automatically the original input occurrence.

Class identity, equal content and Python object identity must not merge business occurrences. Correlation, collection membership and closure retain their exact source and subject scope. Logical repetition and execution attempts remain distinct. The precise durable representation is open, but it must retain these distinctions.

## What this decision does not authorize

- Do not infer source authority from successful validation, equality, output type or a plausible field path.
- Do not claim exact per-field provenance for an opaque transformation. Retaining all supplied inputs is a truthful construction dependency account, not proof of minimal lineage or unchanged projection.
- Frozen models, deep copying and post-hoc equality checks are implementation tools, not universal proofs of immutability, purity or isolation. Python supports custom copying and equality behavior.
- Serialization is not assumed to be an identity-preserving restoration procedure. Revalidating stored data can rerun transformations; skipping validation requires a separately justified trusted restoration boundary.
- Protecting history does not authorize the engine to replace native result semantics. A valid pure transformation may change the result while leaving historical inputs unchanged.
- Append-only history does not make every conclusion monotonic. Closure, cancellation and version-specific authority still require their declared semantics.

## Required engineering consequences

Define the supported value-ownership and pure-callback contract. Evaluator inputs and outputs must not allow one construction to silently rewrite the premises of another or alter replay's meaning. Environmental observations, including clock and fresh identity, enter as recorded evidence rather than hidden validator or default-factory effects.

Use deterministic, versioned identities and encodings where persistence requires them. Do not persist Python object addresses, process-dependent hashes or incidental repr strings as business identity. An identity formula is not a substitute for expressing a distinct intended repetition.

## Falsification and required evidence

Exercise shared references at distinct occurrences, equal values, nested mutable data, validators returning replacements, repeated evaluation, and scoped closure with an open sibling. Show historical evidence unchanged and actual returned values faithfully represented. For the durable outcomes, replay the same version and causal history and verify results, identities and justified work. Do not claim equivalence for arbitrary history reorderings.

This decision requires an explicit ownership strategy; it does not select deep copy, a codec, snapshotting or a storage backend. A strategy is acceptable only within its demonstrated value domain and without weakening the business contract.

## Reference

[Python copying](https://docs.python.org/3.14/library/copy.html) describes reference and copying behavior. Native validator transformations are covered by the sources in 0005.
