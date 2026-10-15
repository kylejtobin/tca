from datetime import date
from enum import StrEnum
from typing import Annotated, Self

from pydantic import ConfigDict, Field, RootModel, model_validator


class Invariant(StrEnum):
    """A rule of registration that construction enforces, in the registry's words."""

    UNLISTED_REFUSAL = "an unlisted refusal is one this program has no word for"


class Fqdn(RootModel[str]):
    """A domain name as it is written: its labels and top-level domain joined by dots, at most
    253 characters."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    root: str = Field(
        max_length=253,
        pattern=r"^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+([a-z]{2,63}|xn--[a-z0-9-]{1,59})$",
    )


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

    @model_validator(mode="after")
    def no_word_for_it(self) -> Self:
        if not all(reason != self.root for reason in RefusalReason):
            raise ValueError(Invariant.UNLISTED_REFUSAL)
        return self


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
