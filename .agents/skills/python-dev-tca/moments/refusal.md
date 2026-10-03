---
type: Moment
description: "What to write when something can fail: the refusal as a variant of the reply and of the outcome, constructed, never caught."
---

# Refusal

You are about to write:

```python
try:
    sequence = client.save(position)
except ClearingError:
    return None
```

Declare every reply the clearing house sends, and give the raw reply to the union:

```python
class ClearingAcknowledgement(BaseModel):
    """The clearing house's reply accepting a record, with the sequence it assigned."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    sequence: ClearingSequence


class ClearingRefusal(BaseModel):
    """The clearing house's reply declining a record, with its reason."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    reason: RefusalReason = Field(alias="error")


ClearingReply = ClearingAcknowledgement | ClearingRefusal
ClearingReplyConstructor: TypeAdapter[ClearingReply] = TypeAdapter(ClearingReply)
```

`ClearingReplyConstructor.validate_json('{"sequence": 7}')` is a `ClearingAcknowledgement`.
`ClearingReplyConstructor.validate_json('{"error": "halted"}')` is a `ClearingRefusal`.

Declare what became of the position, one thing for each reply:

```python
class RecordedPosition(BaseModel):
    """A position the clearing house recorded, with the sequence it assigned."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    sequence: ClearingSequence = Field(validation_alias=AliasPath("reply", "sequence"))
    position: Position


class RefusedPosition(BaseModel):
    """A position the clearing house declined to record, with its reason."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    reason: RefusalReason = Field(validation_alias=AliasPath("reply", "reason"))
    position: Position


PositionOutcome = RecordedPosition | RefusedPosition
PositionOutcomeConstructor: TypeAdapter[PositionOutcome] = TypeAdapter(PositionOutcome)


class PositionSubmission(BaseModel):
    """A position sent to the clearing house, with the house's reply to it."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    position: Position
    reply: ClearingReply

    @property
    def outcome(self) -> PositionOutcome:
        return PositionOutcomeConstructor.validate_python(self, from_attributes=True)
```

`PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"sequence": 7}}').outcome` is a `RecordedPosition` whose `sequence` is `ClearingSequence(7)`.

`PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"error": "halted"}}').outcome` is a `RefusedPosition` whose `reason` is `RefusalReason.HALTED`.

The interpreter holds the action and the client, and returns the outcome:

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

Declare the reply this program publishes, one thing for each outcome:

```python
class FillBooked(BaseModel):
    """This program's reply that a fill was booked, with the sequence and the net quantity."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    sequence: ClearingSequence
    net_quantity: NetQuantity = Field(validation_alias=AliasPath("position", "net_quantity"))


class FillDeclined(BaseModel):
    """This program's reply that a fill was not booked, with the reason."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    reason: RefusalReason


FillReply = FillBooked | FillDeclined
FillReplyConstructor: TypeAdapter[FillReply] = TypeAdapter(FillReply)


class FillReplyRoute(BaseModel):
    """The crossing where this program's reply to a fill leaves."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    outcome: PositionOutcome

    def emit(self) -> str:
        return FillReplyConstructor.validate_python(
            self.outcome, from_attributes=True
        ).model_dump_json(by_alias=True)
```

The hard case, constructed:

`ClearingReplyConstructor.validate_json('{"error": "stale"}')` is a `ClearingRefusal` whose `reason` is `RefusalReason.STALE`.

`FillReplyRoute(outcome=PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"error": "halted"}}').outcome).emit()` is `'{"reason":"halted"}'`.

`FillReplyRoute(outcome=PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"sequence": 7}}').outcome).emit()` is `'{"sequence":7,"net_quantity":"3"}'`.

`ClearingReplyConstructor.validate_json('{"status": "ok"}')` raises `ValidationError`: a reply the clearing house never declared constructs neither variant, and the error passes out of `execute` and `receive_fill` as it is.

In the file:

- `execute` is one `return`, and `ClearingRefusal` appears in the reply union.
- `RefusedPosition` appears in the outcome union, and `FillDeclined` in the published union.
- The raw reply from `self.client.save` goes straight into `ClearingReplyConstructor.validate_json`.
- `RefusalReason` is a `StrEnum` with a member for every reason the clearing house sends: `HALTED`, `STALE`.
- `RefusedPosition` holds the `Position` that was sent, beside the `reason`.
