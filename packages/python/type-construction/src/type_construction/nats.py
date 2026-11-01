"""Native NATS integration contracts.

The module implements the configuration part of docs/architecture/DESIGN.md section 5.4: the
typed connection configuration the native ``nats-py`` client consumes through FastStream's
``NatsBroker``. Applications compose ``NatsConnection`` as a field of their ``Settings``; the
settings class acquires its values, so this module acquires no configuration and opens no
connection.
"""

from typing import Annotated

from pydantic import AnyUrl, Field, UrlConstraints

from type_construction.models import Model

__all__ = ["NatsConnection", "NatsUrl"]

type NatsUrl = Annotated[
    AnyUrl,
    UrlConstraints(allowed_schemes=["nats", "tls", "ws", "wss"], host_required=True),
]
"""One server URL in the forms ``nats.connect`` accepts.

The schemes are the ones the native client connects with. The URL keeps its host and port exactly
as supplied; the native client applies its own default port for each scheme. A native ``NatsDsn``
is not used because it rewrites explicit websocket ports to ``4222`` and admits multi-host strings
that the client rejects.
"""


class NatsConnection(Model):
    """Connection configuration for the native NATS client.

    ``servers`` names the ``servers`` parameter of ``nats.connect`` and ``NatsBroker``: the server
    URLs the client connects to and fails over between, one URL per server. Deployment must supply
    at least one server; the contract declares no endpoint default. Valid configuration
    establishes no connectivity or authorization.
    """

    servers: tuple[NatsUrl, ...] = Field(min_length=1)
