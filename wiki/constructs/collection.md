---
type: Construct
description: A frozen typed sequence with meaning of its own; keyed association has no admitted substrate.
---

# Collection

## Definition

A sequence or association that has meaning of its own, including ordering, multiplicity, or a keyed relation. A sequence with no meaning of its own is a typed tuple field on its owner.

## Required Form

```python
class Fills(RootModel[tuple[Fill, ...]]):
    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[Fill, ...] = Field(min_length=1)
```

- Sequences are tuples so completed collections are recursively immutable.
- Keyed meaning is preserved for associations: key equality determines membership and lookup, and each key has exactly one value. Sequence position never becomes part of association identity.
- Order and multiplicity are preserved whenever they carry meaning.
- Collection bounds go on the root field, and collection invariants are expressed through the declared representation. Program-owned custom validators, including tuple-plus-uniqueness checks, are not admitted; see [construction-rules](./construction-rules.md).
- Collection questions and folds are [transformations](./transformation.md) within their closed algebra.

## Keyed Association

For a fixed set of named semantic keys, a frozen product gives each key its own field. An arbitrary-key association requires a substrate that constructs typed keys and values, retains keyed lookup and equality, and is recursively immutable. `RootModel[dict[K, V]]` does not meet that requirement: freezing the root model leaves the dictionary mutable. A read-only mapping annotation constructs a dictionary too. The tuple form is a sequence, not an association. No admitted substrate satisfies the keyed semantics and immutability together, so the keyed association is a reported construction gap, never a custom container, a mutation convention, or a tuple-and-validator substitute. In the venue world the association was a lookup index, a cost rather than a meaning: the domain fact is the entries, and one value per key is either the source's contract or a transition whose outcome states whether the key was already present.

Source duplicate policy is a separate boundary obligation. Pydantic's JSON parser keeps the last of duplicate object keys silently, so a uniqueness test on the resulting dictionary proves nothing about the source. If the source contract rejects duplicates, the boundary must preserve enough input evidence to reject them before that loss.

## Forbidden

- mutable lists, sets, or dictionaries in completed semantic values
- a sequence named as a collection without collection-level meaning
- members or keys typed as bare primitives when semantic types exist
- ordering, duplicates, or missing entries discarded before deciding their meaning
- `KeyError` exposed as a domain result
- dictionary equality used to claim duplicate source input was rejected
- a keyed association replaced with an ordered sequence merely because tuple construction is available
