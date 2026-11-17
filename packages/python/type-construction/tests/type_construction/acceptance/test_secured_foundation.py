"""The delivered foundation works end to end through public declarations and deployment values.

Governing requirements: docs/product.md section 4 (a developer declares typed configuration and
resource requirements; deployment supplies values; no startup or connection code is written) and
docs/architecture/DESIGN.md sections 5.4, 6.1 and 7 (configuration is acquired through native
sources; resource composition selects the execution integration through typed composition and
imports; resources are realized as native brokers that connect securely). The workflow available
today: an application settings declaration composes two NATS broker resources, deployment
supplies secured pools, credentials and trust through the environment, the framework realizes
both in one runtime, and native delivery reaches handlers with the authenticated clients.
"""

import asyncio
import os
from pathlib import Path

import pytest
from faststream import FastStream
from faststream.nats.annotations import Client
from pydantic_settings import SettingsConfigDict

from type_construction import Settings
from type_construction.nats import NatsResource

START_BOUND = 10.0
STOP_BOUND = 10.0


class OrdersSettings(Settings):
    """A developer's declaration: two broker requirements, one per transport family."""

    model_config = SettingsConfigDict(env_prefix="ORDERS_")

    broker: NatsResource
    edge: NatsResource


def construct[S: Settings](declaration: type[S], /) -> S:
    return declaration()


def test_deployment_configured_resources_connect_securely_over_both_transports(
    monkeypatch: pytest.MonkeyPatch, material: dict[str, Path], secured_nats: dict[str, int]
) -> None:
    for name in list(os.environ):
        monkeypatch.delenv(name)
    for placement, pool in (
        ("BROKER", f'{{"transport":"tcp","urls":["tls://localhost:{secured_nats["tls_port"]}"]}}'),
        (
            "EDGE",
            f'{{"transport":"websocket","urls":["wss://localhost:{secured_nats["wss_port"]}"]}}',
        ),
    ):
        monkeypatch.setenv(f"ORDERS_{placement}__CONNECTION__SERVERS", pool)
        monkeypatch.setenv(
            f"ORDERS_{placement}__CONNECTION__CREDENTIALS",
            str(material["application_credentials"]),
        )
        monkeypatch.setenv(
            f"ORDERS_{placement}__CONNECTION__CERTIFICATE_AUTHORITY",
            str(material["certificate_authority"]),
        )
    settings = construct(OrdersSettings)
    runtime = FastStream()
    broker = settings.broker.bind(runtime)
    edge = settings.edge.bind(runtime)
    schemes: dict[str, str] = {}

    @broker.subscriber("tca.orders.placed")
    async def placed(body: str, client: Client) -> None:
        assert client.connected_url is not None
        schemes[body] = client.connected_url.scheme

    @edge.subscriber("tca.orders.shipped")
    async def shipped(body: str, client: Client) -> None:
        assert client.connected_url is not None
        schemes[body] = client.connected_url.scheme

    async def scenario() -> None:
        try:
            await asyncio.wait_for(runtime.start(), START_BOUND)
            await broker.publish("placed", "tca.orders.placed")
            await edge.publish("shipped", "tca.orders.shipped")
            for _ in range(50):
                if len(schemes) == 2:
                    break
                await asyncio.sleep(0.05)
        finally:
            await asyncio.wait_for(runtime.stop(), STOP_BOUND)

    asyncio.run(scenario())

    assert schemes == {"placed": "tls", "shipped": "wss"}
    assert not broker.config.connection_state and not edge.config.connection_state
