---
name: tca_forbidden_pattern_stub_verb
description: The stub-verb anti-pattern. A `raise`/`pass`/`...` verb body. Read this while building a verb to see why the plan entry already is the work, and what the body must construct instead.
---

## Stub verb

A verb body of `raise NotImplementedError`, `pass`, or bare `...` treats the row as a signature to fill later. But the row already is the work: the placeholder is a missing expansion, not a TODO.

A verb body contains at most one construction statement, with constituents constructing inside that call; it may capture a foreign reply before the construction, re-point a state field to the constructed fact, and emit that fact through a client field. A verb that constructs, emits, and yields nothing declares no transition.

```python
def settle(self) -> Receipt:
    raise NotImplementedError   # the row is the work: construct the Receipt and re-point the state field to it
```
