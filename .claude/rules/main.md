---
paths:
  - "**/main.py"
---

# main.py — Composition Root

This file is the composition root. It builds dependencies, starts services, registers routes.

**Contains:** Client construction, service startup calls, route registration with FastAPI.
**Imports from:** `config.py`, `service/*.py`, `api/*.py`.

No model definitions. No domain logic. No computation. No derivation.
