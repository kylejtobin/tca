---
type: Construct
description: A frozen value describing one intended external effect without executing it.
---

# Action

## Definition

A constructed domain decision authorizes one external effect that must travel independently of its execution. The action is the proof of the intent; the [effect interpreter](./effect-interpreter.md) executes it and proves the occurrence.

## Required Form

```python
class ReadPosition(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    account: AccountId
    instrument: InstrumentId


class PersistPosition(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    position: Position
```

- The action is named for the intended effect, not its handler, client, transport, or eventual outcome.
- It carries every semantic input required to request the effect.
- Reads are effects too, and a read names the thing by its identity: `ReadPosition` requests the account's holding in the instrument. An order identifies the instruction a fill executed, not the position. The read action does not contain or invent the observed state.
- An idempotency or repetition key appears only when repeated execution is part of the effect contract.
- The authorizing domain fact constructs it. When authorization follows succession, the successor fact owns that derivation; no transition procedure or policy at the composition root is needed.
- Related effect alternatives form a union when one interpreter consumes a closed action family.

## Forbidden

- the effect executed
- a client, resource, mutable current-state reference, retry loop, exception, or observed outcome held; a completed immutable state value may be an effect input
- an event that already happened
- ordinary domain input that requests no external effect
- transport serialization or foreign vocabulary
- success claimed from the action's construction
