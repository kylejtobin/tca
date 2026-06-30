---
name: tca_forbidden_pattern_frozen_live_edge
description: The frozen-live-edge anti-pattern. A frozen consistency model. Read this while building a consistency model to see why freezing the one live node contradicts what it is.
---

## Frozen live edge

Freezing the consistency model contradicts what it is: the one node holding live clients and accumulating mutable state. Frozen, it is a different construct wearing the name.

The consistency model is the single unfrozen `BaseModel` of a context, with `arbitrary_types_allowed=True`, clients as fields, and state evolution by re-pointing a field to a newly constructed proven fact. A frozen domain composite holding no client is a concept model, not this.

```python
class MarketSession(BaseModel, frozen=True):   # the consistency model is unfrozen; drop frozen=True and add arbitrary_types_allowed=True
    book: CoinbaseBook
```
