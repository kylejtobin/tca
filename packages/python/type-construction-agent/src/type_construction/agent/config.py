from pydantic_settings import BaseSettings, SettingsConfigDict

from type_construction.agent.integration.model_provider.provider import ModelProvider


class AgentConfig(BaseSettings):
    """What the deployment sets: the model provider the agent runs on."""

    model_config = SettingsConfigDict(
        frozen=True,
        extra="forbid",
        strict=False,
        validate_default=True,
        revalidate_instances="never",
        env_prefix="TCA_",
        env_nested_delimiter="__",
    )
    agent: ModelProvider
