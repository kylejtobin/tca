---
type: Construct
description: This program's published request or reply, carrying exactly the decided wire facts.
---

# Contract Model

## Definition

This program owns a published request or reply whose shape is not already the exact owned domain meaning being published. The contract carries exactly the decided wire facts and nothing that would publish more.

## Required Form

```python
class LimitOrderRequest(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    instrument: InstrumentId
    side: Side
    quantity: Quantity
    limit: Price


class FillBooked(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    sequence: LedgerSequence
    net_quantity: NetQuantity
```

`LimitOrderRequest` is named for what its shape admits: a required limit price admits limit orders, not every order. `FillBooked` carries the ledger's recorded sequence and the position's net quantity; the [egress route](./route.md) projects them from its recorded fact. Carrying `recorded` in the contract would publish the entire position history and repeat the sequence beside it.

- Contract fields compose from declared semantic types, with `instrument: InstrumentId` as in the domain, since another name for the same traded thing duplicates its meaning.
- Requests construct at the route before anything consumes them; replies construct from proven domain facts or observed outcomes.
- An alias appears on a field only when this program deliberately owns that published wire name.
- `@computed_field` serves facts derived from the contract's own fields, returning an explicitly constructed value. Facts projected from an external source fact are ordinary contract fields; the source is not carried merely to compute them.
- A domain model is published directly when ownership, meaning, shape, and evolution policy are identical; direct publication does not make it a contract model.

## Forbidden

- another system's shape treated as this program's contract
- a domain model duplicated merely to create a DTO layer
- serialization with ad hoc `include`, `exclude`, or field-copying dictionaries
- a foreign client, exception, or raw representation exposed
- a route adding or removing fields from the declared contract
