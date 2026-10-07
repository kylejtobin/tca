import asyncio
from pathlib import Path

from pydantic_ai import Agent, TemplateStr
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness import FileSystem, Skills

from type_construction.agent.config import AgentConfig
from type_construction.agent.domain.agent.prompt import Answer, Prompt
from type_construction.agent.domain.agent.type import SkillLibrary, SkillLocation
from type_construction.agent.domain.agent.value import TcaAgentValues
from type_construction.agent.integration.agent_skills.model import SkillDocument
from type_construction.agent.integration.model_provider.interpreter import RunInterpreter
from type_construction.agent.integration.model_provider.model import Reply
from type_construction.agent.parser.skill import read

__all__ = ("Answer", "Prompt", "run", "run_sync")


async def run(prompt: Prompt) -> Answer:
    return await RunInterpreter(
        action=prompt.run,
        client=Agent(
            AgentConfig().provider.client,  # pyright: ignore[reportCallIssue]
            deps_type=TcaAgentValues,
            output_type=Reply,
            instructions=TemplateStr(
                SkillDocument.model_validate_json(read(SkillLocation.TCA_AGENT)).body.root
            ),
            capabilities=(
                LocalWorkspace(Path(__file__).parent, read_only=True),
                Skills(SkillLibrary.SKILLS),
                FileSystem(read_only=True),
            ),
        ),
    ).interpret()


def run_sync(prompt: Prompt) -> Answer:
    return asyncio.run(run(prompt))
