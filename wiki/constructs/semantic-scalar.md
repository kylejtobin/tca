---
type: Construct
description: One atomic meaning over a primitive or a closed value space.
---

# Semantic Scalar

## Definition

One atomic program meaning whose value space is primitive, constrained primitive, or closed vocabulary. If the value has no independent meaning, it stays inside its owning construct.

## Required Form

```python
class Price(RootModel[Decimal]):
    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: Decimal = Field(gt=0, decimal_places=8)


class Spread(RootModel[Decimal]):
    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: Decimal = Field(ge=0)


class NetQuantity(RootModel[Decimal]):
    """Signed holding; negative is short."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )


class Side(StrEnum):
    BUY = "buy"
    SELL = "sell"
```

- A frozen `RootModel[P]` wraps a primitive; a `StrEnum` is a closed string vocabulary on its own, and wrapping it again is a second structure for one meaning.
- In strict Python construction, pass the enum member (`Side.BUY`), not raw `"buy"`. JSON accepts that string and constructs the member; acceptance in JSON mode does not grant Python-mode coercion.
- Every bound goes in `Field`; an open range has a docstring stating that every primitive value is valid.
- The scalar itself crosses semantic boundaries. `.root` is read only inside a transformation, route, interpreter, or composition-root expression that immediately consumes the primitive.

## Forbidden

- the same scalar type for values with different meanings
- a scalar for an incidental primitive
- a bare primitive where a semantic scalar is required
- a `StrEnum` wrapped again unless the wrapper adds a different meaning
- a branch to enforce a bound after construction
