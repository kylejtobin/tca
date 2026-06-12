---
name: tca-service
description: Build a service, the only legal binding between a transport client and the consistency model. MUST be invoked before writing any connect/setup/wiring class. Replaces the forbidden forms; if a service holding domain logic, a repository, a manager, or any class that computes is about to appear, stop and build the shim instead.
---

# service

A service is a connection shim: `connect` binds a transport client to the consistency
model. When a service becomes interesting, domain meaning has escaped into it.

    class AnalysisService:
        def connect(self, bus: EventBusClient) -> AnalysisConsistencyModel:
            return AnalysisConsistencyModel(bus=bus)

`connect` may hold transport-level setup: connection, authentication, subscription.
It holds no domain logic and makes no domain decision; when a service becomes
interesting, domain meaning has escaped into the shell.

## The row

The spec row this card expands. `binds` is the foreign client class, `to` the
consistency_model row. Service rows live under `service/`.

    {"construct": "service", "name": "AnalysisService", "file": "service/analysis.py", "binds": "EventBusClient", "to": "AnalysisConsistencyModel"}

## Allowed patterns

- one class whose `connect` accepts the transport client(s) and returns the constructed
  consistency model
- connection, authentication, subscription setup inside `connect`

Build exactly these patterns. Never invent an exception. If you cannot see how, the
modeling is incomplete or construction is not yet the pipeline: report the gap.
