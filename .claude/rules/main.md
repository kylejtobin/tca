---
paths:
  - "**/main.py"
---

# main.py — the composition root

Derived from the Composition root construct in `docs/type-construction-architecture.md`.
`main.py` is the single top of the wiring graph. It instantiates the concrete clients, hands
them to the services, constructs the active model, and registers the routes. It is the only
place wiring is assembled and holds no domain logic, no model definitions, and no
computation: the imperative shell that builds the typed core and then steps back.

    def main() -> None:
        config = FeedConfig()                                  # construct the typed proof once
        socket = SocketClient(config.socket_url.root)          # instantiate the concrete clients
        store = StoreClient(config.store_dsn.root)
        model = FeedService().connect(socket=socket, store=store)  # bind through the service
        run_feed_loop(lambda raw: model.ingest(raw))           # start the edge, then step back

**The breaks this file forbids:**
- Domain logic, classification, or a model definition here (escaped). Wiring only.
- An orchestrator/pipeline/step-runner sequencing the work. The dependency between proven
  facts is the sequence; the active model drives the construction graph.
- An effect emitted before proof.
