---
type: World
description: "The example world every page uses: a trading venue's fills, the positions they fold into, and a clearing house that records, refuses, and answers empty."
---

# The venue

## What exists

- An order is an account's instruction to trade a quantity of one instrument on one side. A limit order is an order with a limit price.
- A venue executes orders. Each execution is a fill.
- A fill holds its order, account, instrument, side, price, and quantity.
- A position is one account's holding in one instrument: the fold of its fills. It holds the prior position and one fill.
- A flat position is the holding of an account with no fills. It holds the account and the instrument.
- The bids for an instrument are several, best first. Each bid holds a price and a quantity.
- A quote holds a bid price and a spread. Its ask is the bid plus the spread.
- The top of the bids is the best bid, or no bids. The depth of the bids is the quantity resting across them.
- A clearing house holds every position.
- The clearing house's answer to a read is a position or a flat position.
- The clearing house's reply to a record is an acknowledgement holding a sequence, or a refusal holding a reason: `halted` or `stale`.
- A submission holds a position sent to the clearing house and the house's reply to it.
- A recorded position holds the position and the sequence the clearing house assigned. A refused position holds the position and the reason.
- This program's reply to a fill is booked, holding the sequence and the net quantity, or declined, holding the reason.

## The noun table

| name | is | holds | kind |
|---|---|---|---|
| AccountId | The identity of an account. | a str | semantic scalar |
| InstrumentId | The identity of an instrument. | a str | semantic scalar |
| OrderId | The identity of an order. | a str | semantic scalar |
| Side | The direction of an order. | `buy`, `sell` | semantic scalar |
| Price | The amount per unit at which an instrument trades, above zero. | a Decimal | semantic scalar |
| Quantity | The number of units executed or resting, above zero. | a Decimal | semantic scalar |
| NetQuantity | A signed holding; negative is short. Every Decimal is a net quantity. | a Decimal | semantic scalar |
| Spread | The width between a quote's bid and its ask, zero or more. | a Decimal | semantic scalar |
| Depth | The quantity resting across the bids, zero or more. | a Decimal | semantic scalar |
| ClearingSequence | The number the clearing house assigns to a record. | an int | semantic scalar |
| RefusalReason | Why the clearing house declined a record. | `halted`, `stale` | semantic scalar |
| VenueUrl | The address of the clearing house. | a str | semantic scalar |
| Order | An account's instruction to trade a quantity of one instrument on one side. | OrderId, AccountId, InstrumentId, Side, Quantity | concept model |
| LimitOrder | An order with a limit price. | Order, Price | concept model |
| Fill | An execution of part of an order at a price and quantity. | OrderId, AccountId, InstrumentId, Side, Price, Quantity | concept model |
| FlatPosition | The holding of an account with no fills in an instrument. | AccountId, InstrumentId | concept model |
| Position | One account's holding in one instrument, the fold of its fills. | PositionState, Fill | concept model, state-transition shape |
| PositionState | An account's holding in an instrument. | FlatPosition, Position | union |
| Bid | A resting offer to buy at a price and quantity. | Price, Quantity | value object |
| Quote | A bid price and the spread above it at which an instrument is quoted. | Price, Spread | value object |
| Bids | The resting bids for one instrument, best first. | Bid, several | collection |
| BestBid | The first of the bids. | Bid | concept model |
| NoBids | The book has no resting bids. | nothing | concept model |
| TopBid | The top of the bids. | BestBid, NoBids | ordered union |
| ReadPosition | The intended reading of one account's position in one instrument from the clearing house. | AccountId, InstrumentId | action |
| PersistPosition | The intended recording of a position in the clearing house. | Position | action |
| ClearingAcknowledgement | The clearing house's reply accepting a record, with the sequence it assigned. | ClearingSequence | foreign model |
| ClearingRefusal | The clearing house's reply declining a record, with its reason. | RefusalReason | foreign model |
| ClearingReply | The clearing house's reply to a record. | ClearingAcknowledgement, ClearingRefusal | union |
| PositionSubmission | A position sent to the clearing house, with the house's reply to it. | Position, ClearingReply | transformation |
| RecordedPosition | A position the clearing house recorded, with the sequence it assigned. | ClearingSequence, Position | concept model |
| RefusedPosition | A position the clearing house declined to record, with its reason. | RefusalReason, Position | concept model |
| PositionOutcome | What became of a position sent to the clearing house. | RecordedPosition, RefusedPosition | union |
| FillBooked | This program's reply that a fill was booked, with the sequence and the net quantity. | ClearingSequence, NetQuantity | contract model |
| FillDeclined | This program's reply that a fill was not booked, with the reason. | RefusalReason | contract model |
| FillReply | This program's reply to a fill. | FillBooked, FillDeclined | union |
| FillRoute | The crossing where the venue's fill enters. | Fill | route |
| FillReplyRoute | The crossing where this program's reply to a fill leaves. | PositionOutcome | route |
| ReadPositionInterpreter | The one place the clearing house is asked for a position. | ReadPosition, PositionClient | effect interpreter |
| PersistPositionInterpreter | The one place a position is sent to the clearing house. | PersistPosition, PositionClient | effect interpreter |
| VenueConfig | The deployment's address and credential for the clearing house. | VenueUrl, SecretStr | config |

## The unions

An account's holding in an instrument:

```python
PositionState = FlatPosition | Position
PositionStateConstructor: TypeAdapter[PositionState] = TypeAdapter(PositionState)
```

`PositionStateConstructor.validate_json('{"account": "A1", "instrument": "ESZ6"}')` is a `FlatPosition`.

The clearing house's reply to a record:

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

What became of a position sent to the clearing house:

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
```

This program's reply to a fill:

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

`FillReplyConstructor.validate_python(PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"sequence": 7}}').outcome, from_attributes=True)` is a `FillBooked` whose `sequence` is `ClearingSequence(7)` and whose `net_quantity` is `NetQuantity(Decimal("3"))`.

`FillReplyConstructor.validate_python(PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"error": "halted"}}').outcome, from_attributes=True)` is a `FillDeclined` whose `reason` is `RefusalReason.HALTED`.

The top of the bids:

```python
class BestBid(BaseModel):
    """The first of the bids."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    bid: Bid = Field(validation_alias=AliasPath("root", 0))


class NoBids(BaseModel):
    """The book has no resting bids."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )


TopBid = Annotated[
    BestBid | NoBids,
    Field(union_mode="left_to_right"),
]
TopBidConstructor: TypeAdapter[TopBid] = TypeAdapter(TopBid)
```

## The derivations

A position's account, instrument, and net quantity, and the recording it authorizes:

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


class Position(BaseModel):
    """One account's holding in one instrument, the fold of its fills."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    prior: "FlatPosition | Position"
    fill: Fill

    @property
    def account(self) -> AccountId:
        return self.prior.account

    @property
    def instrument(self) -> InstrumentId:
        return self.prior.instrument

    @property
    def net_quantity(self) -> NetQuantity:
        return NetQuantity(
            self.prior.net_quantity.root
            + {Side.BUY: 1, Side.SELL: -1}[self.fill.side] * self.fill.quantity.root
        )

    @property
    def persistence(self) -> "PersistPosition":
        return PersistPosition(position=self)
```

`PositionStateConstructor.validate_json('{"account": "A1", "instrument": "ESZ6"}').net_quantity` is `NetQuantity(Decimal(0))`.

`PositionStateConstructor.validate_json('{"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}').net_quantity` is `NetQuantity(Decimal("3"))`, and its `account` is `AccountId("A1")`.

`PositionStateConstructor.validate_json('{"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}').persistence` is a `PersistPosition` holding that `Position`.

What became of a position sent to the clearing house:

```python
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

A quote's ask:

```python
class Quote(BaseModel):
    """A bid price and the spread above it at which an instrument is quoted."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    bid: Price
    spread: Spread

    @property
    def ask(self) -> Price:
        return Price(self.bid.root + self.spread.root)
```

`Quote.model_validate_json('{"bid": "101.5", "spread": "0.25"}').ask` is `Price(Decimal("101.75"))`.

`Quote.model_validate_json('{"bid": "101.5", "spread": "-0.25"}')` raises `ValidationError`: a quote whose ask is below its bid has no representation.

The top and the depth of the bids:

```python
class Bids(RootModel[tuple[Bid, ...]]):
    """The resting bids for one instrument, best first."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )

    @property
    def top(self) -> TopBid:
        return TopBidConstructor.validate_python(self, from_attributes=True)

    @property
    def depth(self) -> Depth:
        return Depth(sum((bid.quantity.root for bid in self.root), Decimal(0)))
```

`Bids.model_validate_json("[]").top` is `NoBids`.
`Bids.model_validate_json('[{"price": "101.5", "quantity": "3"}]').top` is a `BestBid` whose `bid` is that `Bid`.
`Bids.model_validate_json("[]").depth` is `Depth(Decimal(0))`.
