---
type: Reference
description: How a frozen complete domain thing or fact is constructed from declared meanings. Read when modeling a full concept, refinement, or durable fact.
---

# Concept Model

## Use

Use for one complete domain thing, durable fact, or genuine refinement of another concept. The class is the kind.

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

An order is the account's instruction, identified by the `OrderId` that `Fill.order_id` references; a limit order is an order with a limit price. A fill is complete when it occurs. Remaining quantity belongs to the order, not to a `PartialFill` refinement invented to demonstrate subclassing.

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
- Use a self-typed `prior` field for the [state-transition shape](state-transition.md); the declaration remains a concept model, not an additional form.
- Subclass only when every child is a kind of the parent.
- A refinement inherits every parent field, configuration, property, and semantic method unchanged; it only adds stricter facts. No program-owned custom validator is declared or inherited.
- Put enduring identity in its own semantic scalar field when the thing has identity.
- Keep completed facts frozen and recursively immutable.
- Derive facts implied by existing fields through a transformation.

## Do Not

- add `type`, `kind`, registry, or URI fields to simulate class identity
- subclass to reuse fields when the child is not a kind of the parent
- store a derived fact
- hold clients, resources, current state, or effect execution
- use `None`, `Optional`, or nullable fields instead of named constructed absence
- mirror a foreign or contract representation without distinct ownership
