---
name: tca-main
description: Build the composition root, the only legal top of the program. MUST be invoked before writing main.py or any entrypoint. Replaces the forbidden forms; if a runner, pipeline, orchestrator, step list, or "what calls all this in order" function is about to appear, stop and build the composition root instead.
---

# composition root

`main.py` is the single top of the wiring graph: it constructs the config proof,
instantiates the concrete clients, binds them through the services, constructs the
consistency model, registers the routes, and steps back. It is the imperative shell around
the typed core, and it holds no domain logic, no model definitions, and no computation.

    def main() -> None:
        config = AnalysisConfig()
        bus = EventBusClient(config.bus_url.root)
        model = AnalysisService().connect(bus=bus)
        print(hook_route(sys.stdin.read(), model))

A long-running program's root is the same shape made async: construct, bind, register
shutdown, wait, drain. Signal handling and graceful teardown are wiring and live here,
nowhere else.

    async def main() -> None:
        config = AppConfig()
        nc = await nats.connect(servers=[config.nats_url.root], token=config.token.get_secret_value())
        bucket = await ObjectService().connect(nc.jetstream(), config.bucket_name, metrics)
        shutdown = asyncio.Event()
        for sig in (signal.SIGTERM, signal.SIGINT):
            asyncio.get_running_loop().add_signal_handler(sig, shutdown.set)
        await shutdown.wait()
        await nc.drain()

The interpreter is the orchestrator. A constructed object cannot evaluate before its
arguments construct, and a derivation cannot be read before its model exists; evaluation
order is the pipeline, so nothing sequences above the construction graph. When the
question "what calls all this in order?" arises, the terminal object has not been named:
name it, write its construction as one expression, and sort every step you were about to
write into a boundary construction (parse), a derivation (compute), a union landing
(decide), or an emit (output).

## The row

The spec row this card expands. The file is `main.py`; main and route files are
the only files where module-level functions pass the gate.

    {"construct": "main", "name": "Main", "file": "main.py"}

## Allowed patterns

- one `main()` that constructs config, instantiates clients, binds through services,
  constructs the consistency model, registers or invokes routes, and projects the result
- input read and output emitted only at the edges of `main`

Build exactly these patterns. Never invent an exception. If you cannot see how, the
modeling is incomplete or construction is not yet the pipeline: report the gap.
