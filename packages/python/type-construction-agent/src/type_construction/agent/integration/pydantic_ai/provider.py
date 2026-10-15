from pydantic import BaseModel, ConfigDict
from pydantic_ai import Agent
from pydantic_ai.capabilities import Instrumentation, LocalWorkspace
from pydantic_ai_harness import FileSystem, Skills

from type_construction.agent.domain.agent.prompt import Answer
from type_construction.agent.integration.pydantic_ai.model import AgentName, ModelName


class AgentProvider(BaseModel):
    """Pydantic AI's provider of the agent: the model the deployment names, and nothing else,
    since the library reads the rest for itself. Its one derivation is the TCA agent: the packaged
    prompt as its instructions, working in the directory it runs in with the library's own file
    tools, loading its skills from that directory's `.agents/skills`, the answer as what the
    library constructs, and its runs traced."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    model: ModelName

    @property
    def client(self) -> Agent[None, Answer]:
        return Agent(
            self.model.root,
            name=AgentName.TCA_AGENT,
            output_type=Answer,
            instructions=AgentName.TCA_AGENT.prompt.read_text(),
            capabilities=(
                LocalWorkspace("."),
                Skills(".agents/skills"),
                FileSystem(),
                Instrumentation(),
            ),
        )
