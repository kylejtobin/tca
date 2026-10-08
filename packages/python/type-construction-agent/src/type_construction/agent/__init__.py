import asyncio
from pathlib import Path

from pydantic_ai import Agent, TemplateStr
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness import FileSystem, Skills

from type_construction.agent.config import AgentConfig
from type_construction.agent.domain.agent.prompt import Answer, Prompt
from type_construction.agent.domain.agent.type import PromptLibrary, PromptLocation, SkillLibrary
from type_construction.agent.domain.agent.value import TcaAgentValues
from type_construction.agent.integration.model_provider.interpreter import RunInterpreter
from type_construction.agent.integration.model_provider.model import Reply

__all__ = ("Answer", "Prompt", "run", "run_sync")


async def run(prompt: Prompt) -> Answer:
    return await RunInterpreter(
        action=prompt.run,
        client=Agent(
            AgentConfig().provider.client,  # pyright: ignore[reportCallIssue]
            deps_type=TcaAgentValues,
            output_type=Reply,
            instructions=TemplateStr(
                (
                    Path(__file__).parent / PromptLibrary.PROMPTS / PromptLocation.TCA_AGENT
                ).read_text()
            ),
            capabilities=(
                LocalWorkspace(Path(__file__).parent / PromptLibrary.PROMPTS, read_only=True),
                Skills(SkillLibrary.SKILLS),
                FileSystem(tools=("read_file", "list_directory")),
            ),
        ),
    ).interpret()


def run_sync(prompt: Prompt) -> Answer:
    return asyncio.run(run(prompt))
