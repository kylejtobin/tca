---
type: Construct
description: "A strong alternative whose only failure to construct means the fallback; the fallback admits only what the strong alternative does not, so each holds exactly its meaning, constructed alone or in the union. Holds its variants. Lives beside them."
---

```python
# domain/shop/type.py
from typing import Annotated, Self

from pydantic import ConfigDict, Field, RootModel, model_validator


class UnlistedReason(RootModel[str]):
    """A decline reason the payment provider gave that this program has no word for."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)

    @model_validator(mode="after")
    def no_word_for_it(self) -> Self:
        if not all(reason != self.root for reason in DeclineReason):
            raise ValueError(Invariant.UNLISTED_REASON)
        return self


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

    @model_validator(mode="after")
    def no_word_for_it(self) -> Self:
        if not all(error != self.root for error in ProviderError):
            raise ValueError(Invariant.UNLISTED_ERROR)
        return self


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
