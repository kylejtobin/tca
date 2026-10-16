from pydantic_settings import BaseSettings, SettingsConfigDict

from type_construction.agent.integration.pydantic_ai.provider import AgentProvider


class AgentConfig(BaseSettings):
    """What the deployment sets: the agent's provider, its model, its workspace with its boundary,
    and the history its runs are recorded in, named under `TCA_` in its environment or in a
    `.env` file in its working directory, the environment winning. From the file, as from the
    environment, only the agent's own settings are read; a key another system owns is left to
    it."""

    model_config = SettingsConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        env_prefix="TCA_",
        env_nested_delimiter="__",
        env_file=".env",
        dotenv_filtering="only_existing",
    )
    agent: AgentProvider
