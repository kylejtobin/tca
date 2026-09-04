---
type: Construct
description: The program entrypoint that wires config, clients, bindings, and routes.
---

# composition root

## Definition

The program entrypoint. It constructs config, instantiates concrete clients, passes them to bindings, constructs the consistency model, and registers or invokes routes. It holds no domain logic and defines no domain model.

## Required Form

```python
def main() -> None:
    config = PositionConfig()
    bus = BusClient(config.url.root, config.token.get_secret_value())
    ledger = LedgerClient(config.url.root, config.token.get_secret_value())
    model = PositionBinding().connect(bus=bus, ledger=ledger, opening=Flat())
    run_ingress(lambda raw: fill_route(raw, model))
```

A long-running program's root is the same shape made async; signal handling and graceful teardown are wiring and live here, nowhere else.

```python
async def main() -> None:
    config = PositionConfig()
    bus = BusClient(config.url.root, config.token.get_secret_value())
    ledger = LedgerClient(config.url.root, config.token.get_secret_value())
    model = PositionBinding().connect(bus=bus, ledger=ledger, opening=Flat())
    shutdown = asyncio.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        asyncio.get_running_loop().add_signal_handler(sig, shutdown.set)
    await shutdown.wait()
    await bus.drain()
```

`.root` and `get_secret_value()` are legal here because the composition root is a client binding site, one of the two places the program meets the wire.

## Sorting Rules

Domain construction belongs to the consistency model and its verbs; the root only wires. Client binding belongs to the binding; the root instantiates clients and hands them over. Request handling belongs to routes; the root registers or invokes them. Environment reads belong to config; the root constructs it once.

## Replaced Forms

A runner, pipeline, orchestrator, or step list is a hand-kept copy of an order the construction graph already determines: a value cannot construct before its inputs, so evaluation order is the sequence. A function that calls everything in order means the terminal object has not been named; name it and construct it.

## Allowed Patterns

- one `main()` that constructs config, instantiates clients, binds through bindings, constructs the consistency model, and registers or invokes routes
- the async form with signal handlers, a shutdown event, and client drain
- `.root` and `get_secret_value()` at client instantiation
- input read and output emitted only at the edges of `main`

## Forbidden

- an orchestrator, pipeline, or step-runner sequencing domain work
- a domain computation in the entrypoint
- a domain model defined in the entrypoint's file
- an environment read outside config
