---
type: Moment
description: "What to write when about to keep something between arrivals: nothing is kept; each arrival reads its prior and constructs its successor."
---

# Arrival

You are about to write:

```python
positions: dict[tuple[str, str], Position] = {}
positions[key] = positions[key].apply(fill)
```

Declare the read of the prior as an action and its interpreter. The clearing house holds every position, and each arrival reads its prior from there and constructs its successor:

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

`main.py`, whole:

```python
config = VenueConfig()
client = PositionClient(config.url.root, config.token.get_secret_value())


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

The registration, made once with the framework the application already has:

```text
Input constructor:   FillRoute.receive
Callback:            receive_fill
Output serializer:   FillReplyRoute.emit
```

Add the rows:

| name | is | holds | kind |
|---|---|---|---|
| ReadPosition | The intended reading of one account's position in one instrument from the clearing house. | AccountId, InstrumentId | action |
| ReadPositionInterpreter | The one place the clearing house is asked for a position. | ReadPosition, PositionClient | effect interpreter |

The hard case, constructed:

On an account's first fill, `client.load` returns `'{"account": "A1", "instrument": "ESZ6"}'` and `client.save` returns `'{"sequence": 7}'`. `receive_fill(FillRoute.receive('{"data": {"payload": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}}')).emit()` is `'{"sequence":7,"net_quantity":"3"}'`, and the `Position` it recorded holds a `FlatPosition` as `prior`.

On the second fill, `client.load` returns `'{"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}'` and `client.save` returns `'{"sequence": 8}'`. `receive_fill(FillRoute.receive('{"data": {"payload": {"order_id": "O2", "account": "A1", "instrument": "ESZ6", "side": "sell", "price": "101.75", "quantity": "5"}}}')).emit()` is `'{"sequence":8,"net_quantity":"-2"}'`, and the `Position` it recorded holds the first `Position` as `prior`.

When `client.save` returns `'{"error": "stale"}'`, the same expression is `'{"reason":"stale"}'`. The next arrival reads its prior from the clearing house again.

When `client.load` raises, the exception passes out of `receive_fill` as it is.

In the file:

- `main.py` has one `def`, `receive_fill`, and its body is one `return`.
- Module scope in `main.py` binds two names: `config` and `client`.
- `Position.prior` is given the result of `ReadPositionInterpreter.execute`, inside the returned expression, on every arrival.
- `ReadPosition` holds the two identities the fill carries: `message.fill.account`, `message.fill.instrument`.
- The `PositionOutcome` is held by the returned `FillReplyRoute`.
- `FillRoute.receive`, `receive_fill`, and `FillReplyRoute.emit` are registered once.
