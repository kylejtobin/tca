---
name: tca_forbidden_pattern_body_drifted_from_the_chain
description: The body-drifted anti-pattern. A verb body disagrees with its declared chain. Read this while building a verb to see the two ways the body and the chain diverge.
---

## Body drifted from the chain

The declared chain and the body disagree. A `constructs`/`emits` participant the body never touches is promised work undone; a value-type the chain cannot account for is unmodeled work smuggled in.

The body realizes exactly the chain the row declares: it constructs every `constructs` participant and emits every `emits` participant, and it touches no value-type the chain does not name. Work the body needs that the chain does not carry is a meaning to model in the row first.

```python
# row: emits SignalSnapshot
def observe(self) -> None:
    self.book.ingest(tick)   # never touches the snapshot it promised: construct and emit the SignalSnapshot the chain declares
```
