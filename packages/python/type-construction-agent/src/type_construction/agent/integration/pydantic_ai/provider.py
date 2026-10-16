from pydantic import BaseModel, ConfigDict, RootModel
from pydantic_ai.capabilities import (
    AbstractCapability,
    Capability,
    CombinedCapability,
    IncludeToolReturnSchemas,
    Instrumentation,
    LocalWorkspace,
)
from pydantic_ai.workspaces import LocalWorkspaceBackend
from pydantic_ai.workspaces import Workspace as LibraryWorkspace
from pydantic_ai_harness import BubblewrapSandbox, FileSystem, Shell, Skills
from pydantic_ai_harness.bubblewrap_sandbox import BubblewrapWorkspace
from pydantic_ai_harness.compaction import ClearToolResults, SummarizingCompaction, TieredCompaction
from pydantic_ai_harness.step_persistence import SqliteStepStore, StepPersistence

from type_construction.agent.integration.pydantic_ai.model import (
    AgentName,
    AgentTool,
    ContextShare,
    DatabasePath,
    LocalKind,
    ModelName,
    SandboxKind,
    WorkspacePath,
)


class Local(BaseModel):
    """A workspace on this machine, isolating nothing: the directory the agent models in. Its one
    derivation is the library's local workspace, the capability the agent is built with and
    every run's tools and its check run in."""

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
    """A workspace on this machine whose every command, the agent's and its check alike, runs in
    the library's bubblewrap sandbox: the host read-only, no network, writes only inside the
    directory. Its one derivation is the local workspace wrapped in that sandbox."""

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


class LocalShell(BaseModel):
    """The workspace on this machine reached the library's second way, as a shell that runs a
    command in its directory and reports the exit and both streams; constructed from the
    workspace the deployment named. Its one derivation is the library's workspace over the local
    backend."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    kind: LocalKind
    path: WorkspacePath

    @property
    def client(self) -> LibraryWorkspace:
        return LibraryWorkspace(LocalWorkspaceBackend(self.path.root))


class SandboxedShell(BaseModel):
    """The sandboxed workspace reached as a shell: the same, inside the library's bubblewrap
    sandbox, so the check sees what the agent's commands see and writes only where they may."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    kind: SandboxKind
    path: WorkspacePath

    @property
    def client(self) -> LibraryWorkspace:
        return BubblewrapWorkspace(LibraryWorkspace(LocalWorkspaceBackend(self.path.root)))


class WorkspaceShell(RootModel[LocalShell | SandboxedShell]):
    """The workspace reached as a shell, inside whatever boundary the deployment chose."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def client(self) -> LibraryWorkspace:
        return self.root.client


class Workspace(RootModel[Local | Sandboxed]):
    """The workspace the deployment names, with the boundary it chose. The library reaches it two
    ways, as the capability an agent is built with and as a shell a command runs in, and a
    provider derives one client, so the shell is its own provider, constructed from this one."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )

    @property
    def client(self) -> AbstractCapability[object]:
        return self.root.client

    @property
    def shell(self) -> WorkspaceShell:
        return WorkspaceShell.model_validate(self.root, from_attributes=True)


class HistoryStore(BaseModel):
    """The history reached the library's second way, as the store a run's recorded messages are
    read back from by the library's own `continue_run`, under the run's id; constructed from the
    history the deployment named. Its one derivation is the library's SQLite step store over
    that file."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    database: DatabasePath

    @property
    def client(self) -> SqliteStepStore:
        return SqliteStepStore(database=self.database.root)


class History(BaseModel):
    """Where the agent's runs are recorded: one SQLite file the deployment names. The library
    reaches it two ways, as the capability that records every run and as the store a run is
    read back from, and a provider derives one client, so the store is its own provider,
    constructed from this one. Its one derivation is the library's step persistence over that
    file, which records every run, its model requests, its tool calls and a continuable
    snapshot of its messages under the id the library gave the run, and the agent's own name
    beside it; given no name of ours, so the recorded id is the one a reply carries."""

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
        return StepPersistence(store=SqliteStepStore(database=self.database.root))

    @property
    def store(self) -> HistoryStore:
        return HistoryStore.model_validate(self, from_attributes=True)


class AgentProvider(BaseModel):
    """Pydantic AI's provider of the agent: the model, the workspace and the history the
    deployment names, the share of the model's window a conversation may fill, and nothing
    else, since the library reads the rest for itself. Its one derivation is everything the
    agent is but its model and its callbacks, as one of the library's capabilities: the
    workspace as the run's boundary, the library's own file and shell tools inside it, its
    skills from the workspace's `.agents/skills`, its runs recorded in the history, its
    conversation compacted in tiers when it fills that share of the window, the check's result
    shown to the model as its type, the packaged instructions as
    its instructions, and its runs
    traced. The agent itself is the composition root's, built from
    the model's name, the answer's type, the root's check callback and this capability."""

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
    compaction: ContextShare = ContextShare()

    @property
    def client(self) -> AbstractCapability[None]:
        return CombinedCapability(
            (
                self.workspace.client,
                Skills(".agents/skills"),
                FileSystem(),
                Shell(),
                self.history.client,
                TieredCompaction(
                    tiers=(
                        ClearToolResults(max_fraction=self.compaction.root),
                        SummarizingCompaction(max_fraction=self.compaction.root),
                    ),
                    target_fraction=self.compaction.root,
                ),
                IncludeToolReturnSchemas((AgentTool.CHECK,)),
                Instrumentation(),
                Capability(instructions=AgentName.TCA_AGENT.instructions.read_text()),
            )
        )
