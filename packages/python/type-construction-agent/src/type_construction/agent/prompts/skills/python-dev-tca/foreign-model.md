---
type: Construct
description: "Another system's thing, under its names, parsed from what it sends, serialized to what it accepts. Holds semantic scalars and other foreign models. Lives in integration/<system>/model.py."
---

```python
# integration/payments/model.py
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, RootModel

from domain.shop.type import (
    Amount,
    CardToken,
    ChargeId,
    Currency,
    DeclineReasons,
    OrderId,
    StatedError,
)


class PaymentsResource(StrEnum):
    """What the payment provider holds, relative to its address."""

    CHARGES = "/charges"


class CardCharge(BaseModel):
    """A charge of an amount in a currency to a card, under the payment provider's reference."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
        serialize_by_alias=True,
    )
    amount: Amount = Field(serialization_alias="amt")
    currency: Currency = Field(serialization_alias="cur")
    card: CardToken = Field(serialization_alias="src")
    id: OrderId = Field(serialization_alias="ref")


class ChargeApproved(BaseModel):
    """A charge the payment provider made."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    charge: ChargeId = Field(alias="id")


class ChargeDeclined(BaseModel):
    """A charge the payment provider refused, and why."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    reasons: DeclineReasons = Field(alias="decline_codes")


class ChargeFailed(BaseModel):
    """A charge the payment provider could not attempt, and why."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    error: StatedError


class ChargeReply(RootModel[ChargeApproved | ChargeDeclined | ChargeFailed]):
    """What the payment provider says of a charge."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )

    @property
    def payment(self) -> ChargeApproved | ChargeDeclined | ChargeFailed:
        return self.root
```

```python
# integration/promotions/model.py
from pydantic import BaseModel, ConfigDict

from domain.shop.type import CustomerId, Percent


class DiscountAddress(BaseModel):
    """The place of one customer's discount within the promotions system's discounts, named there by that customer."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    customer: CustomerId


class DiscountOffer(BaseModel):
    """The share the promotions system takes off for a customer; none when it states none."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    percent: Percent = Percent(0)
```

```python
# integration/catalog_index/model.py
from enum import StrEnum
from uuid import uuid5

from pydantic import BaseModel, ConfigDict, Field, RootModel

from domain.shop.type import (
    Category,
    Closeness,
    Currency,
    GroupSize,
    IndexFault,
    IndexStatus,
    MatchLimit,
    PayloadKey,
    PointId,
    PointNamespace,
    PointVersion,
    QueryTime,
    Similarity,
    Sku,
)


class IndexResource(StrEnum):
    """What the catalog's collection answers, relative to its address."""

    GROUPED_QUERY = "points/query/groups"


class CatalogPoint(BaseModel):
    """A product as the catalog index names it."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    sku: Sku

    @property
    def id(self) -> PointId:
        return PointId(uuid5(PointNamespace().root, self.sku.root))


class PointIds(RootModel[tuple[PointId, ...]]):
    """The products a recommendation is drawn toward."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[PointId, ...] = Field(min_length=1)


class Recommend(BaseModel):
    """A recommendation drawn toward some products."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    positive: PointIds


class RecommendQuery(BaseModel):
    """A query that recommends by example."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    recommend: Recommend


class CurrencyMatch(BaseModel):
    """A payload value a product must hold."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    value: Currency


class CurrencyCondition(BaseModel):
    """A product sold in a currency."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    key: PayloadKey = PayloadKey.CURRENCIES
    match: CurrencyMatch


class Conditions(RootModel[tuple[CurrencyCondition, ...]]):
    """Conditions every product in a recommendation meets."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[CurrencyCondition, ...] = Field(min_length=1)


class MarketFilter(BaseModel):
    """The products a market may be offered."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    must: Conditions


class PayloadSelection(RootModel[tuple[PayloadKey, ...]]):
    """The fields the catalog index returns beside each product."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[PayloadKey, ...] = (PayloadKey.SKU, PayloadKey.CATEGORY)


class IndexQuery(BaseModel):
    """A grouped recommendation, as the catalog index accepts it."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
        serialize_by_alias=True,
    )
    query: RecommendQuery
    market: MarketFilter = Field(serialization_alias="filter")
    score_threshold: Closeness
    group_by: PayloadKey = PayloadKey.CATEGORY
    group_size: GroupSize
    limit: MatchLimit
    with_payload: PayloadSelection = PayloadSelection()


class PointPayload(BaseModel):
    """The fields the catalog index returned beside a product."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    sku: Sku
    category: Category


class PointHit(BaseModel):
    """A product the catalog index found, and how alike it scored it."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    id: PointId
    version: PointVersion
    similarity: Similarity = Field(alias="score")
    payload: PointPayload

    @property
    def sku(self) -> Sku:
        return self.payload.sku

    @property
    def category(self) -> Category:
        return self.payload.category


class Hits(RootModel[tuple[PointHit, ...]]):
    """The products the catalog index found in one aisle."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[PointHit, ...] = Field(min_length=1)


class PointGroup(BaseModel):
    """One aisle of a grouped recommendation."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    hits: Hits
    id: Category


class PointGroups(RootModel[tuple[PointGroup, ...]]):
    """Every aisle of a grouped recommendation; none when nothing was close enough."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )


class GroupResult(BaseModel):
    """The aisles the catalog index found."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    groups: PointGroups


class IndexGroups(BaseModel):
    """The catalog index's answer to a grouped recommendation."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    result: GroupResult
    status: IndexStatus
    time: QueryTime

    @property
    def matches(self) -> tuple[PointHit, ...]:
        return tuple(hit for group in self.result.groups.root for hit in group.hits.root)


class IndexFaultStatus(BaseModel):
    """What the catalog index said went wrong."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    error: IndexFault


class IndexFailure(BaseModel):
    """A recommendation the catalog index could not give."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    status: IndexFaultStatus
    time: QueryTime

    @property
    def reason(self) -> IndexFault:
        return self.status.error


class IndexReply(RootModel[IndexGroups | IndexFailure]):
    """What the catalog index says of a grouped recommendation."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )

    @property
    def answer(self) -> IndexGroups | IndexFailure:
        return self.root
```

```python
# integration/model_provider/model.py
from pydantic import BaseModel, ConfigDict

from domain.shop.type import ReplyText


class SupportReply(BaseModel):
    """What the model provider sends back for a question: its words."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    text: ReplyText
```
