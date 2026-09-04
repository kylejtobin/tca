---
type: construct
---

# Route

## Definition

The function at transport ingress. It constructs a contract model or foreign model from raw transport data, unwraps transport wrapper structure, dispatches the value the verb consumes, and serializes the reply. It defines no types and computes no domain fact.

## Required form

```python
def fill_route(raw: str, model: PositionConsistencyModel) -> str:
    message = VenueFillMessage.model_validate_json(raw)
    model.book(message.fill)
    return OrderReceipt(order_id=message.fill.order_id).model_dump_json()
```

The route dispatches `message.fill`, the innermost value the [verb](verb.md) consumes, never the transport wrapper. The reply is one of the two legal serialization sites; the other is the client binding.

## Replaced forms

- A handler that parses fields by hand restates the construction the model performs in one call.
- A handler that computes or decides is domain meaning escaped to the edge: the route turns transport into a construction and back, nothing more.

## Sorting

- The shape the route constructs belongs to its owner → [contract model](contract-model.md) when this program publishes the API, [foreign model](foreign-model.md) when the caller's shape is another system's.
- Domain work → the [verb](verb.md) the route dispatches to.
- Wiring and registration → [composition root](composition-root.md).
- Program placement → lives in `api/<context>.py`; see [topology](topology.md).

## Allowed

- one function per ingress: one construction from raw transport data, one dispatch of the innermost value, one serialized reply
- contract and foreign models imported from the files that declare them
- `model_dump_json` on the reply contract, the route being a legal serialization site

## Forbidden

- parsing transport fields by hand
- transforming or computing domain data
- branching on a domain case
- dispatching a transport wrapper into a verb
- defining any type in the route's file
