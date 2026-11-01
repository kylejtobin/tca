"""Native NATS integration contracts.

The module implements the configuration part of docs/architecture/DESIGN.md section 5.4: the
typed connection configuration the native ``nats-py`` client consumes through FastStream's
``NatsBroker``. The contract uses the section 5.1 forms: named URL refinements, named
collections, product alternatives and an explicitly discriminated sum. It is a plain nested
model because the application's ``Settings`` is the acquisition boundary: one construction of the
application's declaration acquires every requirement, including this one, from the native
sources in native precedence. This module therefore acquires no configuration and opens no
connection.
"""

from typing import Annotated, Literal

from pydantic import AnyUrl, Field, UrlConstraints

from type_construction.models import Model, Root

__all__ = [
    "NatsConnection",
    "TcpPool",
    "TcpServers",
    "TcpUrl",
    "WebSocketPool",
    "WebSocketServers",
    "WebSocketUrl",
]


class TcpUrl(
    Root[
        Annotated[
            AnyUrl,
            UrlConstraints(
                allowed_schemes=["nats", "tls"],
                host_required=True,
            ),
        ]
    ]
):
    """A constructed TCP/TLS server URL."""


class WebSocketUrl(
    Root[
        Annotated[
            AnyUrl,
            UrlConstraints(
                allowed_schemes=["ws", "wss"],
                host_required=True,
            ),
        ]
    ]
):
    """A constructed WebSocket server URL."""


class TcpServers(Root[tuple[TcpUrl, ...]]):
    """A nonempty ordered collection of TCP/TLS server URLs."""

    root: tuple[TcpUrl, ...] = Field(min_length=1)


class WebSocketServers(Root[tuple[WebSocketUrl, ...]]):
    """A nonempty ordered collection of WebSocket server URLs."""

    root: tuple[WebSocketUrl, ...] = Field(min_length=1)


class TcpPool(Model):
    """The pool alternative the native client reaches over TCP, plain or TLS."""

    transport: Literal["tcp"]
    urls: TcpServers


class WebSocketPool(Model):
    """The pool alternative the native client reaches over its WebSocket transport."""

    transport: Literal["websocket"]
    urls: WebSocketServers


class NatsConnection(Model):
    """Connection configuration for the native NATS client.

    ``servers`` is the pool the client connects to and fails over between, projected to the
    ``servers`` parameter of ``nats.connect`` and ``NatsBroker`` as the ordered URL strings of the
    selected alternative. Deployment selects the alternative explicitly through ``transport``;
    the native client runs one transport per connection, so each alternative admits only its own
    URL schemes. Each URL is constructed as a native URL value: equivalent spellings denote the
    same endpoint, and the client receives that endpoint's scheme, host and port meaning and
    applies its own default ports. The contract declares no endpoint default. Valid configuration
    establishes no connectivity or authorization.
    """

    servers: Annotated[
        TcpPool | WebSocketPool,
        Field(discriminator="transport"),
    ]
