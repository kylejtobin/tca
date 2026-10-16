"""The agent as one step of a graph that governs it: the graph owns its state, its transitions
and its execution controls; the agent owns the typed inference crossing, unchanged."""

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

import pytest
from pydantic import ConfigDict, RootModel
from pydantic_ai import CancellationToken, capture_run_messages, models
from pydantic_ai.exceptions import ModelHTTPError, RunCancelled
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ToolCallPart,
    UserPromptPart,
)
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel
from pydantic_ai.usage import RunUsage
from pydantic_graph import Graph, GraphBuilder, StepContext

from type_construction.agent import (
    AgentConfig,
    Answer,
    AnswerText,
    FollowUp,
    Opening,
    PromptText,
    Reply,
    RunId,
    run,
)

MODEL = "TCA_AGENT__MODEL"
SKILLS = Path(__file__).parents[5] / ".agents" / "skills"
COIN = Opening(text=PromptText("Model a coin toss."))
ANSWER = Answer(text=AnswerText("A coin toss is a Face, Heads or Tails, drawn by a Toss."))


class WordCount(RootModel[int]):
    """How many words an answer has: the graph's own typed operation on the agent's answer."""

    model_config = ConfigDict(frozen=True, strict=True)


@dataclass
class Controls:
    """What the graph owns across its steps: the library's usage and cancellation handles."""

    usage: RunUsage = field(default_factory=RunUsage)
    token: CancellationToken = field(default_factory=CancellationToken)


def counting_graph() -> Graph[Controls, AgentConfig, Opening, WordCount]:
    g = GraphBuilder(
        name="count-the-answer",
        state_type=Controls,
        deps_type=AgentConfig,
        input_type=Opening,
        output_type=WordCount,
    )

    @g.step
    async def answer(ctx: StepContext[Controls, AgentConfig, Opening]) -> Reply:
        return await run(
            ctx.deps, ctx.inputs, usage=ctx.state.usage, cancellation_token=ctx.state.token
        )

    @g.step
    async def count(ctx: StepContext[Controls, AgentConfig, Reply]) -> WordCount:
        return WordCount(len(ctx.inputs.answer.text.root.split()))

    g.add(g.edge_from(g.start_node).to(answer), g.edge_from(answer).to(count))
    g.add(g.edge_from(count).to(g.end_node))
    return g.build()


@pytest.fixture
def bare_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """No setting of the agent's in the environment, and no `.env` where it is read from."""
    for name in tuple(os.environ):
        if name.startswith("TCA_"):
            monkeypatch.delenv(name)
    workspace = tmp_path / "workspace"
    shutil.copytree(SKILLS, workspace / ".agents" / "skills")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TCA_AGENT__WORKSPACE__KIND", "local")
    monkeypatch.setenv("TCA_AGENT__WORKSPACE__PATH", str(workspace))


def scripted(monkeypatch: pytest.MonkeyPatch, model: models.Model) -> AgentConfig:
    """The deployment names the library's own test model, and the test hands the library the
    model it holds wherever the library would infer that name."""
    monkeypatch.setenv(MODEL, "test")
    infer = models.infer_model

    def inferred(name: models.Model | str, *rest: object, **named: object) -> models.Model:
        return model if name == "test" else infer(name, *rest, **named)  # pyright: ignore[reportArgumentType, reportCallIssue]

    monkeypatch.setattr(models, "infer_model", inferred)
    return AgentConfig()  # pyright: ignore[reportCallIssue]


def answering() -> TestModel:
    return TestModel(custom_output_args=ANSWER.model_dump_json(), call_tools=[])


def test_the_graph_draws_the_agent_as_one_step() -> None:
    drawn = counting_graph().render(direction="LR")
    assert "[*] --> answer" in drawn
    assert "answer --> count" in drawn
    assert "count --> [*]" in drawn


@pytest.mark.usefixtures("bare_environment")
@pytest.mark.asyncio
async def test_a_prompt_in_gives_the_answers_word_count_out(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = scripted(monkeypatch, answering())
    with capture_run_messages() as messages:
        count = await counting_graph().run(state=Controls(), deps=config, inputs=COIN)
    assert count == WordCount(13)
    request = messages[0]
    assert isinstance(request, ModelRequest)
    assert [part.content for part in request.parts if isinstance(part, UserPromptPart)] == [
        COIN.text.root
    ]


def test_the_domain_crosses_json_whole() -> None:
    assert Opening.model_validate_json(COIN.model_dump_json()) == COIN
    asked = FollowUp(text=PromptText("Again."), after=RunId("run"))
    assert FollowUp.model_validate_json(asked.model_dump_json()) == asked
    assert Answer.model_validate_json(ANSWER.model_dump_json()) == ANSWER
    reply = Reply(answer=ANSWER, run=RunId("run"))
    assert Reply.model_validate_json(reply.model_dump_json()) == reply


@pytest.mark.usefixtures("bare_environment")
@pytest.mark.asyncio
async def test_each_run_of_the_graph_starts_the_agent_afresh(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    graph = counting_graph()
    config = scripted(monkeypatch, answering())
    await graph.run(state=Controls(), deps=config, inputs=Opening(text=PromptText("First.")))
    with capture_run_messages() as messages:
        await graph.run(state=Controls(), deps=config, inputs=Opening(text=PromptText("Second.")))
    prompts = [
        part.content
        for message in messages
        if isinstance(message, ModelRequest)
        for part in message.parts
        if isinstance(part, UserPromptPart)
    ]
    assert prompts == ["Second."]


@pytest.mark.usefixtures("bare_environment")
@pytest.mark.asyncio
async def test_the_graph_s_usage_accumulates_across_its_runs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = scripted(monkeypatch, answering())
    graph, controls = counting_graph(), Controls()
    assert await graph.run(state=controls, deps=config, inputs=COIN) == WordCount(13)
    assert await graph.run(state=controls, deps=config, inputs=COIN) == WordCount(13)
    assert controls.usage.requests == 2
    assert await graph.run(state=Controls(), deps=config, inputs=COIN) == WordCount(13)
    assert controls.usage.requests == 2


@pytest.mark.usefixtures("bare_environment")
@pytest.mark.asyncio
async def test_the_graph_cancels_the_agent_in_flight(monkeypatch: pytest.MonkeyPatch) -> None:
    controls = Controls()

    def model(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        controls.token.cancel()
        return ModelResponse(parts=[ToolCallPart(tool_name="list_directory", args={})])

    config = scripted(monkeypatch, FunctionModel(model))
    with pytest.raises(RunCancelled):
        await counting_graph().run(state=controls, deps=config, inputs=COIN)
    assert controls.token.cancelled


@pytest.mark.usefixtures("bare_environment")
@pytest.mark.asyncio
async def test_the_graph_sees_the_provider_s_own_failure(monkeypatch: pytest.MonkeyPatch) -> None:

    def model(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        raise ModelHTTPError(status_code=503, model_name="test", body="unavailable")

    config = scripted(monkeypatch, FunctionModel(model))
    with pytest.raises(ModelHTTPError):
        await counting_graph().run(state=Controls(), deps=config, inputs=COIN)
