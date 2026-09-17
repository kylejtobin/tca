---
type: Construct
description: A frozen complete domain thing, durable fact, or refinement; the class is the kind.
---

# Concept Model

## Definition

One complete domain thing, durable fact, or genuine refinement of another concept. The class is the kind: refinement is subclassing, never a `type`, `kind`, registry, or URI field.

## Required Form

```python
class Order(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    id: OrderId
    account: AccountId
    instrument: InstrumentId
    side: Side
    quantity: Quantity


class LimitOrder(Order):
    limit: Price
```

An order is the account's instruction, identified by the `OrderId` that `Fill.order_id` references; a limit order is an order with a limit price. A fill is complete when it occurs, so remaining quantity belongs to the order, not to a `PartialFill` refinement invented to demonstrate subclassing.

The recorded fact couples the ledger's acknowledged sequence to the position it recorded:

```python
class PositionRecorded(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    sequence: LedgerSequence
    position: Position
```

- Fields are declared semantic relations to other constructs.
- A self-typed `prior` field is the [state-transition shape](./state-transition.md); the declaration remains a concept model.
- Subclass only when every child is a kind of the parent. A refinement inherits every parent field, configuration, property, and semantic method unchanged and only adds stricter facts.
- Enduring identity is its own semantic scalar field when the thing has identity.
- Completed facts are frozen and recursively immutable.
- Facts implied by existing fields are derived through a [transformation](./transformation.md).
- Identity survives in memory through the class. It does not survive JSON at a base-typed field, so serialized subtype identity that must cross a wire is carried by a discriminated [union](./union.md).

## Forbidden

- a `type`, `kind`, registry, or URI field to simulate class identity
- subclassing to reuse fields when the child is not a kind of the parent
- a stored derived fact
- clients, resources, current state, or effect execution
- `None`, `Optional`, or a nullable field instead of named constructed absence
- a foreign or contract representation mirrored without distinct ownership
