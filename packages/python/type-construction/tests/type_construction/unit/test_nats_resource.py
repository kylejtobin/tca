"""Applications declare a broker requirement as ``NatsResource``; the integration binds it natively.

Governing requirements: docs/architecture/DESIGN.md sections 5.2 (an integration supplies the
resource contract its placement requires), 5.4 (Pydantic Settings constructs configuration; the
binding supplies verified TLS, TLS before any protocol exchange and native credentials to the
native ``NatsBroker``), 6.1 (valid configuration establishes no connectivity; invalid required
configuration fails identifying the setting) and 7 (every binding realizes a separate placement;
equal configuration does not establish sharing; credential contents stay out of models). The
configured native security parameters are observed through the broker's published specification.
Credentials are read at realization only: an audit hook records every open of the referenced file.
"""

import json
import os
import ssl
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from faststream import FastStream
from faststream.nats.security import NatsCredentials
from nats.aio.client import RawCredentials
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from type_construction import Settings
from type_construction.nats import NatsConnection, NatsResource

TCP = '{"transport": "tcp", "urls": ["tls://nats:4222", "tls://backup.example:4223"]}'
WEBSOCKET = '{"transport": "websocket", "urls": ["wss://edge.example"]}'
JWT = "eyJ0eXAiOiJKV1QiLCJhbGciOiJlZDI1NTE5LW5rZXkifQ.canary-jwt"
SEED = "SUACANARYSEEDNEVERLEAVESTHEFILE"
COMPLETE_CREDENTIALS = (
    f"-----BEGIN NATS USER JWT-----\n{JWT}\n------END NATS USER JWT------\n\n"
    f"-----BEGIN USER NKEY SEED-----\n{SEED}\n------END USER NKEY SEED------\n"
)

_opened: list[str] = []


def _record_opens(event: str, arguments: tuple[Any, ...]) -> None:
    if event == "open":
        _opened.append(str(arguments[0]))


sys.addaudithook(_record_opens)


class OrdersSettings(Settings):
    """The public declaration: a broker requirement beside the application's prefix."""

    model_config = SettingsConfigDict(env_prefix="ORDERS_")

    broker: NatsResource


def construct[S: Settings](declaration: type[S], /, **values: Any) -> S:
    """Construct configuration through its declared class, as the launch path will."""
    return declaration(**values)


def _problems(error: ValidationError) -> set[tuple[tuple[int | str, ...], str]]:
    return {(detail["loc"], detail["type"]) for detail in error.errors()}


@pytest.fixture
def credentials(tmp_path: Path) -> Path:
    """A well-framed credentials file whose contents are canaries, never a usable identity."""
    path = tmp_path / "application.creds"
    path.write_text(COMPLETE_CREDENTIALS)
    return path


@pytest.fixture(autouse=True)
def _deployment_environment(
    monkeypatch: pytest.MonkeyPatch, material: dict[str, Path], credentials: Path
) -> Iterator[None]:
    for name in list(os.environ):
        monkeypatch.delenv(name)
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__CREDENTIALS", str(credentials))
    monkeypatch.setenv(
        "ORDERS_BROKER__CONNECTION__CERTIFICATE_AUTHORITY", str(material["certificate_authority"])
    )
    _opened.clear()
    yield
    _opened.clear()


def _opens_of(path: Path) -> int:
    return sum(1 for opened in _opened if opened == str(path))


@pytest.mark.parametrize(
    ("supplied", "expected"),
    [
        (TCP, ["tls://nats:4222", "tls://backup.example:4223"]),
        (WEBSOCKET, ["wss://edge.example/"]),
    ],
    ids=["tcp", "websocket"],
)
def test_settings_supply_either_alternative_as_the_resource_connection(
    monkeypatch: pytest.MonkeyPatch,
    material: dict[str, Path],
    credentials: Path,
    supplied: str,
    expected: list[str],
) -> None:
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", supplied)

    settings = construct(OrdersSettings)

    assert settings.broker == NatsResource(
        connection=NatsConnection.model_validate(
            {
                "servers": json.loads(supplied),
                "credentials": credentials,
                "certificate_authority": material["certificate_authority"],
            }
        )
    )
    assert [str(url.root) for url in settings.broker.connection.servers.urls.root] == expected


def test_missing_or_invalid_required_configuration_fails_before_binding(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    with pytest.raises(ValidationError) as missing:
        construct(OrdersSettings)

    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", '{"transport": "tcp", "urls": []}')
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__CREDENTIALS", str(tmp_path / "absent.creds"))
    with pytest.raises(ValidationError) as invalid:
        construct(OrdersSettings)

    assert _problems(missing.value) == {(("broker", "connection", "servers"), "missing")}
    assert _problems(invalid.value) == {
        (("broker", "connection", "servers", "tcp", "urls"), "too_short"),
        (("broker", "connection", "credentials"), "path_not_file"),
    }


def test_declaration_reads_no_credential_and_binding_opens_no_connection(
    monkeypatch: pytest.MonkeyPatch, credentials: Path
) -> None:
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", TCP)
    owner = FastStream()

    resource = construct(OrdersSettings).broker
    assert _opens_of(credentials) == 0, "construction checks the reference, not the contents"

    broker = resource.bind(owner)

    assert _opens_of(credentials) == 1, "realization reads the referenced file once"
    assert not broker.running
    assert not broker.config.connection_state, "no native connection exists before startup"


@pytest.mark.parametrize(
    ("supplied", "expected"),
    [
        (TCP, ["tls://nats:4222", "tls://backup.example:4223"]),
        (WEBSOCKET, ["wss://edge.example/"]),
    ],
    ids=["tcp", "websocket"],
)
def test_binding_registers_the_returned_broker_with_its_ordered_urls(
    monkeypatch: pytest.MonkeyPatch, supplied: str, expected: list[str]
) -> None:
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", supplied)
    owner = FastStream()

    broker = construct(OrdersSettings).broker.bind(owner)

    assert owner.brokers == [broker]
    assert owner.brokers[0] is broker
    assert broker.specification.url == expected


def test_binding_supplies_verified_tls_first_and_a_credentials_snapshot(
    monkeypatch: pytest.MonkeyPatch, credentials: Path
) -> None:
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", TCP)
    resource = construct(OrdersSettings).broker

    broker = resource.bind(FastStream())
    credentials.write_text(COMPLETE_CREDENTIALS.replace(SEED, "SUAROTATEDSEED"))
    later = resource.bind(FastStream())

    security = broker.specification.security
    assert isinstance(security, NatsCredentials)
    assert isinstance(security.credentials, RawCredentials)
    assert security.credentials.data == COMPLETE_CREDENTIALS, "the snapshot taken at realization"
    assert security.tls_handshake_first is True
    assert security.tls_hostname is None, "hostnames are verified against the URL host"
    context = security.ssl_context
    assert context is not None
    assert context.verify_mode is ssl.CERT_REQUIRED
    assert context.check_hostname is True
    assert context.minimum_version >= ssl.TLSVersion.TLSv1_2
    certificates = context.get_ca_certs()
    assert len(certificates) == 1, "only the referenced authority is trusted"
    assert certificates[0]["subject"] == ((("commonName", "TCA Development CA"),),)
    later_security = later.specification.security
    assert isinstance(later_security, NatsCredentials)
    assert isinstance(later_security.credentials, RawCredentials)
    assert "SUAROTATEDSEED" in later_security.credentials.data, "each realization reads afresh"
    assert SEED not in repr(resource) + resource.model_dump_json() + repr(security)


@pytest.mark.parametrize(
    "content",
    [
        COMPLETE_CREDENTIALS.replace("BEGIN NATS USER JWT", "BEGIN SOMETHING ELSE"),
        COMPLETE_CREDENTIALS.split("-----BEGIN USER NKEY SEED-----", maxsplit=1)[0],
        "",
        "not a credentials file\n",
    ],
    ids=["jwt-marker-missing", "seed-marker-missing", "empty", "unrelated"],
)
def test_credentials_lacking_the_native_markers_are_rejected_at_binding(
    monkeypatch: pytest.MonkeyPatch, credentials: Path, content: str
) -> None:
    """FastStream's ``from_raw`` guard rejects the snapshot; the native file reader would not
    terminate on such content. A rejected realization registers nothing with the runtime."""
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", TCP)
    credentials.write_text(content)
    owner = FastStream()
    resource = construct(OrdersSettings).broker

    with pytest.raises(ValueError, match="markers") as excinfo:
        resource.bind(owner)

    assert owner.brokers == []
    assert content == "" or content.splitlines()[0] not in str(excinfo.value)


def test_each_binding_realizes_a_separate_placement(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", TCP)
    resource = construct(OrdersSettings).broker
    owner = FastStream()
    other = FastStream()

    first = resource.bind(owner)
    second = resource.bind(owner)
    elsewhere = resource.bind(other)

    assert first is not second
    assert owner.brokers == [first, second]
    assert other.brokers == [elsewhere]
    assert elsewhere not in owner.brokers


def test_resource_is_an_immutable_fact(
    monkeypatch: pytest.MonkeyPatch, material: dict[str, Path], credentials: Path
) -> None:
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", TCP)
    resource = construct(OrdersSettings).broker
    replacement = NatsConnection.model_validate(
        {
            "servers": {"transport": "websocket", "urls": ["wss://edge.example"]},
            "credentials": credentials,
            "certificate_authority": material["certificate_authority"],
        }
    )

    with pytest.raises(ValidationError) as excinfo:
        resource.connection = replacement

    assert excinfo.value.errors()[0]["type"] == "frozen_instance"
    assert hash(resource) == hash(construct(OrdersSettings).broker)
