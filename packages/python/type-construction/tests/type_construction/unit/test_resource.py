"""Applications declare a broker requirement as a ``Resource``; the framework realizes it natively.

Governing requirements: docs/architecture/DESIGN.md sections 5.2 (``Resource`` declares an
integration resource's settings; the integration supplies the contract), 5.4 (Pydantic Settings
constructs configuration; the binding supplies verified TLS, TLS before any protocol exchange and
native credentials to the native ``NatsBroker``), 6.1 (valid configuration establishes no
connectivity; invalid required configuration fails identifying the setting) and 7 (every binding
realizes a separate placement; equal configuration does not establish sharing). The configured
native security parameters are observed through the broker's published specification.
"""

import json
import os
import ssl
from pathlib import Path
from typing import Any

import pytest
from faststream import FastStream
from faststream.nats.security import NatsCredentials
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from type_construction import NatsConnection, Resource, Settings
from type_construction.resources import bind_resource

TCP = '{"transport": "tcp", "urls": ["tls://nats:4222", "tls://backup.example:4223"]}'
WEBSOCKET = '{"transport": "websocket", "urls": ["wss://edge.example"]}'


class OrdersSettings(Settings):
    """The public declaration: a broker requirement beside the application's prefix."""

    model_config = SettingsConfigDict(env_prefix="ORDERS_")

    broker: Resource


def construct[S: Settings](declaration: type[S], /, **values: Any) -> S:
    """Construct configuration through its declared class, as the launch path will."""
    return declaration(**values)


def _problems(error: ValidationError) -> set[tuple[tuple[int | str, ...], str]]:
    return {(detail["loc"], detail["type"]) for detail in error.errors()}


@pytest.fixture(autouse=True)
def _deployment_environment(monkeypatch: pytest.MonkeyPatch, material: dict[str, Path]) -> None:
    for name in list(os.environ):
        monkeypatch.delenv(name)
    monkeypatch.setenv(
        "ORDERS_BROKER__CONNECTION__CREDENTIALS", str(material["application_credentials"])
    )
    monkeypatch.setenv(
        "ORDERS_BROKER__CONNECTION__CERTIFICATE_AUTHORITY", str(material["certificate_authority"])
    )


@pytest.mark.parametrize(
    ("supplied", "expected"),
    [
        (TCP, ["tls://nats:4222", "tls://backup.example:4223"]),
        (WEBSOCKET, ["wss://edge.example/"]),
    ],
    ids=["tcp", "websocket"],
)
def test_settings_supply_either_alternative_as_the_resource_connection(
    monkeypatch: pytest.MonkeyPatch, material: dict[str, Path], supplied: str, expected: list[str]
) -> None:
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", supplied)

    settings = construct(OrdersSettings)

    assert settings.broker == Resource(
        connection=NatsConnection.model_validate(
            {
                "servers": json.loads(supplied),
                "credentials": material["application_credentials"],
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


def test_declaration_and_binding_open_no_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", TCP)
    owner = FastStream()

    broker = bind_resource(construct(OrdersSettings).broker, owner)

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

    broker = bind_resource(construct(OrdersSettings).broker, owner)

    assert owner.brokers == [broker]
    assert owner.brokers[0] is broker
    assert broker.specification.url == expected


def test_binding_supplies_verified_tls_first_and_the_referenced_credentials(
    monkeypatch: pytest.MonkeyPatch, material: dict[str, Path]
) -> None:
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", TCP)
    broker = bind_resource(construct(OrdersSettings).broker, FastStream())

    security = broker.specification.security
    assert isinstance(security, NatsCredentials)
    assert security.credentials == material["application_credentials"]
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


def test_each_binding_realizes_a_separate_placement(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", TCP)
    resource = construct(OrdersSettings).broker
    owner = FastStream()
    other = FastStream()

    first = bind_resource(resource, owner)
    second = bind_resource(resource, owner)
    elsewhere = bind_resource(resource, other)

    assert first is not second
    assert owner.brokers == [first, second]
    assert other.brokers == [elsewhere]
    assert elsewhere not in owner.brokers


def test_resource_is_an_immutable_fact(
    monkeypatch: pytest.MonkeyPatch, material: dict[str, Path]
) -> None:
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", TCP)
    resource = construct(OrdersSettings).broker
    replacement = NatsConnection.model_validate(
        {
            "servers": {"transport": "websocket", "urls": ["wss://edge.example"]},
            "credentials": material["application_credentials"],
            "certificate_authority": material["certificate_authority"],
        }
    )

    with pytest.raises(ValidationError) as excinfo:
        resource.connection = replacement

    assert excinfo.value.errors()[0]["type"] == "frozen_instance"
    assert hash(resource) == hash(construct(OrdersSettings).broker)
