from collections.abc import Sequence
from types import NoneType

from pydantic import BaseModel, ConfigDict
from pydantic_ai import Agent, AgentRunResult, CancellationToken, Tool
from pydantic_ai.agent import EventStreamHandler
from pydantic_ai.toolsets import AbstractToolset
from pydantic_ai.usage import RunUsage
from pydantic_ai_harness.step_persistence import continue_run

from type_construction.agent.domain.agent.check import Check, CheckResult
from type_construction.agent.domain.agent.exchange import Answer, FollowUp, Opening
from type_construction.agent.integration.pydantic_ai.model import (
    AgentName,
    AgentTool,
    CheckReply,
    WorkspaceResource,
)
from type_construction.agent.integration.pydantic_ai.provider import AgentProvider, WorkspaceShell


class CheckInterpreter(BaseModel):
    """The one place the work is checked: the script the workspace declares at its root is run in
    the workspace's shell, inside its boundary, and what comes back is read once into what the
    check concluded. The agent calls it as its `check` tool, so the model reads a type."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    action: Check
    provider: WorkspaceShell

    async def interpret(self) -> CheckResult:
        """Run the workspace's check on the work: clean, or failed, with everything it said."""
        return CheckResult.model_validate(
            CheckReply.model_validate(
                await self.provider.client.run((WorkspaceResource.CHECK,)), from_attributes=True
            ),
            from_attributes=True,
        )


class OpeningInterpreter(BaseModel):
    """The one place an opening is answered: the agent is composed for the crossing from the
    model the deployment names, the answer's type, the capability its provider derives and the
    check interpreter as its tool, acquired with its model, run on the opening once in its
    workspace with nothing before it, and released on every path; what it returns is the
    library's own result of the run, whose output is the answer the library constructed, with
    every message, the usage and the run's identity beside it. The caller may hand `interpret`
    the library's own execution resources, unchanged: a usage the run accumulates into; a token
    by which the caller may cancel the run; the toolsets this one run may call beside the
    agent's own; and a handler the library streams the run's events to as they happen, while
    the agent is still held. A handler that fails stops the run, and the agent is released all
    the same."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    action: Opening
    provider: AgentProvider

    async def interpret(
        self,
        *,
        usage: RunUsage | None = None,
        cancellation_token: CancellationToken | None = None,
        toolsets: Sequence[AbstractToolset[None]] | None = None,
        event_stream_handler: EventStreamHandler[None] | None = None,
    ) -> AgentRunResult[Answer]:
        async with Agent(
            self.provider.model.root,
            name=AgentName.TCA_AGENT,
            deps_type=NoneType,
            output_type=Answer,
            tools=(
                Tool(
                    CheckInterpreter(
                        action=Check(), provider=self.provider.workspace.shell
                    ).interpret,
                    name=AgentTool.CHECK,
                ),
            ),
            capabilities=(self.provider.client,),
        ) as agent:
            return await agent.run(
                self.action.text.root,
                usage=usage,
                cancellation_token=cancellation_token,
                toolsets=toolsets,
                event_stream_handler=event_stream_handler,
            )


class FollowUpInterpreter(BaseModel):
    """The one place a follow-up is answered: the same agent, composed the same way, run on the
    follow-up after the messages the library recorded for the run it follows, read back by
    the library's own `continue_run` from the history reached as a store; the run inherits
    that conversation's id, and the library records it as its next run. A run the history
    does not hold is refused with the library's own `LookupError`. What it returns and what
    the caller may hand it are the opening's."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    action: FollowUp
    provider: AgentProvider

    async def interpret(
        self,
        *,
        usage: RunUsage | None = None,
        cancellation_token: CancellationToken | None = None,
        toolsets: Sequence[AbstractToolset[None]] | None = None,
        event_stream_handler: EventStreamHandler[None] | None = None,
    ) -> AgentRunResult[Answer]:
        async with Agent(
            self.provider.model.root,
            name=AgentName.TCA_AGENT,
            deps_type=NoneType,
            output_type=Answer,
            tools=(
                Tool(
                    CheckInterpreter(
                        action=Check(), provider=self.provider.workspace.shell
                    ).interpret,
                    name=AgentTool.CHECK,
                ),
            ),
            capabilities=(self.provider.client,),
        ) as agent:
            return await agent.run(
                self.action.text.root,
                message_history=await continue_run(
                    self.provider.history.store.client, run_id=self.action.after.root
                ),
                usage=usage,
                cancellation_token=cancellation_token,
                toolsets=toolsets,
                event_stream_handler=event_stream_handler,
            )


class ChatInterpreter(BaseModel):
    """The one place a person holds a conversation with the agent at a terminal, in the library's
    own command line: the same agent, composed the same way, acquired for the whole conversation,
    which the library holds for as long as the terminal is open, each prompt a run in its
    workspace, and released when the terminal closes. A request whose only purpose is its effect
    is its own action."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    provider: AgentProvider

    async def interpret(self) -> None:
        async with Agent(
            self.provider.model.root,
            name=AgentName.TCA_AGENT,
            deps_type=NoneType,
            output_type=Answer,
            tools=(
                Tool(
                    CheckInterpreter(
                        action=Check(), provider=self.provider.workspace.shell
                    ).interpret,
                    name=AgentTool.CHECK,
                ),
            ),
            capabilities=(self.provider.client,),
        ) as agent:
            return await agent.to_cli(prog_name=AgentName.TCA_AGENT)
