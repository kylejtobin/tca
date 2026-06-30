---
name: tca_forbidden_pattern_unmodeled_behavior
description: The unmodeled-behavior anti-pattern. A verb, derivation, or consistency-model method with no plan entry. Read this while building any behavior to see why the plan authorizes the act first.
---

## Unmodeled behavior

A verb, derivation, or consistency-model method with no row is behavior built before it was modeled. The ontology authorizes the act first, then the code performs it.

Every act traces to a row: a verb for a state transition, a derivation for a fact implied by frozen fields. Behavior the code needs that no row names is a meaning to place in the ontology before it is written.

```python
def reconcile(self) -> Ledger: ...   # no row names this act: place the verb in the ontology first, then build it
```
