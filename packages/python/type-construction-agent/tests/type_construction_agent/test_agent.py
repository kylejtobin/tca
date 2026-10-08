import os
from pathlib import Path

import pytest
from pydantic import ValidationError
from pydantic_ai import capture_run_messages
from pydantic_ai.messages import ModelRequest
from pydantic_ai.models.test import TestModel

import type_construction.agent
from type_construction.agent import Answer, Prompt, run, run_sync
from type_construction.agent.config import (
    AgentConfig,
    Anthropic,
    AwsBearer,
    AwsKey,
    AwsSession,
    Azure,
    Cloudflare,
    OpenAI,
)
from type_construction.agent.domain.agent.type import (
    AnswerText,
    PromptLibrary,
    PromptLocation,
    PromptText,
)
from type_construction.agent.integration.model_provider.model import Reply

ACCOUNT = "0123456789abcdef0123456789abcdef"
VARIABLES = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "OPENAI_API_VERSION",
    "AZURE_OPENAI_API_KEY",
    "AWS_DEFAULT_REGION",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "AWS_BEARER_TOKEN_BEDROCK",
    "CLOUDFLARE_ACCOUNT_ID",
    "CLOUDFLARE_API_TOKEN",
)


@pytest.fixture
def bare_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in VARIABLES:
        monkeypatch.delenv(name, raising=False)


@pytest.mark.usefixtures("bare_environment")
def test_a_prompt_is_answered_with_the_agent_prompt_as_instructions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = TestModel(custom_output_args=Reply(text=AnswerText("ok")), call_tools=[])
    monkeypatch.setenv("TCA_AGENT_PROVIDER", "openai")
    monkeypatch.setenv("TCA_AGENT_MODEL", "gpt-5")
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.setattr(OpenAI, "client", property(lambda _: model))
    prompt = Prompt(text=PromptText("Model a checkout domain."))
    with capture_run_messages() as messages:
        answer = run_sync(prompt)
    assert answer == Answer(prompt=prompt, text=AnswerText("ok"))
    request = messages[0]
    assert isinstance(request, ModelRequest)
    assert (
        Path(type_construction.agent.__file__).parent
        / PromptLibrary.PROMPTS
        / PromptLocation.TCA_AGENT
    ).read_text().strip() in str(request.instructions)


@pytest.mark.parametrize(
    ("provider", "variables", "variant"),
    (
        ("openai", (("OPENAI_API_KEY", "k"),), OpenAI),
        ("anthropic", (("ANTHROPIC_API_KEY", "k"),), Anthropic),
        (
            "azure",
            (
                ("AZURE_OPENAI_ENDPOINT", "https://x.openai.azure.com"),
                ("OPENAI_API_VERSION", "2024-10-21"),
                ("AZURE_OPENAI_API_KEY", "k"),
            ),
            Azure,
        ),
        (
            "cloudflare",
            (("CLOUDFLARE_ACCOUNT_ID", ACCOUNT), ("CLOUDFLARE_API_TOKEN", "k")),
            Cloudflare,
        ),
        (
            "aws",
            (
                ("AWS_DEFAULT_REGION", "us-east-1"),
                ("AWS_ACCESS_KEY_ID", "k"),
                ("AWS_SECRET_ACCESS_KEY", "k"),
                ("AWS_SESSION_TOKEN", "k"),
            ),
            AwsSession,
        ),
        (
            "aws",
            (
                ("AWS_DEFAULT_REGION", "us-east-1"),
                ("AWS_ACCESS_KEY_ID", "k"),
                ("AWS_SECRET_ACCESS_KEY", "k"),
            ),
            AwsKey,
        ),
        (
            "aws",
            (("AWS_DEFAULT_REGION", "us-east-1"), ("AWS_BEARER_TOKEN_BEDROCK", "k")),
            AwsBearer,
        ),
    ),
)
@pytest.mark.usefixtures("bare_environment")
def test_the_named_provider_is_built_only_from_its_own_variables(
    monkeypatch: pytest.MonkeyPatch,
    provider: str,
    variables: tuple[tuple[str, str], ...],
    variant: type,
) -> None:
    monkeypatch.setenv("TCA_AGENT_PROVIDER", provider)
    monkeypatch.setenv("TCA_AGENT_MODEL", "m")
    for name, value in variables:
        monkeypatch.setenv(name, value)
    assert type(AgentConfig().provider.root) is variant  # pyright: ignore[reportCallIssue]
    for name, _ in variables:
        monkeypatch.delenv(name)
    with pytest.raises(ValidationError):
        assert AgentConfig().provider  # pyright: ignore[reportCallIssue]


needs_a_provider = pytest.mark.skipif(
    "TCA_AGENT_PROVIDER" not in os.environ, reason="no model provider is configured"
)


@needs_a_provider
def test_the_configured_provider_answers() -> None:
    assert run_sync(Prompt(text=PromptText("Reply with one word."))).text.root


@needs_a_provider
@pytest.mark.asyncio
async def test_the_configured_provider_answers_async() -> None:
    assert (await run(Prompt(text=PromptText("Reply with one word.")))).text.root
