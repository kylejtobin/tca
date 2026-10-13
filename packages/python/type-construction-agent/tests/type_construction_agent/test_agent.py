import os
from pathlib import Path

import pytest
from pydantic import ValidationError
from pydantic_ai import Agent, capture_run_messages
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ToolCallPart,
    ToolReturnPart,
)
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel
from pydantic_ai.usage import UsageLimits

import type_construction.agent
from type_construction.agent import AgentConfig, Answer, Prompt, run, run_sync
from type_construction.agent.domain.agent.type import AnswerText, PromptLocation, PromptText
from type_construction.agent.integration.model_provider.provider import ModelProvider

MODEL = "TCA_AGENT__MODEL"
PROMPTS = Path(type_construction.agent.__file__).parent / "prompts"
PAGE = "skills/python-dev-tca/provider.md"


@pytest.fixture
def bare_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in tuple(os.environ):
        if name.startswith("TCA_"):
            monkeypatch.delenv(name)


def held(config: AgentConfig, monkeypatch: pytest.MonkeyPatch) -> Agent[None, Answer]:
    """The provider derives a new agent on each access; a test overrides one, so it holds it."""
    agent = config.agent.client
    monkeypatch.setattr(ModelProvider, "client", property(lambda _: agent))
    return agent


def answered(text: str) -> ModelResponse:
    return ModelResponse(
        parts=[
            ToolCallPart(
                tool_name="final_result", args=Answer(text=AnswerText(text)).model_dump_json()
            )
        ]
    )


@pytest.mark.usefixtures("bare_environment")
def test_a_prompt_is_answered_with_the_agent_prompt_as_instructions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(MODEL, "test")
    config = AgentConfig()  # pyright: ignore[reportCallIssue]
    with (
        held(config, monkeypatch).override(
            model=TestModel(
                custom_output_args=Answer(text=AnswerText("ok")).model_dump_json(), call_tools=[]
            )
        ),
        capture_run_messages() as messages,
    ):
        answer = run_sync(config, Prompt(text=PromptText("Model a checkout domain.")))
    assert answer == Answer(text=AnswerText("ok"))
    request = messages[0]
    assert isinstance(request, ModelRequest)
    assert (PROMPTS / PromptLocation.TCA_AGENT).read_text().strip() in str(request.instructions)


@pytest.mark.usefixtures("bare_environment")
def test_the_deployment_names_the_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(MODEL, "anthropic:claude-opus-5-5")
    agent = AgentConfig().agent  # pyright: ignore[reportCallIssue]
    assert agent.model == "anthropic:claude-opus-5-5"
    assert agent.thinking == "low"
    assert agent.limits == UsageLimits(request_limit=20)
    monkeypatch.setenv("TCA_AGENT__THINKING", "high")
    monkeypatch.setenv("TCA_AGENT__LIMITS__REQUEST_LIMIT", "3")
    agent = AgentConfig().agent  # pyright: ignore[reportCallIssue]
    assert agent.thinking == "high"
    assert agent.limits == UsageLimits(request_limit=3)
    monkeypatch.delenv(MODEL)
    with pytest.raises(ValidationError):
        AgentConfig()  # pyright: ignore[reportCallIssue]


@pytest.mark.usefixtures("bare_environment")
def test_constructing_an_answer_calls_no_model() -> None:
    assert Answer.model_validate_json('{"text": "ok"}') == Answer(text=AnswerText("ok"))


@pytest.mark.usefixtures("bare_environment")
def test_the_named_thinking_level_reaches_the_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(MODEL, "test")
    monkeypatch.setenv("TCA_AGENT__THINKING", "high")
    config = AgentConfig()  # pyright: ignore[reportCallIssue]

    def model(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        assert (info.model_settings or {}).get("openai_reasoning_effort") == "high"
        return answered("ok")

    with held(config, monkeypatch).override(model=FunctionModel(model)):
        answer = run_sync(config, Prompt(text=PromptText("Model a coin toss.")))
    assert answer == Answer(text=AnswerText("ok"))


@pytest.mark.usefixtures("bare_environment")
def test_the_agent_loads_a_skill_and_reads_its_pages(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(MODEL, "test")
    config = AgentConfig()  # pyright: ignore[reportCallIssue]
    returns: list[ToolReturnPart] = []

    def model(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        returns[:] = [
            part
            for message in messages
            if isinstance(message, ModelRequest)
            for part in message.parts
            if isinstance(part, ToolReturnPart)
        ]
        match len(returns):
            case 0:
                return ModelResponse(
                    parts=[ToolCallPart(tool_name="load_capability", args={"id": "python-dev-tca"})]
                )
            case 1:
                return ModelResponse(
                    parts=[ToolCallPart(tool_name="read_file", args={"path": PAGE})]
                )
            case _:
                return answered("ok")

    with held(config, monkeypatch).override(model=FunctionModel(model)):
        answer = run_sync(config, Prompt(text=PromptText("Model a coin toss.")))
    assert answer == Answer(text=AnswerText("ok"))
    skill, page = returns
    assert "python-dev-tca" in str(skill.content)
    assert "Lives in integration/<system>/provider.py" in str(page.content)


@pytest.mark.usefixtures("bare_environment")
def test_a_run_stops_at_the_request_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(MODEL, "test")
    monkeypatch.setenv("TCA_AGENT__LIMITS__REQUEST_LIMIT", "1")
    config = AgentConfig()  # pyright: ignore[reportCallIssue]
    with (
        held(config, monkeypatch).override(
            model=TestModel(custom_output_args='{"not": "an answer"}', call_tools=[])
        ),
        pytest.raises(UsageLimitExceeded),
    ):
        run_sync(config, Prompt(text=PromptText("Model a coin toss.")))


needs_a_provider = pytest.mark.skipif(MODEL not in os.environ, reason="no model is configured")


@needs_a_provider
def test_the_configured_provider_answers() -> None:
    config = AgentConfig()  # pyright: ignore[reportCallIssue]
    assert run_sync(config, Prompt(text=PromptText("Reply with one word."))).text.root


@needs_a_provider
@pytest.mark.asyncio
async def test_the_configured_provider_answers_async() -> None:
    config = AgentConfig()  # pyright: ignore[reportCallIssue]
    assert (await run(config, Prompt(text=PromptText("Reply with one word.")))).text.root
