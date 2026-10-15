---
type: Construct
description: "A domain thing in another system's terms: what this program asks of that system, or what it said back. Its derivations are the foreign model it sends or the domain's next fact. Holds a domain thing, and the foreign model that came back. Lives in integration/<system>/<meaning>.py."
---

```python
# integration/payments/attempt.py
from pydantic import BaseModel, ConfigDict

from domain.shop.order import OrderOutcome, PricedOrder
from integration.payments.model import ChargeApproved, ChargeDeclined, ChargeFailed, ChargeReply


class ChargeAttempt(BaseModel):
    """A priced order's charge, with what the payment provider said of it."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    order: PricedOrder
    reply: ChargeReply

    @property
    def payment(self) -> ChargeApproved | ChargeDeclined | ChargeFailed:
        return self.reply.payment

    @property
    def outcome(self) -> OrderOutcome:
        return OrderOutcome.model_validate(self)
```

```python
# integration/catalog_index/query.py
from pydantic import BaseModel, ConfigDict

from domain.shop.order import FindRelated
from domain.shop.type import AisleLimit, Closeness, ProductsPerAisle
from integration.catalog_index.model import (
    CatalogPoint,
    Conditions,
    CurrencyCondition,
    CurrencyMatch,
    MarketFilter,
    PointIds,
    Recommend,
    RecommendQuery,
)


class RelatedQuery(BaseModel):
    """A search for related products, in the catalog index's terms."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    action: FindRelated

    @property
    def query(self) -> RecommendQuery:
        return RecommendQuery(
            recommend=Recommend(
                positive=PointIds(
                    tuple(
                        CatalogPoint.model_validate(line).id
                        for line in self.action.order.lines.root
                    )
                )
            )
        )

    @property
    def market(self) -> MarketFilter:
        return MarketFilter(
            must=Conditions(
                (CurrencyCondition(match=CurrencyMatch(value=self.action.order.currency)),)
            )
        )

    @property
    def score_threshold(self) -> Closeness:
        return self.action.tuning.closeness

    @property
    def group_size(self) -> ProductsPerAisle:
        return self.action.tuning.per_aisle

    @property
    def limit(self) -> AisleLimit:
        return self.action.tuning.aisles
```

```python
# integration/catalog_index/search.py
from pydantic import BaseModel, ConfigDict

from domain.shop.order import PaidOrder, Recommendation, RecommendedOrder
from integration.catalog_index.model import IndexReply


class RelatedSearch(BaseModel):
    """A paid order's search of the catalog, with what the catalog index said of it."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    order: PaidOrder
    reply: IndexReply

    @property
    def recommendation(self) -> Recommendation:
        return Recommendation.model_validate(self.reply.answer)

    @property
    def recommended(self) -> RecommendedOrder:
        return RecommendedOrder.model_validate(self)
```
