from pydantic import BaseModel, ConfigDict

from type_construction.agent.domain.agent.type import AnswerText, PromptText


class Prompt(BaseModel):
    """A person's request to the agent, in words: the intended asking of it."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    text: PromptText


class Answer(BaseModel):
    """The agent's answer to a prompt, in its words."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    text: AnswerText
