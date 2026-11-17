"""The NATS execution integration: connection contracts, the broker resource and its binding.

The module implements the NATS realization of docs/architecture/DESIGN.md sections 5.4 and 7.
It holds every provider-specific declaration and dependency: the typed connection configuration
the native ``nats-py`` client consumes through FastStream's ``NatsBroker``, the ``NatsResource``
specialization of the shared ``Resource`` contract, and the binding that realizes a resource
placement as a native broker registered with its FastStream runtime. The package installs these
dependencies through the ``nats`` extra; the core exports do not import this module.

The contracts use the section 5.1 forms: named URL and file references, named collections,
product alternatives and an explicitly discriminated sum. Values are acquired through the
application's ``Settings``, which constructs every requirement from the native sources in native
precedence. Importing the module and constructing its models acquires no configuration, reads no
credential and opens no connection; only ``NatsResource.bind`` reads the referenced credentials.
Rejected inputs are hidden from displayed validation errors because a rejected deployment value
may carry a secret, such as a URL with a password.
"""

import ssl
from typing import Annotated, Literal

from faststream import FastStream
from faststream.nats import NatsBroker
from faststream.nats.security import NatsCredentials
from pydantic import AfterValidator, AnyUrl, ConfigDict, Field, FilePath, UrlConstraints
from pydantic_core import PydanticCustomError

from type_construction.models import Model, Root
from type_construction.resources import Resource

__all__ = [
    "CertificateAuthorityFile",
    "CredentialsFile",
    "NatsConnection",
    "NatsResource",
    "TcpPool",
    "TcpServers",
    "TcpUrl",
    "WebSocketPool",
    "WebSocketServers",
    "WebSocketUrl",
    "WithoutCredentials",
]

# Displayed validation errors omit the rejected input; see the module docstring.
HIDE_INPUT = ConfigDict(hide_input_in_errors=True)


URL_CREDENTIALS = "url_credentials"
URL_CREDENTIALS_MESSAGE = "URL must not carry userinfo; credentials are referenced by file"


def _without_credentials(url: AnyUrl) -> AnyUrl:
    if url.username is not None or url.password is not None:
        raise PydanticCustomError(URL_CREDENTIALS, URL_CREDENTIALS_MESSAGE)
    return url


WithoutCredentials = AfterValidator(_without_credentials)
"""The refinement that rejects a parsed URL carrying userinfo.

``UrlConstraints`` cannot express the prohibition, so the refinement inspects the native parsed
``username`` and ``password`` properties after Pydantic has parsed and normalized the URL. It is
the single place the integration states that endpoints never carry credentials.
"""


class TcpUrl(
    Root[
        Annotated[
            AnyUrl,
            UrlConstraints(allowed_schemes=["tls"], host_required=True),
            WithoutCredentials,
        ]
    ]
):
    """A constructed TCP server URL; only the TLS scheme is a member and userinfo is rejected."""

    model_config = HIDE_INPUT


class WebSocketUrl(
    Root[
        Annotated[
            AnyUrl,
            UrlConstraints(allowed_schemes=["wss"], host_required=True),
            WithoutCredentials,
        ]
    ]
):
    """A constructed WebSocket server URL; only the secure scheme is a member and userinfo is
    rejected."""

    model_config = HIDE_INPUT


class TcpServers(Root[tuple[TcpUrl, ...]]):
    """A nonempty ordered collection of TLS server URLs."""

    model_config = HIDE_INPUT

    root: tuple[TcpUrl, ...] = Field(min_length=1)


class WebSocketServers(Root[tuple[WebSocketUrl, ...]]):
    """A nonempty ordered collection of secure WebSocket server URLs."""

    model_config = HIDE_INPUT

    root: tuple[WebSocketUrl, ...] = Field(min_length=1)


class TcpPool(Model):
    """The pool alternative the native client reaches over TLS-first TCP."""

    model_config = HIDE_INPUT

    transport: Literal["tcp"]
    urls: TcpServers


class WebSocketPool(Model):
    """The pool alternative the native client reaches over its secure WebSocket transport."""

    model_config = HIDE_INPUT

    transport: Literal["websocket"]
    urls: WebSocketServers


class CredentialsFile(Root[FilePath]):
    """A deployment reference to a native NATS ``.creds`` file holding the user JWT and NKey seed.

    The model holds the path; construction checks that a file exists there and reads nothing.
    ``NatsResource.bind`` reads the file once, when the placement is realized. The contents never
    enter model values, representations, serialization or validation errors.
    """

    model_config = HIDE_INPUT


class CertificateAuthorityFile(Root[FilePath]):
    """A deployment reference to the PEM bundle of certificate authorities the client trusts."""

    model_config = HIDE_INPUT


class NatsConnection(Model):
    """Connection configuration for the native NATS client.

    ``servers`` is the pool the client connects to and fails over between, projected to the
    ``servers`` parameter of ``nats.connect`` and ``NatsBroker`` as the ordered URL strings of the
    selected alternative. Deployment selects the alternative explicitly through ``transport``.
    Both alternatives admit only secured schemes and reject URLs carrying userinfo: the binding
    performs the TLS handshake before any protocol exchange on TCP, ``wss`` is secured by the
    transport, and identity comes from ``credentials``, the referenced native credentials file.
    ``certificate_authority`` references the trust bundle the client verifies server certificates
    and hostnames against. Each URL is constructed as a native URL value: equivalent spellings
    denote the same endpoint, and the client receives that endpoint's scheme, host and port
    meaning and applies its own default ports. The contract declares no endpoint default. Valid
    configuration establishes no connectivity, authentication or authorization.
    """

    model_config = HIDE_INPUT

    servers: Annotated[
        TcpPool | WebSocketPool,
        Field(discriminator="transport"),
    ]
    credentials: CredentialsFile
    certificate_authority: CertificateAuthorityFile


class NatsResource(Resource[NatsBroker]):
    """Configuration for an application-owned native NATS broker.

    Applications declare it as a field of their ``Settings``; deployment supplies the connection
    through the same nested sources. Realization yields the actual ``NatsBroker``, which handlers
    registered on it, and FastStream's ``Client`` and ``JsClient`` annotations, expose together
    with the nats-py client and JetStream context.
    """

    model_config = HIDE_INPUT

    connection: NatsConnection

    def bind(self, owner: FastStream) -> NatsBroker:
        """Realize this placement as a new native broker registered with ``owner``.

        The broker verifies server certificates and hostnames against the referenced authorities
        only, accepts TLS 1.2 or later (Python's default floor depends on the OpenSSL build's
        configuration), negotiates TLS before any protocol exchange on TCP and authenticates with
        the referenced credentials. The credentials file is read here, once, and the snapshot is
        handed to FastStream's ``NatsCredentials.from_raw``, which rejects content lacking the
        JWT or seed markers before any connection is attempted; the native client would otherwise
        read such a file without terminating. The snapshot lives in the native security object,
        not in this model, and later changes to the file do not affect this broker. Framing is
        all the guard establishes: NKey signing, authentication and authorization remain native
        judgments made when the broker connects. The method constructs and registers only; it
        opens no connection, starts no subscriber, creates no stream and implements no shutdown.
        A rejected snapshot registers nothing.
        """
        connection = self.connection
        trust = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile=str(connection.certificate_authority.root),
        )
        trust.minimum_version = ssl.TLSVersion.TLSv1_2
        security = NatsCredentials.from_raw(
            connection.credentials.root.read_text(),
            ssl_context=trust,
            tls_handshake_first=True,
        )
        broker = NatsBroker(
            servers=[str(url.root) for url in connection.servers.urls.root],
            security=security,
        )
        owner.add_broker(broker)
        return broker
