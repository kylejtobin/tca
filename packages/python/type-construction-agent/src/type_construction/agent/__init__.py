import asyncio

from type_construction.agent.config import AgentConfig
from type_construction.agent.domain.agent.prompt import Answer, Prompt
from type_construction.agent.integration.model_provider.interpreter import AnswerInterpreter

__all__ = ("AgentConfig", "Answer", "Prompt", "run", "run_sync")


async def run(config: AgentConfig, prompt: Prompt) -> Answer:
    return await AnswerInterpreter(prompt=prompt, provider=config.agent).interpret()


def run_sync(config: AgentConfig, prompt: Prompt) -> Answer:
    return asyncio.run(run(config, prompt))
