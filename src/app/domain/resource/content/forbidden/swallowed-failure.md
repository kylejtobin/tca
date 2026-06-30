---
name: tca_forbidden_pattern_swallowed_failure
description: The swallowed-failure anti-pattern. A broad or multi-statement try/except turns failure into procedure. Read this while building an ordered union to see how it models a domain no.
---

## Swallowed failure

A `try`/`except` wider than the single capture form turns failure into procedure: catching `Exception` or `ValidationError`, or running a multi-statement `except` body, instead of letting the failure propagate or constructing it as a value.

One question routes every failure: did the domain say no, or did the proof fail? A construction refusal proves nothing, is never caught, and propagates; catching `ValidationError` manufactures the unproven value. A domain no is a value, modeled through the ordered union: the capture lives in a verb as one call assigned, each declared exception assigned to the same variable, then ordered-union construction from that variable.

```python
try:
    result = call()
except Exception:
    result = None   # failure erased: let a proof failure propagate, or capture a declared exception and feed the ordered union's constructor
```
