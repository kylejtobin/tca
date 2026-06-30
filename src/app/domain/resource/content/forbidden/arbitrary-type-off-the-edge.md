---
name: tca_forbidden_pattern_arbitrary_type_off_the_edge
description: The arbitrary-type anti-pattern. `arbitrary_types_allowed` outside the live model lets an unmodeled foreign object sit inside a value. Read this while building a consistency model to see the one class that may carry it.
---

## Arbitrary type off the edge

`arbitrary_types_allowed` anywhere but the one live model lets an unmodeled foreign object sit inside a value: meaning the ontology never described.

`arbitrary_types_allowed` is legal on the consistency model and nowhere else, because that is the one node where live clients converge. A foreign system's data shape entering a frozen value is a foreign model, named for the foreign thing, lifting whole; a live client is held only by the consistency model.

```python
class Snapshot(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)   # legal only on the consistency model
    client: SomeSDKThing   # a live client belongs on the consistency model; foreign data belongs in a foreign model
```
