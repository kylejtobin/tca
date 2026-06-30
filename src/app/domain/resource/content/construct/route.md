---
name: tca_authorized_construct_route
description: Build a route, the only legal ingress at the transport edge. MUST be invoked before handling any request, message, or hook input. Replaces the forbidden forms; if a handler that parses, computes, decides, or transforms is about to appear, stop and build the route instead.
---
# Route

## Definition

The function at transport ingress. It constructs a contract model or foreign model from raw transport data, unwraps transport wrapper structure, dispatches the value the verb consumes, and serializes the reply. It defines no types and computes no domain fact.

## Required Form

```python
def fill_route(raw: str, model: PositionConsistencyModel) -> str:
    message = VenueFillMessage.model_validate_json(raw)
    model.book(message.fill)
    return OrderReceipt(order_id=message.fill.order_id).model_dump_json()
```

The route dispatches `message.fill`, the innermost value the verb consumes, never the transport wrapper. The reply is one of the two legal serialization sites.

## Sorting Rules

The shape the route constructs belongs to whoever owns it: a contract model when this program publishes the API, a foreign model when the caller's shape is another system's. Domain work belongs to the verb the route dispatches to. Wiring and registration belong to the composition root.

## Replaced Forms

A handler that parses fields by hand restates the construction the model performs in one call. A handler that computes or decides is domain meaning escaped to the edge; the route turns transport into a construction and back, nothing more.

## Construct-Specific Doctrine

(none)

## Allowed Patterns

- one function per ingress: one construction from raw transport data, one dispatch of the innermost value, one serialized reply
- contract and foreign models imported from the files that declare them
- `model_dump_json` on the reply contract, the route being a legal serialization site

## Forbidden

- parsing transport fields by hand
- transforming or computing domain data
- branching on a domain case
- dispatching a transport wrapper into a verb
- defining any type in the route's file

## Halt Rule

Halt when ingress would require a computation or a decision, or when the ingress shape, the dispatched verb, or the reply names no row. Report the row and the requirement: the surface, the foreign thing, or the verb is not yet modeled, and the table is not finished.
