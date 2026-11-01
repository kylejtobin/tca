"""Realized resources connect to secured NATS with verified TLS, credentials and scoped authority.

Governing requirements: docs/architecture/DESIGN.md sections 5.4 (the binding supplies verified
TLS before any protocol exchange, native credentials and native broker, client and JetStream
access), 7 (uses of one realized resource share its native client; equal configuration does not
establish sharing; the application identity holds narrowly scoped permissions distinct from
provisioning authority) and 8.4 (authentication, authorization and successful work remain
distinct facts). A disposable secured server runs with TLS-first TCP, a TLS WebSocket listener
and the generated operator; the application user may publish and subscribe under ``tca.>`` and
read JetStream account information only. Rejections are bounded by a timeout because the native
client keeps retrying; the server log corroborates the rejected handshakes.
"""

import asyncio
import contextlib
from collections.abc import AsyncGenerator, Callable
from pathlib import Path

import pytest
from faststream import FastStream
from faststream.nats import NatsBroker as Broker
from faststream.nats.annotations import Client, JsClient, NatsBroker
from nats.aio.client import Client as NatsClient
from nats.errors import Error as NatsError
from nats.js.client import JetStreamContext
from nats.js.errors import NotFoundError

from type_construction import NatsConnection, Resource
from type_construction.resources import bind_resource

BOUND = 3.0
START_BOUND = 10.0
type Injected = tuple[Broker, NatsClient, JetStreamContext]


def _resource(
    material: dict[str, Path],
    urls: list[str],
    *,
    transport: str = "tcp",
    credentials: str = "application_credentials",
    authority: str = "certificate_authority",
) -> Resource:
    return Resource(
        connection=NatsConnection.model_validate(
            {
                "servers": {"transport": transport, "urls": urls},
                "credentials": material[credentials],
                "certificate_authority": material[authority],
            }
        )
    )


def _observe(broker: Broker, subject: str, received: dict[str, Injected]) -> None:
    @broker.subscriber(subject)
    async def observe(body: str, owner: NatsBroker, client: Client, stream: JsClient) -> None:
        received[body] = (owner, client, stream)


async def _deliver(received: dict[str, Injected], expected: set[str]) -> None:
    for _ in range(50):
        if expected <= received.keys():
            return
        await asyncio.sleep(0.05)
    pytest.fail(f"not delivered within bound: {expected - received.keys()}")


@contextlib.asynccontextmanager
async def _running(*owners: FastStream) -> AsyncGenerator[None]:
    """Start the runtimes through their native lifecycle within a bound, then stop them."""
    try:
        for owner in owners:
            await asyncio.wait_for(owner.start(), START_BOUND)
        yield
    finally:
        for owner in reversed(owners):
            await owner.stop()


async def _start_is_refused(owner: FastStream, broker: Broker) -> None:
    """The native client never completes a connection within the bound."""
    try:
        with pytest.raises(TimeoutError):
            await asyncio.wait_for(owner.start(), BOUND)
        assert not broker.config.connection_state
    finally:
        await owner.stop()


def test_tls_first_tcp_connection_delivers_through_authenticated_native_injection(
    material: dict[str, Path], secured_nats: dict[str, int]
) -> None:
    owner = FastStream()
    resource = _resource(material, [f"tls://localhost:{secured_nats['tls_port']}"])
    first = bind_resource(resource, owner)
    second = bind_resource(resource, owner)
    received: dict[str, Injected] = {}
    _observe(first, "tca.first.one", received)
    _observe(first, "tca.first.two", received)
    _observe(second, "tca.second", received)

    async def scenario() -> None:
        async with _running(owner):
            await first.publish("one", "tca.first.one")
            await first.publish("two", "tca.first.two")
            await second.publish("three", "tca.second")
            await _deliver(received, {"one", "two", "three"})
            assert received["one"][0] is first and received["two"][0] is first
            assert received["three"][0] is second
            assert received["one"][1] is received["two"][1]
            assert received["one"][1] is not received["three"][1]
            assert received["one"][1].client_id != received["three"][1].client_id
            for owner_broker, client, stream in received.values():
                assert isinstance(client, NatsClient)
                assert isinstance(stream, JetStreamContext)
                assert client is owner_broker.config.connection_state.connection
                assert client.connected_url is not None
                assert client.connected_url.scheme == "tls"
                assert (await stream.account_info()).streams >= 0
        assert not first.config.connection_state and not second.config.connection_state

    asyncio.run(scenario())


def test_secure_websocket_connection_delivers_through_authenticated_native_injection(
    material: dict[str, Path], secured_nats: dict[str, int]
) -> None:
    owner = FastStream()
    broker = bind_resource(
        _resource(material, [f"wss://localhost:{secured_nats['wss_port']}"], transport="websocket"),
        owner,
    )
    received: dict[str, Injected] = {}
    _observe(broker, "tca.edge", received)

    async def scenario() -> None:
        async with _running(owner):
            await broker.publish("edge", "tca.edge")
            await _deliver(received, {"edge"})
            _, client, stream = received["edge"]
            assert client.connected_url is not None
            assert client.connected_url.scheme == "wss"
            assert (await stream.account_info()).streams >= 0

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "case",
    [
        ("tcp", "tls", "tls_port", "127.0.0.1", "certificate_authority"),
        ("tcp", "tls", "tls_port", "localhost", "untrusted_certificate_authority"),
        ("websocket", "wss", "wss_port", "127.0.0.1", "certificate_authority"),
        ("websocket", "wss", "wss_port", "localhost", "untrusted_certificate_authority"),
    ],
    ids=[
        "tcp-hostname-mismatch",
        "tcp-untrusted-authority",
        "wss-hostname-mismatch",
        "wss-untrusted-authority",
    ],
)
def test_unverifiable_servers_are_refused(
    material: dict[str, Path],
    secured_nats: dict[str, int],
    server_logs: Callable[[], str],
    case: tuple[str, str, str, str, str],
) -> None:
    """The certificate names ``localhost``; an address outside it or an authority the client
    does not trust must abort the handshake before any protocol exchange."""
    transport, scheme, port, host, authority = case
    owner = FastStream()
    broker = bind_resource(
        _resource(
            material,
            [f"{scheme}://{host}:{secured_nats[port]}"],
            transport=transport,
            authority=authority,
        ),
        owner,
    )
    handshakes_before = server_logs().count("TLS handshake error")

    asyncio.run(_start_is_refused(owner, broker))

    assert server_logs().count("TLS handshake error") > handshakes_before


def test_untrusted_operator_credentials_are_rejected_before_any_work(
    material: dict[str, Path], secured_nats: dict[str, int]
) -> None:
    owner = FastStream()
    broker = bind_resource(
        _resource(
            material,
            [f"tls://localhost:{secured_nats['tls_port']}"],
            credentials="untrusted_credentials",
        ),
        owner,
    )
    received: dict[str, Injected] = {}
    _observe(broker, "tca.never", received)

    async def scenario() -> None:
        try:
            with pytest.raises(NatsError, match="Authorization Violation"):
                await asyncio.wait_for(owner.start(), BOUND)
        finally:
            await owner.stop()

    asyncio.run(scenario())

    assert not broker.config.connection_state
    assert received == {}


def test_malformed_credentials_fail_before_connecting(
    material: dict[str, Path], secured_nats: dict[str, int], tmp_path: Path
) -> None:
    malformed = tmp_path / "malformed.creds"
    malformed.write_text("not a credentials file\n")
    owner = FastStream()
    broker = bind_resource(
        Resource(
            connection=NatsConnection.model_validate(
                {
                    "servers": {
                        "transport": "tcp",
                        "urls": [f"tls://localhost:{secured_nats['tls_port']}"],
                    },
                    "credentials": malformed,
                    "certificate_authority": material["certificate_authority"],
                }
            )
        ),
        owner,
    )

    async def scenario() -> None:
        try:
            # The pinned client raises before opening a socket when the file lacks the JWT
            # marker; the error type is the client's own.
            with pytest.raises((TypeError, NatsError)):
                await asyncio.wait_for(owner.start(), BOUND)
        finally:
            await owner.stop()

    asyncio.run(scenario())

    assert not broker.config.connection_state


def test_application_identity_cannot_publish_outside_its_permissions(
    material: dict[str, Path], secured_nats: dict[str, int]
) -> None:
    """A forbidden publication produces no delivery, while permitted work on the same
    connection proceeds; the connection itself is established and authenticated."""
    urls = [f"tls://localhost:{secured_nats['tls_port']}"]
    application = FastStream()
    broker = bind_resource(_resource(material, urls), application)
    provisioning = FastStream()
    listener = bind_resource(
        _resource(material, urls, credentials="setup_credentials"), provisioning
    )
    received: dict[str, Injected] = {}
    forbidden: list[str] = []
    _observe(broker, "tca.permitted", received)

    @listener.subscriber("outside.tca")
    async def overhear(body: str) -> None:
        forbidden.append(body)

    async def scenario() -> None:
        async with _running(provisioning, application):
            await broker.publish("leak", "outside.tca")
            await broker.publish("work", "tca.permitted")
            await _deliver(received, {"work"})
            await asyncio.sleep(0.3)

    asyncio.run(scenario())

    assert forbidden == []
    assert "work" in received


def test_provisioning_identity_creates_streams_the_application_cannot(
    material: dict[str, Path], secured_nats: dict[str, int]
) -> None:
    urls = [f"tls://localhost:{secured_nats['tls_port']}"]
    application = FastStream()
    broker = bind_resource(_resource(material, urls), application)
    provisioning = FastStream()
    provisioner = bind_resource(
        _resource(material, urls, credentials="setup_credentials"), provisioning
    )

    async def scenario() -> None:
        async with _running(provisioning, application):
            application_js = broker.config.connection_state.stream
            setup_js = provisioner.config.connection_state.stream
            with pytest.raises(TimeoutError):
                await asyncio.wait_for(
                    application_js.add_stream(name="TCA_TEST", subjects=["tca.test.>"]), 1.0
                )
            with pytest.raises(NotFoundError):
                await setup_js.stream_info("TCA_TEST")
            created = await setup_js.add_stream(name="TCA_TEST", subjects=["tca.test.>"])
            try:
                assert created.config.name == "TCA_TEST"
                with pytest.raises(TimeoutError):
                    await asyncio.wait_for(application_js.delete_stream("TCA_TEST"), 1.0)
                assert (await setup_js.stream_info("TCA_TEST")).config.name == "TCA_TEST"
                assert (await application_js.account_info()).streams == 1
            finally:
                await setup_js.delete_stream("TCA_TEST")

    asyncio.run(scenario())


def test_credentials_are_never_sent_before_tls(material: dict[str, Path], tmp_path: Path) -> None:
    """Regression for the adversarial peer: a server advertising no TLS requirement must receive
    a TLS handshake, never the CONNECT command carrying the credentials."""
    captured = bytearray()
    canary = material["application_credentials"].read_text().splitlines()[1].encode()
    assert canary.startswith(b"eyJ"), "the second line of a creds file is the user JWT"

    async def adversary(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        writer.write(
            b'INFO {"server_id":"ADVERSARY","version":"2.15.2","go":"go1.25","host":"0.0.0.0",'
            b'"port":4222,"headers":true,"max_payload":1048576,"proto":1,"auth_required":true,'
            b'"tls_required":false,"nonce":"c2FsdA"}\r\n'
        )
        await writer.drain()
        with contextlib.suppress(TimeoutError):
            captured.extend(await asyncio.wait_for(reader.read(65536), 1.0))
        writer.close()

    async def scenario() -> None:
        server = await asyncio.start_server(adversary, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        owner = FastStream()
        broker = bind_resource(_resource(material, [f"tls://localhost:{port}"]), owner)
        try:
            await _start_is_refused(owner, broker)
        finally:
            server.close()
            await server.wait_closed()

    asyncio.run(scenario())

    assert captured[:3] == b"\x16\x03\x01", "the first bytes are a TLS ClientHello record"
    assert canary not in captured
    assert b"CONNECT" not in captured
    assert b"BEGIN USER NKEY SEED" not in captured
