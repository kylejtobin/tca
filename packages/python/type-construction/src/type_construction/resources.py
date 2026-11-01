"""Native resource contracts and their runtime realization.

The module implements the resource part of docs/architecture/DESIGN.md sections 5.2, 5.4 and 7.
``Resource`` is the immutable configuration an application-owned native NATS broker requires; it
composes the ``NatsConnection`` contract and is acquired through the application's ``Settings``
like any other requirement. ``bind_resource`` is the framework binding that realizes one resource
placement: it constructs the native ``NatsBroker`` from that configuration and registers it with
its owning FastStream runtime. Python's ``ssl`` module verifies server certificates and
hostnames, nats-py performs the TLS handshake first and authenticates with the referenced
credentials file, and the NATS server authorizes each operation. The live broker stays a native
object outside the model, FastStream owns its lifetime, and handlers registered on that broker
receive it and its nats-py client and JetStream context through FastStream's native broker
context. Neither declaring nor binding a resource reads the credentials or opens a connection.
"""

import ssl

from faststream import FastStream
from faststream.nats import NatsBroker
from faststream.nats.security import NatsCredentials

from type_construction.models import Model
from type_construction.nats import NatsConnection

__all__ = ["Resource", "bind_resource"]


class Resource(Model):
    """Configuration for an application-owned native NATS broker."""

    connection: NatsConnection


def bind_resource(
    resource: Resource,
    owner: FastStream,
) -> NatsBroker:
    """Realize one resource placement in the supplied native runtime.

    Every call realizes a separate placement: it constructs a new native broker from the
    resource's connection and registers it with ``owner``. Uses of that placement share the
    returned broker through the association the caller establishes, not through another call.
    Equal configuration does not merge placements, and separate owners hold separate brokers.
    The broker verifies server certificates and hostnames against the referenced certificate
    authorities only, negotiates TLS before any protocol exchange on TCP and authenticates with
    the referenced native credentials file when it connects. The function constructs and
    registers only; it loads no settings, opens no connection, starts no subscriber, creates no
    stream and implements no shutdown.
    """
    connection = resource.connection
    trust = ssl.create_default_context(
        purpose=ssl.Purpose.SERVER_AUTH,
        cafile=str(connection.certificate_authority.root),
    )
    broker = NatsBroker(
        servers=[str(url.root) for url in connection.servers.urls.root],
        security=NatsCredentials.from_file(
            connection.credentials.root,
            ssl_context=trust,
            tls_handshake_first=True,
        ),
    )
    owner.add_broker(broker)
    return broker
