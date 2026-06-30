---
name: tca_authorized_construct_composition_root
description: Build the composition root, the only legal top of the program. MUST be invoked before writing main.py or any entrypoint. Replaces the forbidden forms; if a runner, a pipeline, an orchestrator, a step list, or a function that calls everything in order is about to appear, stop and build the composition root instead.
---
# Composition Root

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

## Construct-Specific Doctrine

(none)

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

## Halt Rule

Halt when wiring would require a domain decision, a domain computation, or a model definition. Report the row and the meaning that has no wiring home: the terminal object is not yet named in the table, and the table is not finished.
