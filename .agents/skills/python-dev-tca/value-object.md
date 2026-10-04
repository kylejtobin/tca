---
type: Construct
description: "A frozen product with no identity, equal when its fields are equal. Holds semantic scalars and value objects. Lives in domain/<context>/value.py."
---

```python
# domain/shop/value.py
from pydantic import BaseModel, ConfigDict, Field, RootModel

from domain.shop.type import (
    Amount, ChargeId, DeclineReasons, Percent, ProviderError, Quantity, Sku, UnitPrice,
)


class Line(BaseModel):
    """A quantity of one product at a unit price."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    sku: Sku
    unit_price: UnitPrice
    quantity: Quantity

    @property
    def amount(self) -> Amount:
        return Amount(self.unit_price.root * self.quantity.root)


class Discount(BaseModel):
    """The share of an order's total taken off for its customer."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    percent: Percent


class Approval(BaseModel):
    """A charge that was made."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    charge: ChargeId


class Decline(BaseModel):
    """A charge that was refused, and why."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    reasons: DeclineReasons


class Failure(BaseModel):
    """A charge that could not be attempted, and why."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    error: ProviderError
```
