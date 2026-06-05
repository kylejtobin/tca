---
paths:
  - "**/api/*.py"
---

# route — the ingress membrane

Derived from the Route construct in `docs/type-construction-architecture.md`. A route is the
ingress membrane at the transport edge. It imports domain-owned contracts, hands a raw
request to a boundary model for construction, dispatches the constructed value to the active
model, and projects the result back onto the transport. It defines no types and computes
nothing.

    def feed_route(raw: str, model: FeedModel) -> str:
        message = FeedEnvelope.model_validate_json(raw)   # construct boundary truth
        model.ingest(message)                              # dispatch to the active model
        return Ack(status=AckStatus("accepted")).model_dump_json()  # project the result

When a route grows interesting, meaning has escaped into the edge and belongs back on the
active model.

**The breaks this file forbids:**
- Computation or transformation inside the route (escaped). Use the active model behind it.
- A domain type defined here. Contracts are imported from the domain's `api.py`.
