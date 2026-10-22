"""One route answered under Logfire's OpenTelemetry integration, in a process of its own, and
every span it exported printed as JSON: what the test of Logfire interoperability reads. Logfire
configures the process's global tracer provider the way a deployment would; the engine depends
on ``opentelemetry-api`` alone and imports nothing from Logfire."""

import asyncio
import json
import sys

import logfire
from opentelemetry import trace
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from type_construction.engine import answer, config, proven
from type_construction_engine import occurrences

EXPORTER = InMemorySpanExporter()
"""Where every span of the process ends up: in memory, with no credentials and no network."""


def main() -> None:
    """Configure Logfire locally, answer the order given on standard input, and print the
    spans."""
    logfire.configure(
        send_to_logfire=False,
        console=False,
        additional_span_processors=[SimpleSpanProcessor(EXPORTER)],
    )
    request = occurrences.PlaceOrder.model_validate_json(sys.stdin.read())
    route = asyncio.run(
        answer(occurrences.Checkout, request, config(occurrences)(), proven(occurrences))
    )
    provider = trace.get_tracer_provider()
    found = [
        {
            "name": span.name,
            "trace": span.context.trace_id if span.context else None,
            "span": span.context.span_id if span.context else None,
            "parent": span.parent.span_id if span.parent else None,
            "attributes": dict(span.attributes or {}),
            "events": [
                {"name": e.name, "attributes": dict(e.attributes or {})} for e in span.events
            ],
            "status": span.status.status_code.name,
        }
        for span in EXPORTER.get_finished_spans()
    ]
    print(
        json.dumps(
            {
                "provider": type(provider).__module__ + "." + type(provider).__name__,
                "reply": route.reply.model_dump_json(),
                "spans": found,
            }
        )
    )


if __name__ == "__main__":
    main()
