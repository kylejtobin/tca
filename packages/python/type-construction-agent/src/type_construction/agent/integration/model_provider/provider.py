from pathlib import Path

from pydantic import BaseModel, ConfigDict
from pydantic_ai import Agent
from pydantic_ai.capabilities import Instrumentation, LocalWorkspace
from pydantic_ai.models import KnownModelName
from pydantic_ai.models.openai import OpenAIChatModelSettings
from pydantic_ai.settings import ThinkingEffort
from pydantic_ai.usage import UsageLimits
from pydantic_ai_harness import FileSystem, Skills

from type_construction.agent.domain.agent.prompt import Answer
from type_construction.agent.domain.agent.type import PromptLocation


class ModelProvider(BaseModel):
    """The model the deployment names, how hard it is asked to think, what one run may use, and
    the prompt that makes it an agent. Its one derivation is the agent: the prompt as its
    instructions, the package's skills as what it may load, and the answer as what it constructs.
    The thinking level is sent under pydantic_ai's unified name, which reaches the models it
    profiles, and under OpenAI's, which reaches an OpenAI-compatible endpoint serving one it does
    not; it is a request, and whether the model honors it is the model's."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=False,
        validate_default=True,
        revalidate_instances="never",
    )
    model: KnownModelName | str
    thinking: ThinkingEffort = "low"
    limits: UsageLimits = UsageLimits(request_limit=20)
    prompt: PromptLocation = PromptLocation.TCA_AGENT

    @property
    def client(self) -> Agent[None, Answer]:
        return Agent(
            self.model,
            name=Path(self.prompt).stem,
            output_type=Answer,
            instructions=(Path(__file__).parents[2] / "prompts" / self.prompt).read_text(),
            model_settings=OpenAIChatModelSettings(
                thinking=self.thinking, openai_reasoning_effort=self.thinking
            ),
            capabilities=(
                LocalWorkspace(Path(__file__).parents[2] / "prompts", read_only=True),
                Skills("skills"),
                FileSystem(read_only=True, tools=("read_file", "list_directory")),
                Instrumentation(),
            ),
        )
