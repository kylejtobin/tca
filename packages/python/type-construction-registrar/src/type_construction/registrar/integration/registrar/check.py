from pydantic import BaseModel, ConfigDict

from type_construction.registrar.domain.registration.name import Availability, RegistrationRequest
from type_construction.registrar.integration.registrar.model import (
    AvailabilityReply,
    Available,
    Premium,
    Reserved,
    Taken,
)


class AvailabilityCheck(BaseModel):
    """A request's asking of the registrar, with what the registrar said of the name."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    request: RegistrationRequest
    reply: AvailabilityReply

    @property
    def standing(self) -> Available | Premium | Taken | Reserved:
        return self.reply.standing

    @property
    def availability(self) -> Availability:
        return Availability.model_validate(self)
