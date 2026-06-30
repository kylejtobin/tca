---
name: tca_authorized_construct_contract_model
description: Build a contract model, the only legal shape for this program's own API request or reply. MUST be invoked before declaring any API surface, request shape, or response shape this program publishes. Replaces the forbidden forms; if one model serving both our API and another system's shape, an alias to a foreign key on our API model, or a hand-built response dict is about to appear, stop and build the contract model instead.
---
# Contract Model

## Definition

A frozen `BaseModel` of this program's own API request or reply, composed of declared types in this program's vocabulary. No alias to another system's key appears on it.

## Required Form

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

## Sorting Rules

Composition direction separates the edge's two models: the contract model is ours, built of our types and names, projecting outward; the foreign model is theirs, named for their thing, its aliases holding their keys, lifting inward. A composite that is a domain fact rather than a surface shape is a concept model.

## Replaced Forms

One model serving as both our API shape and another system's shape fuses our surface with their shape; build one of each. A hand-built response dict is an unproven shape leaving the program; the reply is the contract model itself, serialized at the route.

## Construct-Specific Doctrine

(none)

## Allowed Patterns

- a frozen `BaseModel`, `extra="forbid"`, every field a declared type from this context or its peers
- a request contract a route constructs from raw transport data
- a reply contract constructed from proven facts and serialized whole in the route
- `@computed_field` derivations when a derived fact is part of the published shape

## Forbidden

- an alias to another system's key
- a foreign shape modeled as a contract
- `include`, `exclude`, or `by_alias` on the reply's serialization; a different wire shape is its own contract model
- a contract field whose type is not one of this program's declared types

## Halt Rule

Halt when the published shape would need a foreign alias, an undeclared type, or `include`, `exclude`, or `by_alias` on its serialization. Report the row and the field: either the shape belongs to a foreign model or the type is not yet modeled, and the table is not finished.
