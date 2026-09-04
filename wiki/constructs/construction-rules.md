---
type: Reference
description: Construction replaces validation; the dependency graph determines order.
---

# Construction Rules

Construction replaces validation as a separate step: a value that fails construction does not exist as a domain value. Do not write a check after construction to prove the value again, do not move an unproven value forward, and do not store, pass, or branch on unmodeled data. Do not compute a domain fact in a free function when the fact is implied by a model's fields, and do not sequence domain work in a function, handler, processor, manager, pipeline, or orchestrator. The dependency graph between constructed values determines construction order.
