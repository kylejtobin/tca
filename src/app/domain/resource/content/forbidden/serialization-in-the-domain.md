---
name: tca_forbidden_pattern_serialization_in_the_domain
description: The domain-serialization anti-pattern. A `.model_dump` or `.model_dump_json` anywhere in the domain. Read this while building a verb, derivation, or route to see why serialization is the crossing out of the app, legal only at the edge.
---

## Serialization in the domain

`.model_dump` or `.model_dump_json` turns a proven value into a dict or JSON: the crossing *out* of the application. That crossing belongs only at the edge, where the program meets the wire. Inside the domain a value stays whole, a constructed fact moving between constructions; the domain hands the edge that whole value, never a serialized one, and never reaches past the edge to the transport itself.

The two legal serialization sites are the route reply (`api/`) and the client binding (`service/`). Everywhere else, in a concept model, a derivation, a verb, the consistency model, a `.model_dump`/`.model_dump_json` flattens a value that is still moving inside the program. A verb emits the proven value itself through its client fields and lets the binding serialize at the wire; it never builds the JSON itself, and never hands JSON forward to the binding or the transport.

```python
def book(self, fill: VenueFill) -> None:
    self.latest = Position(prior=self.latest, fill=fill)
    self.bus.publish(self.latest.model_dump())   # publish self.latest whole; let the binding serialize at the wire
```
