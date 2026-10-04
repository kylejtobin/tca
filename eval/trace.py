from pydantic import BaseModel, ConfigDict, Field, RootModel


# ── Scalar ──


class SampleId(RootModel[str]):
    """Name one task so that runs, ratings and results refer to it unambiguously."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1, pattern=r"^[a-z0-9-]+$")


class TaskText(RootModel[str]):
    """State the modeling request exactly as the agent receives it."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class HardType(RootModel[str]):
    """Name the thing whose type no declared construct and no library in the stack produces."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class RequiredConstruct(RootModel[str]):
    """Write the declared type that construction must produce at the hard type."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


# ── Thing ──


class Sample(BaseModel):
    """Write one task the agent attempts, with what a correct delivery declares."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    id: SampleId = Field(
        description="Name the task in lowercase words joined by hyphens, after its hard type.",
    )
    input: TaskText = Field(
        description=(
            "Write the request the agent receives, naming the thing to model and nothing "
            "about how to model it."
        ),
    )
    target: RequiredConstruct = Field(
        description=(
            "Write the declared type a correct delivery constructs at the hard type, copied "
            "from the skill where the skill holds it."
        ),
    )
    hard_type: HardType = Field(
        description=(
            "Name the one thing in the task whose type no declared construct and no library "
            "produces."
        ),
    )


# ── Collection ──


class Dataset(RootModel[tuple[Sample, ...]]):
    """List every task the eval runs, each once."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[Sample, ...] = Field(min_length=1)
