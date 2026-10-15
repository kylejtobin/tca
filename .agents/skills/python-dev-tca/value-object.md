---
type: Construct
description: "A composite part with no standing of its own, equal when its fields are equal; it may name an identity, as an approval names its charge, without being what the domain acts on. Holds semantic scalars and value objects. Lives in domain/<context>/value.py."
---

```python
# domain/shop/value.py
from pydantic import BaseModel, ConfigDict, Field, RootModel

from domain.shop.type import (
    Amount,
    Category,
    ChargeId,
    Closeness,
    DeclineReasons,
    ProductsPerAisle,
    AisleLimit,
    Percent,
    Quantity,
    Similarity,
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
class AisleMatch(BaseModel):
    """A product the catalog found close to an order, and how alike it is."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    sku: Sku
    similarity: Similarity


class Aisle(BaseModel):
    """One aisle a recommendation draws from, and the products it recommends there."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    category: Category
    matches: AisleMatches
```

```python
# domain/shop/value.py
class Recommending(BaseModel):
    """How a recommendation is drawn: how close a product must be, how many per aisle, from how many aisles."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    closeness: Closeness = Closeness()
    per_aisle: ProductsPerAisle = ProductsPerAisle()
    aisles: AisleLimit = AisleLimit()
```
