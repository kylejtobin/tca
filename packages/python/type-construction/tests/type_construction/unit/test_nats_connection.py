"""The supplied NATS connection contract is typed, required, frozen and consumable natively.

Governing requirements: docs/architecture/DESIGN.md sections 5.2 (an integration supplies the
settings contract its resource requires), 5.4 (native ``NatsBroker`` consumes the configuration)
and 6.1 (valid configuration establishes no connectivity). Expected server forms follow the
``servers`` parameter of ``nats.connect``: one URL per server in the schemes the client accepts.
"""

import pytest
from faststream.nats import NatsBroker
from pydantic import AnyUrl, ValidationError

from type_construction import NatsConnection


def test_deployment_must_supply_at_least_one_server() -> None:
    with pytest.raises(ValidationError) as missing:
        NatsConnection.model_validate({})
    with pytest.raises(ValidationError) as empty:
        NatsConnection(servers=())

    assert [(e["loc"], e["type"]) for e in missing.value.errors()] == [(("servers",), "missing")]
    assert [(e["loc"], e["type"]) for e in empty.value.errors()] == [(("servers",), "too_short")]


def test_servers_keep_their_supplied_host_and_port() -> None:
    connection = NatsConnection.model_validate(
        {"servers": ["nats://nats", "tls://backup.example:4223", "wss://edge.example:443/"]}
    )

    assert [(server.scheme, server.host, server.port) for server in connection.servers] == [
        ("nats", "nats", None),
        ("tls", "backup.example", 4223),
        ("wss", "edge.example", 443),
    ]


def test_servers_outside_the_native_forms_are_rejected_at_their_position() -> None:
    with pytest.raises(ValidationError) as excinfo:
        NatsConnection.model_validate(
            {
                "servers": [
                    "nats://nats:4222",
                    "http://nats:8222",
                    "nats.internal:4222",
                    "nats://a:4222,b:4223",
                    "nats://",
                ]
            }
        )

    assert [(e["loc"], e["type"]) for e in excinfo.value.errors()] == [
        (("servers", 1), "url_scheme"),
        (("servers", 2), "url_scheme"),
        (("servers", 3), "url_parsing"),
        (("servers", 4), "url_parsing"),
    ]


def test_native_broker_accepts_the_configured_servers_without_connecting() -> None:
    connection = NatsConnection(servers=(AnyUrl("nats://nats"), AnyUrl("nats://backup:4223")))

    broker = NatsBroker(servers=[str(server) for server in connection.servers])

    assert isinstance(broker, NatsBroker)


def test_connection_rejects_reassignment() -> None:
    connection = NatsConnection(servers=(AnyUrl("nats://nats:4222"),))

    with pytest.raises(ValidationError) as excinfo:
        connection.servers = ()

    assert excinfo.value.errors()[0]["type"] == "frozen_instance"
    assert hash(connection) == hash(NatsConnection(servers=(AnyUrl("nats://nats:4222"),)))
