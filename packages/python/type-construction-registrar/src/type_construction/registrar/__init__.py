import asyncio

from type_construction.registrar.config import RegistrarConfig
from type_construction.registrar.domain.registration.name import (
    Availability,
    Offer,
    RegistrationOutcome,
    RegistrationRequest,
)
from type_construction.registrar.integration.registrar.interpreter import (
    CheckAvailabilityInterpreter,
    RegisterInterpreter,
)

__all__ = (
    "Availability",
    "Offer",
    "RegistrarConfig",
    "RegistrationOutcome",
    "RegistrationRequest",
    "check",
    "check_sync",
    "register",
    "register_sync",
)


async def check(config: RegistrarConfig, request: RegistrationRequest) -> Availability:
    return (
        await CheckAvailabilityInterpreter(
            action=request.availability, provider=config.registrar
        ).interpret()
    ).availability


def check_sync(config: RegistrarConfig, request: RegistrationRequest) -> Availability:
    return asyncio.run(check(config, request))


async def register(config: RegistrarConfig, offer: Offer) -> RegistrationOutcome:
    return (
        await RegisterInterpreter(action=offer.registration, provider=config.registrar).interpret()
    ).outcome


def register_sync(config: RegistrarConfig, offer: Offer) -> RegistrationOutcome:
    return asyncio.run(register(config, offer))
