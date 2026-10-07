from pydantic import BaseModel, ConfigDict


class TcaAgentValues(BaseModel):
    """What fills the TCA agent's words: nothing, because they have no slots."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
