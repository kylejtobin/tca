---
type: construct
---

# Composition root

## Definition

The program entrypoint. It constructs config, instantiates concrete clients, passes them to bindings, constructs the consistency model, and registers or invokes routes. It holds no domain logic and defines no domain model.

## Required form

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

`.root` and `get_secret_value()` are legal here: the composition root is a client binding site, one of the two places the program meets the wire.

## Replaced forms

- A runner, pipeline, orchestrator, or step list is a hand-kept copy of an order the construction graph already determines: a value cannot construct before its inputs, so evaluation order is the sequence.
- A function that calls everything in order means the terminal object has not been named: name it and construct it.

## Sorting

- Domain construction → [consistency model](consistency-model.md) and its [verbs](verb.md); the root only wires.
- Client binding → [binding](binding.md); the root instantiates clients and hands them over.
- Request handling → [route](route.md); the root registers or invokes routes.
- Environment reads → [config](config.md); the root constructs config once.
- Program placement → lives in `main.py`; see [topology](topology.md).

## Allowed

- one `main()` that constructs config, instantiates clients, binds through bindings, constructs the consistency model, and registers or invokes routes
- the async form with signal handlers, a shutdown event, and client drain
- `.root` and `get_secret_value()` at client instantiation
- input read and output emitted only at the edges of `main`

## Forbidden

- an orchestrator, pipeline, or step-runner sequencing domain work
- a domain computation in the entrypoint
- a domain model defined in the entrypoint's file
- an environment read outside config
