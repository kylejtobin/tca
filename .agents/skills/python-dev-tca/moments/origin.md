---
type: Moment
description: "Where an identity, a time, or a random value comes from: derived from content, carried by a reply, or read through an interpreter, never called for inside a derivation."
---

# Origin

You are about to write:

```python
record_id = uuid4()
recorded_at = datetime.now()
```

Declare the value as a field or derivation of the thing it belongs to:

| You need | It is | It comes from |
|---|---|---|
| which order a fill executed | `Fill.order_id` | carried by the venue's fill |
| whose position this is, in what | `Position.account`, `Position.instrument` | derived from `prior` |
| the number of a record, and its place in order | `RecordedPosition.sequence` | carried by the clearing house's reply |
| the position as it stood before this fill | `Position.prior` | read through `ReadPositionInterpreter` |
| when something happened | a field on the thing the observing system sent | carried by that system's message or reply |
| a value only the outside can give now, such as the current time or a random draw | the result of an interpreter's `execute` | read through an interpreter, as `Position.prior` is |

Declare a value another system assigns as a field of the thing it sent:

```python
class OrderId(RootModel[str]):
    """The identity of an order."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ClearingSequence(RootModel[int]):
    """The number the clearing house assigns to a record."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: int = Field(ge=1)


class ClearingAcknowledgement(BaseModel):
    """The clearing house's reply accepting a record, with the sequence it assigned."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    sequence: ClearingSequence
```

Declare a value the thing's own fields determine as a derivation:

```python
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

Declare a value only the outside holds as an action naming it by identity, read through its interpreter:

```python
class ReadPosition(BaseModel):
    """The intended reading of one account's position in one instrument from the clearing house."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    account: AccountId
    instrument: InstrumentId


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

The hard case, constructed:

`PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"sequence": 7}}').outcome.sequence` is `ClearingSequence(7)`: the number the clearing house sent.

`PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"error": "halted"}}').outcome` is a `RefusedPosition`. It holds a `reason`, and a refused position has no `sequence` field.

`PositionStateConstructor.validate_json('{"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}').account` is `AccountId("A1")`, read from its `prior`.

`ClearingReplyConstructor.validate_json('{"sequence": 0}')` raises `ValidationError`: `ge=1`.

`ReadPosition(account=AccountId("A1"), instrument=InstrumentId("ESZ6"))` names the position by the two identities the fill carries.

In the file:

- Every identity and number is a field with a semantic scalar type: `Fill.order_id` is `OrderId`, `RecordedPosition.sequence` is `ClearingSequence`.
- Each such field is on a thing another system sent: the venue's `Fill`, the clearing house's `ClearingAcknowledgement`.
- `Position.account` and `Position.instrument` are derivations reading `self.prior`.
- Every `@property` reads `self` and its fields.
- The order of records is `ClearingSequence`, assigned by the clearing house.
- A value only the outside holds is named by an action and returned by its interpreter's `execute`: `ReadPosition`, `ReadPositionInterpreter`.
