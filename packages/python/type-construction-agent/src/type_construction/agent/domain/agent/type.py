from enum import StrEnum

from pydantic import ConfigDict, Field, RootModel


class PromptText(RootModel[str]):
    """The words a person gives the agent."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class AnswerText(RootModel[str]):
    """The words the agent gives back for a prompt."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class PromptLocation(StrEnum):
    """Where each agent's prompt is kept, within the package's prompts."""

    TCA_AGENT = "agents/tca-agent.md"
