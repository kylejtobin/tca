---
type: Construct
description: "What this program needs to reach another system, as the deployment names it: its address and credential, whose one derivation is its client, which keeps nothing between crossings. Holds semantic scalars. It holds what the deployment names and the library does not read for itself: httpx reads nothing, so an address and a key. Where the deployment names one of several, their union, picked by shape. It is strict, as every class is; the settings source decodes the environment's text against its fields. Its client is acquired by the interpreter that uses it, for one crossing. Lives in integration/<system>/provider.py."
---

```python
# integration/promotions/provider.py
import httpx
from pydantic import BaseModel, ConfigDict

from integration.promotions.model import DiscountsUrl


class Promotions(BaseModel):
    """The promotions system, at the address of its discounts."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    url: DiscountsUrl

    @property
    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.url.root)
```

```python
# integration/payments/provider.py
import httpx
from pydantic import BaseModel, ConfigDict, RootModel

from integration.payments.model import (
    CardProviderName,
    InvoiceProviderName,
    ProviderKey,
    ProviderUrl,
)


class CardPayments(BaseModel):
    """The card provider, at its address, under the shop's key."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    provider: CardProviderName
    url: ProviderUrl
    key: ProviderKey

    @property
    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.url.root,
            auth=(self.key.root.get_secret_value(), ""),
            headers=(("Content-Type", "application/json"),),
        )


class InvoicePayments(BaseModel):
    """The invoicing provider, at its address."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    provider: InvoiceProviderName
    url: ProviderUrl

    @property
    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.url.root,
            headers=(("Content-Type", "application/json"),),
        )


class Payments(RootModel[CardPayments | InvoicePayments]):
    """The payment provider the deployment names, with what that provider takes."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )

    @property
    def client(self) -> httpx.AsyncClient:
        return self.root.client
```

```python
# integration/catalog_index/provider.py
import httpx
from pydantic import BaseModel, ConfigDict

from integration.catalog_index.model import CollectionUrl


class CatalogIndex(BaseModel):
    """The catalog's collection in the index, at its address."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    url: CollectionUrl

    @property
    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.url.root,
            headers=(("Content-Type", "application/json"),),
        )
```
