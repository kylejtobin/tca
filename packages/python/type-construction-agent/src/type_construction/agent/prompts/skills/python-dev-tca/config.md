---
type: Construct
description: "Deployment input, constructed once. Holds semantic scalars. A provider's settings are a config part constructed from the settings by shared names, whose one derivation is its client; when the deployment names one of several providers, their parts are a union picked by shape. Lives in config.py."
---

```python
# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

from domain.shop.type import CollectionUrl, ProviderKey, ProviderUrl


class ShopConfig(BaseSettings):
    """The deployment's addresses for the promotions system and the payment provider, and the provider's key."""

    model_config = SettingsConfigDict(
        frozen=True,
        extra="forbid",
        strict=False,
        validate_default=True,
        revalidate_instances="never",
        env_prefix="SHOP_",
    )
    promotions_url: CollectionUrl
    payments_url: ProviderUrl
    payments_key: ProviderKey
```

```python
# config.py
import httpx
from pydantic import BaseModel, ConfigDict, RootModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_settings import BaseSettings, SettingsConfigDict

from domain.shop.type import (
    BlankPassword,
    CardProviderName,
    CollectionUrl,
    FieldName,
    InvoiceProviderName,
    MediaType,
    ModelName,
    ProviderKey,
    ProviderUrl,
    Unset,
)


class CardPayments(BaseModel):
    """Payments taken by card, at the card provider's address, under its key."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    payments_provider: CardProviderName
    payments_url: ProviderUrl
    payments_key: ProviderKey

    @property
    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.payments_url.root, auth=(self.payments_key.root, BlankPassword().root)
        )


class InvoicePayments(BaseModel):
    """Payments taken by invoice, at the invoicing provider's address."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    payments_provider: InvoiceProviderName
    payments_url: ProviderUrl

    @property
    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.payments_url.root)


class Payments(RootModel[CardPayments | InvoicePayments]):
    """The payment provider the deployment names, with the credentials that provider takes."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def client(self) -> httpx.AsyncClient:
        return self.root.client


class Notices(BaseModel):
    """The model that writes the shop's notices, at Anthropic, under the shop's key."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    notices_model: ModelName
    notices_key: ProviderKey

    @property
    def client(self) -> AnthropicModel:
        return AnthropicModel(
            self.notices_model.root, provider=AnthropicProvider(api_key=self.notices_key.root)
        )


class CatalogIndex(BaseModel):
    """The catalog's collection in the index, at its address."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    index_collection_url: CollectionUrl

    @property
    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.index_collection_url.root,
            headers=((FieldName.CONTENT_TYPE, MediaType.JSON),),
        )


class ShopConfig(BaseSettings):
    """The deployment's addresses, its payment provider, its notice model, and their credentials."""

    model_config = SettingsConfigDict(
        frozen=True,
        extra="forbid",
        strict=False,
        validate_default=True,
        revalidate_instances="never",
        env_prefix="SHOP_",
    )
    promotions_url: CollectionUrl
    payments_provider: CardProviderName | InvoiceProviderName
    payments_url: ProviderUrl
    payments_key: ProviderKey | Unset = Unset()
    notices_model: ModelName
    notices_key: ProviderKey
    index_collection_url: CollectionUrl

    @property
    def payments(self) -> Payments:
        return Payments.model_validate(self)

    @property
    def notices(self) -> Notices:
        return Notices.model_validate(self)

    @property
    def catalog(self) -> CatalogIndex:
        return CatalogIndex.model_validate(self)
```
