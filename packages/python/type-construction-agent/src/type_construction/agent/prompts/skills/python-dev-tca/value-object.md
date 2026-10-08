---
type: Construct
description: "A frozen product with no identity, equal when its fields are equal. Holds semantic scalars and value objects. Lives in domain/<context>/value.py."
---

```python
# domain/shop/value.py
from pydantic import BaseModel, ConfigDict, Field, RootModel

from domain.shop.type import (
    Amount,
    ChargeId,
    DeclineReasons,
    Percent,
    Quantity,
    Sku,
    StatedError,
    UnitPrice,
)


class Line(BaseModel):
    """A quantity of one product at a unit price."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
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
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    percent: Percent


class Approval(BaseModel):
    """A charge that was made."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    charge: ChargeId


class Decline(BaseModel):
    """A charge that was refused, and why."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    reasons: DeclineReasons


class Failure(BaseModel):
    """A charge that could not be attempted, and why."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    error: StatedError
```

```python
# domain/shop/value.py
class Match(BaseModel):
    """A product the catalog found close to an order, in its aisle, and how alike it is."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    sku: Sku
    category: Category
    similarity: Similarity
```

```python
# domain/shop/value.py
class SupportValues(BaseModel):
    """What fills the support agent's prompt: the customer it answers."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    customer: CustomerId
```
