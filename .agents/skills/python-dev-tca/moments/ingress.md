---
type: Moment
description: "What to write when another system sends something: its shape declared as a foreign model or route, and the raw input handed to the constructor."
---

# Ingress

You are about to write:

```python
body = json.loads(raw)
fill = Fill(price=Decimal(body["data"]["payload"]["price"]), ...)
```

Declare the message's shape, and give the whole raw message to the constructor:

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

Declare the other system's own thing where its names differ, with its names as aliases:

```python
class ClearingRefusal(BaseModel):
    """The clearing house's reply declining a record, with its reason."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    reason: RefusalReason = Field(alias="error")
```

What the other system sent, and the constructor it is given to:

| The other system sent | It is given to |
|---|---|
| the venue's fill message, a JSON string | `FillRoute.receive(raw)` |
| the clearing house's reply to a record, a JSON string | `ClearingReplyConstructor.validate_json(raw)` |
| the clearing house's answer to a read, a JSON string | `PositionStateConstructor.validate_json(raw)` |
| a constructed thing with attributes | `TopBidConstructor.validate_python(self, from_attributes=True)` |

Add the rows:

| name | is | holds | kind |
|---|---|---|---|
| FillRoute | The crossing where the venue's fill enters. | Fill | route |
| ClearingRefusal | The clearing house's reply declining a record, with its reason. | RefusalReason | foreign model |

The hard case, constructed:

`FillRoute.receive('{"data": {"payload": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}}').fill` is a `Fill` whose `side` is `Side.BUY` and whose `price` is `Price(Decimal("101.5"))`.

`FillRoute.receive('{"data": {"payload": {"order_id": "O1"}}}')` raises `ValidationError`: no `Fill` is constructed, and no part of the message is held.

`FillRoute.receive('{"data": {"payload": {"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}}, "trace": "x"}')` raises `ValidationError`: `extra="forbid"`.

`ClearingReplyConstructor.validate_json('{"error": "halted"}')` is a `ClearingRefusal` whose `reason` is `RefusalReason.HALTED`.

`Bid(price=Price(Decimal("101.5")), quantity=Quantity(Decimal("3")))` is a `Bid`: in Python, under `strict=True`, each field is given its constructed type, and `Side.BUY` is given for a `Side`.

In the file:

- `receive` is one `return` of `cls.model_validate_json(raw)`.
- One route is constructed from the whole message, and its field is the thing the message holds: `FillRoute.fill` is a `Fill`.
- Each wrapper the message nests its thing under is a step in `AliasPath("data", "payload")`.
- Each of the other system's names sits inside `alias=`, `validation_alias=`, or `AliasPath`: `Field(alias="error")`.
- Every field of the constructed `Fill` is already its semantic type: `Side`, `Price`, `Quantity`.
- `FillRoute` holds the domain `Fill` itself, because the venue's fill has the `Fill` shape; `ClearingRefusal` is its own class, because the clearing house says `error`.
