from pydantic import BaseModel, ConfigDict

from type_construction.agent.domain.agent.type import AnswerText, PromptText, RunId


class Opening(BaseModel):
    """A person's request to the agent that opens an exchange: words with nothing said before
    them. Its only purpose is its effect, so it is its own action."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    text: PromptText


class FollowUp(BaseModel):
    """A person's request to the agent that continues an exchange: words after a reply, named by
    the run that produced it, so the agent sees everything said before them. Its own action."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    text: PromptText
    after: RunId


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


class Reply(BaseModel):
    """The agent's reply to a prompt: its answer, and the identity of the run that produced it,
    after which a follow-up continues the exchange."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    answer: Answer
    run: RunId
