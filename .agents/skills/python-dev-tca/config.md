---
type: Construct
description: "Deployment input: one BaseSettings whose fields are the providers this program reaches and the value objects a deployment may set, named by the environment, nested; absence is the declared default. Strict as every class is: the settings source decodes the environment's text against each field's type. Holds providers and value objects. Lives in config.py."
---

```python
# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

from domain.shop.value import Recommending
from integration.catalog_index.provider import CatalogIndex
from integration.payments.provider import Payments
from integration.promotions.provider import Promotions


class ShopConfig(BaseSettings):
    """What the deployment sets: the systems the shop reaches, and how a recommendation is drawn."""

    model_config = SettingsConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        env_prefix="SHOP_",
        env_nested_delimiter="__",
    )
    promotions: Promotions
    payments: Payments
    catalog: CatalogIndex
    recommending: Recommending = Recommending()
```

```text
SHOP_PROMOTIONS__URL=https://promotions.example/discounts/
SHOP_PAYMENTS__PROVIDER=card
SHOP_PAYMENTS__URL=https://payments.example
SHOP_PAYMENTS__KEY=
SHOP_CATALOG__URL=https://index.example/collections/catalog/
SHOP_RECOMMENDING__CLOSENESS=0.8
```
