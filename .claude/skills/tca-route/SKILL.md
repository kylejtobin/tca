---
name: tca-route
description: Build a route, the only legal ingress at the transport edge. MUST be invoked before handling any request, message, or hook input. Replaces the forbidden forms; if a handler that parses, computes, decides, or transforms is about to appear, stop and build the route instead.
---

# route

A route turns transport into typed construction and back: construct, dispatch,
project. It defines no types and computes nothing; when a route grows interesting,
meaning has escaped to the edge.

    def hook_route(raw_message: str, model: AnalysisConsistencyModel) -> str:
        envelope = HookEnvelopeBoundary.model_validate_json(raw_message)   # construct
        model.analyze(envelope)                                            # dispatch
        return AckBoundary(message=AckMessage("accepted")).model_dump_json()  # project

## The row

The spec row this card expands. Route rows live under `api/`; route files are
the only files (with main) where module-level functions pass the gate.

    {"construct": "route", "name": "HookRoute", "file": "api/analysis.py"}

## Allowed patterns

- one function per ingress: boundary construction, one dispatch to the consistency model,
  one projected response
- contracts imported from the domain's `api.py`

Build exactly these patterns. Never invent an exception. If you cannot see how, the
modeling is incomplete or construction is not yet the pipeline: report the gap.
