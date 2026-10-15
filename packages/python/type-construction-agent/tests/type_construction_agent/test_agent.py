"""The agent as a deployment and a program cross it: a model named, a prompt answered, the
library's own resources handed through, and the configured model acquired and released."""

import asyncio
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from collections.abc import AsyncIterable
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from types import TracebackType

import pytest
from pydantic import ValidationError
from pydantic_ai import (
    AgentRunResult,
    AgentStreamEvent,
    CancellationToken,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    RunContext,
    capture_run_messages,
    models,
)
from pydantic_ai.exceptions import ModelHTTPError, RunCancelled, UnexpectedModelBehavior, UserError
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    RetryPromptPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.test import TestModel
from pydantic_ai.toolsets import FunctionToolset
from pydantic_ai.workspaces import WorkspaceUnavailableError

import type_construction.agent
from type_construction.agent import (
    AgentConfig,
    AgentName,
    AgentProvider,
    Answer,
    AnswerInterpreter,
    AnswerText,
    Local,
    LocalKind,
    ModelName,
    Prompt,
    PromptText,
    Sandboxed,
    SandboxKind,
    Workspace,
    WorkspacePath,
    run,
    run_sync,
)

MODEL = "TCA_AGENT__MODEL"
KIND = "TCA_AGENT__WORKSPACE__KIND"
WORKSPACE = "TCA_AGENT__WORKSPACE__PATH"
SKILLS = Path(__file__).parents[5] / ".agents" / "skills"
README = Path(type_construction.agent.__file__).parents[3] / "README.md"
COIN = Prompt(text=PromptText("Model a coin toss."))
OK = Answer(text=AnswerText("ok"))


@pytest.fixture
def bare_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """No setting of the agent's in the environment, no `.env` where it is read from, and the
    workspace the deployment names beside the process directory, holding the skills."""
    for name in tuple(os.environ):
        if name.startswith(("TCA_", "OPENAI_")):
            monkeypatch.delenv(name)
    workspace = tmp_path / "workspace"
    shutil.copytree(SKILLS, workspace / ".agents" / "skills")
    checked(workspace, "exit 0")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv(KIND, "local")
    monkeypatch.setenv(WORKSPACE, str(workspace))
    return workspace


def checked(workspace: Path, script: str) -> None:
    """The workspace's check, as the workspace declares it: one script named check at its root."""
    (workspace / "check").write_text(f"#!/bin/sh\n{script}\n")
    (workspace / "check").chmod(0o755)


def scripted(monkeypatch: pytest.MonkeyPatch, model: models.Model) -> AgentConfig:
    """The deployment names the library's own test model, and the test hands the library the
    model it holds wherever the library would infer that name."""
    monkeypatch.setenv(MODEL, "test")
    infer = models.infer_model

    def inferred(name: models.Model | str, *rest: object, **named: object) -> models.Model:
        return model if name == "test" else infer(name, *rest, **named)  # pyright: ignore[reportArgumentType, reportCallIssue]

    monkeypatch.setattr(models, "infer_model", inferred)
    return AgentConfig()  # pyright: ignore[reportCallIssue]


def answered(text: str) -> ModelResponse:
    return ModelResponse(
        parts=[
            ToolCallPart(
                tool_name="final_result", args=Answer(text=AnswerText(text)).model_dump_json()
            )
        ]
    )


def returns(messages: list[ModelMessage]) -> list[ToolReturnPart | RetryPromptPart]:
    return [
        part
        for message in messages
        if isinstance(message, ModelRequest)
        for part in message.parts
        if isinstance(part, ToolReturnPart | RetryPromptPart)
    ]


class Endpoint:
    """A provider's API stood in for by a local server: what it was sent, and where it is. A
    request that asks to be streamed is answered with the streamed reply, where one is given."""

    def __init__(
        self, reply: bytes, content_type: str, delay: float = 0.0, *, status: int = 200
    ) -> None:
        self.paths: list[str] = []
        self.bodies: list[dict[str, object]] = []
        self.raw: list[bytes] = []
        self.streamed = b""
        served = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                served.paths.append(self.path)
                served.raw.append(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                is_json = self.headers.get("Content-Type", "").startswith("application/json")
                body: dict[str, object] = json.loads(served.raw[-1]) if is_json else {}
                if is_json:
                    served.bodies.append(body)
                time.sleep(delay)
                streams = bool(served.streamed) and body.get("stream") is True
                answer = served.streamed if streams else reply
                kind = "text/event-stream" if streams else content_type
                try:
                    self.send_response(status)
                    self.send_header("Content-Type", kind)
                    self.send_header("Content-Length", str(len(answer)))
                    self.end_headers()
                    self.wfile.write(answer)
                except BrokenPipeError:
                    pass

            def log_message(self, format: str, *args: object) -> None:  # noqa: A002
                pass

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        self.serving = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self) -> Endpoint:
        self.serving.start()
        return self

    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.serving.join()


CHAT_COMPLETION = json.dumps(
    {
        "id": "reply",
        "object": "chat.completion",
        "created": 0,
        "model": "deployed",
        "choices": [
            {
                "index": 0,
                "finish_reason": "tool_calls",
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call",
                            "type": "function",
                            "function": {"name": "final_result", "arguments": OK.model_dump_json()},
                        }
                    ],
                },
            }
        ],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    }
).encode()

CHUNKS: tuple[dict[str, object], ...] = (
    {
        "id": "reply",
        "object": "chat.completion.chunk",
        "created": 0,
        "model": "deployed",
        "choices": [
            {
                "index": 0,
                "delta": {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "index": 0,
                            "id": "call",
                            "type": "function",
                            "function": {"name": "final_result", "arguments": OK.model_dump_json()},
                        }
                    ],
                },
                "finish_reason": None,
            }
        ],
    },
    {
        "id": "reply",
        "object": "chat.completion.chunk",
        "created": 0,
        "model": "deployed",
        "choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
    },
)
CHAT_STREAM = (
    "".join(f"data: {json.dumps(chunk)}\n\n" for chunk in CHUNKS) + "data: [DONE]\n\n"
).encode()


def served_by(monkeypatch: pytest.MonkeyPatch, served: Endpoint) -> AgentConfig:
    """The deployment names an OpenAI-compatible endpoint as the library documents it: the
    model under the library's `openai-chat` provider, and the endpoint under that provider's
    own variables."""
    monkeypatch.setenv(MODEL, "openai-chat:deployed")
    monkeypatch.setenv("OPENAI_BASE_URL", f"{served.url}/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    return AgentConfig()  # pyright: ignore[reportCallIssue]


def answering(provider: AgentProvider) -> AnswerInterpreter:
    """The answering of the coin toss, constructed as the composition root constructs it."""
    return AnswerInterpreter(prompt=COIN, provider=provider)


def acquisitions(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Each completed acquisition of a configured endpoint model, and each release of one."""
    seen: list[str] = []
    enter, leave = OpenAIChatModel.__aenter__, OpenAIChatModel.__aexit__

    async def acquired(model: OpenAIChatModel) -> OpenAIChatModel:
        entered = await enter(model)
        seen.append("acquired")
        return entered

    async def released(model: OpenAIChatModel, *exited: object) -> bool | None:
        seen.append("released")
        return await leave(model, *exited)  # pyright: ignore[reportArgumentType]

    monkeypatch.setattr(OpenAIChatModel, "__aenter__", acquired)
    monkeypatch.setattr(OpenAIChatModel, "__aexit__", released)
    return seen


class Held(TestModel):
    """A test's own model, which records whether anything but the test acquires it."""

    def __init__(self) -> None:
        super().__init__(custom_output_args=OK.model_dump_json(), call_tools=[])
        self.held: list[str] = []

    async def __aenter__(self) -> Held:
        self.held.append("acquired")
        return self

    async def __aexit__(self, *exited: object) -> None:
        self.held.append("released")


def watching(events: list[AgentStreamEvent], *, enough: int = 0):  # noqa: ANN201
    async def watch(ctx: RunContext[None], stream: AsyncIterable[AgentStreamEvent]) -> None:
        async for event in stream:
            events.append(event)
            if enough and len(events) >= enough:
                raise SeenEnoughError

    return watch


class SeenEnoughError(Exception):
    """The watcher has seen what it came for and stops the run."""


def conversed(
    served: Endpoint, cwd: Path, said: str, **environment: str
) -> subprocess.CompletedProcess[str]:
    """The agent's command line, run as a person runs it, on the endpoint the test serves."""
    return subprocess.run(  # noqa: S603
        (str(Path(sys.executable).parent / "tca-agent"),),
        input=f"{said}\n/exit\n",
        capture_output=True,
        text=True,
        check=False,
        cwd=cwd,
        env={
            **{k: v for k, v in os.environ.items() if not k.startswith(("TCA_", "OTEL_"))},
            MODEL: "openai-chat:deployed",
            KIND: "local",
            WORKSPACE: str(cwd),
            "OPENAI_BASE_URL": f"{served.url}/v1",
            "OPENAI_API_KEY": "test",
            "PYDANTIC_AI_NO_BANNER": "1",
            **environment,
        },
        timeout=60,
    )


def test_the_deployment_names_the_model_and_the_workspace_and_nothing_else(
    monkeypatch: pytest.MonkeyPatch, bare_environment: Path
) -> None:
    monkeypatch.setenv(MODEL, "openai-chat:@cf/zai-org/glm-5.3-flash")
    config = AgentConfig()  # pyright: ignore[reportCallIssue]
    assert config.agent == AgentProvider(
        model=ModelName("openai-chat:@cf/zai-org/glm-5.3-flash"),
        workspace=Workspace(
            Local(kind=LocalKind("local"), path=WorkspacePath(str(bare_environment)))
        ),
    )
    monkeypatch.setenv(KIND, "sandbox")
    assert AgentConfig().agent.workspace == Workspace(  # pyright: ignore[reportCallIssue]
        Sandboxed(kind=SandboxKind("sandbox"), path=WorkspacePath(str(bare_environment)))
    )
    monkeypatch.setenv(KIND, "container")
    with pytest.raises(ValidationError):
        AgentConfig()  # pyright: ignore[reportCallIssue]
    monkeypatch.setenv(KIND, "local")
    monkeypatch.setenv(MODEL, "")
    with pytest.raises(ValidationError):
        AgentConfig()  # pyright: ignore[reportCallIssue]
    monkeypatch.delenv(MODEL)
    with pytest.raises(ValidationError):
        AgentConfig()  # pyright: ignore[reportCallIssue]
    monkeypatch.setenv(MODEL, "test")
    monkeypatch.setenv(WORKSPACE, "")
    with pytest.raises(ValidationError):
        AgentConfig()  # pyright: ignore[reportCallIssue]
    monkeypatch.delenv(WORKSPACE)
    with pytest.raises(ValidationError):
        AgentConfig()  # pyright: ignore[reportCallIssue]
    monkeypatch.setenv(WORKSPACE, str(bare_environment))
    monkeypatch.setenv("TCA_AGENT__THINKING", "high")
    with pytest.raises(ValidationError):
        AgentConfig()  # pyright: ignore[reportCallIssue]


@pytest.mark.usefixtures("bare_environment")
def test_a_deployment_configures_the_agent_from_its_dotenv_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / ".env").write_text(
        "TCA_AGENT__MODEL=test\n"
        "REGISTRAR__URL=https://registrar.example\n"
        "ANTHROPIC_API_KEY=another-systems-key\n"
    )
    assert AgentConfig().agent.model == ModelName("test")  # pyright: ignore[reportCallIssue]
    monkeypatch.setenv(MODEL, "anthropic:claude-opus-5-5")
    assert AgentConfig().agent.model == ModelName("anthropic:claude-opus-5-5")  # pyright: ignore[reportCallIssue]
    monkeypatch.delenv(MODEL)
    (tmp_path / ".env").write_text("TCA_AGENT__MODEL=\n")
    with pytest.raises(ValidationError):
        AgentConfig()  # pyright: ignore[reportCallIssue]
    with pytest.raises(ValidationError):
        AgentConfig(
            agent=AgentProvider(
                model=ModelName("test"),
                workspace=Workspace(
                    Local(kind=LocalKind("local"), path=WorkspacePath(str(tmp_path)))
                ),
            ),
            agnet=None,  # pyright: ignore[reportCallIssue]
        )


@pytest.mark.usefixtures("bare_environment")
def test_a_model_the_library_cannot_build_is_refused_in_its_words(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(MODEL, "anthropic:claude-opus-5-5")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(UserError, match="ANTHROPIC_API_KEY"):
        run_sync(AgentConfig(), COIN)  # pyright: ignore[reportCallIssue]
    monkeypatch.setenv(MODEL, "nonsense:x")
    with pytest.raises(UserError, match="Unknown model"):
        run_sync(AgentConfig(), COIN)  # pyright: ignore[reportCallIssue]


@pytest.mark.usefixtures("bare_environment")
def test_the_library_constructs_the_answer_from_the_instructed_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = scripted(
        monkeypatch, TestModel(custom_output_args=OK.model_dump_json(), call_tools=[])
    )
    with capture_run_messages() as messages:
        answer = run_sync(config, COIN)
    assert isinstance(answer, Answer)
    assert answer == OK
    request = messages[0]
    assert isinstance(request, ModelRequest)
    assert request.instructions is not None
    assert request.instructions.startswith(AgentName.TCA_AGENT.prompt.read_text())
    assert not request.instructions.startswith("---")


@pytest.mark.usefixtures("bare_environment")
def test_an_answer_the_model_cannot_form_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    def empty(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        return ModelResponse(parts=[ToolCallPart(tool_name="final_result", args={"text": ""})])

    config = scripted(monkeypatch, FunctionModel(empty))
    with pytest.raises(UnexpectedModelBehavior):
        run_sync(config, COIN)


@pytest.mark.usefixtures("bare_environment")
def test_the_readme_examples_run(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    examples = [block.split("```", 1)[0] for block in README.read_text().split("```python\n")[1:]]
    with Endpoint(CHAT_COMPLETION, "application/json") as served:
        served.streamed = CHAT_STREAM
        served_by(monkeypatch, served)
        for example in examples:
            exec(example, {})  # noqa: S102
    assert capsys.readouterr().out.splitlines() == ["ok"]
    with pytest.raises(ValidationError):
        Prompt(text=PromptText(""))


@pytest.mark.usefixtures("bare_environment")
def test_a_cancelled_token_stops_the_run_and_stays_cancelled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token = CancellationToken()
    calls: list[int] = []

    def model(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        calls.append(len(messages))
        token.cancel()
        return ModelResponse(parts=[ToolCallPart(tool_name="list_directory", args={})])

    config = scripted(monkeypatch, FunctionModel(model))
    with pytest.raises(RunCancelled):
        asyncio.run(run(config, COIN, cancellation_token=token))
    assert len(calls) == 1
    assert token.cancelled
    with pytest.raises(RunCancelled):
        run_sync(config, COIN, cancellation_token=token)
    assert len(calls) == 1


def test_the_agent_loads_the_skills_its_workspace_holds(
    monkeypatch: pytest.MonkeyPatch, bare_environment: Path
) -> None:
    own = bare_environment / ".agents/skills/release-notes"
    own.mkdir()
    (own / "SKILL.md").write_text(
        "---\nname: release-notes\ndescription: The workspace's own.\n---\nWrite them short.\n"
    )
    calls = (
        ToolCallPart(tool_name="load_capability", args={"id": "release-notes"}),
        ToolCallPart(tool_name="load_capability", args={"id": "python-dev-tca"}),
        ToolCallPart(
            tool_name="read_file", args={"path": ".agents/skills/python-dev-tca/provider.md"}
        ),
    )
    seen: list[ToolReturnPart | RetryPromptPart] = []

    def model(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        seen[:] = returns(messages)
        if len(seen) == len(calls):
            return answered("ok")
        return ModelResponse(parts=[calls[len(seen)]])

    assert run_sync(scripted(monkeypatch, FunctionModel(model)), COIN) == OK
    theirs, tca, page = seen
    assert "Write them short." in str(theirs.content)
    assert "python-dev-tca" in str(tca.content)
    assert (SKILLS / "python-dev-tca" / "provider.md").read_text().splitlines()[2] in str(
        page.content
    )


def test_the_agent_reads_edits_and_writes_the_files_in_its_workspace(
    monkeypatch: pytest.MonkeyPatch, bare_environment: Path
) -> None:
    (bare_environment / "checkout.py").write_text("price = 1\n")
    calls = (
        ToolCallPart(tool_name="read_file", args={"path": "checkout.py"}),
        ToolCallPart(
            tool_name="edit_file",
            args={"path": "checkout.py", "old_text": "price = 1", "new_text": "price = 2"},
        ),
        ToolCallPart(tool_name="write_file", args={"path": "order.py", "content": "order = 1\n"}),
    )
    seen: list[ToolReturnPart | RetryPromptPart] = []

    def model(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        seen[:] = returns(messages)
        if len(seen) == len(calls):
            return answered("ok")
        return ModelResponse(parts=[calls[len(seen)]])

    assert run_sync(scripted(monkeypatch, FunctionModel(model)), COIN) == OK
    read, edited, written = seen
    assert "price = 1" in str(read.content)
    assert isinstance(edited, ToolReturnPart)
    assert isinstance(written, ToolReturnPart)
    assert (bare_environment / "checkout.py").read_text() == "price = 2\n"
    assert (bare_environment / "order.py").read_text() == "order = 1\n"
    assert not Path("checkout.py").exists()
    assert not Path("order.py").exists()


def test_the_agent_runs_the_check_its_workspace_declares(
    monkeypatch: pytest.MonkeyPatch, bare_environment: Path
) -> None:
    checked(bare_environment, "echo 'coin.py: a step'; echo 'and a warning' >&2; exit 3")
    calls = (
        ToolCallPart(tool_name="run_command", args={"command": "./check"}),
        ToolCallPart(tool_name="run_command", args={"command": "./check"}),
    )
    seen: list[ToolReturnPart | RetryPromptPart] = []

    def model(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        seen[:] = returns(messages)
        if len(seen) == 1:
            checked(bare_environment, "echo 'All checks passed!'; exit 0")
        if len(seen) == len(calls):
            return answered("ok")
        return ModelResponse(parts=[calls[len(seen)]])

    assert run_sync(scripted(monkeypatch, FunctionModel(model)), COIN) == OK
    failed, clean = seen
    assert isinstance(failed, ToolReturnPart)
    assert "coin.py: a step" in str(failed.content)
    assert "and a warning" in str(failed.content)
    assert "exit code: 3" in str(failed.content)
    assert isinstance(clean, ToolReturnPart)
    assert "All checks passed!" in str(clean.content)
    assert "exit code" not in str(clean.content)


@pytest.mark.skipif(shutil.which("bwrap") is None, reason="the library's sandbox needs bwrap")
def test_a_sandboxed_workspace_keeps_the_agent_s_commands_and_its_check_inside(
    monkeypatch: pytest.MonkeyPatch, bare_environment: Path
) -> None:
    monkeypatch.setenv(KIND, "sandbox")
    home = Path.home()
    for escape in ("escaped-by-shell", "escaped-by-check"):
        (home / escape).unlink(missing_ok=True)
    checked(bare_environment, "touch ~/escaped-by-check")
    calls = (
        ToolCallPart(tool_name="run_command", args={"command": "touch ~/escaped-by-shell"}),
        ToolCallPart(tool_name="run_command", args={"command": "touch kept"}),
        ToolCallPart(tool_name="run_command", args={"command": "./check"}),
    )
    seen: list[ToolReturnPart | RetryPromptPart] = []

    def model(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        seen[:] = returns(messages)
        if len(seen) == len(calls):
            return answered("ok")
        return ModelResponse(parts=[calls[len(seen)]])

    assert run_sync(scripted(monkeypatch, FunctionModel(model)), COIN) == OK
    escaped, kept, checked_inside = seen
    assert "exit code" in str(escaped.content)
    assert isinstance(kept, ToolReturnPart)
    assert isinstance(checked_inside, ToolReturnPart)
    assert "Read-only file system" in str(checked_inside.content)
    assert "exit code" in str(checked_inside.content)
    assert (bare_environment / "kept").exists()
    assert not (home / "escaped-by-shell").exists()
    assert not (home / "escaped-by-check").exists()


@pytest.mark.usefixtures("bare_environment")
def test_a_workspace_that_does_not_exist_is_refused_in_the_library_s_words(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv(WORKSPACE, str(tmp_path / "nowhere"))
    with pytest.raises(WorkspaceUnavailableError, match="nowhere"):
        run_sync(scripted(monkeypatch, TestModel(custom_output_args=OK.model_dump_json())), COIN)


@pytest.mark.usefixtures("bare_environment")
def test_a_caller_hands_one_run_the_tools_it_may_call(monkeypatch: pytest.MonkeyPatch) -> None:
    def remember(word: str) -> str:
        """Keep one word for the caller."""
        return f"kept {word}"

    seen: list[ToolReturnPart | RetryPromptPart] = []

    def model(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        seen[:] = returns(messages)
        if seen:
            return answered(str(seen[0].content))
        return ModelResponse(
            parts=[ToolCallPart(tool_name="remember", args={"word": "pomegranate"})]
        )

    config = scripted(monkeypatch, FunctionModel(model))
    handed = run_sync(config, COIN, toolsets=[FunctionToolset([remember])])
    assert handed == Answer(text=AnswerText("kept pomegranate"))
    assert isinstance(seen[0], ToolReturnPart)
    withheld = run_sync(config, COIN)
    assert isinstance(seen[0], RetryPromptPart)
    assert "remember" in withheld.text.root


@pytest.mark.usefixtures("bare_environment")
def test_runs_share_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    config = scripted(
        monkeypatch, TestModel(custom_output_args=OK.model_dump_json(), call_tools=[])
    )
    first, second = Prompt(text=PromptText("First.")), Prompt(text=PromptText("Second."))
    assert config.agent.client is not config.agent.client
    run_sync(config, first)
    with capture_run_messages() as messages:
        run_sync(config, second)
    prompts = [
        part.content
        for message in messages
        if isinstance(message, ModelRequest)
        for part in message.parts
        if isinstance(part, UserPromptPart)
    ]
    assert prompts == ["Second."]


@pytest.mark.usefixtures("bare_environment")
def test_a_configured_model_is_acquired_for_each_crossing_and_released(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lifecycle = acquisitions(monkeypatch)
    with Endpoint(CHAT_COMPLETION, "application/json") as served:
        config = served_by(monkeypatch, served)
        assert run_sync(config, COIN) == OK
        assert run_sync(config, COIN) == OK
    assert served.paths == ["/v1/chat/completions"] * 2
    assert lifecycle == ["acquired", "released", "acquired", "released"]


@pytest.mark.usefixtures("bare_environment")
def test_a_model_the_library_builds_is_acquired_for_each_crossing_and_released(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    held = Held()
    config = scripted(monkeypatch, held)
    assert run_sync(config, COIN) == OK
    assert asyncio.run(run(config, COIN)) == OK
    assert held.held == ["acquired", "released", "acquired", "released"]


@pytest.mark.usefixtures("bare_environment")
def test_a_caller_sees_a_run_s_whole_result(monkeypatch: pytest.MonkeyPatch) -> None:
    config = scripted(monkeypatch, Held())
    result = asyncio.run(answering(config.agent).interpret())
    assert isinstance(result, AgentRunResult)
    assert result.output == OK
    assert [type(message) for message in result.all_messages()] == [
        ModelRequest,
        ModelResponse,
        ModelRequest,
    ]
    assert result.usage.requests == 1
    assert result.run_id


@pytest.mark.usefixtures("bare_environment")
def test_a_caller_watches_each_tool_call_as_it_happens(monkeypatch: pytest.MonkeyPatch) -> None:
    events: list[AgentStreamEvent] = []
    model = TestModel(custom_output_args=OK.model_dump_json(), call_tools=["list_directory"])
    config = scripted(monkeypatch, model)
    result = asyncio.run(answering(config.agent).interpret(event_stream_handler=watching(events)))
    called = [event for event in events if isinstance(event, FunctionToolCallEvent)]
    returned = [event for event in events if isinstance(event, FunctionToolResultEvent)]
    assert [event.part.tool_name for event in called] == ["list_directory"]
    assert [event.part.tool_name for event in returned] == ["list_directory"]
    assert result.output == OK


@pytest.mark.usefixtures("bare_environment")
@pytest.mark.parametrize("ending", ["completes", "watcher stops", "cancelled", "fails"])
def test_a_watched_run_releases_its_configured_model_however_it_ends(
    monkeypatch: pytest.MonkeyPatch, ending: str
) -> None:
    lifecycle = acquisitions(monkeypatch)
    token = CancellationToken()
    events: list[AgentStreamEvent] = []
    status = 503 if ending == "fails" else 200
    with Endpoint(CHAT_COMPLETION, "application/json", status=status) as served:
        served.streamed = CHAT_STREAM
        answered_by = answering(served_by(monkeypatch, served).agent)
        handler = watching(events, enough=1 if ending == "watcher stops" else 0)
        if ending == "cancelled":
            token.cancel()
        refused = {"watcher stops": SeenEnoughError, "cancelled": RunCancelled}.get(
            ending, ModelHTTPError
        )
        if ending == "completes":
            assert asyncio.run(answered_by.interpret(event_stream_handler=handler)).output == OK
            assert events
        else:
            with pytest.raises(refused):
                asyncio.run(
                    answered_by.interpret(event_stream_handler=handler, cancellation_token=token)
                )
    assert lifecycle == ["acquired", "released"]


def test_a_person_holds_a_conversation_with_the_agent_at_a_terminal(tmp_path: Path) -> None:
    shutil.copytree(SKILLS, tmp_path / ".agents" / "skills")
    with Endpoint(CHAT_STREAM, "text/event-stream") as served:
        chat = conversed(served, tmp_path, "Model a coin toss.")
    assert chat.returncode == 0, chat.stderr
    assert "ok" in chat.stdout
    assert "Model a coin toss." in json.dumps(json.loads(served.raw[0])["messages"])


def test_an_operator_has_the_agent_s_spans_exported_by_naming_a_collector(tmp_path: Path) -> None:
    shutil.copytree(SKILLS, tmp_path / ".agents" / "skills")
    with (
        Endpoint(CHAT_STREAM, "text/event-stream") as served,
        Endpoint(b"", "application/x-protobuf") as collector,
    ):
        unnamed = conversed(served, tmp_path, "Model a coin toss.")
        assert collector.paths == []
        named = conversed(
            served, tmp_path, "Model a coin toss.", OTEL_EXPORTER_OTLP_ENDPOINT=collector.url
        )
    assert unnamed.returncode == named.returncode == 0, named.stderr
    assert "/v1/traces" in collector.paths
    exported = b"".join(collector.raw)
    assert b"invoke_agent tca-agent" in exported
    assert b"Model a coin toss." in exported


def test_the_configured_provider_answers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    shutil.copytree(SKILLS, tmp_path / ".agents" / "skills")
    monkeypatch.setenv(KIND, "local")
    monkeypatch.setenv(WORKSPACE, str(tmp_path))
    config = AgentConfig()  # pyright: ignore[reportCallIssue]
    answer = run_sync(config, Prompt(text=PromptText("Reply with one word.")))
    assert isinstance(answer, Answer)
    assert answer.text.root


@pytest.mark.asyncio
async def test_the_configured_provider_answers_async(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    shutil.copytree(SKILLS, tmp_path / ".agents" / "skills")
    monkeypatch.setenv(KIND, "local")
    monkeypatch.setenv(WORKSPACE, str(tmp_path))
    config = AgentConfig()  # pyright: ignore[reportCallIssue]
    answer = await run(config, Prompt(text=PromptText("Reply with one word.")))
    assert isinstance(answer, Answer)
    assert answer.text.root


def test_the_configured_provider_works_in_its_workspace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    shutil.copytree(SKILLS, tmp_path / ".agents" / "skills")
    (tmp_path / "NOTE.md").write_text("pomegranate\n")
    monkeypatch.setenv(KIND, "local")
    monkeypatch.setenv(WORKSPACE, str(tmp_path))
    asked = Prompt(
        text=PromptText(
            "Read the file NOTE.md in your workspace, write the one word it contains to a "
            "new file REPLY.md beside it, and reply with only that word."
        )
    )
    answer = run_sync(AgentConfig(), asked)  # pyright: ignore[reportCallIssue]
    assert "pomegranate" in answer.text.root.lower()
    assert "pomegranate" in (tmp_path / "REPLY.md").read_text().lower()
