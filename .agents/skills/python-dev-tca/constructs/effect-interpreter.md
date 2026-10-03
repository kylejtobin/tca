---
type: Construct
description: "Shape of the one place an external call is made: an action, a capability, one execute, one raw reply constructed as a union."
---

# Effect interpreter

A read:

```python
class ReadPositionInterpreter(BaseModel):
    """The one place the clearing house is asked for a position."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        arbitrary_types_allowed=True,
    )
    action: ReadPosition
    client: PositionClient = Field(exclude=True, repr=False)

    def execute(self) -> PositionState:
        return PositionStateConstructor.validate_json(
            self.client.load(
                self.action.account.root,
                self.action.instrument.root,
            )
        )
```

A write:

```python
class PersistPositionInterpreter(BaseModel):
    """The one place a position is sent to the clearing house."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        arbitrary_types_allowed=True,
    )
    action: PersistPosition
    client: PositionClient = Field(exclude=True, repr=False)

    def execute(self) -> PositionOutcome:
        return PositionSubmission(
            position=self.action.position,
            reply=ClearingReplyConstructor.validate_json(
                self.client.save(self.action.position.model_dump_json())
            ),
        ).outcome
```

Every reply the capability sends is a variant of one union:

```python
PositionState = FlatPosition | Position
PositionStateConstructor: TypeAdapter[PositionState] = TypeAdapter(PositionState)

ClearingReply = ClearingAcknowledgement | ClearingRefusal
ClearingReplyConstructor: TypeAdapter[ClearingReply] = TypeAdapter(ClearingReply)
```

| The capability | Sends | The union |
|---|---|---|
| `PositionClient.load(account, instrument)` | a position, or the flat position | `PositionState` |
| `PositionClient.save(position)` | an acknowledgement, or a refusal | `ClearingReply` |

Constructed:

When `client.load` returns `'{"account": "A1", "instrument": "ESZ6"}'`, `ReadPositionInterpreter.execute` returns a `FlatPosition`.

When `client.load` returns `'{"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}'`, `ReadPositionInterpreter.execute` returns that `Position`.

When `client.save` returns `'{"sequence": 7}'`, `PersistPositionInterpreter.execute` returns a `RecordedPosition` whose `sequence` is `ClearingSequence(7)`.

When `client.save` returns `'{"error": "halted"}'`, `PersistPositionInterpreter.execute` returns a `RefusedPosition` whose `reason` is `RefusalReason.HALTED`.

When `client.save` returns `'{"status": "ok"}'`, the constructor raises `ValidationError`, and it passes out of `execute` as it is. So does anything the client raises, and so do `CancelledError`, `KeyboardInterrupt`, and `SystemExit`.

In the file:

- `arbitrary_types_allowed=True` is in this `model_config`, for the `client` field typed as the imported `PositionClient`.
- The outcome is constructed from the action and the reply: a `PositionSubmission` holding `self.action.position` and the constructed `ClearingReply`, read as `.outcome`.
- Constructing the interpreter calls nothing; `execute` is called in `receive_fill`.
- Placement: `integration/clearing/interpreter.py`.
