---
type: Reference
description: "The one table of mandatory Pydantic settings per construct."
---

# Configuration

| The class is | Its base | Its exact settings |
|---|---|---|
| value object, concept model, transformation model, action, contract model, route, union variant | `BaseModel` | `frozen=True`, `extra="forbid"`, `strict=True`, `validate_default=True`, `revalidate_instances="never"` |
| semantic scalar, collection | `RootModel` | `frozen=True`, `strict=True`, `validate_default=True`, `revalidate_instances="never"` |
| foreign model | `BaseModel` | `frozen=True`, `strict=True`, `validate_default=True`, `revalidate_instances="never"`, and `extra` as the source's contract says |
| config | `BaseSettings` | `frozen=True`, `extra="forbid"`, `strict=False`, `validate_default=True`, `revalidate_instances="never"` |
| effect interpreter | `BaseModel` | `frozen=True`, `extra="forbid"`, `strict=True`, `validate_default=True`, `revalidate_instances="never"`, `arbitrary_types_allowed=True` |
| closed vocabulary | `StrEnum` | none |

An owned `BaseModel`:

```python
class Fill(BaseModel):
    """An execution of part of an order at a price and quantity."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
```

A `RootModel`:

```python
class Price(RootModel[Decimal]):
    """The amount per unit at which an instrument trades, above zero."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
```

A foreign `BaseModel`, where the source sends exactly these fields:

```python
class ClearingRefusal(BaseModel):
    """The clearing house's reply declining a record, with its reason."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
```

A `BaseSettings`:

```python
class VenueConfig(BaseSettings):
    """The deployment's address and credential for the clearing house."""

    model_config = SettingsConfigDict(
        frozen=True, extra="forbid", strict=False,
        validate_default=True, revalidate_instances="never",
        env_prefix="VENUE_",
    )
```

An effect interpreter:

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
```

A refinement inherits its parent's settings:

```python
class LimitOrder(Order):
    """An order with a limit price."""

    limit: Price
```

The constructor for each input:

| The input is | The constructor |
|---|---|
| named Python values | `Bid(price=Price(Decimal("101.5")), quantity=Quantity(Decimal("3")))` |
| a JSON string | `FillRoute.receive(raw)`, which is `cls.model_validate_json(raw)` |
| a JSON string for a union alias | `ClearingReplyConstructor.validate_json(raw)` |
| a constructed thing, for a union alias | `PositionOutcomeConstructor.validate_python(self, from_attributes=True)` |
| environment text | `VenueConfig()` |

The serializer for each output, called in a route or an interpreter:

| The output is | The serializer |
|---|---|
| a model, to JSON | `model_dump_json(by_alias=True)` |
| a contract with a `@computed_field`, to be read back | `model_dump_json(by_alias=True, round_trip=True)` |
| a scalar's primitive, at a client call | `.root` |
| a secret, at the client's construction | `.get_secret_value()` |

In the file:

- Every class has the settings of its line in the table above, written out on the class, in this order.
- Every class body is a docstring, `model_config`, fields, and `@property` derivations. A route also has `receive` or `emit`; an interpreter also has `execute`.
- Every field's type is frozen or a `tuple`, so the value is immutable at every level.
- Every value enters through a constructor in the table above.
- A constructed instance given to a field is held as it is: `revalidate_instances="never"`.
- Fields construct when the model does; a `@property` constructs when it is read.
- Every default is a complete value, and its omission means that value.
- `validation_alias` and `AliasPath` name where input sits; `serialization_alias` names output; `alias` names both.
- A `ValidationError` means nothing was constructed, and it passes out as it is.
