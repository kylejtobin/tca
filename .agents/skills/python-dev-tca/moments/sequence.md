---
type: Moment
description: "What to write when about to do one thing and then another: the later fact holds the earlier fact as a field, and construction runs the order."
---

# Sequence

You are about to write:

```python
position = apply_fill(prior, fill)
sequence = client.save(position)
```

Declare the later fact, with the earlier fact as a field:

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


class PersistPosition(BaseModel):
    """The intended recording of a position in the clearing house."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    position: Position


class RecordedPosition(BaseModel):
    """A position the clearing house recorded, with the sequence it assigned."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    sequence: ClearingSequence = Field(validation_alias=AliasPath("reply", "sequence"))
    position: Position
```

The later fact, and the field that holds the earlier fact:

| The later fact | Holds the earlier fact as |
|---|---|
| `Position` | `prior: "FlatPosition \| Position"`, `fill: Fill` |
| `PersistPosition` | `position: Position` |
| `PositionSubmission` | `position: Position`, `reply: ClearingReply` |
| `RecordedPosition`, `RefusedPosition` | `position: Position` |
| `FillReplyRoute` | `outcome: PositionOutcome` |

The whole order is one expression in `main.py`. The innermost construction is the earliest fact:

```python
def receive_fill(message: FillRoute) -> FillReplyRoute:
    return FillReplyRoute(
        outcome=PersistPositionInterpreter(
            action=Position(
                prior=ReadPositionInterpreter(
                    action=ReadPosition(
                        account=message.fill.account,
                        instrument=message.fill.instrument,
                    ),
                    client=client,
                ).execute(),
                fill=message.fill,
            ).persistence,
            client=client,
        ).execute(),
    )
```

Add the rows:

| name | is | holds | kind |
|---|---|---|---|
| Position | One account's holding in one instrument, the fold of its fills. | PositionState, Fill | concept model, state-transition shape |
| PersistPosition | The intended recording of a position in the clearing house. | Position | action |
| RecordedPosition | A position the clearing house recorded, with the sequence it assigned. | ClearingSequence, Position | concept model |

The hard case, constructed:

`PositionStateConstructor.validate_json('{"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}')` is the `Position` after an account's first fill. Its `prior` is a `FlatPosition` and its `fill` is a `Fill`, both constructed by the one call.

`PositionStateConstructor.validate_json('{"prior": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "fill": {"order_id": "O2", "account": "A1", "instrument": "ESZ6", "side": "sell", "price": "101.75", "quantity": "5"}}')` is the `Position` after its second fill. Its `prior` is the first `Position`, whole, and its `net_quantity` is `NetQuantity(Decimal("-2"))`.

`PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"error": "halted"}}').outcome` is a `RefusedPosition` whose `position` is the `Position` that was sent.

In the file:

- `receive_fill` is one `return` of one nested expression.
- Each later fact's class has a field typed as the earlier fact: `Position.prior`, `PersistPosition.position`, `RecordedPosition.position`, `FillReplyRoute.outcome`.
- The innermost call in `receive_fill` constructs `ReadPosition`, and the outermost constructs `FillReplyRoute`.
- Each successor is a new `Position` that holds its predecessor whole as `prior`.
