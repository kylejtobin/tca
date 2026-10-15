---
type: Construct
description: "A strong alternative whose only failure to construct means the fallback. Holds its variants. Lives beside them."
---

```python
# domain/shop/type.py
from typing import Annotated


class UnlistedReason(RootModel[str]):
    """A decline reason the payment provider gave that this program has no word for."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class StatedReason(
    RootModel[Annotated[DeclineReason | UnlistedReason, Field(union_mode="left_to_right")]]
):
    """A reason the payment provider gave for declining a charge."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )


class UnlistedError(RootModel[str]):
    """An error the payment provider gave that this program has no word for."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class StatedError(
    RootModel[Annotated[ProviderError | UnlistedError, Field(union_mode="left_to_right")]]
):
    """An error the payment provider gave for not attempting a charge."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
```
