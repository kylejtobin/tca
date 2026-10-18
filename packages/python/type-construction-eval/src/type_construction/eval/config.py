from pydantic_settings import BaseSettings, SettingsConfigDict

from type_construction.eval.integration.inspect.provider import Record


class EvalConfig(BaseSettings):
    """What the deployment sets: the record, by the one directory it lives in and the model
    the runner binds runs to, from which every system that reaches the record is derived.
    Named under `EVAL_` in the environment. Where the process sends its spans is the
    OpenTelemetry SDK's own setting, read by the SDK from its standard variables."""

    model_config = SettingsConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        env_prefix="EVAL_",
        env_nested_delimiter="__",
    )
    record: Record
