from pydantic import BaseModel, ConfigDict

from type_construction.registrar.domain.registration.name import Register
from type_construction.registrar.domain.registration.type import (
    Amount,
    Currency,
    Fqdn,
    RegistrantId,
    Term,
)


class RegistrationQuery(BaseModel):
    """An offered name's registration, in the registrar's terms."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    action: Register

    @property
    def fqdn(self) -> Fqdn:
        return self.action.offer.request.name.fqdn

    @property
    def term(self) -> Term:
        return self.action.offer.request.term

    @property
    def registrant(self) -> RegistrantId:
        return self.action.offer.request.registrant

    @property
    def amount(self) -> Amount:
        return self.action.offer.cost.amount

    @property
    def currency(self) -> Currency:
        return self.action.offer.cost.currency
