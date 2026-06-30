---
name: tca_forbidden_pattern_open_product
description: The open-product anti-pattern. A value, concept, foreign, or contract model that is unfrozen or admits extras stops being a fixed fact. Read this while building any product to see the config every product carries.
---

## Open product

A value, concept, foreign, or contract model left unfrozen can mutate after construction; one that does not forbid extras silently absorbs unmodeled fields. Either way it stops being a fixed, fully-described fact.

Every product type carries `model_config = ConfigDict(frozen=True, extra="forbid")`. The consistency model is the one exception, because it is the live node that accumulates state; freezing it is its own violation.

```python
class SignalSnapshot(BaseModel):   # no frozen, no extra="forbid": add model_config = ConfigDict(frozen=True, extra="forbid")
    spread: Spread
```
