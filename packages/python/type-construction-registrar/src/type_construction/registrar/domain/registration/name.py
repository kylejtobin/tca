from pydantic import BaseModel, ConfigDict, RootModel

from type_construction.registrar.domain.registration.type import Amount, Fqdn, RegistrantId, Term
from type_construction.registrar.domain.registration.value import (
    Cost,
    Grant,
    Holding,
    PremiumQuote,
    Quote,
    Refusal,
    Reservation,
)


class RegistrationRequest(BaseModel):
    """A registrant's request for a name over a term."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    registrant: RegistrantId
    name: Fqdn
    term: Term

    @property
    def availability(self) -> CheckAvailability:
        return CheckAvailability(request=self)


class CheckAvailability(BaseModel):
    """The intended asking of the registrar whether a requested name can be had."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    request: RegistrationRequest


class AvailableName(BaseModel):
    """A requested name the registrar will sell at its ordinary price."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    request: RegistrationRequest
    standing: Quote

    @property
    def cost(self) -> Cost:
        return Cost(
            amount=Amount(self.standing.price.root * self.request.term.root),
            currency=self.standing.currency,
        )


class PremiumName(BaseModel):
    """A requested name the registrar will sell at a premium."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    request: RegistrationRequest
    standing: PremiumQuote

    @property
    def cost(self) -> Cost:
        return Cost(
            amount=Amount(
                self.standing.premium.root
                + self.standing.renewal.root * (self.request.term.root - 1)
            ),
            currency=self.standing.currency,
        )


class TakenName(BaseModel):
    """A requested name someone else holds."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    request: RegistrationRequest
    standing: Holding


class ReservedName(BaseModel):
    """A requested name the registrar keeps from registration."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    request: RegistrationRequest
    standing: Reservation


class Availability(RootModel[AvailableName | PremiumName | TakenName | ReservedName]):
    """What became of a request at the registrar's availability answer."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def request(self) -> RegistrationRequest:
        return self.root.request

    @property
    def standing(self) -> Quote | PremiumQuote | Holding | Reservation:
        return self.root.standing


class Offer(RootModel[AvailableName | PremiumName]):
    """A requested name the registrar will sell, at a cost for its term."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def request(self) -> RegistrationRequest:
        return self.root.request

    @property
    def cost(self) -> Cost:
        return self.root.cost

    @property
    def registration(self) -> Register:
        return Register(offer=self)


class Register(BaseModel):
    """The intended registering of an offered name for its term at its cost."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    offer: Offer


class RegisteredName(BaseModel):
    """An offered name the registrar registered."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    offer: Offer
    answer: Grant


class RefusedName(BaseModel):
    """An offered name the registrar refused to register."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )
    offer: Offer
    answer: Refusal


class RegistrationOutcome(RootModel[RegisteredName | RefusedName]):
    """What became of a registration at the registrar."""

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_default=True,
        revalidate_instances="never",
        from_attributes=True,
    )

    @property
    def offer(self) -> Offer:
        return self.root.offer

    @property
    def answer(self) -> Grant | Refusal:
        return self.root.answer
