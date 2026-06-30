---
name: tca_forbidden_pattern_module_level_function
description: The module-level-function anti-pattern. A top-level `def` is free-floating behavior, a derivation that has not found its model. Read this while building a derivation to see the two files that license a module function.
---

## Module-level function

A top-level `def` outside route and composition-root files is free-floating behavior. Behavior lives on models as derivations, or in the two file kinds that license module functions.

A fact you are about to compute in a function is a derivation that has not found its model yet: name it on the value whose fields imply it, and the procedure is gone, the work done by the construction the derivation returns. A standalone function computing from a model's fields is that derivation escaped from its owner.

The two licensed homes are the only ones:

- a route is the function at transport ingress: one construction from raw transport data, one dispatch of the innermost value, one serialized reply.
- the composition root is the one `main()` that wires config, clients, bindings, the consistency model, and routes.

Anywhere else, the meaning belongs on a model: a derivation for an implied fact, a verb for a state transition.

```python
def normalize(x): ...   # a derivation on the value whose fields imply the normalized fact
```
