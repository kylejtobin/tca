from pydantic import BaseModel, ConfigDict

from type_construction.registrar.domain.registration.type import (
    Amount,
    Currency,
    ExpiryDate,
    Price,
    Refusals,
    RegistrationId,
    ReservedPolicy,
)


class Quote(BaseModel):
    """What the registrar asks per year for a name, in its currency."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    price: Price
    currency: Currency


class PremiumQuote(BaseModel):
    """What the registrar asks for a premium name: a premium the first year, then a renewal."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    premium: Price
    renewal: Price
    currency: Currency


class Holding(BaseModel):
    """Someone else's hold on a name, until a date."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    expires: ExpiryDate


class Reservation(BaseModel):
    """The registrar's keeping of a name from registration, under a policy."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    policy: ReservedPolicy


class Cost(BaseModel):
    """What a name costs for its term, in the registrar's currency."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    amount: Amount
    currency: Currency


class Grant(BaseModel):
    """A registration that was granted, under the registrar's identity, until a date."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    id: RegistrationId
    expires: ExpiryDate


class Refusal(BaseModel):
    """A registration that was refused, and why."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    reasons: Refusals
