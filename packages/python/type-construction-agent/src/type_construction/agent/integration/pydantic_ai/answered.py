from pydantic import BaseModel, ConfigDict, Field

from type_construction.agent.domain.agent.prompt import Answer, Reply
from type_construction.agent.domain.agent.type import RunId


class AnsweredRun(BaseModel):
    """A run the library answered, read from its result in the library's terms: the answer it
    constructed as the run's output, the domain's own type validated as the agent's contract,
    beside the identity the library gave the run and records it under. Its derivation is the
    domain's reply."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    answer: Answer = Field(alias="output")
    run: RunId = Field(alias="run_id")

    @property
    def reply(self) -> Reply:
        return Reply.model_validate(self, from_attributes=True)
