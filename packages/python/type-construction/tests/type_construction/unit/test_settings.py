"""Applications declare configuration by specializing ``Settings`` and composing contracts.

Governing requirements: docs/architecture/DESIGN.md sections 5.2 (the ``Settings`` contract and
native composition), 6.1 (importing declarations acquires nothing; invalid required configuration
identifies the setting), 7 (deployment supplies values through native sources in the documented
order), 8.1 (freezing prevents reassignment, not mutation inside containers) and 10 (invalid
required settings fail at construction). Expected values derive from the declared contract and
the documented native source order, never from the implementation under test.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Literal

import pytest
from pydantic import AnyUrl, Field, ValidationError
from pydantic_settings import SettingsConfigDict

from type_construction import Model, NatsConnection, Settings


class Database(Model):
    """An application-owned configuration requirement beside the integration contract."""

    host: str
    pool_size: int = Field(5, ge=1)


class OrdersSettings(Settings):
    """The public declaration: typed fields, a prefix, an alias and a composed contract."""

    model_config = SettingsConfigDict(env_prefix="ORDERS_")

    nats: NatsConnection
    database: Database
    region: str = Field(validation_alias="DEPLOY_REGION")
    mode: Literal["prod", "staging"] = "prod"


def construct[S: Settings](declaration: type[S], /, **values: Any) -> S:
    """Construct configuration through its declared class, as the launch path will.

    Static checkers model required settings fields as constructor parameters; deployment sources
    supply them at construction, so the declaration is called through its type.
    """
    return declaration(**values)


@pytest.fixture(autouse=True)
def _deployment_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Start every test from an empty deployment environment."""
    for name in list(os.environ):
        monkeypatch.delenv(name)


def _supply_required_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORDERS_NATS__SERVERS", '["nats://nats", "tls://backup.example:4223"]')
    monkeypatch.setenv("ORDERS_DATABASE__HOST", "db.internal")
    monkeypatch.setenv("DEPLOY_REGION", "eu-west")


def _problems(error: ValidationError) -> set[tuple[tuple[int | str, ...], str]]:
    return {(detail["loc"], detail["type"]) for detail in error.errors()}


def test_environment_constructs_the_declared_composition(monkeypatch: pytest.MonkeyPatch) -> None:
    _supply_required_values(monkeypatch)

    settings = construct(OrdersSettings)

    assert settings.nats == NatsConnection(
        servers=(AnyUrl("nats://nats"), AnyUrl("tls://backup.example:4223"))
    )
    assert settings.database == Database(host="db.internal", pool_size=5)
    assert settings.region == "eu-west"
    assert settings.mode == "prod"


def test_missing_required_values_identify_each_setting() -> None:
    with pytest.raises(ValidationError) as excinfo:
        construct(OrdersSettings)

    assert _problems(excinfo.value) == {
        (("nats",), "missing"),
        (("database",), "missing"),
        (("DEPLOY_REGION",), "missing"),
    }


def test_invalid_supplied_values_identify_nested_locations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _supply_required_values(monkeypatch)
    monkeypatch.setenv("ORDERS_NATS__SERVERS", '["nats://nats:4222", "http://nats:8222"]')
    monkeypatch.setenv("ORDERS_DATABASE__POOL_SIZE", "0")
    monkeypatch.setenv("ORDERS_MODE", "test")

    with pytest.raises(ValidationError) as excinfo:
        construct(OrdersSettings)

    assert _problems(excinfo.value) == {
        (("nats", "servers", 1), "url_scheme"),
        (("database", "pool_size"), "greater_than_equal"),
        (("mode",), "literal_error"),
    }


def test_invalid_declared_default_fails_at_construction() -> None:
    class Misdeclared(Settings):
        retries: int = Field(default=0, ge=1)

    with pytest.raises(ValidationError) as excinfo:
        construct(Misdeclared)

    assert _problems(excinfo.value) == {(("retries",), "greater_than_equal")}


def test_enabled_sources_keep_native_precedence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    secrets = tmp_path / "secrets"
    secrets.mkdir()
    (secrets / "orders_mode").write_text("staging")
    (secrets / "orders_database").write_text('{"host": "secret-db", "pool_size": 2}')
    env_file = tmp_path / ".env"
    env_file.write_text(
        'ORDERS_NATS__SERVERS=["nats://dotenv:4222"]\nORDERS_DATABASE__HOST=dotenv-db\n'
    )
    monkeypatch.setenv("ORDERS_NATS__SERVERS", '["nats://env:4222"]')
    monkeypatch.setenv("DEPLOY_REGION", "env-region")

    class Deployed(OrdersSettings):
        model_config = SettingsConfigDict(env_file=env_file, secrets_dir=secrets)

    settings = construct(Deployed, DEPLOY_REGION="init-region")

    assert settings.region == "init-region", "initialization values precede the environment"
    assert settings.nats.servers == (AnyUrl("nats://env:4222"),), "env precedes dotenv"
    assert settings.database.host == "dotenv-db", "dotenv precedes secret files"
    assert settings.database.pool_size == 2, "nested values merge per field across sources"
    assert settings.mode == "staging", "secret files precede declared defaults"


def test_alias_names_the_receiving_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    _supply_required_values(monkeypatch)
    monkeypatch.delenv("DEPLOY_REGION")
    monkeypatch.setenv("ORDERS_REGION", "by-prefixed-name")
    monkeypatch.setenv("REGION", "by-name")

    with pytest.raises(ValidationError) as excinfo:
        construct(OrdersSettings)
    assert _problems(excinfo.value) == {(("DEPLOY_REGION",), "missing")}

    monkeypatch.setenv("DEPLOY_REGION", "eu-west")
    assert construct(OrdersSettings).region == "eu-west"


def test_applications_specialize_without_redeclaring_the_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BillingSettings(Settings):
        model_config = SettingsConfigDict(env_prefix="BILLING_")

        nats: NatsConnection

    _supply_required_values(monkeypatch)
    monkeypatch.setenv("BILLING_NATS__SERVERS", '["nats://billing-nats"]')

    billing = construct(BillingSettings)
    orders = construct(OrdersSettings)

    assert billing.nats == NatsConnection(servers=(AnyUrl("nats://billing-nats"),))
    assert orders.nats != billing.nats
    assert BillingSettings.model_config.get("validate_default") is True
    assert BillingSettings.model_config.get("frozen") is True
    assert BillingSettings.model_config.get("env_nested_delimiter") == "__"


def test_frozen_rejects_reassignment_not_container_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Labelled(Settings):
        nats: NatsConnection
        labels: list[str]

    monkeypatch.setenv("NATS__SERVERS", '["nats://nats"]')
    monkeypatch.setenv("LABELS", '["blue"]')
    settings = construct(Labelled)

    with pytest.raises(ValidationError) as top_level:
        settings.labels = []
    with pytest.raises(ValidationError) as nested:
        settings.nats.servers = ()
    settings.labels.append("green")

    assert top_level.value.errors()[0]["type"] == "frozen_instance"
    assert nested.value.errors()[0]["type"] == "frozen_instance"
    assert settings.labels == ["blue", "green"]


def test_composed_settings_are_hashable_facts(monkeypatch: pytest.MonkeyPatch) -> None:
    _supply_required_values(monkeypatch)

    assert hash(construct(OrdersSettings)) == hash(construct(OrdersSettings))


def test_importing_declarations_acquires_no_configuration() -> None:
    declaration = (
        "from pydantic import ValidationError\n"
        "from type_construction import NatsConnection, Settings\n"
        "class App(Settings):\n"
        "    nats: NatsConnection\n"
        "print('declared')\n"
        "try:\n"
        "    App()\n"
        "except ValidationError as error:\n"
        "    print(error.errors()[0]['loc'])\n"
    )

    result = subprocess.run(  # noqa: S603 - the interpreter and script are fixed test inputs
        [sys.executable, "-I", "-c", declaration],
        env={},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["declared", "('nats',)"]
