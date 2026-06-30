---
name: tca_forbidden_pattern_field_the_ontology_did_not_model
description: The unmodeled-field anti-pattern. A class field disagrees with its plan entry. Read this while building any composite to see the three ways the class and the plan drift apart.
---

## Field the ontology didn't model

Class and catalog disagree. An extra field is unmodeled meaning entering source; a missing field is modeled meaning never rendered; a wrong annotation breaks the edge. The ontology row is the authority for the field set and each field's type.

The class carries exactly the fields its row declares, each with the declared type. A field the code needs that no row names is a meaning to place in the ontology first, not to add to the class.

```python
class SignalSnapshot(BaseModel, frozen=True, extra="forbid"):
    spread: Spread
    urgency: int   # no row declares this: place the meaning in the ontology, or remove the field
```
