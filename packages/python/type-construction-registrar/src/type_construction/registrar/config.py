from pydantic_settings import BaseSettings, SettingsConfigDict

from type_construction.registrar.integration.registrar.provider import Registrar


class RegistrarConfig(BaseSettings):
    """What the deployment sets: the registrar this program reaches."""

    model_config = SettingsConfigDict(
        frozen=True,
        extra="forbid",
        strict=False,
        validate_default=True,
        revalidate_instances="never",
        env_nested_delimiter="__",
    )
    registrar: Registrar
