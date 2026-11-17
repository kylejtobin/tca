# type-construction

TCA is a declarative, event-driven application framework under development.

The package exports two configuration-only Pydantic value bases, a configuration
base and the shared resource contract:

```python
from type_construction import Model, Resource, Root, Settings
```

`Model` extends `BaseModel`; `Root[T]` extends `RootModel[T]`. Both enable
`validate_default=True` and `frozen=True` without overriding native construction.

`Settings` extends `pydantic_settings.BaseSettings` with the same guarantees,
nested environment variables delimited by `__`, and `hide_input_in_errors=True`,
because a rejected deployment value may itself be a secret. Applications
specialize it with typed fields and compose integration-supplied contracts as
nested fields. The application's settings class is the acquisition boundary:
native Pydantic Settings acquires every requirement in its documented order:
initialization values, environment, configured dotenv, configured secret files,
then defaults.

`Resource[Native]` is the configuration of an integration resource whose
realization yields a native object of type `Native`. An execution integration
specializes it with typed configuration and implements `bind(owner)`, which
realizes one resource placement in one FastStream runtime and returns the actual
native object. Application authors declare the supplied specializations as
settings fields; they do not call `bind`. Each call realizes a separate
placement: uses of one placement share its native object, equal configuration
realized again yields a distinct object, and separate runtimes own separate
objects. Live objects are never model fields and are never serialized.

`type_construction.diagnostics` supplies `Problem` and `problems(error)`, the
framework's typed projection of a Pydantic `ValidationError` to locations, kinds
and messages. It omits the rejected inputs and the native exception context,
which Pydantic's default `errors()` includes.

The core imports without the NATS client. The NATS execution integration is
`type_construction.nats` and requires the `nats` installation extra:
`type-construction[nats]`, which installs `faststream[nats]` and
`nats-py[aiohttp,nkeys]`.

```python
from type_construction.nats import NatsConnection, NatsResource
```

`NatsConnection` is the connection contract the native client consumes. `servers`
is a discriminated sum of two secured pool alternatives selected by the required
`transport` field: `TcpPool` (`"tcp"`) holds `TcpServers`, a nonempty collection of
`TcpUrl` values with the `tls` scheme, and `WebSocketPool` (`"websocket"`) holds
`WebSocketServers`, a nonempty collection of `WebSocketUrl` values with the `wss`
scheme. Every URL is a native `AnyUrl` refined by `WithoutCredentials`: a URL
carrying a username, token or password is rejected at construction, and the
rejected value is hidden from the displayed error. `credentials` references the
deployment's native NATS `.creds` file and `certificate_authority` references the
PEM bundle the client trusts; both are paths to existing files, and their contents
never enter model values, representations, serialization or validation errors.
Deployment supplies the selected alternative and the references, for example
`ORDERS_NATS__SERVERS='{"transport":"tcp","urls":["tls://nats:4222"]}'`,
`ORDERS_NATS__CREDENTIALS=/run/secrets/tca/application.creds` and
`ORDERS_NATS__CERTIFICATE_AUTHORITY=/run/secrets/tca/ca.pem`. A missing or
unknown discriminator, an untagged list, an empty collection, a hostless URL, a
plaintext `nats://` or `ws://` URL, a URL outside the selected alternative, a URL
with userinfo or a reference to a missing file fails configuration construction.
URLs are native URL values, so equivalent spellings denote the same endpoint, IPv6
hosts are admitted, and the client applies its own default ports. The constituent
types are exported from `type_construction.nats`.

`NatsResource` is the `Resource[NatsBroker]` specialization: its `connection`
field is a `NatsConnection`, and an application declares it as a settings field,
so deployment supplies it through the same nested variables, for example
`ORDERS_BROKER__CONNECTION__SERVERS='{"transport":"tcp","urls":["tls://nats:4222"]}'`
with `ORDERS_BROKER__CONNECTION__CREDENTIALS` and
`ORDERS_BROKER__CONNECTION__CERTIFICATE_AUTHORITY`. Its `bind` constructs a native
`NatsBroker` from the connection's ordered URLs, a Python SSL context that requires
and verifies the server certificate and hostname against the referenced
authorities only, and the TLS handshake before any protocol exchange on TCP, then
registers the broker with the owning FastStream runtime and returns it. Binding
reads the credentials file once and hands that snapshot to FastStream's
`NatsCredentials.from_raw`, which rejects content lacking the JWT or seed markers
before any connection is attempted; the snapshot lives in the native security
object, not in the model, and later changes to the file do not affect the
realized broker. Declaring or constructing a resource reads no credential and
opens no connection. The native client signs the server's nonce with the NKey and
the NATS server authenticates and authorizes each operation; the application
identity holds least-privilege permissions, and provisioning uses a separate
identity. Handlers registered on the broker receive it, its nats-py `Client` and
its `JetStreamContext` through FastStream's native broker context.

Development runs a secured NATS server from `compose.yaml`. `just secrets`
generates the certificates, operator credentials and server configuration under
`TCA_SECRETS` (default `~/.local/state/tca/secrets`), outside the repository tree,
partitioned by consumer: the application container mounts `application/` read
only at `/run/secrets/tca`, the NATS container mounts `server/` read only, and
`provisioning/` (setup credentials and signing keys) is mounted nowhere. Repeated
`just secrets` preserves existing complete material; incomplete material fails
without changes. `just reset` removes the Compose project's containers and its
JetStream volume and generates new identities, because data persisted under the
previous account cannot be reached by the new one. The test suite generates its
own disposable material, servers and Compose project, and requires `docker`,
`openssl` and the environment's `just` on the host.

Remaining application constructs, shared startup and native execution
integrations are not yet implemented.
The product definition and architectural contract are maintained in the
[TCA repository](https://github.com/kylejtobin/tca).
