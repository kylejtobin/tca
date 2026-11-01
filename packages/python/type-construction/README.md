# type-construction

TCA is a declarative, event-driven application framework under development.

The package currently exports two configuration-only Pydantic value bases, a
configuration base and the NATS connection contract:

```python
from type_construction import Model, NatsConnection, Root, Settings
```

`Model` extends `BaseModel`; `Root[T]` extends `RootModel[T]`. Both enable
`validate_default=True` and `frozen=True` without overriding native construction.

`Settings` extends `pydantic_settings.BaseSettings` with the same guarantees and
nested environment variables delimited by `__`. Applications specialize it with
typed fields and compose `NatsConnection`, the `servers` configuration the native
NATS client consumes, as a nested field. The application's settings class is the
acquisition boundary: native Pydantic Settings acquires every requirement in its
documented order: initialization values, environment, configured dotenv,
configured secret files, then defaults.

`NatsConnection.servers` is one of the pools the native client connects with:
`TcpPool`, nonempty `nats://` and `tls://` URLs, or `WebSocketPool`, nonempty
`ws://` and `wss://` URLs, both exported from `type_construction.nats`. A pool
mixing the two transport families fails configuration construction. URLs are
native URL values, so equivalent spellings denote the same endpoint and the
client applies its own default ports. The WebSocket transport is available
because the distribution requires `nats-py[aiohttp]`.

Remaining application constructs and native execution integrations are not yet
implemented.
The product definition and architectural contract are maintained in the
[TCA repository](https://github.com/kylejtobin/tca).
