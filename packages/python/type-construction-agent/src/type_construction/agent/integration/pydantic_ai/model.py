from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import ConfigDict, Field, RootModel


class AgentName(StrEnum):
    """The one name an agent goes by: to the library, in its spans, at the command line and in its
    telemetry; the packaged prompt it is instructed by is kept under it."""

    TCA_AGENT = "tca-agent"

    @property
    def prompt(self) -> Path:
        return (Path(__file__).parents[2] / "prompts" / "agents" / self.value).with_suffix(".md")


class LocalKind(RootModel[Literal["local"]]):
    """The deployment's word for a workspace on this machine, which isolates nothing; a literal
    root, since the settings source decodes the environment's word under a union of providers
    as text."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )


class SandboxKind(RootModel[Literal["sandbox"]]):
    """The deployment's word for a workspace on this machine whose commands run in the library's
    bubblewrap sandbox: the host read-only, no network, writes only inside the directory."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )


class WorkspacePath(RootModel[str]):
    """The directory the agent models in, as the library's workspace takes it: where it reads,
    writes, runs the check the directory declares as `check` at its root, and loads its skills
    from `.agents/skills`. It holds the work and nothing else; the agent's own configuration is
    read where the program runs, not here. The library refuses a directory that does not exist
    when the run starts."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


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
