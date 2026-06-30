---
name: tca_forbidden_pattern_dead_handle
description: The dead-handle anti-pattern. A client field reached by no verb. Read this while building a consistency model or binding to see why a capability wired to nothing is structure with no act crossing it.
---

## Dead handle

A client held on the consistency model but reached by no verb is a capability wired to nothing: structure with no act crossing through it.

Every client field exists for a verb that crosses through it. A verb is a state transition on the consistency model that may emit the constructed fact through a client field; a client no verb touches names no transition and belongs nowhere, or its verb is missing and must be modeled.

```python
class MarketSession(BaseModel):
    coinbase: CoinbaseClient   # no verb ever touches self.coinbase: either a verb must emit through it, or the field is unwired structure
```
