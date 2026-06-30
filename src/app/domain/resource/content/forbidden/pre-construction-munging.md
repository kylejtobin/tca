---
name: tca_forbidden_pattern_pre_construction_munging
description: The pre-construction-munging anti-pattern. A `@model_validator(mode="before")` that fixes data ahead of construction is an alias, a path, or a nested model not yet written. Read this while building a foreign model to see the one wrap that is legal.
---

## Pre-construction munging

A before-validator outside an ordered-union file, or one that indexes, renames, routes, or computes rather than the bare wrap, is data-fixing smuggled ahead of construction. The crossing the model performs in one call is being done by hand first, so the value that reaches construction is already unprovenly reshaped.

A before-validator that indexes, renames, routes, or computes is an alias, a path, or a nested model not yet written:

- a key rename is `Field(alias=...)`;
- data wrapped at one key is `validation_alias`, nested wrappers an `AliasPath`, the wrapper modeled and never indexed past;
- nested structure is a nested foreign model.

The only legal before-validator is the ordered union's wrap: a single line on the failure variant that places the bare input under its field name so the variants can be attempted, with a recorded substrate run showing the declarative inventory refuses the shape. One return, constant keys, the input as every value.

```python
@model_validator(mode="before")
def fix(cls, v):
    v["price"] = v.pop("px")   # a rename: Field(alias="px") on the price field
    return v
```
