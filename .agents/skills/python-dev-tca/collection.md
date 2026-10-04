---
type: Construct
description: "Several of one thing, with a meaning of their own, as a frozen tuple. Holds its members. Lives beside them."
---

```python
# domain/shop/type.py
class DeclineReasons(RootModel[tuple[StatedReason, ...]]):
    """Every reason the payment provider gave for declining one charge."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
```

```python
# domain/shop/value.py
class Lines(RootModel[tuple[Line, ...]]):
    """The lines of one order, as the customer sent them."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
    root: tuple[Line, ...] = Field(min_length=1)

    @property
    def amount(self) -> Amount:
        return Amount(sum(line.amount.root for line in self.root))
```
