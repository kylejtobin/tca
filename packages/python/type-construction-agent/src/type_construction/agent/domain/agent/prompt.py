from pydantic import BaseModel, ConfigDict

from type_construction.agent.domain.agent.type import AnswerText, PromptText


class Prompt(BaseModel):
    """A person's request to the agent, in words."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    text: PromptText

    @property
    def run(self) -> Run:
        return Run(prompt=self)


class Answer(BaseModel):
    """A prompt, with the words the agent gave back for it."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    prompt: Prompt
    text: AnswerText


class Run(BaseModel):
    """The intended run of the agent on a prompt."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    prompt: Prompt
