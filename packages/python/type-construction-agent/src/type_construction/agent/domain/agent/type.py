from typing import Literal

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


class Success(RootModel[Literal[0]]):
    """The exit with which a check passes."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )


class Failure(RootModel[int]):
    """The exit with which a check fails."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(ge=1)


class Output(RootModel[str]):
    """What a check said on one of its streams, in its own words; nothing is a valid saying."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
