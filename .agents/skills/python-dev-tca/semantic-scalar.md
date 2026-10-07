---
type: Construct
description: "One atomic meaning over a primitive or a closed vocabulary, constrained so an invalid value cannot be constructed. Holds a primitive. Lives in domain/<context>/type.py."
---

```python
# domain/shop/type.py
from enum import StrEnum

from pydantic import ConfigDict, Field, RootModel


class OrderId(RootModel[str]):
    """The identity of an order."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class CustomerId(RootModel[str]):
    """The identity of a customer."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class Sku(RootModel[str]):
    """The identity of a product."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class CardToken(RootModel[str]):
    """The payment provider's name for a customer's card."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ChargeId(RootModel[str]):
    """The payment provider's identity for a charge it made."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ProviderUrl(RootModel[str]):
    """The address of another system this program calls."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class CollectionUrl(RootModel[str]):
    """The address of a collection another system holds; each thing in it is named relative to it."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^https?://[^/]+/(.+/)?$")


class ProviderKey(RootModel[str]):
    """The key another system knows this program by; never shown, never published."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1, repr=False, exclude=True)


class UnitPrice(RootModel[int]):
    """The price of one unit, in minor units of the currency, above zero."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(gt=0)


class Quantity(RootModel[int]):
    """The number of units on a line, above zero."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(gt=0)


class Amount(RootModel[int]):
    """An amount of money in minor units of the currency, zero or more."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(ge=0)


class Percent(RootModel[int]):
    """A share of an amount, in hundredths, from none to all."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(ge=0, le=100)


class Currency(StrEnum):
    """The currency a cart is priced in."""

    USD = "usd"
    EUR = "eur"


class DeclineReason(StrEnum):
    """Why the payment provider declined a charge."""

    INSUFFICIENT_FUNDS = "insufficient_funds"
    EXPIRED_CARD = "expired_card"


class ProviderError(StrEnum):
    """Why the payment provider could not attempt a charge."""

    RATE_LIMITED = "rate_limited"
    UNAVAILABLE = "unavailable"


class MediaType(StrEnum):
    """The form of a message body that crosses between this program and another system."""

    JSON = "application/json"


class FieldName(StrEnum):
    """The name of a header this program sends to another system."""

    CONTENT_TYPE = "Content-Type"


class BlankPassword(RootModel[str]):
    """The password the payment provider's scheme leaves blank, because the key alone names this program."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(default="", max_length=0)


class CardProviderName(StrEnum):
    """The card provider, as a deployment names its payment provider."""

    CARD = "card"


class InvoiceProviderName(StrEnum):
    """The invoicing provider, as a deployment names its payment provider."""

    INVOICE = "invoice"


class Unset(RootModel[str]):
    """A setting the environment does not give."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(default="", max_length=0)
```

```python
# domain/shop/type.py
class NoticeText(RootModel[str]):
    """The words a customer is sent about their order."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ModelName(RootModel[str]):
    """The name a model provider knows one of its models by."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class SkillName(RootModel[str]):
    """The name an agent's words are known by, the same as their directory."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")


class SkillDescription(RootModel[str]):
    """What an agent's words are for, and when they are used."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class SkillBody(RootModel[str]):
    """The words an agent is given."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class SkillLocation(StrEnum):
    """Where each agent's own words are kept, within the package."""

    DECLINE_NOTICE = "prompts/agents/decline-notice/SKILL.md"


class SkillLibrary(StrEnum):
    """Where the skills an agent may load are kept, within the package."""

    SKILLS = "prompts/skills"
```
