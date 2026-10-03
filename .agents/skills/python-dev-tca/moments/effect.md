---
type: Moment
description: "What to write when asking another system for something: the action as a thing, one interpreter, one request, and the raw reply constructed as a union."
---

# Effect

You are about to write:

```python
response = requests.post(url, json=position.dict())
response.raise_for_status()
```

Declare what is asked for as a thing that holds what the request needs:

```python
class PersistPosition(BaseModel):
    """The intended recording of a position in the clearing house."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    position: Position


class ReadPosition(BaseModel):
    """The intended reading of one account's position in one instrument from the clearing house."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    account: AccountId
    instrument: InstrumentId
```

The fact that authorizes the action constructs it: `Position.persistence` is `PersistPosition(position=self)`.

Declare one interpreter for each action. It holds the action and the client, and `execute` gives the raw reply to the union:

```python
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

The client is bound once, in `main.py`:

```python
config = VenueConfig()
client = PositionClient(config.url.root, config.token.get_secret_value())
```

The hard case, constructed:

`PositionStateConstructor.validate_json('{"prior": {"account": "A1", "instrument": "ESZ6"}, "fill": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}').persistence` is a `PersistPosition` holding that `Position`. The client has not been called.

When `client.load` returns `'{"account": "A1", "instrument": "ESZ6"}'` and `client.save` returns `'{"sequence": 7}'`, `receive_fill(FillRoute.receive('{"data": {"payload": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}}')).emit()` is `'{"sequence":7,"net_quantity":"3"}'`.

When `client.save` returns `'{"error": "halted"}'`, the same expression is `'{"reason":"halted"}'`.

When `client.load` returns `'{"account": "A1", "instrument": "ESZ6"}'`, `ReadPositionInterpreter.execute` returns a `FlatPosition`: the account has no fills.

When `client.save` raises, the exception passes out of `execute` and `receive_fill` as it is.

In the file:

- Each action's name is the intended effect, and it holds what the request needs: `PersistPosition.position`, `ReadPosition.account`, `ReadPosition.instrument`.
- Each action has one interpreter class, named for the action and `Interpreter`.
- Each interpreter has two fields: `action`, and `client` typed as the imported `PositionClient` with `Field(exclude=True, repr=False)`.
- `execute` is one `return`: one call on `self.client`, with its raw reply given to a union's constructor.
- `.root` and `model_dump_json` are called at the client call.
- `Position.persistence` constructs the `PersistPosition`, and `receive_fill` passes it to the interpreter.
- `PositionClient` is imported in `integration/clearing/interpreter.py` and `main.py`.
