from pydantic import BaseModel, ConfigDict, RootModel

from type_construction.agent.domain.agent.type import Failure, Output, Success


class Check(BaseModel):
    """The agent's asking whether the work it just modeled is clean: a request whose only purpose
    is its effect, so it is its own action, handed to the interpreter that performs it."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )


class Clean(BaseModel):
    """A check that passed, with everything it said: the work may go on."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    exit: Success
    out: Output
    err: Output


class Failed(BaseModel):
    """A check that failed, with everything it said: the work is not done."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    exit: Failure
    out: Output
    err: Output


class CheckResult(RootModel[Clean | Failed]):
    """What a check concluded of the work: clean or failed, by its exit, with what it said."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
