---
type: Construct
description: "The site in main.py where bindings are made once and one callback returns one terminal expression."
---

# Composition root

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

The expression, from the inside out:

| The expression | Is |
|---|---|
| `ReadPosition(account=..., instrument=...)` | the position asked for, named by the fill's identities |
| `ReadPositionInterpreter(...).execute()` | the `PositionState` the clearing house holds |
| `Position(prior=..., fill=message.fill)` | the position after this fill |
| `.persistence` | the `PersistPosition` that position authorizes |
| `PersistPositionInterpreter(...).execute()` | the `PositionOutcome` |
| `FillReplyRoute(outcome=...)` | the reply, serialized by `emit` |

Constructed:

When `client.load` returns `'{"account": "A1", "instrument": "ESZ6"}'` and `client.save` returns `'{"sequence": 7}'`, `receive_fill(FillRoute.receive('{"data": {"payload": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}}')).emit()` is `'{"sequence":7,"net_quantity":"3"}'`.

When `client.save` returns `'{"error": "halted"}'`, the same expression is `'{"reason":"halted"}'`.

In both, `receive_fill(FillRoute.receive('{"data": {"payload": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}}')).outcome.position.prior` is a `FlatPosition`: the account's first fill.

In the file:

- Module scope binds two names, once: `config` and `client`. The client lives as long as its own documentation says.
- The callback returns the route itself.
- `main.py` is a site: `config`, `client`, and `receive_fill` have no rows in the noun table.
- Placement: `main.py`.
