---
type: Construct
description: "The one place an action's external effect exists; what it returns is the next fact. Holds an action and the client. Lives in integration/<system>/interpreter.py."
---

```python
# integration/promotions/interpreter.py
import httpx
from pydantic import BaseModel, ConfigDict, Field

from domain.shop.order import PricedOrder, ReadDiscount
from domain.shop.value import Discount
from integration.promotions.model import DiscountAddress, DiscountOffer


class ReadDiscountInterpreter(BaseModel):
    """The one place the promotions system is asked for a customer's discount."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        arbitrary_types_allowed=True,
    )
    action: ReadDiscount
    client: httpx.AsyncClient = Field(exclude=True, repr=False)

    async def interpret(self) -> PricedOrder:
        return PricedOrder(
            order=self.action.order,
            discount=Discount.model_validate(
                DiscountOffer.model_validate_json(
                    (
                        await self.client.get(
                            DiscountAddress.model_validate(self.action.order).customer.root
                        )
                    ).content
                )
            ),
        )
```

```python
# integration/payments/interpreter.py
import httpx
from pydantic import BaseModel, ConfigDict, Field

from domain.shop.order import Charge
from integration.payments.attempt import ChargeAttempt
from integration.payments.model import CardCharge, ChargeReply, PaymentsResource


class ChargeInterpreter(BaseModel):
    """The one place a priced order is charged at the payment provider."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        arbitrary_types_allowed=True,
    )
    action: Charge
    client: httpx.AsyncClient = Field(exclude=True, repr=False)

    async def interpret(self) -> ChargeAttempt:
        return ChargeAttempt(
            order=self.action.order,
            reply=ChargeReply.model_validate_json(
                (
                    await self.client.post(
                        PaymentsResource.CHARGES,
                        content=CardCharge.model_validate(self.action.order).model_dump_json(),
                    )
                ).content
            ),
        )
```

```python
# integration/model_provider/interpreter.py
from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai.agent import AbstractAgent

from domain.shop.order import NotifiedOrder, WriteNotice
from domain.shop.value import DeclineNoticeValues
from integration.model_provider.model import NoticeReply


class WriteNoticeInterpreter(BaseModel):
    """The one place a declined order's notice is written by the model the shop names."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        arbitrary_types_allowed=True,
    )
    action: WriteNotice
    client: AbstractAgent[DeclineNoticeValues, NoticeReply] = Field(exclude=True, repr=False)

    async def interpret(self) -> NotifiedOrder:
        return NotifiedOrder(
            order=self.action.order,
            notice=(
                await self.client.run(deps=DeclineNoticeValues.model_validate(self.action.order))
            ).output.text,
        )
```
