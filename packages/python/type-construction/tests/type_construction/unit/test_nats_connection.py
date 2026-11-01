"""The supplied NATS connection contract models secured server pools and credential references.

Governing requirements: docs/architecture/DESIGN.md sections 5.1 (named refinements, named
collections, product alternatives and an explicitly discriminated sum; named roots keep native
JSON root shape), 5.2 (an integration supplies the settings contract its resource requires), 5.3
(alternatives are selected by declared discriminator values), 5.4 (native ``NatsBroker`` consumes
the configuration through ``nats-py``; connections are verified TLS with native credentials and
no plaintext fallback) and 6.1 (valid configuration establishes no connectivity). The native
``servers`` parameter receives the ordered URL strings of the selected alternative. Credential
and trust material is referenced by path; contents never enter model values.
"""

import asyncio
from pathlib import Path
from typing import Any

import pytest
from faststream.nats import NatsBroker
from nats.aio.client import Client
from nats.aio.transport import WebSocketTransport
from pydantic import AnyUrl, ValidationError

from type_construction import NatsConnection
from type_construction.nats import (
    CertificateAuthorityFile,
    CredentialsFile,
    TcpPool,
    TcpServers,
    TcpUrl,
    WebSocketPool,
    WebSocketServers,
    WebSocketUrl,
)

TCP = {"transport": "tcp", "urls": ["tls://nats", "tls://backup.example:4223"]}
WEBSOCKET = {"transport": "websocket", "urls": ["wss://edge.example:8443", "wss://edge.example"]}
CANARY_FILE = "-----BEGIN NATS USER JWT-----\neyJ0.canary.jwt\n------END NATS USER JWT------\n"


@pytest.fixture
def references(tmp_path: Path) -> dict[str, str]:
    """Deployment references to credential and trust files; contents are placeholders."""
    credentials = tmp_path / "application.creds"
    credentials.write_text(CANARY_FILE)
    authority = tmp_path / "ca.pem"
    authority.write_text("-----BEGIN CERTIFICATE-----\nplaceholder\n-----END CERTIFICATE-----\n")
    return {"credentials": str(credentials), "certificate_authority": str(authority)}


def _connection(pool: dict[str, Any], references: dict[str, str]) -> NatsConnection:
    return NatsConnection.model_validate({"servers": pool, **references})


def _problems(error: ValidationError) -> set[tuple[tuple[int | str, ...], str]]:
    return {(detail["loc"], detail["type"]) for detail in error.errors()}


def _servers(connection: NatsConnection) -> list[str]:
    """The ``servers`` argument the native client and broker receive."""
    return [str(url.root) for url in connection.servers.urls.root]


def _endpoints(client: Client) -> list[tuple[str, str | None, int | None]]:
    return [(server.scheme, server.hostname, server.port) for server in client.servers]


def test_each_tagged_alternative_constructs_directly(references: dict[str, str]) -> None:
    tcp = _connection(TCP, references)
    websocket = _connection(WEBSOCKET, references)

    assert isinstance(tcp.servers, TcpPool)
    assert isinstance(websocket.servers, WebSocketPool)
    assert _servers(tcp) == ["tls://nats", "tls://backup.example:4223"]
    assert _servers(websocket) == ["wss://edge.example:8443/", "wss://edge.example/"]


def test_constructed_values_retain_their_model_types_and_serialize_natively(
    references: dict[str, str],
) -> None:
    tcp = _connection(TCP, references)
    websocket = _connection(WEBSOCKET, references)

    assert all(isinstance(url, TcpUrl) for url in tcp.servers.urls.root)
    assert all(isinstance(url, WebSocketUrl) for url in websocket.servers.urls.root)
    assert isinstance(tcp.credentials, CredentialsFile)
    assert isinstance(tcp.certificate_authority, CertificateAuthorityFile)
    assert tcp.model_dump(mode="json") == {
        "servers": {"transport": "tcp", "urls": ["tls://nats", "tls://backup.example:4223"]},
        **references,
    }
    assert websocket.model_dump(mode="json")["servers"] == {
        "transport": "websocket",
        "urls": ["wss://edge.example:8443/", "wss://edge.example/"],
    }


def test_already_constructed_values_compose(references: dict[str, str]) -> None:
    tcp = NatsConnection(
        servers=TcpPool(
            transport="tcp",
            urls=TcpServers(
                (TcpUrl(AnyUrl("tls://nats")), TcpUrl(AnyUrl("tls://backup.example:4223")))
            ),
        ),
        credentials=CredentialsFile(Path(references["credentials"])),
        certificate_authority=CertificateAuthorityFile(Path(references["certificate_authority"])),
    )
    websocket = NatsConnection(
        servers=WebSocketPool(
            transport="websocket",
            urls=WebSocketServers(
                (
                    WebSocketUrl(AnyUrl("wss://edge.example:8443")),
                    WebSocketUrl(AnyUrl("wss://edge.example")),
                )
            ),
        ),
        credentials=tcp.credentials,
        certificate_authority=tcp.certificate_authority,
    )

    assert tcp == _connection(TCP, references)
    assert websocket == _connection(WEBSOCKET, references)
    assert hash(tcp) == hash(_connection(TCP, references))


def test_missing_and_unknown_discriminators_fail(references: dict[str, str]) -> None:
    with pytest.raises(ValidationError) as missing:
        _connection({"urls": ["tls://nats"]}, references)
    with pytest.raises(ValidationError) as unknown:
        _connection({"transport": "quic", "urls": ["tls://nats"]}, references)
    with pytest.raises(ValidationError) as direct:
        TcpPool.model_validate({"urls": ["tls://nats"]})

    assert _problems(missing.value) == {(("servers",), "union_tag_not_found")}
    assert _problems(unknown.value) == {(("servers",), "union_tag_invalid")}
    assert _problems(direct.value) == {(("transport",), "missing")}


def test_untagged_lists_cannot_select_an_alternative(references: dict[str, str]) -> None:
    with pytest.raises(ValidationError) as excinfo:
        _connection(["tls://nats", "tls://backup.example:4223"], references)  # type: ignore[arg-type]

    assert _problems(excinfo.value) == {(("servers",), "model_attributes_type")}


def test_deployment_must_supply_pool_credentials_and_trust() -> None:
    with pytest.raises(ValidationError) as excinfo:
        NatsConnection.model_validate({})

    assert _problems(excinfo.value) == {
        (("servers",), "missing"),
        (("credentials",), "missing"),
        (("certificate_authority",), "missing"),
    }


@pytest.mark.parametrize(
    ("pool", "expected"),
    [
        (
            {"transport": "tcp", "urls": ["tls://nats", "nats://nats:4222"]},
            {(("servers", "tcp", "urls", 1), "url_scheme")},
        ),
        (
            {"transport": "websocket", "urls": ["wss://edge.example", "ws://edge.example"]},
            {(("servers", "websocket", "urls", 1), "url_scheme")},
        ),
        (
            {"transport": "tcp", "urls": ["tls://nats", "wss://edge.example"]},
            {(("servers", "tcp", "urls", 1), "url_scheme")},
        ),
        (
            {"transport": "websocket", "urls": ["wss://edge.example", "tls://nats"]},
            {(("servers", "websocket", "urls", 1), "url_scheme")},
        ),
        (
            {"transport": "tcp", "urls": ["tls://nats", "http://nats:8222", "tls://a:4222,b:4223"]},
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
    ids=[
        "tcp-plaintext-scheme",
        "websocket-plaintext-scheme",
        "tcp-mixed",
        "websocket-mixed",
        "tcp-foreign-forms",
        "tcp-empty",
        "websocket-empty",
    ],
)
def test_each_alternative_admits_only_its_secured_scheme_and_a_nonempty_collection(
    references: dict[str, str],
    pool: dict[str, object],
    expected: set[tuple[tuple[int | str, ...], str]],
) -> None:
    with pytest.raises(ValidationError) as excinfo:
        _connection(pool, references)

    assert _problems(excinfo.value) == expected


@pytest.mark.parametrize(
    ("pool", "expected"),
    [
        ({"transport": "tcp", "urls": ["tls://"]}, (("servers", "tcp", "urls", 0), "url_parsing")),
        (
            {"transport": "websocket", "urls": ["wss://"]},
            (("servers", "websocket", "urls", 0), "url_parsing"),
        ),
    ],
    ids=["tcp", "websocket"],
)
def test_each_alternative_requires_a_host(
    references: dict[str, str],
    pool: dict[str, object],
    expected: tuple[tuple[int | str, ...], str],
) -> None:
    with pytest.raises(ValidationError) as excinfo:
        _connection(pool, references)

    assert expected in _problems(excinfo.value)


def test_full_url_contract_excludes_host_port_forms_the_native_client_accepts(
    references: dict[str, str],
) -> None:
    """``nats.internal:4222`` is a server the client defaults to ``nats://``; this contract
    declares full secured URLs, so the form is outside it although the client would accept it."""
    client = Client()
    client.set_server_pool(["nats.internal:4222"])

    with pytest.raises(ValidationError) as excinfo:
        _connection({"transport": "tcp", "urls": ["tls://nats", "nats.internal:4222"]}, references)

    assert _endpoints(client) == [("nats", "nats.internal", 4222)]
    assert _problems(excinfo.value) == {(("servers", "tcp", "urls", 1), "url_scheme")}


def test_credential_and_trust_references_must_name_existing_files(
    tmp_path: Path, references: dict[str, str]
) -> None:
    missing = tmp_path / "absent.creds"
    directory = tmp_path / "directory"
    directory.mkdir()

    with pytest.raises(ValidationError) as excinfo:
        NatsConnection.model_validate(
            {"servers": TCP, "credentials": str(missing), "certificate_authority": str(directory)}
        )

    assert _problems(excinfo.value) == {
        (("credentials",), "path_not_file"),
        (("certificate_authority",), "path_not_file"),
    }
    assert {detail["input"] for detail in excinfo.value.errors()} == {str(missing), str(directory)}


def test_representations_carry_references_not_credential_contents(
    references: dict[str, str],
) -> None:
    connection = _connection(TCP, references)

    rendered = " ".join((repr(connection), str(connection), connection.model_dump_json()))

    assert references["credentials"] in rendered
    assert "canary" not in rendered
    assert "BEGIN NATS USER JWT" not in rendered


def test_equivalent_spellings_denote_the_same_endpoint(references: dict[str, str]) -> None:
    explicit = _connection(
        {"transport": "websocket", "urls": ["wss://edge.example:443/"]}, references
    )
    implicit = _connection({"transport": "websocket", "urls": ["wss://edge.example"]}, references)

    assert explicit == implicit
    assert _servers(explicit) == ["wss://edge.example/"]


def test_native_client_pool_initialization_receives_the_ordered_urls(
    references: dict[str, str],
) -> None:
    client = Client()

    client.set_server_pool(_servers(_connection(TCP, references)))
    tcp = _endpoints(client)
    client.set_server_pool(_servers(_connection(WEBSOCKET, references)))

    assert tcp == [("tls", "nats", 4222), ("tls", "backup.example", 4223)]
    assert _endpoints(client) == [("wss", "edge.example", 8443), ("wss", "edge.example", None)]


def test_native_broker_configuration_receives_the_ordered_urls(
    references: dict[str, str],
) -> None:
    tcp = NatsBroker(servers=_servers(_connection(TCP, references)))
    websocket = NatsBroker(servers=_servers(_connection(WEBSOCKET, references)))

    assert tcp.specification.url == ["tls://nats", "tls://backup.example:4223"]
    assert websocket.specification.url == ["wss://edge.example:8443/", "wss://edge.example/"]


def test_websocket_transport_initialization_succeeds_with_the_declared_dependencies() -> None:
    async def construct() -> type[WebSocketTransport]:
        transport = WebSocketTransport()
        # Release the session the transport opened; it has no public teardown before connecting.
        await transport._client.close()  # pyright: ignore[reportPrivateUsage, reportUnknownMemberType]
        return type(transport)

    assert asyncio.run(construct()) is WebSocketTransport


def test_connection_rejects_reassignment(references: dict[str, str]) -> None:
    connection = _connection(TCP, references)
    other = _connection(WEBSOCKET, references)
    pool = connection.servers
    assert isinstance(pool, TcpPool)

    with pytest.raises(ValidationError) as top_level:
        connection.servers = other.servers
    with pytest.raises(ValidationError) as nested:
        pool.urls = TcpServers((TcpUrl(AnyUrl("tls://other")),))

    assert top_level.value.errors()[0]["type"] == "frozen_instance"
    assert nested.value.errors()[0]["type"] == "frozen_instance"
