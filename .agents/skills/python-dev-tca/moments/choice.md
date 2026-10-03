---
type: Moment
description: "What to write when about to check a condition: a union whose variant construction picks, with the differing behavior as a same-named derivation on each variant."
---

# Choice

You are about to write:

```python
if isinstance(state, FlatPosition):
    net = Decimal(0)
```

Declare each answer as a thing, and put the differing behavior on each under one name:

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


PositionState = FlatPosition | Position
PositionStateConstructor: TypeAdapter[PositionState] = TypeAdapter(PositionState)
```

`self.prior.net_quantity`, `self.prior.account`, and `self.prior.instrument` read the same name on whichever variant `prior` is.

A choice among the members of one vocabulary is the case table in `Position.net_quantity`, with every member of `Side` as a key:

```python
class Side(StrEnum):
    """The direction of an order."""

    BUY = "buy"
    SELL = "sell"
```

A check that two fields agree is the fields themselves: store the independent one and the difference, and derive the other.

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

A choice made from another thing is a union given that thing:

```python
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

`PositionStateConstructor.validate_json('{"account": "A1", "instrument": "ESZ6"}')` is a `FlatPosition`, and its `net_quantity` is `NetQuantity(Decimal(0))`.

`PositionStateConstructor.validate_json('{"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "sell", "price": "101.5", "quantity": "3"}}')` is a `Position`, and its `net_quantity` is `NetQuantity(Decimal("-3"))`.

`PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"error": "halted"}}').outcome` is a `RefusedPosition`, and the `FillReplyRoute` holding it emits `'{"reason":"halted"}'`.

`Bids.model_validate_json("[]").top` is `NoBids`.

`Quote.model_validate_json('{"bid": "101.5", "spread": "0.25"}').ask` is `Price(Decimal("101.75"))`.

`Quote.model_validate_json('{"bid": "101.5", "spread": "-0.25"}')` raises `ValidationError`: a quote whose ask is below its bid has no representation.

In the file:

- Each answer to the question is a class, and the union alias names the question: `PositionState = FlatPosition | Position`.
- Each variant has the derivation the consumer reads, under one name and one return type: `FlatPosition.net_quantity`, `Position.net_quantity`.
- The class tells the variants apart: `FlatPosition` holds `account` and `instrument`; `Position` holds `prior` and `fill`.
- A choice among the members of `Side` is the case table `{Side.BUY: 1, Side.SELL: -1}[self.fill.side]`, with every member as a key.
- A choice made from another thing is a union's constructor given that thing: `FillReplyConstructor.validate_python(self.outcome, from_attributes=True)`.
- A relation between two fields is carried by which fields are stored: `Quote` holds `bid` and `spread`, and `ask` is a derivation.
