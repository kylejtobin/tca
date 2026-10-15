from enum import StrEnum
from pathlib import Path

from pydantic import ConfigDict, Field, RootModel


class AgentName(StrEnum):
    """The one name an agent goes by: to the library, in its spans, at the command line and in its
    telemetry; the packaged prompt it is instructed by is kept under it."""

    TCA_AGENT = "tca-agent"

    @property
    def prompt(self) -> Path:
        return (Path(__file__).parents[2] / "prompts" / "agents" / self.value).with_suffix(".md")


class ModelName(RootModel[str]):
    """A model as pydantic_ai names it, its provider first: `anthropic:claude-opus-5-5`,
    `openai-chat:gpt-5`; `test` is the library's own offline model. That provider reads its own
    credentials and endpoint from the environment, under its own names. The library refuses a
    provider it does not know when the agent is built."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)
