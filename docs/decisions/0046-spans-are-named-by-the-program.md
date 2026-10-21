# 0046. The engine emits OpenTelemetry spans named by the program's classes, through the API alone

Status: accepted

## Context

A run should be observable without a page writing a log line, and without the engine forcing a backend on a deployment.

## Rejected

Logging calls on pages or in the engine. A vendor SDK as a dependency of the engine. Request or record contents as span attributes. A `skipped` event per refused union member, which the passes no longer produce: a member that cannot exist is never asked for.

## Decision

The engine depends on `opentelemetry-api`. `answer` is one span named for the route with `tca.request` and, when the run ends, `tca.passes`; each performed action is a child span named for the action with `tca.party` from the connection it holds and `tca.record` from the record it heard; a refusal or a client exception sets the span's status through `start_as_current_span`'s defaults. Attributes are class names and counts, never contents. The deployment configures the SDK and the exporter through the standard `OTEL_*` variables; the dev container exports to the Jaeger service in `compose.yaml`. With no SDK the calls are no-ops.

## Evidence

Not run under the SDK since the rewrite; the calls are the same three as before, `start_as_current_span` on the route and on each action and `set_attribute` for the counts. Refuted by a span tree under the in-memory exporter that differs from: one `Checkout` span with `tca.request=PlaceOrder` and `tca.passes`, and one child per performed action with `tca.party` and `tca.record`.

## Consequences

A page has no logging. A kind uses the standard OpenTelemetry instrumentation for its client. Refuted by a measurement spans cannot give; none named.
