---
type: Construct
description: "Shape of one intended external effect as a frozen value that performs nothing."
---

# Action

A write holds the thing to be sent:

```python
class PersistPosition(BaseModel):
    """The intended recording of a position in the clearing house."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    position: Position
```

A read holds the identity of the thing asked for:

```python
class ReadPosition(BaseModel):
    """The intended reading of one account's position in one instrument from the clearing house."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    account: AccountId
    instrument: InstrumentId
```

The fact that authorizes the action constructs it:

```python
    @property
    def persistence(self) -> "PersistPosition":
        return PersistPosition(position=self)
```

Constructed:

`PositionStateConstructor.validate_json('{"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}').persistence` is a `PersistPosition` holding that `Position`. The clearing house has been sent nothing.

`ReadPosition(account=AccountId("A1"), instrument=InstrumentId("ESZ6"))` is a `ReadPosition`. The clearing house has been asked nothing.

`PersistPositionInterpreter.execute` and `ReadPositionInterpreter.execute` make the calls.

In the file:

- The class body is a docstring, `model_config`, and fields.
- Where repeating the effect is part of its contract, the repeat key is a field of the action.
- One interpreter takes it: [effect-interpreter.md](effect-interpreter.md). A closed family of actions that one interpreter takes is a union of actions.
- Placement: `domain/venue/position.py`, beside the fact that authorizes it.
