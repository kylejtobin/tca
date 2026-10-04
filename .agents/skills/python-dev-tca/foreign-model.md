---
type: Construct
description: "Another system's thing, under its names, parsed from what it sends, serialized to what it accepts. Holds semantic scalars and other foreign models. Lives in integration/<system>/model.py."
---

```python
# integration/payments/model.py
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, RootModel

from domain.shop.type import (
    Amount, CardToken, ChargeId, Currency, DeclineReasons, OrderId, StatedError,
)


class PaymentsResource(StrEnum):
    """What the payment provider holds, relative to its address."""

    CHARGES = "/charges"


class CardCharge(BaseModel):
    """A charge of an amount in a currency to a card, under the payment provider's reference."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True, serialize_by_alias=True,
    )
    amount: Amount = Field(serialization_alias="amt")
    currency: Currency = Field(serialization_alias="cur")
    card: CardToken = Field(serialization_alias="src")
    id: OrderId = Field(serialization_alias="ref")


class ChargeApproved(BaseModel):
    """A charge the payment provider made."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    charge: ChargeId = Field(alias="id")


class ChargeDeclined(BaseModel):
    """A charge the payment provider refused, and why."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    reasons: DeclineReasons = Field(alias="decline_codes")


class ChargeFailed(BaseModel):
    """A charge the payment provider could not attempt, and why."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    error: StatedError


class ChargeReply(RootModel[ChargeApproved | ChargeDeclined | ChargeFailed]):
    """What the payment provider says of a charge."""

    model_config = ConfigDict(
        frozen=True, strict=True,
        validate_default=True, revalidate_instances="never",
    )
```

```python
# integration/promotions/model.py
from pydantic import BaseModel, ConfigDict

from domain.shop.type import CustomerId, Percent


class CustomerDiscount(BaseModel):
    """The discount the promotions system holds for one customer, named in its collection by that customer."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        from_attributes=True,
    )
    customer: CustomerId


class DiscountOffer(BaseModel):
    """The share the promotions system takes off for a customer; none when it states none."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
    )
    percent: Percent = Percent(0)
```
