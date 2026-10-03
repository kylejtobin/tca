---
type: Moment
description: "What to write when about to name a type: the practitioner's noun for the thing, never the step that produced it."
---

# Naming

You are about to write:

```python
class ParsedFillData(BaseModel): ...
class PersistResult(BaseModel): ...
```

Declare each class under the trader's noun for the thing, with the row's `is` sentence as its docstring:

```python
class Fill(BaseModel):
    """An execution of part of an order at a price and quantity."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    order_id: OrderId
    account: AccountId
    instrument: InstrumentId
    side: Side
    price: Price
    quantity: Quantity


class RecordedPosition(BaseModel):
    """A position the clearing house recorded, with the sequence it assigned."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    sequence: ClearingSequence = Field(validation_alias=AliasPath("reply", "sequence"))
    position: Position
```

The trader's words, and the class:

| A trader says | The class |
|---|---|
| a fill | `Fill` |
| a buy, a sell | `Fill`, holding `side: Side` |
| the position | `Position` |
| a flat position | `FlatPosition` |
| the bids | `Bids` |
| the best bid, no bids | `BestBid`, `NoBids` |
| the top of the bids | `TopBid` |
| the clearing house's reply | `ClearingReply`: `ClearingAcknowledgement` or `ClearingRefusal` |
| the position it recorded, the position it refused | `RecordedPosition`, `RefusedPosition` |
| our reply to the fill | `FillReply`: `FillBooked` or `FillDeclined` |

A crossing is named for the domain noun, then `Route` or `Interpreter`:

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

A file is named for the thing it holds:

```text
domain/venue/type.py                  AccountId, InstrumentId, OrderId, Side, Price, Quantity,
                                      NetQuantity, Spread, Depth, ClearingSequence, RefusalReason, VenueUrl
domain/venue/value.py                 Bid, Quote
domain/venue/order.py                 Order, LimitOrder
domain/venue/fill.py                  Fill
domain/venue/position.py              FlatPosition, Position, PositionState,
                                      ReadPosition, PersistPosition,
                                      RecordedPosition, RefusedPosition, PositionOutcome
domain/venue/bids.py                  Bids, BestBid, NoBids, TopBid
domain/venue/api.py                   FillBooked, FillDeclined, FillReply
```

Add the rows:

| name | is | holds | kind |
|---|---|---|---|
| Fill | An execution of part of an order at a price and quantity. | OrderId, AccountId, InstrumentId, Side, Price, Quantity | concept model |
| RecordedPosition | A position the clearing house recorded, with the sequence it assigned. | ClearingSequence, Position | concept model |

The hard case, constructed:

`Fill.model_validate_json('{"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "sell", "price": "101.5", "quantity": "3"}')` is a `Fill` whose `side` is `Side.SELL`.

`PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"error": "halted"}}').outcome` is a `RefusedPosition`.

`PositionStateConstructor.validate_json('{"account": "A1", "instrument": "ESZ6"}')` is a `FlatPosition`.

`Bids.model_validate_json("[]").top` is `NoBids`.

In the file:

- Every class name is a `name` in the noun table, and its docstring is that row's `is`.
- Every domain class name is a noun a trader says: `Fill`, `Position`, `FlatPosition`, `Bids`.
- The refusal, the flat position, and the empty book each have a class of their own: `RefusedPosition`, `FlatPosition`, `NoBids`.
- One `Fill` class serves both sides, and `Fill.side` holds which.
- Each route's name is the domain noun and `Route`; each effect interpreter's name is the action's name and `Interpreter`.
- Each domain file is named for the thing it holds: `fill.py`, `position.py`, `bids.py`. Scalars are in `type.py`, value objects in `value.py`, contracts in `api.py`.
