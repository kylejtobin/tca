---
paths:
  - "**/api/**"
---

# Route Files

Each route file is a thin membrane mapping transport to domain contracts.

**Contains:** Route definitions using FastAPI decorators. Request and response types imported from `domain/context/api.py`.
**Imports from:** `domain/context/api.py` for contracts. FastAPI for routing.

No model definitions in this file. No computation. No transformation. Contracts are domain-owned — import them, do not redefine them here.
