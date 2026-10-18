from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, RootModel

from type_construction.eval.domain.evaluation.type import SpanId, TraceId


class Scope(StrEnum):
    """The name the eval's own spans are emitted under: OpenTelemetry's instrumentation scope,
    which says who opened a span."""

    EVAL = "type-construction-eval"


class Attribute(StrEnum):
    """The keys the eval puts on the spans it opens, as the collector's mapping and the
    documents name them; carried as the run's baggage into the span's start."""

    DATASET_NAME = "eval.dataset.name"
    DATASET_VERSION = "eval.dataset.version"
    CASE_ID = "eval.case.id"
    SYSTEM_NAME = "eval.system.name"
    SYSTEM_VERSION = "eval.system.version"
    REPETITION = "eval.repetition"
    SPAN_KIND = "eval.span.kind"
    INPUT = "eval.input"
    OUTPUT = "eval.output"


class SpanKind(StrEnum):
    """What a span the eval opens is, in the vocabulary the trace viewer reads."""

    CHAIN = "CHAIN"


class SpanName(StrEnum):
    """The low-cardinality name of the span the eval opens for a run; the case is appended."""

    RUN = "run"


class TraceNumber(RootModel[int]):
    """A trace's identity as OpenTelemetry holds it in the process, a number; its one
    derivation is the identity as it is written."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(gt=0)

    @property
    def id(self) -> TraceId:
        return TraceId(format(self.root, "032x"))


class SpanNumber(RootModel[int]):
    """A span's identity as OpenTelemetry holds it in the process, a number; its one
    derivation is the identity as it is written."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(gt=0)

    @property
    def id(self) -> SpanId:
        return SpanId(format(self.root, "016x"))


class SpanContextRecord(BaseModel):
    """What OpenTelemetry says of a span it opened: the identity of its trace and its own,
    read once from the span's context."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    trace_id: TraceNumber
    span_id: SpanNumber
