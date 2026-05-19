---
paths:
  - "**/main.py"
---

# main.py — Composition Root

This file is the composition root and nothing else. Its job is to compose proven dependencies and yield process lifecycle.

## What it contains

- **Observability bridge.** Install a loop exception handler that forwards to the project's logger. One call.
- **Config construction — single expression per root.** Each `BaseSettings` model is constructed in one expression. The model itself binds environment variables; `main.py` never reads `os.environ` or `os.getenv` directly. Multi-line config assembly is a configuration layer that was never forged — fix the layer, not `main.py`.
- **Transport connect — one call.** Open the transport client (HTTP framework startup, message-broker connect, database pool open). The result is a proven client object handed to services.
- **Services bound.** Each `service/*.py` exposes a class with a single `connect()` method. `main.py` calls `await Service().connect(client_or_bus)` and receives the active model the service binds. No services share construction logic; each is a transport shim.
- **Keep-alive primitive.** One of: `await event.wait()` on a shutdown event set by a signal handler; `await asyncio.gather(*long_running_tasks)`; a documented irreducible-seam polling loop bridging a third-party SDK that does not surface exceptions through the asyncio loop.
- **Drain on shutdown.** A `try`/`finally` whose `finally` drains the transport (`await client.drain()`, `await pool.close()`, etc.).

## What it must NOT contain

- `os.environ`, `os.getenv`, or any direct environment-variable read. Configuration enters through `BaseSettings`.
- Multi-expression config construction. If composing a config root takes more than one expression, the missing piece is a typed configuration model — forge it.
- Model definitions, domain logic, computation, derivation.
- Hardcoded lists of opaque identifiers (subjects, channels, instruments, file globs). These are domain truths and live as frozen registry constructs the active model receives.
- `try`/`except` around domain operations. Domain failures bubble through the loop exception handler.
- Coordinator scripts that sequence multiple service calls beyond the single binding pattern.

## Imports from

`config.py` (typed `BaseSettings` roots), `service/*.py` (transport shims), `api/*.py` (route registration if the project has an HTTP layer), `domain/<context>/<concept>.py` (frozen registry constructs that enumerate domain values for binding).

## Shape

```python
async def main() -> None:
    asyncio.get_running_loop().set_exception_handler(forward_to_logger)

    transport_cfg = TransportConfig()
    domain_cfg = DomainConfig()
    subjects = SubjectRegistry.from_config(domain_cfg)

    client = await transport.connect(transport_cfg.url, transport_cfg.token)

    bus = await EventService().connect(client)
    _active = await DomainService().connect(bus, subjects)

    try:
        await shutdown_event.wait()
    finally:
        await client.drain()

asyncio.run(main())
```

That is the entire shape. Anything else is escaped scope.

## Synchronous (non-asyncio) variants

For frameworks that own the loop (FastAPI via uvicorn, Flask, sync workers), `main.py` is even thinner: construct config, construct dependencies, construct the framework's app, return it. The framework drives lifecycle. The same rules apply: single-expression config construction, no environ reads, no domain logic.
