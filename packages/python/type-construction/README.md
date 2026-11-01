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

`NatsConnection.servers` is a discriminated sum of two pool alternatives selected
by the required `transport` field: `TcpPool` (`"tcp"`) holds `TcpServers`, a
nonempty collection of `TcpUrl` values with the `nats` or `tls` scheme, and
`WebSocketPool` (`"websocket"`) holds `WebSocketServers`, a nonempty collection
of `WebSocketUrl` values with the `ws` or `wss` scheme. Deployment supplies the
selected alternative, for example
`ORDERS_NATS__SERVERS='{"transport":"tcp","urls":["nats://nats:4222","tls://backup.example:4223"]}'`.
A missing or unknown discriminator, an untagged list, an empty collection, a
hostless URL or a URL outside the selected alternative's schemes fails
configuration construction. URLs are native URL values, so equivalent spellings
denote the same endpoint, and the client applies its own default ports. The
constituent types are exported from `type_construction.nats`. The WebSocket
transport is available because the distribution requires `nats-py[aiohttp]`.

Remaining application constructs and native execution integrations are not yet
implemented.
The product definition and architectural contract are maintained in the
[TCA repository](https://github.com/kylejtobin/tca).
