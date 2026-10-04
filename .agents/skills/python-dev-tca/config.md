---
type: Construct
description: "Deployment input, constructed once. Holds semantic scalars and secrets. Lives in config.py."
---

```python
# config.py
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from domain.shop.type import ProviderUrl


class ShopConfig(BaseSettings):
    """The deployment's addresses for the promotions system and the payment provider, and the provider's key."""

    model_config = SettingsConfigDict(
        frozen=True, extra="forbid", strict=False,
        validate_default=True, revalidate_instances="never",
        env_prefix="SHOP_",
    )
    promotions_url: ProviderUrl
    payments_url: ProviderUrl
    payments_key: SecretStr
```
