"""Framework-owned diagnostics explain failed construction without repeating rejected inputs.

Governing requirements: docs/architecture/DESIGN.md sections 5.2 (diagnostics are framework-owned
typed facts), 6.1 (invalid required configuration identifies the setting) and 7 (configuration
holds references to secrets; credential contents never enter ordinary values or URLs). A rejected
deployment value may itself be a secret, so the displayed error and the structured problems must
omit it while still naming the location and the failed rule. The canary is a password that must
not survive into any rendering.
"""

import pytest
from pydantic import Field, ValidationError
from pydantic_settings import SettingsConfigDict

from type_construction import Model, Settings
from type_construction.diagnostics import Problem, problems

CANARY = "hunter2-canary"


class Endpoint(Model):
    host: str = Field(min_length=1)
    port: int = Field(ge=1, le=65535)


class ServiceSettings(Settings):
    model_config = SettingsConfigDict(env_prefix="SERVICE_")

    endpoint: Endpoint
    token: str = Field(pattern=r"^[a-z]{8}$")


def test_problems_identify_location_kind_and_message_only() -> None:
    with pytest.raises(ValidationError) as excinfo:
        Endpoint.model_validate({"host": "", "port": CANARY})

    found = problems(excinfo.value)

    assert found == (
        Problem(
            location=("host",),
            kind="string_too_short",
            message="String should have at least 1 character",
        ),
        Problem(
            location=("port",),
            kind="int_parsing",
            message="Input should be a valid integer, unable to parse string as an integer",
        ),
    )
    assert all(set(problem.model_dump()) == {"location", "kind", "message"} for problem in found)
    assert CANARY not in repr(found)


def test_settings_hide_rejected_deployment_values_in_displayed_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SERVICE_ENDPOINT", '{"host": "db", "port": 5432}')
    monkeypatch.setenv("SERVICE_TOKEN", CANARY)

    with pytest.raises(ValidationError) as excinfo:
        ServiceSettings()  # pyright: ignore[reportCallIssue]

    displayed = str(excinfo.value)
    assert "token" in displayed and "string_pattern_mismatch" in displayed
    assert CANARY not in displayed
    assert CANARY in str(excinfo.value.errors()), "the native default rendering keeps the input"
    assert problems(excinfo.value) == (
        Problem(
            location=("token",),
            kind="string_pattern_mismatch",
            message="String should match pattern '^[a-z]{8}$'",
        ),
    )
