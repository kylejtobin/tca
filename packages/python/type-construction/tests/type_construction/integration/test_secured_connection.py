"""Realized resources connect to secured NATS with verified TLS, credentials and scoped authority.

Governing requirements: docs/architecture/DESIGN.md sections 5.4 (the binding supplies verified
TLS before any protocol exchange, native credentials and native broker, client and JetStream
access), 7 (uses of one realized resource share its native client; equal configuration does not
establish sharing; the application identity holds least-privilege permissions distinct from
provisioning authority; no plaintext fallback) and 8.4 (authentication, authorization and
successful work remain distinct facts). Disposable secured servers run with TLS-first TCP, a TLS
WebSocket listener and the generated operator; the application user may publish and subscribe
under ``tca.>`` and read JetStream account information only.

Failures are established at their actual stage. Content lacking the native markers is rejected
by the binding before any socket opens; a well-framed identity the operator does not know is
rejected natively at authentication; a forbidden operation by an authenticated identity is
rejected natively by the server, observed through the client's error callback and the server
log, while permitted work on the same connection proceeds. Every start, stop and external command
is bounded, and a cleanup failure is attached to the test failure instead of replacing it.
"""

import asyncio
import contextlib
import logging
import subprocess
import sys
import textwrap
from collections.abc import AsyncGenerator, Callable, Iterator
from pathlib import Path
from typing import Protocol

import pytest
from faststream import FastStream
from faststream.nats import NatsBroker as Broker
from faststream.nats.annotations import Client, JsClient, NatsBroker
from nats.aio.client import Client as NatsClient
from nats.errors import Error as NatsError
from nats.js.client import JetStreamContext
from nats.js.errors import NotFoundError

from type_construction.nats import NatsConnection, NatsResource

BOUND = 3.0
START_BOUND = 10.0
STOP_BOUND = 10.0
RECONNECT_BOUND = 30.0
SUBPROCESS_DEADLINE = 30.0
BROKER_LOGGER = "faststream.access.nats"
type Injected = tuple[Broker, NatsClient, JetStreamContext]


class RestartableServer(Protocol):
    """What the ``secured_server`` fixture yields: a server that keeps its port across restarts."""

    @property
    def tls_port(self) -> int: ...

    def stop(self) -> None: ...

    def start(self) -> None: ...


# Runs the actual binding against a live server with the credentials file named first. The
# process must end by the binding's rejection; the native file reader would never return.
BINDING_SUBPROCESS = textwrap.dedent(
    """
    import asyncio, sys
    from pathlib import Path
    from faststream import FastStream
    from type_construction.nats import NatsConnection, NatsResource

    credentials, authority, url = sys.argv[1:4]
    resource = NatsResource(connection=NatsConnection.model_validate({
        "servers": {"transport": "tcp", "urls": [url]},
        "credentials": credentials,
        "certificate_authority": authority,
    }))
    owner = FastStream()

    async def main() -> None:
        broker = resource.bind(owner)
        try:
            await owner.start()
            print("connected", bool(broker.config.connection_state))
        finally:
            await owner.stop()

    asyncio.run(main())
    """
)


def _resource(
    material: dict[str, Path],
    urls: list[str],
    *,
    transport: str = "tcp",
    credentials: str = "application_credentials",
    authority: str = "certificate_authority",
) -> NatsResource:
    return NatsResource(
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


async def _stop(*owners: FastStream) -> None:
    for owner in reversed(owners):
        await asyncio.wait_for(owner.stop(), STOP_BOUND)


@contextlib.asynccontextmanager
async def _running(*owners: FastStream) -> AsyncGenerator[None]:
    """Start the runtimes within a bound, then stop them; keep the scenario's failure if a
    bounded stop also fails."""
    try:
        for owner in owners:
            await asyncio.wait_for(owner.start(), START_BOUND)
        yield
    except BaseException as failure:
        try:
            await _stop(*owners)
        except Exception as cleanup_failure:
            failure.add_note(f"stopping the runtimes also failed: {cleanup_failure!r}")
        raise
    else:
        await _stop(*owners)


async def _start_is_refused(owner: FastStream, broker: Broker) -> None:
    """The native client never completes a connection within the bound."""
    async with _running():
        with pytest.raises(TimeoutError):
            await asyncio.wait_for(owner.start(), BOUND)
        assert not broker.config.connection_state
        await _stop(owner)


@pytest.fixture
def broker_log(caplog: pytest.LogCaptureFixture) -> Iterator[Callable[[], list[str]]]:
    """Capture the broker's native error reports; FastStream's logger does not propagate."""
    logger = logging.getLogger(BROKER_LOGGER)
    logger.addHandler(caplog.handler)
    try:
        yield lambda: [record.getMessage() for record in caplog.records]
    finally:
        logger.removeHandler(caplog.handler)


def _secrets(material: dict[str, Path], name: str) -> tuple[str, str]:
    """The JWT and seed lines of a credentials file: canaries that must stay in the file."""
    lines = material[name].read_text().splitlines()
    jwt = lines[lines.index("-----BEGIN NATS USER JWT-----") + 1]
    seed = lines[lines.index("-----BEGIN USER NKEY SEED-----") + 1]
    assert jwt.startswith("eyJ") and seed.startswith("SU")
    return jwt, seed


def test_tls_first_tcp_connection_delivers_through_authenticated_native_injection(
    material: dict[str, Path], secured_nats: dict[str, int]
) -> None:
    owner = FastStream()
    resource = _resource(material, [f"tls://localhost:{secured_nats['tls_port']}"])
    first = resource.bind(owner)
    second = resource.bind(owner)
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
    broker = _resource(
        material, [f"wss://localhost:{secured_nats['wss_port']}"], transport="websocket"
    ).bind(owner)
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
    broker_log: Callable[[], list[str]],
    case: tuple[str, str, str, str, str],
) -> None:
    """The certificate names ``localhost``; an address outside it or an authority the client
    does not trust must abort the handshake before any protocol exchange."""
    transport, scheme, port, host, authority = case
    owner = FastStream()
    broker = _resource(
        material,
        [f"{scheme}://{host}:{secured_nats[port]}"],
        transport=transport,
        authority=authority,
    ).bind(owner)
    handshakes_before = server_logs().count("TLS handshake error")

    asyncio.run(_start_is_refused(owner, broker))

    assert server_logs().count("TLS handshake error") > handshakes_before
    jwt, seed = _secrets(material, "application_credentials")
    assert not any(jwt in line or seed in line for line in broker_log())


def test_unknown_identity_is_rejected_natively_at_authentication(
    material: dict[str, Path],
    secured_nats: dict[str, int],
    server_logs: Callable[[], str],
    broker_log: Callable[[], list[str]],
) -> None:
    """Well-framed credentials from an operator the server does not know pass the binding's
    framing guard and are refused by the server; nothing is delivered and no secret is logged."""
    owner = FastStream()
    broker = _resource(
        material,
        [f"tls://localhost:{secured_nats['tls_port']}"],
        credentials="untrusted_credentials",
    ).bind(owner)
    received: dict[str, Injected] = {}
    _observe(broker, "tca.never", received)
    refusals_before = server_logs().count("authentication error")

    async def scenario() -> None:
        async with _running():
            with pytest.raises(NatsError, match=r"(?i)authorization violation"):
                await asyncio.wait_for(owner.start(), BOUND)
            await _stop(owner)

    asyncio.run(scenario())

    assert not broker.config.connection_state
    assert received == {}
    assert server_logs().count("authentication error") > refusals_before
    jwt, seed = _secrets(material, "untrusted_credentials")
    for rendered in (*broker_log(), server_logs()):
        assert jwt not in rendered and seed not in rendered


@pytest.mark.parametrize(
    "content",
    [
        "not a credentials file\n",
        "-----BEGIN USER NKEY SEED-----\nSUACANARY\n------END USER NKEY SEED------\n",
    ],
    ids=["no-markers", "seed-only"],
)
def test_marker_less_credentials_end_in_the_bindings_rejection_not_the_blocking_reader(
    material: dict[str, Path], secured_nats: dict[str, int], tmp_path: Path, content: str
) -> None:
    """Regression for the native combined-file reader, which loops without end when the JWT
    marker is absent. The actual binding runs in a subprocess under an external deadline; the
    process must exit through the guard's rejection, and reaching the deadline is a failure."""
    credentials = tmp_path / "marker-less.creds"
    credentials.write_text(content)
    command = [
        sys.executable,
        "-I",
        "-c",
        BINDING_SUBPROCESS,
        str(credentials),
        str(material["certificate_authority"]),
        f"tls://localhost:{secured_nats['tls_port']}",
    ]

    try:
        result = subprocess.run(  # noqa: S603 - the interpreter and script are fixed test inputs
            command, capture_output=True, text=True, timeout=SUBPROCESS_DEADLINE, check=False
        )
    except subprocess.TimeoutExpired:
        pytest.fail("the binding did not terminate: the blocking credentials reader was reached")

    assert result.returncode != 0
    assert "connected" not in result.stdout
    assert "ValueError" in result.stderr and "markers" in result.stderr
    assert content.splitlines()[0] not in result.stderr


def test_application_identity_cannot_publish_outside_its_permissions(
    material: dict[str, Path],
    secured_nats: dict[str, int],
    server_logs: Callable[[], str],
    broker_log: Callable[[], list[str]],
) -> None:
    """The server rejects the forbidden publication natively, the rejection reaches the client,
    the prohibited subject receives nothing, and permitted work on the same authenticated
    connection proceeds before and after the rejection."""
    urls = [f"tls://localhost:{secured_nats['tls_port']}"]
    application = FastStream()
    broker = _resource(material, urls).bind(application)
    provisioning = FastStream()
    listener = _resource(material, urls, credentials="setup_credentials").bind(provisioning)
    received: dict[str, Injected] = {}
    forbidden: list[str] = []
    _observe(broker, "tca.permitted", received)

    @listener.subscriber("outside.tca")
    async def overhear(body: str) -> None:
        forbidden.append(body)

    violation = 'Publish Violation - Subject "outside.tca"'
    violations_before = server_logs().count(violation)

    async def scenario() -> None:
        async with _running(provisioning, application):
            await broker.publish("before", "tca.permitted")
            await _deliver(received, {"before"})
            await broker.publish("leak", "outside.tca")
            for _ in range(50):
                if any("outside.tca" in message for message in broker_log()):
                    break
                await asyncio.sleep(0.05)
            await broker.publish("after", "tca.permitted")
            await _deliver(received, {"after"})
            assert received["before"][1] is received["after"][1]
            assert received["after"][1].is_connected

    asyncio.run(scenario())

    assert forbidden == []
    assert server_logs().count(violation) == violations_before + 1
    rejections = [
        m for m in broker_log() if 'permissions violation for publish to "outside.tca"' in m
    ]
    assert len(rejections) == 1


def test_provisioning_identity_creates_streams_the_application_cannot(
    material: dict[str, Path],
    secured_nats: dict[str, int],
    server_logs: Callable[[], str],
    broker_log: Callable[[], list[str]],
) -> None:
    """A JetStream API request outside the application's permissions is rejected natively by the
    server; the client observes the rejection and the request receives no reply. The stream does
    not exist until the provisioning identity creates it, and the application identity's
    permitted account query still succeeds."""
    urls = [f"tls://localhost:{secured_nats['tls_port']}"]
    application = FastStream()
    broker = _resource(material, urls).bind(application)
    provisioning = FastStream()
    provisioner = _resource(material, urls, credentials="setup_credentials").bind(provisioning)
    create = 'Publish Violation - Subject "$JS.API.STREAM.CREATE.TCA_TEST"'
    delete = 'Publish Violation - Subject "$JS.API.STREAM.DELETE.TCA_TEST"'

    async def scenario() -> None:
        async with _running(provisioning, application):
            application_js = broker.config.connection_state.stream
            setup_js = provisioner.config.connection_state.stream
            with pytest.raises(TimeoutError):
                await asyncio.wait_for(
                    application_js.add_stream(name="TCA_TEST", subjects=["tca.test.>"]), BOUND
                )
            with pytest.raises(NotFoundError):
                await setup_js.stream_info("TCA_TEST")
            created = await setup_js.add_stream(name="TCA_TEST", subjects=["tca.test.>"])
            try:
                assert created.config.name == "TCA_TEST"
                with pytest.raises(TimeoutError):
                    await asyncio.wait_for(application_js.delete_stream("TCA_TEST"), BOUND)
                assert (await setup_js.stream_info("TCA_TEST")).config.name == "TCA_TEST"
                assert (await application_js.account_info()).streams == 1
            finally:
                await setup_js.delete_stream("TCA_TEST")

    asyncio.run(scenario())

    log = server_logs()
    assert log.count(create) == 1 and log.count(delete) == 1
    rejections = [m for m in broker_log() if "permissions violation for publish to" in m]
    assert ["stream.create.tca_test" in m for m in rejections] == [True, False]
    assert "stream.delete.tca_test" in rejections[1]


def test_credentials_are_never_sent_before_tls(material: dict[str, Path]) -> None:
    """Regression for the adversarial peer: a server advertising no TLS requirement must receive
    a TLS handshake, never the CONNECT command carrying the credentials."""
    captured = bytearray()
    jwt, seed = _secrets(material, "application_credentials")

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
        broker = _resource(material, [f"tls://localhost:{port}"]).bind(owner)
        try:
            await _start_is_refused(owner, broker)
        finally:
            server.close()
            await asyncio.wait_for(server.wait_closed(), BOUND)

    asyncio.run(scenario())

    assert captured[:3] == b"\x16\x03\x01", "the first bytes are a TLS ClientHello record"
    assert jwt.encode() not in captured and seed.encode() not in captured
    assert b"CONNECT" not in captured
    assert b"BEGIN USER NKEY SEED" not in captured


def test_security_policy_survives_native_reconnection(
    material: dict[str, Path],
    secured_server: Callable[..., contextlib.AbstractContextManager[RestartableServer]],
) -> None:
    """A pool of a secured server and a plaintext peer: after the server stops, the client's
    reconnection attempts reach the peer with a TLS handshake only, and once the server returns
    the client reconnects over TLS with its credentials and delivery resumes."""
    attempts: list[bytes] = []
    jwt, seed = _secrets(material, "application_credentials")

    async def adversary(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        writer.write(
            b'INFO {"server_id":"ADVERSARY","version":"2.15.2","go":"go1.25","host":"0.0.0.0",'
            b'"port":4222,"headers":true,"max_payload":1048576,"proto":1,"auth_required":true,'
            b'"tls_required":false,"nonce":"c2FsdA"}\r\n'
        )
        await writer.drain()
        with contextlib.suppress(TimeoutError):
            attempts.append(await asyncio.wait_for(reader.read(65536), 1.0))
        writer.close()

    async def until(condition: Callable[[], bool], bound: float, failure: str) -> None:
        for _ in range(int(bound / 0.05)):
            if condition():
                return
            await asyncio.sleep(0.05)
        pytest.fail(failure)

    async def scenario() -> None:
        peer = await asyncio.start_server(adversary, "127.0.0.1", 0)
        peer_port = peer.sockets[0].getsockname()[1]
        try:
            with secured_server(keep_port=True) as server:
                owner = FastStream()
                broker = _resource(
                    material,
                    [f"tls://localhost:{server.tls_port}", f"tls://localhost:{peer_port}"],
                ).bind(owner)
                received: dict[str, Injected] = {}
                _observe(broker, "tca.again", received)
                async with _running(owner):
                    await broker.publish("first", "tca.again")
                    await _deliver(received, {"first"})
                    client = received["first"][1]
                    assert client.connected_url is not None
                    assert client.connected_url.port == server.tls_port

                    await asyncio.to_thread(server.stop)
                    await until(lambda: not client.is_connected, BOUND, "no disconnect observed")
                    await until(lambda: bool(attempts), RECONNECT_BOUND, "peer never attempted")
                    await asyncio.to_thread(server.start)
                    await until(lambda: client.is_connected, RECONNECT_BOUND, "no reconnection")

                    assert client.connected_url is not None
                    assert client.connected_url.scheme == "tls"
                    assert client.connected_url.port == server.tls_port
                    await broker.publish("second", "tca.again")
                    await _deliver(received, {"second"})
                    assert received["second"][1] is client
                    assert (await received["second"][2].account_info()).streams >= 0
        finally:
            peer.close()
            await asyncio.wait_for(peer.wait_closed(), BOUND)

    asyncio.run(scenario())

    assert attempts, "the reconnecting client tried the plaintext peer"
    for attempt in attempts:
        assert attempt[:3] == b"\x16\x03\x01", "every attempt opened with a TLS ClientHello"
        assert jwt.encode() not in attempt and seed.encode() not in attempt
        assert b"CONNECT" not in attempt
