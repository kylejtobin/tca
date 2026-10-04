---
type: Construct
description: "The one place an action's external call is made. Holds an action and the client. Lives in integration/<system>/interpreter.py."
---

```python
# integration/promotions/interpreter.py
import httpx
from pydantic import BaseModel, ConfigDict, Field

from domain.shop.discount import DiscountStateConstructor
from domain.shop.order import PricedOrder, ReadDiscount


class ReadDiscountInterpreter(BaseModel):
    """The one place the promotions system is asked for a customer's discount."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        arbitrary_types_allowed=True,
    )
    action: ReadDiscount
    client: httpx.AsyncClient = Field(exclude=True, repr=False)

    async def execute(self) -> PricedOrder:
        return PricedOrder(
            order=self.action.order,
            discount=DiscountStateConstructor.validate_json(
                (await self.client.get(f"/discounts/{self.action.order.customer.root}")).text
            ),
        )
```

```python
# integration/payments/interpreter.py
import httpx
from pydantic import BaseModel, ConfigDict, Field

from domain.shop.order import Charge
from integration.payments.attempt import ChargeAttempt
from integration.payments.model import ChargeReplyConstructor, ChargeRequest


class ChargeInterpreter(BaseModel):
    """The one place a priced order is charged at the payment provider."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", strict=True,
        validate_default=True, revalidate_instances="never",
        arbitrary_types_allowed=True,
    )
    action: Charge
    client: httpx.AsyncClient = Field(exclude=True, repr=False)

    async def execute(self) -> ChargeAttempt:
        return ChargeAttempt(
            order=self.action.order,
            payment=ChargeReplyConstructor.validate_json(
                (
                    await self.client.post(
                        "/charges",
                        content=ChargeRequest.model_validate(
                            self.action.order, from_attributes=True
                        ).model_dump_json(by_alias=True),
                    )
                ).text
            ),
        )
```
