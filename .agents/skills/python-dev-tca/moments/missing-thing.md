---
type: Moment
description: "What to do when no form fits: a thing is missing from the noun table; name it and find the construct that produces its facts."
---

# Missing thing

You are about to write:

```python
def to_outcome(position: Position, reply: ClearingReply) -> PositionOutcome:
    return RefusedPosition(...) if isinstance(reply, ClearingRefusal) else RecordedPosition(...)
```

Declare the thing that holds the function's parameters, with the function's return value as a derivation on it:

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

What you need, the thing that holds its inputs, and where it is read:

| You need | The thing that holds the inputs | Read it as |
|---|---|---|
| what became of a position, given the reply | `PositionSubmission`, holding `position` and `reply` | `.outcome` |
| the position after a fill | `Position`, holding `prior` and `fill` | the `Position` itself |
| the net holding | `Position` | `.net_quantity` |
| the best bid | `Bids` | `.top` |
| the quantity resting | `Bids` | `.depth` |
| the recording of a position | `Position` | `.persistence`, given to `PersistPositionInterpreter` |
| the prior position | `ReadPosition`, holding `account` and `instrument` | `ReadPositionInterpreter.execute` |
| the fill in a message | `FillRoute`, holding `fill` | `FillRoute.receive` |
| the reply to publish | `FillReplyRoute`, holding `outcome` | `.emit` |

What a derivation's one returned expression may be:

| The expression | In the venue |
|---|---|
| a constructor given fields | `PersistPosition(position=self)` |
| a field or derivation read | `self.prior.account` |
| arithmetic over those | `self.prior.net_quantity.root + {Side.BUY: 1, Side.SELL: -1}[self.fill.side] * self.fill.quantity.root` |
| a fold over a held tuple | `sum((bid.quantity.root for bid in self.root), Decimal(0))` |
| a total case table over a `StrEnum` | `{Side.BUY: 1, Side.SELL: -1}[self.fill.side]` |
| a union given a thing | `PositionOutcomeConstructor.validate_python(self, from_attributes=True)` |
| an ordered union whose only refusal is the fallback | `TopBidConstructor.validate_python(self, from_attributes=True)` |

Add the rows:

| name | is | holds | kind |
|---|---|---|---|
| PositionSubmission | A position sent to the clearing house, with the house's reply to it. | Position, ClearingReply | transformation |

The hard case, constructed:

`PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"sequence": 7}}').outcome` is a `RecordedPosition` whose `sequence` is `ClearingSequence(7)`.

`PositionSubmission.model_validate_json('{"position": {"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "reply": {"error": "halted"}}').outcome` is a `RefusedPosition` whose `reason` is `RefusalReason.HALTED`.

The agreement of `fill.instrument` with `prior.instrument` has no structural form on this substrate. `Position` holds `prior` and `fill` as declared, and the gap is reported in words to the person you are working for.

In the file:

- Each thing a function would have computed is a class holding the function's parameters as fields: `PositionSubmission.position`, `PositionSubmission.reply`.
- The function's return value is a `@property` on that class, taking `self`, with one `return`: `PositionSubmission.outcome`.
- The one `def` at module level is `receive_fill` in `main.py`.
- Every class is a row in the noun table, and every row is a class or an alias.
- Every meaning the program has is one row, and every row is one meaning.
- Each returned expression is built from the rows of the table above.
- The new row's `kind` is one of the forms in `constructs/`: `PositionSubmission` is a transformation.
