"""Applications declare a broker requirement as a ``Resource``; the framework realizes it natively.

Governing requirements: docs/architecture/DESIGN.md sections 5.2 (``Resource`` declares an
integration resource's settings; the integration supplies the contract), 5.4 (Pydantic Settings
constructs configuration and native ``NatsBroker`` objects establish connections), 6.1 (valid
configuration establishes no connectivity; invalid required configuration fails identifying the
setting) and 7 (every binding realizes a separate placement; equal configuration does not
establish sharing). Expected URL strings follow the ``servers`` parameter of ``nats.connect``.
"""

import json
import os
from typing import Any

import pytest
from faststream import FastStream
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from type_construction import NatsConnection, Resource, Settings
from type_construction.resources import bind_resource

TCP = '{"transport": "tcp", "urls": ["nats://nats:4222", "tls://backup.example:4223"]}'
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
def _deployment_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in list(os.environ):
        monkeypatch.delenv(name)


@pytest.mark.parametrize(
    ("supplied", "expected"),
    [
        (TCP, ["nats://nats:4222", "tls://backup.example:4223"]),
        (WEBSOCKET, ["wss://edge.example/"]),
    ],
    ids=["tcp", "websocket"],
)
def test_settings_supply_either_alternative_as_the_resource_connection(
    monkeypatch: pytest.MonkeyPatch, supplied: str, expected: list[str]
) -> None:
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", supplied)

    settings = construct(OrdersSettings)

    assert settings.broker == Resource(
        connection=NatsConnection.model_validate({"servers": json.loads(supplied)})
    )
    assert [str(url.root) for url in settings.broker.connection.servers.urls.root] == expected


def test_missing_or_invalid_required_configuration_fails_before_binding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ValidationError) as missing:
        construct(OrdersSettings)

    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", '{"transport": "tcp", "urls": []}')
    with pytest.raises(ValidationError) as invalid:
        construct(OrdersSettings)

    assert _problems(missing.value) == {(("broker",), "missing")}
    assert _problems(invalid.value) == {
        (("broker", "connection", "servers", "tcp", "urls"), "too_short")
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
        (TCP, ["nats://nats:4222", "tls://backup.example:4223"]),
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


def test_resource_is_an_immutable_fact(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORDERS_BROKER__CONNECTION__SERVERS", TCP)
    resource = construct(OrdersSettings).broker
    replacement = NatsConnection.model_validate(
        {"servers": {"transport": "websocket", "urls": ["wss://edge.example"]}}
    )

    with pytest.raises(ValidationError) as excinfo:
        resource.connection = replacement

    assert excinfo.value.errors()[0]["type"] == "frozen_instance"
    assert hash(resource) == hash(construct(OrdersSettings).broker)
