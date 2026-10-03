---
type: Construct
description: "Shape of closed alternatives on one axis, each variant carrying its own facts."
---

# Union

Each variant is a class holding only its own facts. The alias is the union, and its `TypeAdapter` sits beside it:

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

The venue's unions:

```python
PositionState = FlatPosition | Position
PositionStateConstructor: TypeAdapter[PositionState] = TypeAdapter(PositionState)

ClearingReply = ClearingAcknowledgement | ClearingRefusal
ClearingReplyConstructor: TypeAdapter[ClearingReply] = TypeAdapter(ClearingReply)

PositionOutcome = RecordedPosition | RefusedPosition
PositionOutcomeConstructor: TypeAdapter[PositionOutcome] = TypeAdapter(PositionOutcome)

FillReply = FillBooked | FillDeclined
FillReplyConstructor: TypeAdapter[FillReply] = TypeAdapter(FillReply)
```

Behavior that differs by variant is one derivation name on each variant, read from the union value:

```python
class FlatPosition(BaseModel):
    """The holding of an account with no fills in an instrument."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    account: AccountId
    instrument: InstrumentId

    @property
    def net_quantity(self) -> NetQuantity:
        return NetQuantity(Decimal(0))
```

`Position.net_quantity` reads `self.prior.net_quantity`, and `prior` is either variant.

Constructed, from raw input:

`ClearingReplyConstructor.validate_json('{"sequence": 7}')` is a `ClearingAcknowledgement`.

`ClearingReplyConstructor.validate_json('{"error": "halted"}')` is a `ClearingRefusal`.

`PositionStateConstructor.validate_json('{"account": "A1", "instrument": "ESZ6"}')` is a `FlatPosition`.

Constructed, from a thing this program holds:

`PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"sequence": 7}}').outcome` is a `RecordedPosition`, constructed by `PositionOutcomeConstructor.validate_python(self, from_attributes=True)`.

`PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"error": "halted"}}').outcome` is a `RefusedPosition`.

In the file:

- Each union has one alias, with its `TypeAdapter` beside it, named for the alias and `Constructor`.
- Each alias is one axis: `PositionState` is flat or holding; `PositionOutcome` is recorded or refused.
- Each variant is a frozen model with its own docstring, holding the facts of its case.
- The variants differ in their fields, and construction picks by them.
- A `Literal` discriminator field appears where the other system's data carries one.
- A field that may be either is annotated with the union: `Position.prior`, `PositionSubmission.reply`, `FillReplyRoute.outcome`.
- Placement: beside its variants, in their file.
