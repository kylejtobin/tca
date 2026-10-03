---
type: Construct
description: "Shape and configuration of a full domain thing, refinement, or durable fact, including the state-transition shape with a self-typed prior."
---

# Concept model

A full domain thing:

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
```

A thing with identity, and a refinement that is a kind of it:

```python
class Order(BaseModel):
    """An account's instruction to trade a quantity of one instrument on one side."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    id: OrderId
    account: AccountId
    instrument: InstrumentId
    side: Side
    quantity: Quantity


class LimitOrder(Order):
    """An order with a limit price."""

    limit: Price
```

The state-transition shape, a self-typed `prior` and an opening thing:

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

A durable fact, each holding the earlier fact it is about:

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
```

Constructed:

`PositionStateConstructor.validate_json('{"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}')` is a `Position` whose `prior` is a `FlatPosition`.

`PositionStateConstructor.validate_json('{"prior": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "fill": {"order_id": "O2", "account": "A1", "instrument": "ESZ6", "side": "sell", "price": "101.75", "quantity": "5"}}')` is a `Position` whose `prior` is the first `Position`, whole, and whose `net_quantity` is `NetQuantity(Decimal("-2"))`.

`LimitOrder.model_validate_json('{"id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "quantity": "3", "limit": "101.5"}')` is a `LimitOrder`, and it is an `Order`.

`PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"sequence": 7}}').outcome` is a `RecordedPosition` whose `sequence` is `ClearingSequence(7)`.

In the file:

- The class is the kind: `FlatPosition`, `Position`, and `LimitOrder` are told apart by their class.
- `LimitOrder(Order)` adds `limit: Price` and inherits every field, every derivation, and the `model_config` of `Order`.
- Identity is its own semantic scalar field: `Order.id` is `OrderId`.
- Placement: `domain/venue/<concept>.py`, named for the thing: `fill.py`, `order.py`, `position.py`.
