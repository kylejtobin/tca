"""Parties that record their opening and closing, and the deployments that hold them; not a
program, since nothing here is a route."""

from typing import override

from type_construction.world import Config, Connection, Setting


class Said(Setting[str]):
    """The JSON a stand-in party answers with."""


class Party(Connection):
    """A party that answers with the one line the deployment gave it."""

    says: Said

    @override
    async def open(self) -> None:
        pass

    @override
    async def close(self) -> None:
        pass


class Fine(Party):
    """A party that opens."""

    @override
    async def open(self) -> None:
        LOG.append("open:Fine")

    @override
    async def close(self) -> None:
        LOG.append("close:Fine")


class Down(Party):
    """A party whose open raises."""

    @override
    async def open(self) -> None:
        LOG.append("open:Down")
        down = ConnectionError("down")
        raise down


class Later(Party):
    """A party opened after the first."""

    @override
    async def open(self) -> None:
        LOG.append("open:Later")

    @override
    async def close(self) -> None:
        LOG.append("close:Later")


class Opened(Config):
    """A deployment whose second party is down."""

    fine: Fine
    down: Down


class Lifecycle(Config):
    """A deployment of two parties that record their opening and closing."""

    fine: Fine
    later: Later


LOG: list[str] = []
"""What the parties' open and close wrote."""
