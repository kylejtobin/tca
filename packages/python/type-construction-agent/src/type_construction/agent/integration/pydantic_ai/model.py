from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel

from type_construction.agent.domain.agent.type import Failure, Output, Success


class AgentName(StrEnum):
    """The one name an agent goes by: to the library, in its spans, at the command line and in its
    telemetry; the packaged instructions it is given are kept under it."""

    TCA_AGENT = "tca-agent"

    @property
    def instructions(self) -> Path:
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


class DatabasePath(RootModel[str]):
    """The SQLite file the agent's runs are recorded in, as the library's store takes it, relative
    to where the program runs: made when it is missing, used when it is there."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ContextShare(RootModel[float]):
    """The share of the model's context window a conversation may fill before the library
    compacts it, as the library's tiered compaction takes its target: above it, the oldest tool
    results are cleared first, and the older messages summarized by the same model only if that
    is not enough; the window is the model's own, which the library resolves from the model a
    request goes to. Seven tenths when the deployment names nothing, leaving the rest for the
    model's answer and the next tool results."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: float = Field(default=0.7, gt=0, le=1)


class WorkspaceResource(StrEnum):
    """What a workspace declares at its root, by the name the agent reaches it under."""

    CHECK = "./check"


class AgentTool(StrEnum):
    """The one name a tool of this program goes by to the model and to the library."""

    CHECK = "check"


class CheckReply(BaseModel):
    """What the library's workspace hands back from the check: the exit, and what it printed on
    each stream."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    exit: Success | Failure = Field(alias="exit_code")
    out: Output = Field(alias="stdout")
    err: Output = Field(alias="stderr")


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
