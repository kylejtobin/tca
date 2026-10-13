from pydantic import BaseModel, ConfigDict

from type_construction.agent.domain.agent.prompt import Answer, Prompt
from type_construction.agent.integration.model_provider.provider import ModelProvider


class AnswerInterpreter(BaseModel):
    """The one place a prompt is answered: the model the deployment names is run on it once, and
    what it returns is the answer, constructed by the library."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    prompt: Prompt
    provider: ModelProvider

    async def interpret(self) -> Answer:
        return (
            await self.provider.client.run(
                self.prompt.text.root, usage_limits=self.provider.limits
            )
        ).output
