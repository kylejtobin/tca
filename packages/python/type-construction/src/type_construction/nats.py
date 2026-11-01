"""Native NATS integration contracts.

The module implements the configuration part of docs/architecture/DESIGN.md section 5.4: the
typed connection configuration the native ``nats-py`` client consumes through FastStream's
``NatsBroker``. The contract is a plain nested model because the application's ``Settings`` is
the acquisition boundary: one construction of the application's declaration acquires every
requirement, including this one, from the native sources in native precedence. This module
therefore acquires no configuration and opens no connection.
"""

from typing import Annotated

from pydantic import AnyUrl, Field, UrlConstraints

from type_construction.models import Model, Root

__all__ = ["NatsConnection", "TcpPool", "TcpUrl", "WebSocketPool", "WebSocketUrl"]

type TcpUrl = Annotated[
    AnyUrl,
    UrlConstraints(allowed_schemes=["nats", "tls"], host_required=True),
]
"""A server the native client reaches over TCP, plain (``nats``) or TLS (``tls``)."""

type WebSocketUrl = Annotated[
    AnyUrl,
    UrlConstraints(allowed_schemes=["ws", "wss"], host_required=True),
]
"""A server the native client reaches over its WebSocket transport (``ws`` or ``wss``)."""


class TcpPool(Root[tuple[TcpUrl, ...]]):
    """A nonempty pool of TCP and TLS servers, one URL per server."""

    root: tuple[TcpUrl, ...] = Field(min_length=1)


class WebSocketPool(Root[tuple[WebSocketUrl, ...]]):
    """A nonempty pool of WebSocket servers, one URL per server."""

    root: tuple[WebSocketUrl, ...] = Field(min_length=1)


class NatsConnection(Model):
    """Connection configuration for the native NATS client.

    ``servers`` names the ``servers`` parameter of ``nats.connect`` and ``NatsBroker``: the pool
    the client connects to and fails over between. The native client runs one transport per
    connection, so a valid pool is either TCP/TLS servers or WebSocket servers; a pool mixing
    the two families is not a member of either alternative and fails construction. Each URL is
    constructed as a native URL value: equivalent spellings denote the same endpoint, and the
    client receives that endpoint's scheme, host and port meaning and applies its own default
    ports. Deployment must supply the pool; the contract declares no endpoint default. Valid
    configuration establishes no connectivity or authorization.
    """

    servers: TcpPool | WebSocketPool
