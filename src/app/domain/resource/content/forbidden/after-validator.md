---
name: tca_forbidden_pattern_after_validator
description: The after-validator anti-pattern. A `@model_validator(mode="after")` names something the model left unmodeled. Read this while building a concept or value object to see why it escapes the type, and how to move that fact into the structure.
---

## After validator

A `@model_validator(mode="after")` runs once the object is already built, so it can only police a value the structure let exist. Its presence is a question, never a fix: what did the model leave unmodeled, so that a fact has to be checked at runtime instead of carried by the type? Move that fact into the structure, so the invalid state cannot be constructed at all.

- A cross-field relation (`bid <= ask`) reparameterizes to a base and a non-negative offset, making the second field a derivation.
- A single-field bound belongs on the scalar's own `Field`.
- An "exactly one of these" is a union selected by construction.

There is no legal after-validator: every one names something that was not modeled.

```python
@model_validator(mode="after")
def check(self):                # what wasn't modeled? bid and ask stored raw, their ordering left to a check.
    if self.bid > self.ask:     # model bid and a non-negative Spread, derive ask: the inverted quote can't be built.
        raise ValueError
    return self
```
