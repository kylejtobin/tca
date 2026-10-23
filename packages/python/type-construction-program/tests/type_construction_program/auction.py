"""A lot sold at the highest amount bid before a deadline.

Bids arrive from bidders over time. The deadline is a declared duration after the time the
clock is read, and the clock says when it has elapsed. ``Highest`` chooses among every amount
bid; the bids are closed by ``Elapsed``, which the program obtains by sending the clock a
``Deadline``; the clock acknowledges the deadline and says ``Elapsed`` later. A sealed auction
supplies every amount in its input instead, with no interaction.
"""

from datetime import datetime, timedelta
from decimal import Decimal

from pydantic import Field

from type_construction.program import Correlation, Interaction, Program, Source
from type_construction.world import Duration, Fact, Greatest, Record, Scalar, Value


class LotId(Scalar[str]):
    root: str = Field(min_length=1)


class Amount(Scalar[Decimal]):
    root: Decimal = Field(gt=0)


class Instant(Scalar[datetime]):
    """A point in time, as the clock says it."""


class BiddingWindow(Duration):
    """How long bidding stays open after the clock is read."""

    root: timedelta = timedelta(hours=1)


class Lot(Value):
    id: LotId


class RunAuction(Value):
    """The command: auction this lot."""

    lot: Lot


class SealedBids(Value):
    """The command for a sealed auction: the lot and every amount, supplied at once."""

    lot: Lot
    amounts: tuple[Amount, ...]


class Bid(Record):
    lot: LotId = Field(alias="lot_id")
    amount: Amount


class ReadClock(Value):
    """What the program sends the clock to learn the time: nothing."""


class Now(Record):
    """What the clock says the time is."""

    at: Instant


class Deadline(Value):
    """What the program sends the clock: say when this long after that reading has passed."""

    since: Now
    grace: BiddingWindow


class TimerSet(Record):
    """The clock's receipt: it will say when this instant has passed."""

    at: Instant


class Elapsed(Record):
    """What the clock says when the deadline has passed."""

    at: Instant


class Highest(Greatest[Amount]):
    """The greatest amount among every amount bid."""


class Hammered(Fact):
    """The outcome: the lot goes at the highest amount."""

    lot: Lot
    highest: Highest


CLOCK = Source("clock")
BIDDERS = Source("bidders")

BIDS = Interaction(
    source=BIDDERS,
    receives=(Bid,),
    correlated=(Correlation(received="lot", subject="lot.id"),),
    closed_by=Elapsed,
)
UNCLOSED_BIDS = Interaction(
    source=BIDDERS,
    receives=(Bid,),
    correlated=(Correlation(received="lot", subject="lot.id"),),
)
READ_CLOCK = Interaction(source=CLOCK, sends=ReadClock, receives=(Now,))
TIMER = Interaction(source=CLOCK, sends=Deadline, acknowledges=TimerSet, receives=(Elapsed,))

AUCTION = Program(goal=Hammered, accepts=RunAuction, interactions=(BIDS, READ_CLOCK, TIMER))
SEALED = Program(goal=Hammered, accepts=SealedBids)

LOT = RunAuction(lot=Lot(id=LotId("lot-7")))
