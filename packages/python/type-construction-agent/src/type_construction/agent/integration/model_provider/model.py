from pydantic import BaseModel, ConfigDict

from type_construction.agent.domain.agent.type import AnswerText


class Reply(BaseModel):
    """What the model provider sends back for a prompt: the agent's words."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    text: AnswerText
