from datetime import date
from enum import StrEnum
from typing import Annotated

from pydantic import ConfigDict, Field, RootModel, SecretStr


class Label(RootModel[str]):
    """One label of a domain name: letters, digits and inner hyphens, up to sixty-three."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[a-z0-9]$|^[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$")


class TopLevelDomain(RootModel[str]):
    """The top-level domain a name is registered under, as the registry spells it."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[a-z]{2,63}$|^xn--[a-z0-9-]{1,59}$")


class Labels(RootModel[tuple[Label, ...]]):
    """The labels of a domain name beneath its top-level domain, outermost first."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[Label, ...] = Field(min_length=1)


class Fqdn(RootModel[str]):
    """A domain name as it is written: its labels and top-level domain joined by dots."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class Term(RootModel[int]):
    """How many years a name is asked for, from one to ten."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: int = Field(ge=1, le=10)


class RegistrantId(RootModel[str]):
    """The registrar's identity for the one who asks for a name."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class Price(RootModel[int]):
    """What the registrar asks for one year of a name, in minor units, above zero."""

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


class Currency(StrEnum):
    """The currency the registrar prices a name in."""

    USD = "usd"
    EUR = "eur"


class RegistrationId(RootModel[str]):
    """The registrar's identity for a registration it granted."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ExpiryDate(RootModel[date]):
    """The day a name's registration ends."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: date


class ReservedPolicy(RootModel[str]):
    """The policy under which the registrar keeps a name from registration."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class RefusalReason(StrEnum):
    """Why the registrar refused a registration."""

    OBJECT_EXISTS = "object_exists"
    POLICY_VIOLATION = "policy_violation"
    REGISTRANT_INVALID = "registrant_invalid"


class UnlistedRefusal(RootModel[str]):
    """A refusal reason the registrar gave that this program has no word for."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class StatedRefusal(
    RootModel[Annotated[RefusalReason | UnlistedRefusal, Field(union_mode="left_to_right")]]
):
    """A reason the registrar gave for refusing a registration."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )


class Refusals(RootModel[tuple[StatedRefusal, ...]]):
    """Every reason the registrar gave for refusing one registration."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: tuple[StatedRefusal, ...] = Field(min_length=1)


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


class ProviderUrl(RootModel[str]):
    """The address of another system this program calls."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(min_length=1)


class ResourcePath(RootModel[str]):
    """The place of one thing the registrar holds, relative to its address."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(pattern=r"^[a-z]+(/[^/]+)*$")


class ProviderKey(RootModel[SecretStr]):
    """The key the registrar knows this program by; never shown, never published."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: SecretStr = Field(min_length=1)


class BlankPassword(RootModel[str]):
    """The password the registrar's scheme leaves blank; the key alone names this program."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(default="", max_length=0)


class MediaType(StrEnum):
    """The form of a message body that crosses between this program and the registrar."""

    JSON = "application/json"


class FieldName(StrEnum):
    """The name of a header this program sends to the registrar."""

    CONTENT_TYPE = "Content-Type"
