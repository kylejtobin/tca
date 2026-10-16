import asyncio
from collections.abc import Sequence

from pydantic_ai import AgentRunResult, CancellationToken
from pydantic_ai.toolsets import AbstractToolset
from pydantic_ai.usage import RunUsage

from type_construction.agent.config import AgentConfig
from type_construction.agent.domain.agent.check import Check, CheckResult, Clean, Failed
from type_construction.agent.domain.agent.prompt import Answer, Prompt
from type_construction.agent.domain.agent.type import (
    AnswerText,
    Failure,
    Output,
    PromptText,
    Success,
)
from type_construction.agent.integration.pydantic_ai.interpreter import (
    AnswerInterpreter,
    ChatInterpreter,
    CheckInterpreter,
)
from type_construction.agent.integration.pydantic_ai.model import (
    AgentName,
    AgentTool,
    CheckReply,
    DatabasePath,
    LocalKind,
    ModelName,
    SandboxKind,
    WorkspacePath,
    WorkspaceResource,
)
from type_construction.agent.integration.pydantic_ai.provider import (
    AgentProvider,
    History,
    Local,
    LocalShell,
    Sandboxed,
    SandboxedShell,
    Workspace,
    WorkspaceShell,
)

__all__ = (
    "AgentConfig",
    "AgentName",
    "AgentProvider",
    "AgentTool",
    "Answer",
    "AnswerInterpreter",
    "AnswerText",
    "ChatInterpreter",
    "Check",
    "CheckInterpreter",
    "CheckReply",
    "CheckResult",
    "Clean",
    "DatabasePath",
    "Failed",
    "Failure",
    "History",
    "Local",
    "LocalKind",
    "LocalShell",
    "ModelName",
    "Output",
    "Prompt",
    "PromptText",
    "SandboxKind",
    "Sandboxed",
    "SandboxedShell",
    "Success",
    "Workspace",
    "WorkspacePath",
    "WorkspaceResource",
    "WorkspaceShell",
    "answer",
    "chat",
    "run",
    "run_sync",
)


async def answer(
    config: AgentConfig,
    prompt: Prompt,
    *,
    usage: RunUsage | None = None,
    cancellation_token: CancellationToken | None = None,
    toolsets: Sequence[AbstractToolset[None]] | None = None,
) -> AgentRunResult[Answer]:
    return await AnswerInterpreter(prompt=prompt, provider=config.agent).interpret(
        usage=usage, cancellation_token=cancellation_token, toolsets=toolsets
    )


async def run(
    config: AgentConfig,
    prompt: Prompt,
    *,
    usage: RunUsage | None = None,
    cancellation_token: CancellationToken | None = None,
    toolsets: Sequence[AbstractToolset[None]] | None = None,
) -> Answer:
    return (
        await answer(
            config, prompt, usage=usage, cancellation_token=cancellation_token, toolsets=toolsets
        )
    ).output


def run_sync(
    config: AgentConfig,
    prompt: Prompt,
    *,
    usage: RunUsage | None = None,
    cancellation_token: CancellationToken | None = None,
    toolsets: Sequence[AbstractToolset[None]] | None = None,
) -> Answer:
    return asyncio.run(
        run(config, prompt, usage=usage, cancellation_token=cancellation_token, toolsets=toolsets)
    )


def chat(config: AgentConfig) -> None:
    return asyncio.run(ChatInterpreter(provider=config.agent).interpret())
