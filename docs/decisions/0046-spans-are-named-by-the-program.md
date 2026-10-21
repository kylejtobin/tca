# 0046. The engine emits OpenTelemetry spans named by the program's classes, through the API alone

Status: accepted

## Context

A run should be observable without a page writing a log line, and without the engine forcing a backend on a deployment.

## Rejected

Logging calls on pages or in the engine. A vendor SDK as a dependency of the engine. Request or record contents as span attributes.

## Decision

The engine depends on `opentelemetry-api`. `answer` is one span named for the route with `tca.request` and `tca.levels`; each performed action is a child span named for the action with `tca.party` and `tca.record`; a skipped union member is a `skipped` event with `tca.class`; a refusal or a client exception sets the span's status through `start_as_current_span`'s defaults. Attributes are class names and counts, never contents. The deployment configures the SDK and the exporter through the standard `OTEL_*` variables; the dev container exports to the Jaeger service in `compose.yaml`. With no SDK the calls are no-ops.

## Evidence

Under the SDK with an in-memory exporter, a two-line order produced `Checkout` with `tca.request=PlaceOrder`, `tca.levels=6` and two `skipped` events, and four child spans, two `Quote` with `tca.party=Catalog, tca.record=Price` and two `Charge` with `tca.party=Payments, tca.record=Charged`, all with status unset.

## Consequences

A page has no logging. A kind uses the standard OpenTelemetry instrumentation for its client. Refuted by a measurement spans cannot give; none named.
