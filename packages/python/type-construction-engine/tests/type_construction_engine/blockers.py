"""A program whose one conclusion holds two premises that can each fail on their own: a fact
that needs the screening's yes, and a relation over the amount that arrived. A flagged
screening and an amount over the limit block the route twice, and the run names both."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Literal, override

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
)


class Amount(Scalar[Decimal]):
    """What arrives to be screened."""

    root: Decimal = Field(gt=0)


class Ask(Request):
    """What arrives: an amount."""

    amount: Amount


class Said(Setting[str]):
    """The JSON a stand-in party answers with."""


class Fraud(Connection):
    """A party that screens with the one line the deployment gave it."""

    says: Said

    @override
    @asynccontextmanager
    async def open(self) -> AsyncGenerator[None]:
        yield


class Clear(Record):
    """The screening's yes."""

    status: Literal["clear"]


class Reason(Scalar[str]):
    """Why the screening said no."""

    root: str = Field(min_length=1)


class Flagged(Record):
    """The screening's no."""

    status: Literal["flagged"]
    reason: Reason


class Screen(Action[Fraud, Clear | Flagged]):
    """Ask whether the amount is clear."""

    ask: Ask

    @override
    async def perform(self) -> Clear | Flagged:
        return hear(self, self.party.says.root)


class Screened(Fact):
    """An amount the screening cleared."""

    ask: Ask
    clear: Clear


class Refused(Fact):
    """An amount the screening flagged: the other record's conclusion, so the proof reaches
    it."""

    ask: Ask
    flagged: Flagged


class Limit(Scalar[Decimal]):
    """The amount at or under which an amount is low."""

    root: Decimal = Decimal(10)


class Low(AtMost[Amount, Limit]):
    """An amount at or under the limit."""


class Concluded(Fact):
    """A cleared, low amount."""

    screened: Screened
    low: Low


class Noted(Fact):
    """A flagged amount, which the second route concludes."""

    refused: Refused


class Answered(Reply[Concluded]):
    """What leaves for a cleared, low amount."""


class Declined(Reply[Noted]):
    """What leaves for a flagged amount."""


class Approve(Route[Ask, Answered]):
    """Approve a cleared, low amount."""


class Decline(Route[Ask, Declined]):
    """Note a flagged amount."""


class Deployment(Config):
    """The screening."""

    fraud: Fraud
