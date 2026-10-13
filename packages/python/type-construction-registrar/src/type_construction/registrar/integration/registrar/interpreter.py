from pydantic import BaseModel, ConfigDict

from type_construction.registrar.domain.registration.name import CheckAvailability, Register
from type_construction.registrar.integration.registrar.attempt import RegistrationAttempt
from type_construction.registrar.integration.registrar.check import AvailabilityCheck
from type_construction.registrar.integration.registrar.model import (
    AvailabilityAddress,
    AvailabilityReply,
    RegistrarResource,
    RegistrationOrder,
    RegistrationReply,
)
from type_construction.registrar.integration.registrar.provider import Registrar
from type_construction.registrar.integration.registrar.query import RegistrationQuery


class CheckAvailabilityInterpreter(BaseModel):
    """The one place the registrar is asked whether a name can be had."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    action: CheckAvailability
    provider: Registrar

    async def interpret(self) -> AvailabilityCheck:
        return AvailabilityCheck(
            request=self.action.request,
            reply=AvailabilityReply.model_validate_json(
                (
                    await self.provider.client.get(
                        AvailabilityAddress.model_validate(self.action.request.name).path.root
                    )
                ).content
            ),
        )


class RegisterInterpreter(BaseModel):
    """The one place an offered name is registered at the registrar."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
        revalidate_instances="never",
    )
    action: Register
    provider: Registrar

    async def interpret(self) -> RegistrationAttempt:
        return RegistrationAttempt(
            offer=self.action.offer,
            reply=RegistrationReply.model_validate_json(
                (
                    await self.provider.client.post(
                        RegistrarResource.REGISTRATIONS,
                        content=RegistrationOrder.model_validate(
                            RegistrationQuery(action=self.action)
                        ).model_dump_json(),
                    )
                ).content
            ),
        )
