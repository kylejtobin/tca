from opentelemetry import trace
from opentelemetry.trace import Tracer
from pydantic import BaseModel, ConfigDict

from type_construction.eval.integration.subject.model import Scope


class Tracing(BaseModel):
    """The trace as this process emits it. The SDK the process configured from the standard
    variables carries every span to the collector and reads those variables itself, and the
    eval's spans are emitted under the eval's own name, so the deployment names nothing
    here. Its one derivation is the library's tracer under that scope, which keeps nothing
    between crossings."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )

    @property
    def client(self) -> Tracer:
        return trace.get_tracer(Scope.EVAL)
