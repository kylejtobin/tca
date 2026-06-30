---
name: tca_forbidden_pattern_union_as_a_class
description: The union-as-a-class anti-pattern. A class wrapping a choice invents a node for a type alias. Read this while building a union to see the alias the choice actually is.
---

## Union as a class

Wrapping a choice in a class invents a node for what is purely a type alias. The choice is selected by discriminator or ordered attempt, never by a class body.

A union is a closed set of frozen variants over one axis, rendered as one alias: `Annotated[A | B, Field(discriminator="kind")]` for identity-carrying data, or `Annotated[A | B, Field(union_mode="left_to_right")]` for foreign data expected to fail. The alias is the union's one form; a class around it is a structure created only to provide `model_validate` the alias already provides.

```python
class SignalUnion(BaseModel): ...   # invents a node: SignalUnion = Annotated[A | B, Field(discriminator="kind")]
```
