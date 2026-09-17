---
type: Reference
description: How this program's request or reply contract is constructed and serialized. Read when defining a program-owned external interface.
---

# Contract Model

## Use

Use when this program owns a published request or reply whose shape is not already the exact owned domain meaning being published.

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

Name this `LimitOrderRequest`: its required limit price admits limit orders, not every order. Use `instrument: InstrumentId` as in the domain; another name for the same traded thing duplicates its meaning.

`FillBooked` carries exactly the decided wire facts: sequence and net quantity. The [egress route](route.md) projects them from its recorded fact. Putting `recorded` in the contract would publish the entire position history and repeat the sequence beside it; do not carry that source fact or add computed fields here.

- Compose contract fields from declared semantic types.
- Construct requests at the route before anything consumes them.
- Construct replies from proven domain facts or observed outcomes.
- Put an alias on a field only when this program deliberately owns that published wire name.
- Use `@computed_field` for facts derived from the contract's own fields, returning an explicitly constructed value. Facts projected from an external source fact are ordinary contract fields; do not carry the source merely to compute them.
- Publish the domain model directly when ownership, meaning, shape, and evolution policy are identical; direct publication does not make it a contract-model construct.

## Do Not

- treat another system's shape as this program's contract
- duplicate a domain model merely to create a DTO layer
- serialize with ad hoc `include`, `exclude`, or field-copying dictionaries
- expose a foreign client, exception, or raw representation
- let a route add or remove fields from the declared contract
