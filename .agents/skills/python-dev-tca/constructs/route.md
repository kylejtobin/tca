---
type: Construct
description: "Shape of one transport crossing: ingress constructed from the whole message, egress projected from a constructed fact."
---

# Route

Ingress, constructed from the whole message:

```python
class FillRoute(BaseModel):
    """The crossing where the venue's fill enters."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    fill: Fill = Field(validation_alias=AliasPath("data", "payload"))

    @classmethod
    def receive(cls, raw: str) -> "FillRoute":
        return cls.model_validate_json(raw)
```

Egress, holding the constructed fact and projecting the contract from it:

```python
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

Registered once, with the framework the application already has:

```text
Input constructor:   FillRoute.receive
Callback:            receive_fill
Output serializer:   FillReplyRoute.emit
```

Constructed:

`FillRoute.receive('{"data": {"payload": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}}').fill` is a `Fill` whose `side` is `Side.BUY`.

`FillRoute.receive('{"data": {}}')` raises `ValidationError`: no route is constructed.

`FillReplyRoute(outcome=PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"sequence": 7}}').outcome).emit()` is `'{"sequence":7,"net_quantity":"3"}'`.

`FillReplyRoute(outcome=PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"error": "halted"}}').outcome).emit()` is `'{"reason":"halted"}'`.

In the file:

- The name is the domain noun and `Route`: `FillRoute`, `FillReplyRoute`.
- `emit` is one `return`: the contract constructed from the held fact, then `model_dump_json(by_alias=True)`.
- The egress route is its own class, holding the fact the reply is projected from: `outcome: PositionOutcome`.
- A header, a status, or framing the transport carries is a field of the route.
- Placement: `api/venue.py`.
