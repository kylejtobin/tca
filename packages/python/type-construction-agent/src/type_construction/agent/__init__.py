import asyncio
from collections.abc import Sequence

from pydantic_ai import AgentRunResult, CancellationToken
from pydantic_ai.toolsets import AbstractToolset
from pydantic_ai.usage import RunUsage

from type_construction.agent.config import AgentConfig
from type_construction.agent.domain.agent.check import Check, CheckResult, Clean, Failed
from type_construction.agent.domain.agent.prompt import Answer, FollowUp, Opening, Reply
from type_construction.agent.domain.agent.type import (
    AnswerText,
    Failure,
    Output,
    PromptText,
    RunId,
    Success,
)
from type_construction.agent.integration.pydantic_ai.answered import AnsweredRun
from type_construction.agent.integration.pydantic_ai.interpreter import (
    ChatInterpreter,
    CheckInterpreter,
    FollowUpInterpreter,
    OpeningInterpreter,
)
from type_construction.agent.integration.pydantic_ai.model import (
    AgentName,
    AgentTool,
    CheckReply,
    ContextShare,
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
    HistoryStore,
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
    "AnswerText",
    "AnsweredRun",
    "ChatInterpreter",
    "Check",
    "CheckInterpreter",
    "CheckReply",
    "CheckResult",
    "Clean",
    "ContextShare",
    "DatabasePath",
    "Failed",
    "Failure",
    "FollowUp",
    "FollowUpInterpreter",
    "History",
    "HistoryStore",
    "Local",
    "LocalKind",
    "LocalShell",
    "ModelName",
    "Opening",
    "OpeningInterpreter",
    "Output",
    "PromptText",
    "Reply",
    "RunId",
    "SandboxKind",
    "Sandboxed",
    "SandboxedShell",
    "Success",
    "Workspace",
    "WorkspacePath",
    "WorkspaceResource",
    "WorkspaceShell",
    "answer",
    "answer_follow_up",
    "chat",
    "follow_up",
    "follow_up_sync",
    "run",
    "run_sync",
)


async def answer(
    config: AgentConfig,
    prompt: Opening,
    *,
    usage: RunUsage | None = None,
    cancellation_token: CancellationToken | None = None,
    toolsets: Sequence[AbstractToolset[None]] | None = None,
) -> AgentRunResult[Answer]:
    return await OpeningInterpreter(action=prompt, provider=config.agent).interpret(
        usage=usage, cancellation_token=cancellation_token, toolsets=toolsets
    )


async def run(
    config: AgentConfig,
    prompt: Opening,
    *,
    usage: RunUsage | None = None,
    cancellation_token: CancellationToken | None = None,
    toolsets: Sequence[AbstractToolset[None]] | None = None,
) -> Reply:
    return AnsweredRun.model_validate(
        await answer(
            config, prompt, usage=usage, cancellation_token=cancellation_token, toolsets=toolsets
        ),
        from_attributes=True,
    ).reply


def run_sync(
    config: AgentConfig,
    prompt: Opening,
    *,
    usage: RunUsage | None = None,
    cancellation_token: CancellationToken | None = None,
    toolsets: Sequence[AbstractToolset[None]] | None = None,
) -> Reply:
    return asyncio.run(
        run(config, prompt, usage=usage, cancellation_token=cancellation_token, toolsets=toolsets)
    )


async def answer_follow_up(
    config: AgentConfig,
    prompt: FollowUp,
    *,
    usage: RunUsage | None = None,
    cancellation_token: CancellationToken | None = None,
    toolsets: Sequence[AbstractToolset[None]] | None = None,
) -> AgentRunResult[Answer]:
    return await FollowUpInterpreter(action=prompt, provider=config.agent).interpret(
        usage=usage, cancellation_token=cancellation_token, toolsets=toolsets
    )


async def follow_up(
    config: AgentConfig,
    prompt: FollowUp,
    *,
    usage: RunUsage | None = None,
    cancellation_token: CancellationToken | None = None,
    toolsets: Sequence[AbstractToolset[None]] | None = None,
) -> Reply:
    return AnsweredRun.model_validate(
        await answer_follow_up(
            config, prompt, usage=usage, cancellation_token=cancellation_token, toolsets=toolsets
        ),
        from_attributes=True,
    ).reply


def follow_up_sync(
    config: AgentConfig,
    prompt: FollowUp,
    *,
    usage: RunUsage | None = None,
    cancellation_token: CancellationToken | None = None,
    toolsets: Sequence[AbstractToolset[None]] | None = None,
) -> Reply:
    return asyncio.run(
        follow_up(
            config, prompt, usage=usage, cancellation_token=cancellation_token, toolsets=toolsets
        )
    )


def chat(config: AgentConfig) -> None:
    return asyncio.run(ChatInterpreter(provider=config.agent).interpret())
