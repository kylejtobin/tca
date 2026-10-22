"""A program whose one outcome for an element is Cheap: an amount the party says over the limit
refutes Low, and the run stalls naming it."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import override

from pydantic import Field

from type_construction.engine import hear
from type_construction.world import (
    Action,
    AtMost,
    Config,
    Connection,
    Fact,
    Record,
    Reply,
    Request,
    Route,
    Scalar,
    Setting,
    Value,
)


class Name(Scalar[str]):
    """What an element is called."""

    root: str = Field(min_length=1)


class Element(Value):
    """One thing the request holds several of."""

    name: Name


class Elements(Request):
    """What arrives: the elements, any number."""

    each: tuple[Element, ...]


class Said(Setting[str]):
    """The JSON a stand-in party answers with."""


class Party(Connection):
    """A party that answers with the one line the deployment gave it."""

    says: Said

    @override
    @asynccontextmanager
    async def open(self) -> AsyncGenerator[None]:
        yield


class Amount(Scalar[Decimal]):
    """What the party says an element is worth."""

    root: Decimal = Field(gt=0)


class Heard(Record):
    """What the party says about an element."""

    amount: Amount


class Tell[P: Party, T: Record](Action[P, T]):
    """An action toward a stand-in party."""

    @override
    async def perform(self) -> T:
        return hear(self, self.party.says.root)


class Asked(Tell[Party, Heard]):
    """Ask the party about one element."""

    element: Element


class Limit(Scalar[Decimal]):
    """The amount at or under which an element is low."""

    root: Decimal = Decimal(10)


class Low(AtMost[Amount, Limit]):
    """An amount at or under the limit, with no complement declared."""


class Cheap(Fact):
    """An element the party valued low; the only outcome."""

    element: Element
    low: Low


class Concluded(Fact):
    """Every element valued low."""

    valued: tuple[Cheap, ...]


class Answered(Reply[Concluded]):
    """What leaves."""


class Operation(Route[Elements, Answered]):
    """Value each element."""


class Parties(Config):
    """The one party."""

    party: Party
