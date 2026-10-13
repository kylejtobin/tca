from pydantic import BaseModel, ConfigDict

from type_construction.registrar.domain.registration.name import Offer, RegistrationOutcome
from type_construction.registrar.integration.registrar.model import (
    Refused,
    Registered,
    RegistrationReply,
)


class RegistrationAttempt(BaseModel):
    """An offered name's registration, with what the registrar said of it."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    offer: Offer
    reply: RegistrationReply

    @property
    def answer(self) -> Registered | Refused:
        return self.reply.answer

    @property
    def outcome(self) -> RegistrationOutcome:
        return RegistrationOutcome.model_validate(self)
