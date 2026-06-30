---
name: tca_forbidden_pattern_surface_drifted_from_the_verb_row
description: The drifted-surface anti-pattern. A verb signature that does not match its plan entry. Read this while building a verb to see the ways the surface diverges from what the plan declared.
---

## Surface drifted from the verb row

The signature claims what the row did not: a missing or wrong return annotation, a yielding verb not typed as an iterator, parameters that do not match the row's `accepts`, or parameters where the row declared none.

The verb's surface is the row rendered exactly: the parameter is the innermost constructed value the row's `accepts` names, and the return annotation is the row's declared type, with a yielding verb typed as an `AsyncIterator` (or `Iterator`) of the fact it yields.

```python
def project(self) -> dict:            # row says -> SignalSnapshot: annotate the row's declared type
def stream(self) -> SignalSnapshot:   # yields, but not typed Iterator: type it Iterator[SignalSnapshot]
```
