---
paths:
  - "**/service/*.py"
  - "**/service.py"
---

# service — the transport binding shim

Derived from the Service construct in `docs/type-construction-architecture.md`. A service is
a connection shim, glue and not a value construct: a small class whose `connect` binds a
transport client to the active model so the active model has its client field. It holds no
domain logic, owns no domain types, and makes no domain decision.

    class FeedService:
        def connect(self, socket: SocketClient, store: StoreClient) -> FeedModel:
            return FeedModel(socket=socket, store=store)

Transport-level setup is the whole of it: connection, authentication, subscription. When a
service becomes interesting, domain meaning has escaped into it and belongs back on the
active model.

**The breaks this file forbids:**
- Domain logic, classification, or derivation inside the service (escaped). It belongs on
  the active model.
- A domain type defined here. The service owns none.
