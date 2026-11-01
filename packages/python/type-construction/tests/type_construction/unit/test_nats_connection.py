"""The supplied NATS connection contract is a discriminated sum of transport pool alternatives.

Governing requirements: docs/architecture/DESIGN.md sections 5.1 (named refinements, named
collections, product alternatives and an explicitly discriminated sum; named roots keep native
JSON root shape), 5.2 (an integration supplies the settings contract its resource requires), 5.3
(alternatives are selected by declared discriminator values), 5.4 (native ``NatsBroker`` consumes
the configuration through ``nats-py``) and 6.1 (valid configuration establishes no connectivity).
The native ``servers`` parameter receives the ordered URL strings of the selected alternative.
Native consumption is observed through the public server pool of the pinned client, the public
server list of the pinned broker and the client's WebSocket transport class.
"""

import asyncio

import pytest
from faststream.nats import NatsBroker
from nats.aio.client import Client
from nats.aio.transport import WebSocketTransport
from pydantic import AnyUrl, ValidationError

from type_construction import NatsConnection
from type_construction.nats import (
    TcpPool,
    TcpServers,
    TcpUrl,
    WebSocketPool,
    WebSocketServers,
    WebSocketUrl,
)

TCP = {"transport": "tcp", "urls": ["nats://nats", "tls://backup.example:4223"]}
WEBSOCKET = {"transport": "websocket", "urls": ["ws://edge.example:8080", "wss://edge.example"]}


def _problems(error: ValidationError) -> set[tuple[tuple[int | str, ...], str]]:
    return {(detail["loc"], detail["type"]) for detail in error.errors()}


def _servers(connection: NatsConnection) -> list[str]:
    """The ``servers`` argument the native client and broker receive."""
    return [str(url.root) for url in connection.servers.urls.root]


def _endpoints(client: Client) -> list[tuple[str, str | None, int | None]]:
    return [(server.scheme, server.hostname, server.port) for server in client.servers]


def test_each_tagged_alternative_constructs_directly() -> None:
    tcp = NatsConnection.model_validate({"servers": TCP})
    websocket = NatsConnection.model_validate({"servers": WEBSOCKET})

    assert isinstance(tcp.servers, TcpPool)
    assert isinstance(websocket.servers, WebSocketPool)
    assert _servers(tcp) == ["nats://nats", "tls://backup.example:4223"]
    assert _servers(websocket) == ["ws://edge.example:8080/", "wss://edge.example/"]


def test_constructed_urls_retain_their_model_types_and_serialize_as_json_strings() -> None:
    tcp = NatsConnection.model_validate({"servers": TCP})
    websocket = NatsConnection.model_validate({"servers": WEBSOCKET})

    assert all(isinstance(url, TcpUrl) for url in tcp.servers.urls.root)
    assert all(isinstance(url, WebSocketUrl) for url in websocket.servers.urls.root)
    assert tcp.model_dump(mode="json") == {
        "servers": {"transport": "tcp", "urls": ["nats://nats", "tls://backup.example:4223"]}
    }
    assert websocket.model_dump_json() == (
        '{"servers":{"transport":"websocket",'
        '"urls":["ws://edge.example:8080/","wss://edge.example/"]}}'
    )


def test_already_constructed_values_compose() -> None:
    tcp = NatsConnection(
        servers=TcpPool(
            transport="tcp",
            urls=TcpServers(
                (TcpUrl(AnyUrl("nats://nats")), TcpUrl(AnyUrl("tls://backup.example:4223")))
            ),
        )
    )
    websocket = NatsConnection(
        servers=WebSocketPool(
            transport="websocket",
            urls=WebSocketServers(
                (
                    WebSocketUrl(AnyUrl("ws://edge.example:8080")),
                    WebSocketUrl(AnyUrl("wss://edge.example")),
                )
            ),
        )
    )

    assert tcp == NatsConnection.model_validate({"servers": TCP})
    assert websocket == NatsConnection.model_validate({"servers": WEBSOCKET})
    assert hash(tcp) == hash(NatsConnection.model_validate({"servers": TCP}))


def test_missing_and_unknown_discriminators_fail() -> None:
    with pytest.raises(ValidationError) as missing:
        NatsConnection.model_validate({"servers": {"urls": ["nats://nats"]}})
    with pytest.raises(ValidationError) as unknown:
        NatsConnection.model_validate({"servers": {"transport": "quic", "urls": ["nats://nats"]}})
    with pytest.raises(ValidationError) as direct:
        TcpPool.model_validate({"urls": ["nats://nats"]})

    assert _problems(missing.value) == {(("servers",), "union_tag_not_found")}
    assert _problems(unknown.value) == {(("servers",), "union_tag_invalid")}
    assert _problems(direct.value) == {(("transport",), "missing")}


def test_untagged_lists_cannot_select_an_alternative() -> None:
    with pytest.raises(ValidationError) as excinfo:
        NatsConnection.model_validate({"servers": ["nats://nats", "tls://backup.example:4223"]})

    assert _problems(excinfo.value) == {(("servers",), "model_attributes_type")}


def test_deployment_must_supply_the_pool() -> None:
    with pytest.raises(ValidationError) as excinfo:
        NatsConnection.model_validate({})

    assert _problems(excinfo.value) == {(("servers",), "missing")}


@pytest.mark.parametrize(
    ("pool", "expected"),
    [
        (
            {"transport": "tcp", "urls": ["nats://nats", "wss://edge.example"]},
            {(("servers", "tcp", "urls", 1), "url_scheme")},
        ),
        (
            {"transport": "websocket", "urls": ["wss://edge.example", "nats://nats"]},
            {(("servers", "websocket", "urls", 1), "url_scheme")},
        ),
        (
            {
                "transport": "tcp",
                "urls": ["nats://nats", "http://nats:8222", "nats://a:4222,b:4223"],
            },
            {
                (("servers", "tcp", "urls", 1), "url_scheme"),
                (("servers", "tcp", "urls", 2), "url_parsing"),
            },
        ),
        ({"transport": "tcp", "urls": []}, {(("servers", "tcp", "urls"), "too_short")}),
        (
            {"transport": "websocket", "urls": []},
            {(("servers", "websocket", "urls"), "too_short")},
        ),
    ],
    ids=["tcp-mixed", "websocket-mixed", "tcp-foreign-forms", "tcp-empty", "websocket-empty"],
)
def test_each_alternative_rejects_foreign_schemes_and_empty_collections(
    pool: dict[str, object], expected: set[tuple[tuple[int | str, ...], str]]
) -> None:
    with pytest.raises(ValidationError) as excinfo:
        NatsConnection.model_validate({"servers": pool})

    assert _problems(excinfo.value) == expected


@pytest.mark.parametrize(
    ("pool", "expected"),
    [
        (
            {"transport": "tcp", "urls": ["nats://"]},
            (("servers", "tcp", "urls", 0), "url_parsing"),
        ),
        (
            {"transport": "websocket", "urls": ["wss://"]},
            (("servers", "websocket", "urls", 0), "url_parsing"),
        ),
    ],
    ids=["tcp", "websocket"],
)
def test_each_alternative_requires_a_host(
    pool: dict[str, object], expected: tuple[tuple[int | str, ...], str]
) -> None:
    with pytest.raises(ValidationError) as excinfo:
        NatsConnection.model_validate({"servers": pool})

    assert expected in _problems(excinfo.value)


def test_full_url_contract_excludes_host_port_forms_the_native_client_accepts() -> None:
    """``nats.internal:4222`` is a server the client defaults to ``nats://``; this contract
    declares full URLs, so the form is outside it although the client would accept it."""
    client = Client()
    client.set_server_pool(["nats.internal:4222"])

    with pytest.raises(ValidationError) as excinfo:
        NatsConnection.model_validate(
            {"servers": {"transport": "tcp", "urls": ["nats://nats", "nats.internal:4222"]}}
        )

    assert _endpoints(client) == [("nats", "nats.internal", 4222)]
    assert _problems(excinfo.value) == {(("servers", "tcp", "urls", 1), "url_scheme")}


def test_equivalent_spellings_denote_the_same_endpoint() -> None:
    explicit = NatsConnection.model_validate(
        {"servers": {"transport": "websocket", "urls": ["wss://edge.example:443/"]}}
    )
    implicit = NatsConnection.model_validate(
        {"servers": {"transport": "websocket", "urls": ["wss://edge.example"]}}
    )

    assert explicit == implicit
    assert _servers(explicit) == ["wss://edge.example/"]


def test_native_client_pool_initialization_receives_the_ordered_urls() -> None:
    client = Client()

    client.set_server_pool(_servers(NatsConnection.model_validate({"servers": TCP})))
    tcp = _endpoints(client)
    client.set_server_pool(_servers(NatsConnection.model_validate({"servers": WEBSOCKET})))

    assert tcp == [("nats", "nats", 4222), ("tls", "backup.example", 4223)]
    assert _endpoints(client) == [("ws", "edge.example", 8080), ("wss", "edge.example", None)]


def test_native_broker_configuration_receives_the_ordered_urls() -> None:
    tcp = NatsBroker(servers=_servers(NatsConnection.model_validate({"servers": TCP})))
    websocket = NatsBroker(servers=_servers(NatsConnection.model_validate({"servers": WEBSOCKET})))

    assert tcp.specification.url == ["nats://nats", "tls://backup.example:4223"]
    assert websocket.specification.url == ["ws://edge.example:8080/", "wss://edge.example/"]


def test_websocket_transport_initialization_succeeds_with_the_declared_dependencies() -> None:
    async def construct() -> type[WebSocketTransport]:
        transport = WebSocketTransport()
        # Release the session the transport opened; it has no public teardown before connecting.
        await transport._client.close()  # pyright: ignore[reportPrivateUsage, reportUnknownMemberType]
        return type(transport)

    assert asyncio.run(construct()) is WebSocketTransport


def test_connection_rejects_reassignment() -> None:
    connection = NatsConnection.model_validate({"servers": TCP})
    other = NatsConnection.model_validate({"servers": WEBSOCKET})
    pool = connection.servers
    assert isinstance(pool, TcpPool)

    with pytest.raises(ValidationError) as top_level:
        connection.servers = other.servers
    with pytest.raises(ValidationError) as nested:
        pool.urls = TcpServers((TcpUrl(AnyUrl("nats://other")),))

    assert top_level.value.errors()[0]["type"] == "frozen_instance"
    assert nested.value.errors()[0]["type"] == "frozen_instance"
