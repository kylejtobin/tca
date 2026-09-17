---
type: Reference
description: How one admitted atomic meaning is constructed over a primitive or closed value space. Read when a value has independent identity, vocabulary, units, or constraints.
---

# Semantic Scalar

## Use

Use for one atomic program meaning whose value space is primitive, constrained primitive, or closed vocabulary. If the value has no independent meaning, keep it inside its owning construct.

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

- Use frozen `RootModel[P]` when the meaning wraps a primitive.
- Use `StrEnum` when the meaning is exactly a closed string vocabulary.
- In strict Python construction, pass the enum member (`Side.BUY`), not raw `"buy"`. JSON accepts that string and constructs the member; acceptance in JSON mode does not grant Python-mode coercion. Keep the scalar strict.
- Put every bound in `Field`; an open range has a docstring stating that every primitive value is valid.
- Pass the scalar itself across semantic boundaries. Read `.root` only inside a transformation, route, interpreter, or composition root that immediately consumes the primitive.

## Do Not

- use the same scalar type for values with different meanings
- create a scalar for an incidental primitive
- use a bare primitive where a semantic scalar is required
- wrap a `StrEnum` again unless the wrapper adds a different meaning
- branch to enforce a bound after construction
