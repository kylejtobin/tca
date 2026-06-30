---
name: tca_forbidden_pattern_multiple_constructions_in_one_verb
description: The multiple-construction anti-pattern. Two top-level construction statements in a verb. Read this while building a verb to see why a verb is one construction, with constituents built inside that call.
---

## Multiple constructions in one verb

Two or more top-level construction statements sequence the graph by hand. A verb is one state transition, which is one construction, with constituents constructing inside that single call.

The body holds at most one construction statement. A constituent the composite holds constructs inside the composite's own call, proven by coercion there; a constituent built in a separate statement beside the composite restates what the composite's call already proves.

```python
def advance(self) -> SignalSnapshot:
    spread = Spread(...)             # one
    return SignalSnapshot(spread)    # two: construct the Spread inside the SignalSnapshot call, so the verb has one construction
```
