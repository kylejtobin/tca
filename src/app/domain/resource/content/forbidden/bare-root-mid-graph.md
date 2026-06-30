---
name: tca_forbidden_pattern_bare_root_mid_graph
description: The bare-root anti-pattern. A `.root` value held as a bare primitive mid-graph. Read this while building any construct that reads `.root` to see which consumption and wire-edge readings are legal and which break the graph.
---

## Bare `.root` mid-graph

`.root` unwraps a `RootModel` to its bare inner primitive, dropping the proof the scalar or collection carried. The unwrap is innocent in itself; what the program does with the bare value next is what this anti-pattern names. The violation is a **held unwrap**: a `.root` whose primitive is kept inside the program rather than immediately fed onward. Held is a closed set of three structural homes:

- **bound to a name** — `px = self.quote.price.root` (the proof is dropped a statement early and carried as a loose primitive),
- **operated on as a raw value** — `self.bid.root + self.ask.root` (the proof is consumed by arithmetic or comparison, not by a construction),
- **handed to a method or non-constructing call** — `self.bus.publish(self.spread.root)` (the bare value is pushed to I/O instead of the binding serializing a whole proven value at the wire).

Everything else an unwrap can do is **consumed, not held**, and is not a violation. A `.root` fed *straight* into a construction is consumed by it: an argument to a Type call, a key or value in a mapping being built, an element splatted into a collection, a comprehension source, an f-string that feeds a construction. So is a `.root` at the **wire edge** (a route reply under `api/`, a client binding under `service/`), where unwrapping to a bare primitive is the legal crossing out of the program. These are legal because they are simply not a held unwrap, not because of an exception carved out for them.

```python
@cached_property
def snapshot(self) -> Snapshot:
    price = self.quote.price.root             # BAD: held — bound to a name, the proof dropped early
    return Snapshot(price=Price(price))

@cached_property
def tag(self) -> Tag:
    return Tag(self.symbol.root)              # GOOD: consumed — fed straight into the construction
```
