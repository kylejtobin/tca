"""Handlers on a realized resource receive its native broker objects through FastStream injection.

Governing requirements: docs/architecture/DESIGN.md sections 5.4 (bindings preserve access to
the actual ``NatsBroker``, nats-py ``Client`` and ``JetStreamContext`` through FastStream's
native broker context and its ``Client`` and ``JsClient`` annotations) and 7 (uses of one
realized resource share its native instance; equal configuration does not establish sharing;
separate runtimes own separate clients). Handlers are invoked through FastStream's in-memory
test harness, which exercises native receiving and injection against unconnected brokers. It
establishes association and isolation only; live connectivity is outside these tests.
"""

import asyncio
import os
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any

import pytest
from faststream import FastStream
from faststream.nats import NatsBroker as Broker
from faststream.nats import TestNatsBroker
from faststream.nats.annotations import Client, JsClient, NatsBroker
from pydantic_settings import SettingsConfigDict

from type_construction import Resource, Settings
from type_construction.resources import bind_resource

type Injected = tuple[Broker, object, object]


class OrdersSettings(Settings):
    model_config = SettingsConfigDict(env_prefix="ORDERS_")

    broker: Resource


def construct[S: Settings](declaration: type[S], /) -> S:
    """Construct configuration through its declared class, as the launch path will."""
    return declaration()


def _declared_resource() -> Resource:
    return construct(OrdersSettings).broker


@pytest.fixture(autouse=True)
def _deployment_environment(monkeypatch: pytest.MonkeyPatch, material: dict[str, Path]) -> None:
    for name in list(os.environ):
        monkeypatch.delenv(name)
    monkeypatch.setenv(
        "ORDERS_BROKER__CONNECTION__SERVERS", '{"transport": "tcp", "urls": ["tls://nats:4222"]}'
    )
    monkeypatch.setenv(
        "ORDERS_BROKER__CONNECTION__CREDENTIALS", str(material["application_credentials"])
    )
    monkeypatch.setenv(
        "ORDERS_BROKER__CONNECTION__CERTIFICATE_AUTHORITY", str(material["certificate_authority"])
    )


def _observe(broker: Broker, subject: str, received: dict[str, Injected]) -> None:
    """Register a framework-owned verification handler recording what injection supplied."""

    @broker.subscriber(subject)
    async def observe(body: str, owner: NatsBroker, client: Client, stream: JsClient) -> None:
        received[body] = (owner, client, stream)


def _run(scenario: Callable[[], Coroutine[Any, Any, None]]) -> None:
    asyncio.run(scenario())


def test_two_handlers_on_one_realized_resource_share_its_broker_and_clients() -> None:
    owner = FastStream()
    broker = bind_resource(_declared_resource(), owner)
    received: dict[str, Injected] = {}
    _observe(broker, "orders.placed", received)
    _observe(broker, "orders.shipped", received)

    async def scenario() -> None:
        async with TestNatsBroker(broker):
            await broker.publish("placed", "orders.placed")
            await broker.publish("shipped", "orders.shipped")

    _run(scenario)

    assert received["placed"][0] is broker
    assert received["shipped"][0] is broker
    assert (
        received["placed"][1] is received["shipped"][1] is broker.config.connection_state.connection
    )
    assert received["placed"][2] is received["shipped"][2] is broker.config.connection_state.stream


def test_equal_configuration_realized_twice_in_one_owner_keeps_distinct_brokers() -> None:
    owner = FastStream()
    resource = _declared_resource()
    first = bind_resource(resource, owner)
    second = bind_resource(resource, owner)
    received: dict[str, Injected] = {}
    _observe(first, "orders.first", received)
    _observe(second, "orders.second", received)

    async def scenario() -> None:
        async with TestNatsBroker(first, second):
            await first.publish("first", "orders.first")
            await second.publish("second", "orders.second")

    _run(scenario)

    assert first.specification.url == second.specification.url
    assert received["first"][0] is first
    assert received["second"][0] is second
    assert received["first"][1] is not received["second"][1]
    assert received["first"][2] is not received["second"][2]


def test_separate_owners_using_the_same_declaration_keep_isolated_brokers() -> None:
    resource = _declared_resource()
    owner = FastStream()
    other = FastStream()
    here = bind_resource(resource, owner)
    there = bind_resource(resource, other)
    received: dict[str, Injected] = {}
    _observe(here, "orders.here", received)
    _observe(there, "orders.there", received)

    async def scenario() -> None:
        async with TestNatsBroker(here, there):
            await here.publish("here", "orders.here")
            await there.publish("there", "orders.there")

    _run(scenario)

    assert owner.brokers == [here]
    assert other.brokers == [there]
    assert received["here"][0] is here
    assert received["there"][0] is there
    assert received["here"][1] is not received["there"][1]
