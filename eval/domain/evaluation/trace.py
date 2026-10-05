from pydantic import BaseModel, ConfigDict, Field, RootModel

from domain.evaluation.type import InputText, TraceId
from domain.evaluation.value import Output, Steps


class Trace(BaseModel):
    """A record of one run of the agent: what it received, every step it took, and what it answered with."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    id: TraceId
    input: InputText
    steps: Steps
    output: Output


class Traces(RootModel[tuple[Trace, ...]]):
    """The traces of one error analysis or one experiment."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[Trace, ...] = Field(min_length=1)
