from pathlib import Path

import pytest
from pydantic import ValidationError
from pydantic_ai import Agent, TemplateStr
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.test import TestModel
from pydantic_ai_harness import Skills

import type_construction.agent
from type_construction.agent import Answer, Prompt
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
    PromptText,
    SkillLibrary,
    SkillLocation,
    SkillName,
)
from type_construction.agent.domain.agent.value import TcaAgentValues
from type_construction.agent.integration.agent_skills.model import SkillDocument
from type_construction.agent.integration.model_provider.interpreter import RunInterpreter
from type_construction.agent.integration.model_provider.model import Reply
from type_construction.agent.parser.skill import read

ACCOUNT = "0123456789abcdef0123456789abcdef"


@pytest.fixture(autouse=True)
def bare_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
    monkeypatch.delenv("AWS_SESSION_TOKEN", raising=False)
    monkeypatch.delenv("AWS_BEARER_TOKEN_BEDROCK", raising=False)


@pytest.mark.asyncio
async def test_a_prompt_is_answered() -> None:
    prompt = Prompt(text=PromptText("Say hello."))
    assert await RunInterpreter(
        action=prompt.run,
        client=Agent(
            TestModel(custom_output_args=Reply(text=AnswerText("Hello."))),
            deps_type=TcaAgentValues,
            output_type=Reply,
        ),
    ).interpret() == Answer(prompt=prompt, text=AnswerText("Hello."))


def test_an_empty_prompt_cannot_be_constructed() -> None:
    with pytest.raises(ValidationError):
        Prompt(text=PromptText(""))


@pytest.mark.asyncio
@pytest.mark.parametrize("skill", ("python-dev-tca", "docker-infra-tca", "smell-check"))
async def test_each_skill_is_offered_to_the_agent(skill: str) -> None:
    model = TestModel(custom_output_args=Reply(text=AnswerText("ok")), call_tools=[])
    result = await Agent(
        model,
        deps_type=TcaAgentValues,
        output_type=Reply,
        capabilities=(
            LocalWorkspace(Path(type_construction.agent.__file__).parent, read_only=True),
            Skills(SkillLibrary.SKILLS),
        ),
    ).run("ok", deps=TcaAgentValues())
    assert f"- {skill}: " in str(result.all_messages()[0])


def test_the_tca_agent_words_are_a_template_over_its_values() -> None:
    assert (
        TemplateStr(
            SkillDocument.model_validate_json(read(SkillLocation.TCA_AGENT)).body.root,
            deps_type=TcaAgentValues,
        )
        .render(TcaAgentValues())
        .startswith("You are the TCA agent.")
    )


def test_the_tca_agent_skill_is_shipped_and_read() -> None:
    assert SkillDocument.model_validate_json(read(SkillLocation.TCA_AGENT)).name == SkillName(
        "tca-agent"
    )


def test_openai_is_constructed_when_named_even_with_other_keys_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TCA_AGENT_PROVIDER", "openai")
    monkeypatch.setenv("TCA_AGENT_MODEL", "gpt-5")
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    config = AgentConfig()  # pyright: ignore[reportCallIssue]
    assert type(config.provider.root) is OpenAI
    assert type(config.provider.client) is OpenAIChatModel


def test_anthropic_is_constructed_when_named(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TCA_AGENT_PROVIDER", "anthropic")
    monkeypatch.setenv("TCA_AGENT_MODEL", "claude-sonnet-5-5")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    config = AgentConfig()  # pyright: ignore[reportCallIssue]
    assert type(config.provider.root) is Anthropic
    assert type(config.provider.client) is AnthropicModel


def test_azure_is_constructed_when_named(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TCA_AGENT_PROVIDER", "azure")
    monkeypatch.setenv("TCA_AGENT_MODEL", "deployment")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://x.openai.azure.com")
    monkeypatch.setenv("OPENAI_API_VERSION", "2024-10-21")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "k")
    config = AgentConfig()  # pyright: ignore[reportCallIssue]
    assert type(config.provider.root) is Azure
    assert type(config.provider.client) is OpenAIChatModel


def test_cloudflare_is_constructed_at_its_account(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TCA_AGENT_PROVIDER", "cloudflare")
    monkeypatch.setenv("TCA_AGENT_MODEL", "@cf/meta/llama-3.1-8b-instruct")
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", ACCOUNT)
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "k")
    config = AgentConfig()  # pyright: ignore[reportCallIssue]
    assert type(config.provider.root) is Cloudflare
    assert type(config.provider.client) is OpenAIChatModel


def test_aws_with_a_temporary_key_is_constructed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TCA_AGENT_PROVIDER", "aws")
    monkeypatch.setenv("TCA_AGENT_MODEL", "m")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "k")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "k")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "k")
    config = AgentConfig()  # pyright: ignore[reportCallIssue]
    assert type(config.provider.root) is AwsSession
    assert type(config.provider.client) is BedrockConverseModel


def test_aws_with_a_long_lived_key_is_constructed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TCA_AGENT_PROVIDER", "aws")
    monkeypatch.setenv("TCA_AGENT_MODEL", "m")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "k")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "k")
    config = AgentConfig()  # pyright: ignore[reportCallIssue]
    assert type(config.provider.root) is AwsKey
    assert type(config.provider.client) is BedrockConverseModel


def test_aws_with_a_bedrock_api_key_is_constructed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TCA_AGENT_PROVIDER", "aws")
    monkeypatch.setenv("TCA_AGENT_MODEL", "m")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_BEARER_TOKEN_BEDROCK", "k")
    config = AgentConfig()  # pyright: ignore[reportCallIssue]
    assert type(config.provider.root) is AwsBearer
    assert type(config.provider.client) is BedrockConverseModel


def test_a_named_provider_without_its_credentials_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TCA_AGENT_PROVIDER", "openai")
    monkeypatch.setenv("TCA_AGENT_MODEL", "gpt-5")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    with pytest.raises(ValidationError):
        assert AgentConfig().provider  # pyright: ignore[reportCallIssue]


def test_credentials_are_never_shown(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TCA_AGENT_PROVIDER", "openai")
    monkeypatch.setenv("TCA_AGENT_MODEL", "gpt-5")
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    assert "'k'" not in repr(AgentConfig())  # pyright: ignore[reportCallIssue]
