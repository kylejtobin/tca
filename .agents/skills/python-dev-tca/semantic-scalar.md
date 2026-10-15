---
type: Construct
description: "One atomic meaning over a primitive, a closed vocabulary or a library's vocabulary, constrained so an invalid value cannot be constructed. Holds a primitive. Lives where its meaning is defined: domain/<context>/type.py, or integration/<system>/model.py when the system's contract or the deployment defines it."
---

```python
# domain/shop/type.py
from enum import StrEnum

from pydantic import ConfigDict, Field, RootModel


class OrderId(RootModel[str]):
    """The identity of an order."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class CustomerId(RootModel[str]):
    """The identity of a customer."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class Sku(RootModel[str]):
    """The identity of a product."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class CardToken(RootModel[str]):
    """The payment provider's name for a customer's card."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ChargeId(RootModel[str]):
    """The payment provider's identity for a charge it made."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class UnitPrice(RootModel[int]):
    """The price of one unit, in minor units of the currency, above zero."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(gt=0)


class Quantity(RootModel[int]):
    """The number of units on a line, above zero."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(gt=0)


class Amount(RootModel[int]):
    """An amount of money in minor units of the currency, zero or more."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(ge=0)


class Percent(RootModel[int]):
    """A share of an amount, in hundredths, from none to all."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(ge=0, le=100)


class Currency(StrEnum):
    """The currency an order is priced in."""

    USD = "usd"
    EUR = "eur"


class DeclineReason(StrEnum):
    """Why the payment provider declined a charge."""

    INSUFFICIENT_FUNDS = "insufficient_funds"
    EXPIRED_CARD = "expired_card"


class ProviderError(StrEnum):
    """Why the payment provider could not attempt a charge."""

    RATE_LIMITED = "rate_limited"
    UNAVAILABLE = "unavailable"
```

```python
# domain/shop/type.py
class Category(RootModel[str]):
    """The aisle of the catalog a product belongs to."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[a-z]+(-[a-z]+)*$")


class Similarity(RootModel[float]):
    """How alike two products are, as the catalog index scores them."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: float = Field(ge=-1, le=1)


class Closeness(RootModel[float]):
    """How alike a product must be to one an order bought to be recommended beside it."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: float = Field(default=0.8, ge=-1, le=1)


class AisleLimit(RootModel[int]):
    """At most how many aisles a recommendation draws from."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(default=4, ge=1)


class ProductsPerAisle(RootModel[int]):
    """How many products a recommendation takes from each aisle."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(default=1, ge=1)


class Invariant(StrEnum):
    """A rule of the shop that construction enforces, in the shop's words."""

    EACH_PRODUCT_ONCE = "a product is recommended once from its aisle"
    EACH_AISLE_ONCE = "an aisle is drawn from once"
    UNLISTED_REASON = "an unlisted decline reason is one the shop has no word for"
    UNLISTED_ERROR = "an unlisted provider error is one the shop has no word for"


class IndexFault(RootModel[str]):
    """Why the catalog index could not answer."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)
```

```python
# integration/payments/model.py
from enum import StrEnum

from pydantic import ConfigDict, Field, RootModel, SecretStr


class ProviderUrl(RootModel[str]):
    """Where the payment provider is."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ProviderKey(RootModel[SecretStr]):
    """The key the payment provider knows the shop by; never shown, never published."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: SecretStr = Field(min_length=1)


class CardProviderName(StrEnum):
    """The card provider, as a deployment names its payment provider."""

    CARD = "card"


class InvoiceProviderName(StrEnum):
    """The invoicing provider, as a deployment names its payment provider."""

    INVOICE = "invoice"
```

```python
# integration/promotions/model.py
from pydantic import ConfigDict, Field, RootModel


class DiscountsUrl(RootModel[str]):
    """Where the promotions system keeps its customers' discounts."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^https?://[^/]+/(.+/)?$")
```

```python
# integration/catalog_index/model.py
from enum import StrEnum
from uuid import UUID

from pydantic import ConfigDict, Field, RootModel


class CollectionUrl(RootModel[str]):
    """Where the catalog index keeps the catalog's collection."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^https?://[^/]+/(.+/)?$")


class PointId(RootModel[UUID]):
    """The catalog index's name for a product."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: UUID


class PointNamespace(RootModel[UUID]):
    """The namespace the catalog index's product names are made in."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: UUID = UUID("6f1c2b8e-3a0d-4c1e-9f57-2d4b8a6e1c33")


class PointVersion(RootModel[int]):
    """The catalog index's revision of a product."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(ge=0)


class QueryTime(RootModel[float]):
    """How long the catalog index took to answer, in seconds."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: float = Field(ge=0)


class IndexStatus(StrEnum):
    """The catalog index's word for an answer it could give."""

    OK = "ok"


class IndexInvariant(StrEnum):
    """A rule of the catalog index's answer that construction enforces."""

    EVERY_HIT_IN_ITS_AISLE = "every hit of a group is in the group's aisle"


class PayloadKey(StrEnum):
    """A field the catalog index keeps beside each product."""

    SKU = "sku"
    CATEGORY = "category"
    CURRENCIES = "currencies"
```
