---
type: Construct
description: "Another system's thing, under its names, parsed from what it sends, serialized to what it accepts. Holds semantic scalars and other foreign models. Lives in integration/<system>/model.py."
---

```python
# integration/payments/model.py
from pydantic import BaseModel, ConfigDict, Field, RootModel

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


class ChargeReply(RootModel[ChargeApproved | ChargeDeclined | ChargeFailed]):
    """The payment provider's reply to a charge."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
```

```python
# integration/promotions/model.py
from pydantic import BaseModel, ConfigDict

from domain.shop.type import CustomerId, Percent, ProviderPath


class DiscountRequest(BaseModel):
    """The promotions system's question for a customer's discount."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    customer: CustomerId

    @property
    def path(self) -> ProviderPath:
        return ProviderPath(f"/discounts/{self.customer.root}")


class DiscountOffer(BaseModel):
    """The share of the total the promotions system takes off for a customer, none when it states none."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    percent: Percent = Percent(0)
```
