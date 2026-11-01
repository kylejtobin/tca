"""Native resource contracts and their runtime realization.

The module implements the resource part of docs/architecture/DESIGN.md sections 5.2, 5.4 and 7.
``Resource`` is the immutable configuration an application-owned native NATS broker requires; it
composes the ``NatsConnection`` contract and is acquired through the application's ``Settings``
like any other requirement. ``bind_resource`` is the framework binding that realizes one resource
placement: it constructs the native ``NatsBroker`` from that configuration and registers it with
its owning FastStream runtime. The live broker stays a native object outside the model, FastStream
owns its lifetime, and handlers registered on that broker receive it and its nats-py client and
JetStream context through FastStream's native broker context. Neither declaring nor binding a
resource opens a connection.
"""

from faststream import FastStream
from faststream.nats import NatsBroker

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
    The function constructs and registers only; it loads no settings, opens no connection,
    starts no subscriber, creates no stream and implements no shutdown.
    """
    broker = NatsBroker(
        servers=[str(url.root) for url in resource.connection.servers.urls.root],
    )
    owner.add_broker(broker)
    return broker
