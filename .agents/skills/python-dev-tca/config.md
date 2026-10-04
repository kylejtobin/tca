---
type: Construct
description: "Deployment input, constructed once. Holds semantic scalars. Lives in config.py."
---

```python
# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

from domain.shop.type import ProviderKey, ProviderUrl


class ShopConfig(BaseSettings):
    """The deployment's addresses for the promotions system and the payment provider, and the provider's key."""

    model_config = SettingsConfigDict(
        frozen=True, extra="forbid", strict=False,
        validate_default=True, revalidate_instances="never",
        env_prefix="SHOP_",
    )
    promotions_url: ProviderUrl
    payments_url: ProviderUrl
    payments_key: ProviderKey
```
