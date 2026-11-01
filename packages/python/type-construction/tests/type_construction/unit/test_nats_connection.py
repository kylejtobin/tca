"""The supplied NATS connection contract models the server pool the native client accepts.

Governing requirements: docs/architecture/DESIGN.md sections 5.2 (an integration supplies the
settings contract its resource requires), 5.4 (native ``NatsBroker`` consumes the configuration
through ``nats-py``) and 6.1 (valid configuration establishes no connectivity). Expected forms
follow the ``servers`` parameter of ``nats.connect``: a nonempty pool of TCP/TLS servers or a
nonempty pool of WebSocket servers, one URL per server, never both transport families in one
pool. Native consumption is observed through the public server pool of the pinned client, the
public server list of the pinned broker and the client's WebSocket transport class.
"""

import asyncio

import pytest
from faststream.nats import NatsBroker
from nats.aio.client import Client
from nats.aio.transport import WebSocketTransport
from pydantic import AnyUrl, ValidationError

from type_construction import NatsConnection
from type_construction.nats import TcpPool, WebSocketPool

TCP_SERVERS = ["nats://nats", "tls://backup.example:4223"]
WEBSOCKET_SERVERS = ["ws://edge.example:8080", "wss://edge.example"]


def _problems(error: ValidationError) -> set[tuple[tuple[int | str, ...], str]]:
    return {(detail["loc"], detail["type"]) for detail in error.errors()}


def _servers(connection: NatsConnection) -> list[str]:
    """The ``servers`` argument the native client and broker receive."""
    return [str(server) for server in connection.servers.root]


def _endpoints(client: Client) -> list[tuple[str, str | None, int | None]]:
    return [(server.scheme, server.hostname, server.port) for server in client.servers]


def test_deployment_must_supply_a_nonempty_pool() -> None:
    with pytest.raises(ValidationError) as missing:
        NatsConnection.model_validate({})
    with pytest.raises(ValidationError) as empty:
        NatsConnection.model_validate({"servers": []})

    assert _problems(missing.value) == {(("servers",), "missing")}
    assert _problems(empty.value) == {
        (("servers", "TcpPool"), "too_short"),
        (("servers", "WebSocketPool"), "too_short"),
    }


def test_tcp_and_tls_servers_form_one_pool() -> None:
    connection = NatsConnection.model_validate({"servers": TCP_SERVERS})

    assert connection.servers == TcpPool(
        (AnyUrl("nats://nats"), AnyUrl("tls://backup.example:4223"))
    )


def test_websocket_servers_form_one_pool() -> None:
    connection = NatsConnection.model_validate({"servers": WEBSOCKET_SERVERS})

    assert connection.servers == WebSocketPool(
        (AnyUrl("ws://edge.example:8080"), AnyUrl("wss://edge.example"))
    )


def test_mixed_transport_families_fail_configuration_construction() -> None:
    with pytest.raises(ValidationError) as excinfo:
        NatsConnection.model_validate({"servers": ["nats://nats", "wss://edge.example"]})

    assert _problems(excinfo.value) == {
        (("servers", "TcpPool", 1), "url_scheme"),
        (("servers", "WebSocketPool", 0), "url_scheme"),
    }


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

    problems = _problems(excinfo.value)
    assert {problem for problem in problems if problem[0][1] == "TcpPool"} == {
        (("servers", "TcpPool", 1), "url_scheme"),
        (("servers", "TcpPool", 2), "url_scheme"),
        (("servers", "TcpPool", 3), "url_parsing"),
        (("servers", "TcpPool", 4), "url_parsing"),
    }
    assert (("servers", "WebSocketPool", 0), "url_scheme") in problems


def test_equivalent_spellings_denote_the_same_endpoint() -> None:
    explicit = NatsConnection.model_validate({"servers": ["wss://edge.example:443/"]})
    implicit = NatsConnection.model_validate({"servers": ["wss://edge.example"]})
    client = Client()

    client.set_server_pool(_servers(NatsConnection.model_validate({"servers": ["nats://nats"]})))
    defaulted = _endpoints(client)
    client.set_server_pool(
        _servers(NatsConnection.model_validate({"servers": ["nats://nats:4222"]}))
    )

    assert explicit == implicit
    assert defaulted == _endpoints(client) == [("nats", "nats", 4222)]


def test_native_client_receives_each_pool_as_its_servers() -> None:
    client = Client()

    client.set_server_pool(_servers(NatsConnection.model_validate({"servers": TCP_SERVERS})))
    tcp = _endpoints(client)
    client.set_server_pool(_servers(NatsConnection.model_validate({"servers": WEBSOCKET_SERVERS})))

    assert tcp == [("nats", "nats", 4222), ("tls", "backup.example", 4223)]
    assert _endpoints(client) == [("ws", "edge.example", 8080), ("wss", "edge.example", None)]


def test_native_broker_receives_each_pool_as_its_servers() -> None:
    tcp = NatsBroker(servers=_servers(NatsConnection.model_validate({"servers": TCP_SERVERS})))
    ws = NatsBroker(servers=_servers(NatsConnection.model_validate({"servers": WEBSOCKET_SERVERS})))

    assert tcp.specification.url == ["nats://nats", "tls://backup.example:4223"]
    assert ws.specification.url == ["ws://edge.example:8080/", "wss://edge.example/"]


def test_websocket_transport_is_available_to_the_native_client() -> None:
    async def construct() -> type[WebSocketTransport]:
        transport = WebSocketTransport()
        # Release the session the transport opened; it has no public teardown before connecting.
        await transport._client.close()  # pyright: ignore[reportPrivateUsage, reportUnknownMemberType]
        return type(transport)

    assert asyncio.run(construct()) is WebSocketTransport


def test_connection_rejects_reassignment() -> None:
    connection = NatsConnection.model_validate({"servers": TCP_SERVERS})

    with pytest.raises(ValidationError) as top_level:
        connection.servers = WebSocketPool((AnyUrl("wss://edge.example"),))
    with pytest.raises(ValidationError) as nested:
        connection.servers.root = ()

    assert top_level.value.errors()[0]["type"] == "frozen_instance"
    assert nested.value.errors()[0]["type"] == "frozen_instance"
    assert hash(connection) == hash(NatsConnection.model_validate({"servers": TCP_SERVERS}))
