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
