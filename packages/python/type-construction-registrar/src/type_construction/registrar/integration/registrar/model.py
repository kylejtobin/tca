from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, RootModel, SecretStr

from type_construction.registrar.domain.registration.type import (
    Amount,
    Currency,
    ExpiryDate,
    Fqdn,
    Price,
    Refusals,
    RegistrantId,
    RegistrationId,
    ReservedPolicy,
    Term,
)


class ProviderUrl(RootModel[str]):
    """Where the registrar is."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ProviderKey(RootModel[SecretStr]):
    """The key the registrar knows this program by; never shown, never published."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: SecretStr = Field(min_length=1)


class ResourcePath(RootModel[str]):
    """The place of one thing the registrar holds, relative to its address."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[a-z]+(/[^/]+)*$")


class AvailableStatus(StrEnum):
    """The registrar's word for a name that can be had at its ordinary price."""

    AVAILABLE = "available"


class PremiumStatus(StrEnum):
    """The registrar's word for a name that can be had at a premium."""

    PREMIUM = "premium"


class TakenStatus(StrEnum):
    """The registrar's word for a name someone else holds."""

    TAKEN = "taken"


class ReservedStatus(StrEnum):
    """The registrar's word for a name it keeps from registration."""

    RESERVED = "reserved"


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
    name: Fqdn

    @property
    def path(self) -> ResourcePath:
        return ResourcePath("/".join((RegistrarResource.AVAILABILITY, self.name.root)))


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
