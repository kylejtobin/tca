"""Native NATS integration contracts.

The module implements the configuration part of docs/architecture/DESIGN.md section 5.4: the
typed connection configuration the native ``nats-py`` client consumes through FastStream's
``NatsBroker``. The contract uses the section 5.1 forms: named URL and file references, named
collections, product alternatives and an explicitly discriminated sum. It is a plain nested
model because the application's ``Settings`` is the acquisition boundary: one construction of the
application's declaration acquires every requirement, including this one, from the native
sources in native precedence. This module therefore acquires no configuration, reads no
credential and opens no connection.
"""

from typing import Annotated, Literal

from pydantic import AnyUrl, Field, FilePath, UrlConstraints

from type_construction.models import Model, Root

__all__ = [
    "CertificateAuthorityFile",
    "CredentialsFile",
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
                allowed_schemes=["tls"],
                host_required=True,
            ),
        ]
    ]
):
    """A constructed TCP server URL; only the TLS scheme is a member."""


class WebSocketUrl(
    Root[
        Annotated[
            AnyUrl,
            UrlConstraints(
                allowed_schemes=["wss"],
                host_required=True,
            ),
        ]
    ]
):
    """A constructed WebSocket server URL; only the secure scheme is a member."""


class TcpServers(Root[tuple[TcpUrl, ...]]):
    """A nonempty ordered collection of TLS server URLs."""

    root: tuple[TcpUrl, ...] = Field(min_length=1)


class WebSocketServers(Root[tuple[WebSocketUrl, ...]]):
    """A nonempty ordered collection of secure WebSocket server URLs."""

    root: tuple[WebSocketUrl, ...] = Field(min_length=1)


class TcpPool(Model):
    """The pool alternative the native client reaches over TLS-first TCP."""

    transport: Literal["tcp"]
    urls: TcpServers


class WebSocketPool(Model):
    """The pool alternative the native client reaches over its secure WebSocket transport."""

    transport: Literal["websocket"]
    urls: WebSocketServers


class CredentialsFile(Root[FilePath]):
    """A deployment reference to a native NATS ``.creds`` file holding the user JWT and NKey seed.

    The model holds the path; the native client reads the file when it connects. The contents
    never enter model values, representations, serialization or validation errors.
    """


class CertificateAuthorityFile(Root[FilePath]):
    """A deployment reference to the PEM bundle of certificate authorities the client trusts."""


class NatsConnection(Model):
    """Connection configuration for the native NATS client.

    ``servers`` is the pool the client connects to and fails over between, projected to the
    ``servers`` parameter of ``nats.connect`` and ``NatsBroker`` as the ordered URL strings of the
    selected alternative. Deployment selects the alternative explicitly through ``transport``.
    Both alternatives admit only secured schemes: the binding performs the TLS handshake before
    any protocol exchange on TCP, and ``wss`` is secured by the transport. ``credentials``
    references the native credentials file the client authenticates with and
    ``certificate_authority`` references the trust bundle it verifies server certificates and
    hostnames against. Each URL is constructed as a native URL value: equivalent spellings denote
    the same endpoint, and the client receives that endpoint's scheme, host and port meaning and
    applies its own default ports. The contract declares no endpoint default. Valid configuration
    establishes no connectivity, authentication or authorization.
    """

    servers: Annotated[
        TcpPool | WebSocketPool,
        Field(discriminator="transport"),
    ]
    credentials: CredentialsFile
    certificate_authority: CertificateAuthorityFile
