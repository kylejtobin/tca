# type-construction

TCA is a declarative, event-driven application framework under development.

The package currently exports two configuration-only Pydantic value bases, a
configuration base, the NATS connection contract and the broker resource:

```python
from type_construction import Model, NatsConnection, Resource, Root, Settings
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

`NatsConnection` is the connection contract the native client consumes. `servers`
is a discriminated sum of two secured pool alternatives selected by the required
`transport` field: `TcpPool` (`"tcp"`) holds `TcpServers`, a nonempty collection of
`TcpUrl` values with the `tls` scheme, and `WebSocketPool` (`"websocket"`) holds
`WebSocketServers`, a nonempty collection of `WebSocketUrl` values with the `wss`
scheme. `credentials` references the deployment's native NATS `.creds` file and
`certificate_authority` references the PEM bundle the client trusts; both are
paths to existing files, and their contents never enter model values,
representations, serialization or validation errors. Deployment supplies the
selected alternative and the references, for example
`ORDERS_NATS__SERVERS='{"transport":"tcp","urls":["tls://nats:4222"]}'`,
`ORDERS_NATS__CREDENTIALS=/run/secrets/tca/application.creds` and
`ORDERS_NATS__CERTIFICATE_AUTHORITY=/run/secrets/tca/ca.pem`. A missing or
unknown discriminator, an untagged list, an empty collection, a hostless URL, a
plaintext `nats://` or `ws://` URL, a URL outside the selected alternative or a
reference to a missing file fails configuration construction. URLs are native URL
values, so equivalent spellings denote the same endpoint, and the client applies
its own default ports. The constituent types are exported from
`type_construction.nats`. The distribution requires `nats-py[aiohttp,nkeys]`, so
the WebSocket transport and credentials signing are available.

`Resource` is the configuration for an application-owned native NATS broker. It
composes `NatsConnection` as its `connection` field and is declared as a field of
the application's settings, so deployment supplies it through the same nested
variables, for example
`ORDERS_BROKER__CONNECTION__SERVERS='{"transport":"tcp","urls":["tls://nats:4222"]}'`
with `ORDERS_BROKER__CONNECTION__CREDENTIALS` and
`ORDERS_BROKER__CONNECTION__CERTIFICATE_AUTHORITY`. The framework realizes a
resource placement with `bind_resource` in `type_construction.resources`: it
constructs a native `NatsBroker` from the connection's ordered URLs, a Python SSL
context that requires and verifies the server certificate and hostname against the
referenced authorities only, the TLS handshake before any protocol exchange on
TCP, and the referenced credentials loaded natively by nats-py, then registers the
broker with the owning FastStream runtime. Application authors do not call it.
Each call realizes a separate placement; uses of one placement share the returned
broker, equal configuration does not merge placements, and separate runtimes own
separate brokers. Handlers registered on that broker receive it, its nats-py
`Client` and its `JetStreamContext` through FastStream's native broker context.
Declaring or binding a resource reads no credential and opens no connection;
FastStream owns the broker's lifetime. The NATS server authorizes each operation
under the identity's permissions; provisioning uses a separate identity.

Development runs a secured NATS server from `compose.yaml`. `just secrets`
generates the development certificates, operator credentials and server
configuration into `.secrets`, which stays out of commits and images and is
mounted read only. The test suite generates its own disposable material and
server and requires `docker` and `openssl` on the host.

Remaining application constructs, shared startup and native execution
integrations are not yet implemented.
The product definition and architectural contract are maintained in the
[TCA repository](https://github.com/kylejtobin/tca).
