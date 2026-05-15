---
paths:
  - "**/service/**"
---

# Service Files — Transport Shims

Each service file is a class with a single connect function.

**Shape:**
```python
class CatalogService:
    async def connect(self, client: TransportClient) -> None:
        # Transport-level setup only: connection, auth, subscription
        # Bind client to the active model
```

**Contains:** One class. One connect function. Accepts a client, binds it to the context's active model.
**Imports from:** The context's active model in `domain/context/`.

No domain logic. No computation. No classification. No derivation. Every service file has this same boring shape.
