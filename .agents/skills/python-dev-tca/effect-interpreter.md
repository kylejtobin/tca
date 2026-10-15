---
type: Construct
description: "The one place an action's external effect exists; what it returns is the next fact. Holds an action and the provider it reaches; acquires the provider's client for its one crossing, and releases it on every path. Lives in integration/<system>/interpreter.py."
---

```python
# integration/promotions/interpreter.py
from pydantic import BaseModel, ConfigDict

from domain.shop.order import PricedOrder, ReadDiscount
from domain.shop.value import Discount
from integration.promotions.model import DiscountAddress, DiscountOffer
from integration.promotions.provider import Promotions


class ReadDiscountInterpreter(BaseModel):
    """The one place the promotions system is asked for a customer's discount."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    action: ReadDiscount
    provider: Promotions

    async def interpret(self) -> PricedOrder:
        async with self.provider.client as client:
            return PricedOrder(
                order=self.action.order,
                discount=Discount.model_validate(
                    DiscountOffer.model_validate_json(
                        (
                            await client.get(
                                DiscountAddress.model_validate(self.action.order).customer.root
                            )
                        ).content
                    )
                ),
            )
```

```python
# integration/payments/interpreter.py
from pydantic import BaseModel, ConfigDict

from domain.shop.order import Charge
from integration.payments.attempt import ChargeAttempt
from integration.payments.model import CardCharge, ChargeReply, PaymentsResource
from integration.payments.provider import Payments


class ChargeInterpreter(BaseModel):
    """The one place a priced order is charged at the payment provider."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    action: Charge
    provider: Payments

    async def interpret(self) -> ChargeAttempt:
        async with self.provider.client as client:
            return ChargeAttempt(
                order=self.action.order,
                reply=ChargeReply.model_validate_json(
                    (
                        await client.post(
                            PaymentsResource.CHARGES,
                            content=CardCharge.model_validate(self.action.order).model_dump_json(),
                        )
                    ).content
                ),
            )
```

```python
# integration/catalog_index/interpreter.py
from pydantic import BaseModel, ConfigDict

from domain.shop.order import FindRelated
from integration.catalog_index.model import IndexQuery, IndexReply, IndexResource
from integration.catalog_index.provider import CatalogIndex
from integration.catalog_index.query import RelatedQuery
from integration.catalog_index.search import RelatedSearch


class FindRelatedInterpreter(BaseModel):
    """The one place the catalog index is asked for products close to the ones an order bought."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    action: FindRelated
    provider: CatalogIndex

    async def interpret(self) -> RelatedSearch:
        async with self.provider.client as client:
            return RelatedSearch(
                order=self.action.order,
                reply=IndexReply.model_validate_json(
                    (
                        await client.post(
                            IndexResource.GROUPED_QUERY,
                            content=IndexQuery.model_validate(
                                RelatedQuery(action=self.action)
                            ).model_dump_json(),
                        )
                    ).content
                ),
            )
```
