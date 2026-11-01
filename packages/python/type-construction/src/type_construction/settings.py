"""Configuration base for framework and application settings.

The base implements docs/architecture/DESIGN.md sections 5.2 and 7. It establishes the required
native configuration and nothing else: Pydantic Settings supplies source acquisition, precedence,
parsing, nested construction, aliases, defaults and validation. Importing this module acquires
no deployment configuration; construction of a specialized class does.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings"]


class Settings(BaseSettings):
    """Base for typed configuration requirements constructed from native deployment sources.

    Applications specialize it with typed fields, ``Field`` and ``SettingsConfigDict`` and compose
    integration-supplied configuration contracts as nested fields. Enabled sources keep the native
    precedence: initialization values, environment, configured dotenv, configured secret files,
    then declared defaults. Nested fields receive environment values through the ``__``
    delimiter, so ``NATS__SERVERS`` supplies ``servers`` of a field named ``nats``.
    """

    model_config = SettingsConfigDict(
        validate_default=True,
        frozen=True,
        env_nested_delimiter="__",
    )
