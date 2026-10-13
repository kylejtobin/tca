from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, RootModel

from type_construction.registrar.domain.registration.type import (
    Amount,
    AvailableStatus,
    Currency,
    ExpiryDate,
    Fqdn,
    PremiumStatus,
    Price,
    Refusals,
    RegistrantId,
    RegistrationId,
    ReservedPolicy,
    ReservedStatus,
    ResourcePath,
    TakenStatus,
    Term,
)


class RegistrarResource(StrEnum):
    """What the registrar holds, relative to its address."""

    AVAILABILITY = "availability"
    REGISTRATIONS = "registrations"


class AvailabilityAddress(BaseModel):
    """The place of one name's availability among the registrar's answers, named by that name."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    fqdn: Fqdn

    @property
    def path(self) -> ResourcePath:
        return ResourcePath("/".join((RegistrarResource.AVAILABILITY, self.fqdn.root)))


class Available(BaseModel):
    """A name the registrar will sell at its ordinary price per year."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    status: AvailableStatus
    price: Price
    currency: Currency


class Premium(BaseModel):
    """A name the registrar will sell at a premium for its first year and a renewal price after."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    status: PremiumStatus
    premium: Price
    renewal: Price
    currency: Currency


class Taken(BaseModel):
    """A name someone else holds, and until when."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    status: TakenStatus
    expires: ExpiryDate


class Reserved(BaseModel):
    """A name the registrar keeps from registration, and under what policy."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    status: ReservedStatus
    policy: ReservedPolicy


class AvailabilityReply(RootModel[Available | Premium | Taken | Reserved]):
    """What the registrar says of a name's availability."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )

    @property
    def standing(self) -> Available | Premium | Taken | Reserved:
        return self.root


class RegistrationOrder(BaseModel):
    """A name registered to a registrant for some years at an amount, as the registrar takes it."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
        serialize_by_alias=True,
    )
    fqdn: Fqdn = Field(serialization_alias="name")
    term: Term = Field(serialization_alias="years")
    registrant: RegistrantId
    amount: Amount
    currency: Currency


class Registered(BaseModel):
    """A registration the registrar granted, under its identity, until a date."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    id: RegistrationId
    expires: ExpiryDate


class Refused(BaseModel):
    """A registration the registrar refused, and every reason why."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    reasons: Refusals = Field(alias="refusals")


class RegistrationReply(RootModel[Registered | Refused]):
    """What the registrar says of a registration."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )

    @property
    def answer(self) -> Registered | Refused:
        return self.root
