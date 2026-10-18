from pydantic import BaseModel, ConfigDict

from type_construction.eval.domain.evaluation.run import OracleProduce, Trace
from type_construction.eval.domain.evaluation.value import Address, Capture
from type_construction.eval.integration.subject.model import SpanContextRecord


class OracleProduction(BaseModel):
    """The oracle's production in the trace's terms: the expectation itself stands as what the
    system produced, so the capture is known before the span opens."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    action: OracleProduce

    @property
    def capture(self) -> Capture:
        return Capture(judged_form=self.action.expectation)


class SpannedProduction(BaseModel):
    """A production performed under the run's root span: what OpenTelemetry said of the
    span, the address, and the capture; its derivation is the trace."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    context: SpanContextRecord
    address: Address
    capture: Capture

    @property
    def trace(self) -> Trace:
        return Trace(
            address=self.address,
            trace=self.context.trace_id.id,
            span=self.context.span_id.id,
            capture=self.capture,
        )
