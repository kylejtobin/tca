---
type: Construct
description: "Shape and configuration of one atomic meaning over a primitive or a closed vocabulary."
---

# Semantic scalar

Over a primitive, with its bound in `Field`:

```python
class Price(RootModel[Decimal]):
    """The amount per unit at which an instrument trades, above zero."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: Decimal = Field(gt=0, decimal_places=8)


class Quantity(RootModel[Decimal]):
    """The number of units executed or resting, above zero."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: Decimal = Field(gt=0)


class Spread(RootModel[Decimal]):
    """The width between a quote's bid and its ask, zero or more."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: Decimal = Field(ge=0)


class Depth(RootModel[Decimal]):
    """The quantity resting across the bids, zero or more."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: Decimal = Field(ge=0)


class ClearingSequence(RootModel[int]):
    """The number the clearing house assigns to a record."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: int = Field(ge=1)
```

Over a primitive with no bound, with a docstring saying every value is valid:

```python
class NetQuantity(RootModel[Decimal]):
    """A signed holding; negative is short. Every Decimal is a net quantity."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
```

Over a string, one class for each meaning:

```python
class AccountId(RootModel[str]):
    """The identity of an account."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class InstrumentId(RootModel[str]):
    """The identity of an instrument."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class OrderId(RootModel[str]):
    """The identity of an order."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class VenueUrl(RootModel[str]):
    """The address of the clearing house."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: str = Field(min_length=1)
```

A closed vocabulary:

```python
class Side(StrEnum):
    """The direction of an order."""

    BUY = "buy"
    SELL = "sell"


class RefusalReason(StrEnum):
    """Why the clearing house declined a record."""

    HALTED = "halted"
    STALE = "stale"
```

Constructed:

`Price(Decimal("101.5"))` is a `Price`.

`Price.model_validate_json('"101.5"')` is `Price(Decimal("101.5"))`.

`Price(Decimal("0"))` raises `ValidationError`: `gt=0`.

`Fill.model_validate_json('{"order_id": "O1", "account": "A1", "instrument": "ESZ6", "side": "buy", "price": "101.5", "quantity": "3"}').side` is `Side.BUY`: JSON gives the member's value, `"buy"`.

`Bid(price=Price(Decimal("101.5")), quantity=Quantity(Decimal("3")))` is a `Bid`: Python, under `strict=True`, gives each field its constructed type, and gives `Side.BUY` for a `Side`.

In the file:

- Every field of every model is a semantic scalar, another model, a union alias, a tuple of those, or `SecretStr`.
- Each meaning has its own class: `AccountId`, `InstrumentId`, and `OrderId` are three classes over `str`.
- Every bound is in `Field` on `root`: `gt=0`, `ge=1`, `min_length=1`.
- `NetQuantity` has no bound, and its docstring says every `Decimal` is one.
- A closed vocabulary is a `StrEnum`, used directly as the field's type: `side: Side`.
- `.root` is read inside a derivation, a route, an interpreter, or `main.py`, where the primitive is used at once.
- Placement: `domain/venue/type.py`.
