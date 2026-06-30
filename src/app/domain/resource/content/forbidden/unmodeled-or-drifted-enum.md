---
name: tca_forbidden_pattern_unmodeled_or_drifted_enum
description: The drifted-enum anti-pattern. An enum that is neither a value space nor a union axis. Read this while building a semantic scalar or union to see why an enum must be one of those, and how its members drift from the modeled set.
---

## Unmodeled or drifted enum

An enum that is neither a scalar's value space nor a union's axis carries vocabulary the catalog does not recognize. One whose members differ from the modeled set has drifted from what it mirrors.

A `StrEnum` exists in exactly two roles: the value space a frozen `RootModel` scalar wraps, or the axis a union's variants pin with `kind: Literal[Axis.MEMBER]`. Its members are exactly the modeled set; a member no row names is vocabulary the ontology never declared.

```python
class Venue(StrEnum):
    COINBASE = "coinbase"   # no row names this: the enum is a scalar's value space or a union's axis, with members exactly the modeled set
```
