from pydantic import BaseModel, ConfigDict, RootModel
from pydantic_ai import Agent
from pydantic_ai.capabilities import AbstractCapability, Instrumentation, LocalWorkspace
from pydantic_ai_harness import BubblewrapSandbox, FileSystem, Shell, Skills
from pydantic_ai_harness.step_persistence import SqliteStepStore, StepPersistence

from type_construction.agent.domain.agent.prompt import Answer
from type_construction.agent.integration.pydantic_ai.model import (
    AgentName,
    DatabasePath,
    LocalKind,
    ModelName,
    SandboxKind,
    WorkspacePath,
)


class Local(BaseModel):
    """A workspace on this machine, isolating nothing: the directory the agent models in. Its one
    derivation is the library's local workspace, the capability an agent is built with and every
    run's tools run in."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    kind: LocalKind
    path: WorkspacePath

    @property
    def client(self) -> AbstractCapability[object]:
        return LocalWorkspace(self.path.root)


class Sandboxed(BaseModel):
    """A workspace on this machine whose every command runs in the library's bubblewrap sandbox:
    the host read-only, no network, writes only inside the directory. Its one derivation is the
    local workspace wrapped in that sandbox."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    kind: SandboxKind
    path: WorkspacePath

    @property
    def client(self) -> AbstractCapability[object]:
        return BubblewrapSandbox(LocalWorkspace(self.path.root))


class Workspace(RootModel[Local | Sandboxed]):
    """The workspace the deployment names, with the boundary it chose."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )

    @property
    def client(self) -> AbstractCapability[object]:
        return self.root.client


class History(BaseModel):
    """Where the agent's runs are recorded: one SQLite file the deployment names. Its one
    derivation is the library's step persistence over that file, which records every run, its
    model requests, its tool calls and a continuable snapshot of its messages, under the agent's
    name, and from which a conversation is continued by the library's own `continue_run`."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    database: DatabasePath

    @property
    def client(self) -> AbstractCapability[object]:
        return StepPersistence(
            store=SqliteStepStore(database=self.database.root), agent_name=AgentName.TCA_AGENT
        )


class AgentProvider(BaseModel):
    """Pydantic AI's provider of the agent: the model, the workspace and the history the
    deployment names, and nothing else, since the library reads the rest for itself. Its one
    derivation is the TCA agent: the packaged prompt as its instructions, the workspace as the
    run's boundary, the library's own file and shell tools inside it, its skills from the
    workspace's `.agents/skills`, its runs recorded in the history, the answer as what the
    library constructs, and its runs traced. The agent carries no callback of this program: it
    checks its work with the shell, by the check the workspace declares, and the program's own
    checks are interpreters the program runs."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    model: ModelName
    workspace: Workspace
    history: History = History(database=DatabasePath("tca-agent.sqlite"))

    @property
    def client(self) -> Agent[None, Answer]:
        return Agent(
            self.model.root,
            name=AgentName.TCA_AGENT,
            output_type=Answer,
            instructions=AgentName.TCA_AGENT.prompt.read_text(),
            capabilities=(
                self.workspace.client,
                Skills(".agents/skills"),
                FileSystem(),
                Shell(),
                self.history.client,
                Instrumentation(),
            ),
        )
