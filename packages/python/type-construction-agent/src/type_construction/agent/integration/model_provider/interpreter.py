from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai.agent import AbstractAgent

from type_construction.agent.domain.agent.prompt import Answer, Run
from type_construction.agent.domain.agent.value import TcaAgentValues
from type_construction.agent.integration.model_provider.model import Reply


class RunInterpreter(BaseModel):
    """The one place a prompt is run on the model the deployment names."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        arbitrary_types_allowed=True,
    )
    action: Run
    client: AbstractAgent[TcaAgentValues, Reply] = Field(exclude=True, repr=False)

    async def interpret(self) -> Answer:
        return Answer(
            prompt=self.action.prompt,
            text=(
                await self.client.run(
                    self.action.prompt.text.root, deps=TcaAgentValues.model_validate(self.action)
                )
            ).output.text,
        )
