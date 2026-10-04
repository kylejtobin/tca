---
type: Construct
description: "Another system's thing, under its names, as it sends it or accepts it. Holds semantic scalars and other foreign models. Lives in integration/<system>/model.py."
---

```python
# integration/payments/model.py
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from domain.shop.type import (
    Amount, CardToken, ChargeId, Currency, DeclineReasons, OrderId, ProviderError,
)


class ChargeRequest(BaseModel):
    """The charge the payment provider accepts."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    amount: Amount = Field(serialization_alias="amt")
    currency: Currency = Field(serialization_alias="cur")
    card: CardToken = Field(serialization_alias="src")
    id: OrderId = Field(serialization_alias="ref")


class ChargeApproved(BaseModel):
    """The payment provider's reply that it made the charge."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    charge: ChargeId = Field(alias="id")


class ChargeDeclined(BaseModel):
    """The payment provider's reply that it declined the charge."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    reasons: DeclineReasons = Field(alias="decline_codes")


class ChargeFailed(BaseModel):
    """The payment provider's reply that it could not attempt the charge."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    error: ProviderError


ChargeReply = ChargeApproved | ChargeDeclined | ChargeFailed
ChargeReplyConstructor: TypeAdapter[ChargeReply] = TypeAdapter(ChargeReply)
```
