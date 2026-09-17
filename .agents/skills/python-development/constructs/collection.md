---
type: Reference
description: How a typed sequence or association is constructed when the collection has meaning of its own. Read when order, multiplicity, uniqueness, keys, or collection constraints matter.
---

# Collection

## Use

Use when the sequence or association has meaning of its own, including ordering, multiplicity, or a keyed relation. Otherwise use a typed tuple field on its owner.

## Required Forms

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

- Use tuples for sequences so completed collections are recursively immutable.
- Preserve keyed meaning for associations: key equality determines membership and lookup, and each key has exactly one value. Sequence position must not accidentally become part of association identity.
- Preserve order and multiplicity whenever they carry meaning.
- Put collection bounds on the root field and express collection invariants through the declared representation. Program-owned custom validators, including tuple-plus-uniqueness checks, are not admitted; see [construction](../construction.md).
- Put collection questions and folds in [transformations](transformation.md), within their closed algebra.

For a fixed set of named semantic keys, a frozen product can give each key its own field. An arbitrary-key association requires a substrate that constructs typed keys and values, retains keyed lookup and equality, and is recursively immutable. `RootModel[dict[K, V]]` does not meet that requirement: freezing the root model leaves the dictionary mutable. A read-only mapping annotation does not itself establish immutable storage either. The tuple form above is a sequence, not an implementation of arbitrary-key association. If no admitted substrate satisfies the required keyed semantics and immutability, report that construction gap rather than introduce a custom container, mutation convention, or tuple-and-validator substitute.

Source duplicate policy is a separate boundary obligation. A dictionary has one value per surviving key, but duplicate JSON keys may have been discarded before Pydantic receives it. If the source contract rejects duplicates, the boundary must preserve enough input evidence to reject them before that loss; a uniqueness test on the resulting dictionary proves nothing about the source.

## Do Not

- use mutable lists, sets, or dictionaries in completed semantic values
- name a sequence as a collection without collection-level meaning
- type members or keys as bare primitives when semantic types exist
- discard ordering, duplicates, or missing entries before deciding their meaning
- expose `KeyError` as a domain result
- use dictionary equality to claim duplicate source input was rejected
- replace a keyed association with an ordered sequence merely because tuple construction is available
