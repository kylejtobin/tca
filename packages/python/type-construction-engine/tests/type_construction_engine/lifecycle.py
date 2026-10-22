"""Parties that record what they acquire and release, and the deployments that hold them; not
a program, since nothing here is a route."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import override

from type_construction.world import Config, Connection, Setting

LOG: list[str] = []
"""What the parties wrote as they acquired and released, in order."""


@asynccontextmanager
async def held(name: str) -> AsyncGenerator[None]:
    """One thing a party acquires on entry and releases on exit, recorded either way."""
    LOG.append(f"open:{name}")
    try:
        yield
    finally:
        LOG.append(f"close:{name}")


class Said(Setting[str]):
    """The JSON a stand-in party answers with."""


class Party(Connection):
    """A party that answers with the one line the deployment gave it."""

    says: Said

    @override
    @asynccontextmanager
    async def open(self) -> AsyncGenerator[None]:
        yield


class Fine(Party):
    """A party that opens."""

    @override
    @asynccontextmanager
    async def open(self) -> AsyncGenerator[None]:
        async with held("Fine"):
            yield


class Down(Party):
    """A party that acquires its client and then fails its handshake: the client is released
    by the ``async with`` that acquired it."""

    @override
    @asynccontextmanager
    async def open(self) -> AsyncGenerator[None]:
        async with held("Down"):
            await self.handshake()
            yield

    async def handshake(self) -> None:
        """What the party refuses."""
        down = ConnectionError("down")
        raise down


class Slow(Party):
    """A party whose handshake never answers: its open ends only by cancellation."""

    @override
    @asynccontextmanager
    async def open(self) -> AsyncGenerator[None]:
        async with held("Slow"):
            await asyncio.Event().wait()
            yield


class Later(Party):
    """A party opened after the first."""

    @override
    @asynccontextmanager
    async def open(self) -> AsyncGenerator[None]:
        async with held("Later"):
            yield


class Opened(Config):
    """A deployment whose second party is down."""

    fine: Fine
    down: Down


class Hanging(Config):
    """A deployment whose second party never finishes opening."""

    fine: Fine
    slow: Slow


class Lifecycle(Config):
    """A deployment of two parties that record their opening and closing."""

    fine: Fine
    later: Later
