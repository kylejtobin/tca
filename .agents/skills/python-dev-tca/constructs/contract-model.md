---
type: Construct
description: "Shape and configuration of this program's published request or reply."
---

# Contract model

The reply this program publishes, holding exactly the facts it sends:

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
```

The egress route gives the outcome to the union and serializes the contract:

```python
    def emit(self) -> str:
        return FillReplyConstructor.validate_python(
            self.outcome, from_attributes=True
        ).model_dump_json(by_alias=True)
```

Constructed:

`FillReplyConstructor.validate_python(PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"sequence": 7}}').outcome, from_attributes=True)` is a `FillBooked` whose `sequence` is `ClearingSequence(7)` and whose `net_quantity` is `NetQuantity(Decimal("3"))`.

`FillReplyConstructor.validate_python(PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"error": "halted"}}').outcome, from_attributes=True)` is a `FillDeclined` whose `reason` is `RefusalReason.HALTED`.

`FillReplyRoute(outcome=PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"sequence": 7}}').outcome).emit()` is `'{"sequence":7,"net_quantity":"3"}'`.

`FillReplyRoute(outcome=PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"error": "halted"}}').outcome).emit()` is `'{"reason":"halted"}'`.

In the file:

- Every field is a declared semantic type under the domain's name for it: `sequence`, `net_quantity`, `reason`.
- Each field is lifted from the outcome by its name or an `AliasPath`: `sequence` from `recorded.sequence`, `net_quantity` from `recorded.position.net_quantity`.
- A published request is the field of its ingress route, constructed by `receive` before anything reads it.
- A published name that differs from the field's name is a `serialization_alias` on that field.
- A fact derived from the contract's own fields is a `@computed_field` returning a constructed value.
- Where the published shape is the domain thing's own, the domain thing is published as it is.
- Placement: `domain/venue/api.py`.
