---
type: construct
---

# Contract model

## Definition

A frozen `BaseModel` of this program's own API request or reply, composed of declared types in this program's vocabulary. No alias to another system's key appears on it.

## Required form

```python
class OrderRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    product: ProductId
    side: OrderSide
    quantity: Quantity
    price: Price


class OrderReceipt(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    order_id: OrderId
```

A request that does not conform fails construction at the surface; nothing behind the route sees it. The reply leaves whole: the route serializes the contract model itself.

## Sorting

- This program's own API request or reply shape → this construct.
- Another system's shape → [foreign model](foreign-model.md). Composition direction separates the edge's two models: the contract model is ours, built of our types and names, projecting outward; the foreign model is theirs, named for their thing, its aliases holding their keys, lifting inward.
- A composite that is a domain fact rather than a surface shape → [concept model](concept-model.md).
- Program placement → lives in `domain/<context>/api.py`; see [topology](topology.md).

## Allowed

- a frozen `BaseModel`, `extra="forbid"`, every field a declared type from this context or its peers
- a request contract a route constructs from raw transport data
- a reply contract constructed from proven facts and serialized whole in the route
- `@computed_field` derivations when a derived fact is part of the published shape

## Forbidden

- an alias to another system's key
- a foreign shape modeled as a contract
- `include`, `exclude`, or `by_alias` on the reply's serialization; a different wire shape is its own contract model
- a contract field whose type is not one of this program's declared types
