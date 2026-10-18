from contextlib import AsyncExitStack

from opentelemetry.baggage import set_baggage
from pydantic import BaseModel, ConfigDict

from type_construction.eval.domain.evaluation.run import OracleProduce, Trace
from type_construction.eval.integration.subject.model import (
    Attribute,
    SpanContextRecord,
    SpanKind,
    SpanName,
)
from type_construction.eval.integration.subject.production import (
    OracleProduction,
    SpannedProduction,
)
from type_construction.eval.integration.subject.provider import Tracing


class OracleProduceInterpreter(BaseModel):
    """The one place the oracle's production is performed: the run's root span is the
    capability, acquired from the tracer under the address, the input and the output as
    baggage, since the oracle's capture is known from the expectation before the span opens,
    and released on every path; what comes back is the trace."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    action: OracleProduce
    provider: Tracing

    async def interpret(self) -> Trace:
        async with AsyncExitStack() as stack:
            return SpannedProduction(
                context=SpanContextRecord.model_validate(
                    stack.enter_context(
                        self.provider.client.start_as_current_span(
                            f"{SpanName.RUN} {self.action.address.case.root}",
                            context=set_baggage(
                                Attribute.OUTPUT,
                                OracleProduction(action=self.action).capture.judged_form.root,
                                set_baggage(
                                    Attribute.INPUT,
                                    self.action.input.root,
                                    set_baggage(
                                        Attribute.SPAN_KIND,
                                        SpanKind.CHAIN,
                                        set_baggage(
                                            Attribute.REPETITION,
                                            self.action.address.repetition.root,
                                            set_baggage(
                                                Attribute.SYSTEM_VERSION,
                                                self.action.address.system.version.root,
                                                set_baggage(
                                                    Attribute.SYSTEM_NAME,
                                                    self.action.address.system.name.root,
                                                    set_baggage(
                                                        Attribute.CASE_ID,
                                                        self.action.address.case.root,
                                                        set_baggage(
                                                            Attribute.DATASET_VERSION,
                                                            self.action.address.dataset.version.root,
                                                            set_baggage(
                                                                Attribute.DATASET_NAME,
                                                                self.action.address.dataset.name.root,
                                                            ),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        )
                    ).get_span_context(),
                    from_attributes=True,
                ),
                address=self.action.address,
                capture=OracleProduction(action=self.action).capture,
            ).trace
