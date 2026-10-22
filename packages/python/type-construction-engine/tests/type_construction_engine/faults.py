"""A program with every fault the proof refuses, in one module: a record no action hears, two
classes that hold each other through a forward reference the engine resolves, a fact that
holds a scalar two carriers in its scope both hold, an action toward a party the config holds
twice, a bare sum over an element class two collections hold, a class whose fields name two
sibling elements, a collection of a once-per-run class, a route that would exist once per
element, a scalar nothing holds, a bare primitive on a fact, a request that holds a fact, a
deployment that holds a business value, two deployments, two union members the proof cannot
tell apart, relations their operands' intervals decide, a relation kind that compares nothing,
two records one action hears that no field tells apart, and an action performed on one branch
of a choice that holds nothing deciding it. The same scalar on two carriers, the same record
heard by two actions and the same element class in two collections are not faults by
themselves: only a field that could be filled from two of them is."""

from decimal import Decimal
from typing import override

from pydantic import Field

from type_construction.engine import hear
from type_construction.world import (
    Action,
    AtMost,
    Beyond,
    Config,
    Connection,
    Equal,
    Fact,
    Numeric,
    Record,
    Relation,
    Reply,
    Request,
    Route,
    Scalar,
    Setting,
    Sum,
    Value,
)


class Name(Scalar[str]):
    """What an element is called."""

    root: str = Field(min_length=1)


class Element(Value):
    """One thing the request holds several of."""

    name: Name


class Tag(Scalar[str]):
    """What a second element is called."""

    root: str = Field(min_length=1)


class Second(Value):
    """Another thing the request holds several of, beside the elements."""

    tag: Tag


class Amount(Scalar[Decimal]):
    """What the party says an element is worth."""

    root: Decimal = Field(gt=0)


class SmallAmount(Scalar[Decimal]):
    """An amount at most 100."""

    root: Decimal = Field(gt=0, le=100)


class LargeAmount(Scalar[Decimal]):
    """An amount over 100."""

    root: Decimal = Field(gt=100)


class Elements(Request):
    """What arrives: the elements, the seconds, and two bounded amounts."""

    each: tuple[Element, ...]
    others: tuple[Second, ...]
    small: SmallAmount
    large: LargeAmount


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


class Heard(Record):
    """What the party says about an element, with the element's name, which Element carries
    too."""

    amount: Amount
    name: Name


class Tell[P: Party, T: Record](Action[P, T]):
    """An action toward a stand-in party."""

    @override
    async def perform(self) -> T:
        return hear(self, self.party.says.root)


class Asked(Tell[Party, Heard]):
    """Ask the party about one element."""

    element: Element


class Reasked(Tell[Party, Heard]):
    """A second action hearing the same record, about a second: legitimate, since a second's
    scope and an element's are apart."""

    second: Second


class Named(Fact):
    """A fact that holds the name an element and the record about it both carry: ambiguous at
    ``name``, since both are in its scope."""

    element: Element
    name: Name


class Spare(Party):
    """A party the deployment holds twice."""


class Ping(Scalar[str]):
    """What the spare party says."""

    root: str = Field(min_length=1)


class Pinged(Record):
    """The spare party's answer."""

    ping: Ping


class Spared(Tell[Spare, Pinged]):
    """An action toward the spare party: ambiguous at ``party``, held twice by the config."""

    element: Element


class Pung(Fact):
    """An element the spare party answered about."""

    element: Element
    pinged: Pinged


class Word(Scalar[str]):
    """What one record says."""

    root: str = Field(min_length=1)


class Other(Scalar[str]):
    """What the other record says, under the same key."""

    root: str = Field(min_length=1)


class Echo(Record):
    """One of two records the party may say, under the key ``said``."""

    said: Word


class Alike(Record):
    """The other, under the same key and with no Literal to tell it apart."""

    told: Other = Field(alias="said")


class Both(Tell[Party, Echo | Alike]):
    """An action hearing two records no field tells apart."""

    element: Element


class Spoken(Fact):
    """Whichever the party said."""

    element: Element
    which: Echo | Alike


class Limit(Scalar[Decimal]):
    """The amount at or under which an element is low."""

    root: Decimal = Decimal(10)


class Low(AtMost[Amount, Limit]):
    """An amount at or under the limit."""


class High(Beyond[Amount, Limit]):
    """An amount over the limit."""


class Cheap(Fact):
    """An element the party valued low."""

    element: Element
    low: Low


class Receipt(Scalar[str]):
    """What the party says when charged."""

    root: str = Field(min_length=1)


class Charged(Record):
    """The party's answer to a charge."""

    receipt: Receipt


class Charge(Tell[Party, Charged]):
    """Charge for an element: performed when Priced holds and not when Free holds, yet holding
    nothing that decides between them."""

    element: Element


class Priced(Fact):
    """An element valued low, charged for."""

    element: Element
    low: Low
    charged: Charged


class Free(Fact):
    """An element valued high, not charged for."""

    element: Element
    high: High


class Outcome(Fact):
    """Priced or free."""

    element: Element
    which: Priced | Free


class Impossible(Beyond[SmallAmount, LargeAmount]):
    """A small amount beyond a large one: never holds."""


class Certain(AtMost[SmallAmount, LargeAmount]):
    """A small amount at most a large one: never refuses."""


class Never(Equal[SmallAmount, LargeAmount]):
    """A small amount equal to a large one: never holds."""


class AtOrUnder(AtMost[Amount, Limit]):
    """An amount at or under the limit."""


class Exactly(Equal[Amount, Limit]):
    """An amount equal to the limit, which is also at or under it."""


class Either(Fact):
    """Two outcomes the proof cannot show exclusive."""

    element: Element
    which: AtOrUnder | Exactly


class Near[A: Numeric, B: Numeric](Relation):
    """A relation kind that compares nothing: it never refuses."""

    value: A
    bound: B


class Undecided(Near[Amount, Limit]):
    """An amount near the limit."""


class Stray(Scalar[str]):
    """A scalar nothing holds."""

    root: str = Field(min_length=1)


class Bare(Fact):
    """A fact with a bare primitive field."""

    element: Element
    count: int


class Egg(Fact):
    """A fact that holds a fact that holds it."""

    chicken: "Chicken"  # noqa: UP037
    elements: Elements


class Chicken(Fact):
    """The other half of the cycle."""

    egg: Egg


class Note(Scalar[str]):
    """What a record no action hears would say."""

    root: str = Field(min_length=1)


class Unheard(Record):
    """A record no action hears."""

    note: Note


class Twin(Fact):
    """A fact that holds an element and a second: it would exist per element of two things."""

    element: Element
    second: Second


class Wrong(Fact):
    """A reply's fact that holds a per-element fact directly."""

    cheap: Cheap


class AnsweredWrong(Reply[Wrong]):
    """A reply that would exist once per element."""


class Misplaced(Route[Elements, AnsweredWrong]):
    """A route whose reply would exist once per element."""


class Direct(Request):
    """A request that holds a fact, which does not arrive."""

    cheap: Cheap


class Total(Sum[Amount]):
    """A bare sum over the amounts: ambiguous at ``of``, since the party says an amount about
    each element and about each second, and nothing held says which collection."""


class Collects(Fact):
    """A collection of a class that exists once per run."""

    every: tuple[Certain, ...]


class Concluded(Fact):
    """Every element valued low, with every fault the proof refuses held once or collected."""

    valued: tuple[Cheap, ...]
    total: Total
    certain: Certain
    impossible: Impossible
    never: Never
    either: tuple[Either, ...]
    undecided: tuple[Undecided, ...]
    unheard: Unheard
    spoken: tuple[Spoken, ...]
    outcomes: tuple[Outcome, ...]
    bare: tuple[Bare, ...]
    twins: tuple[Twin, ...]
    eggs: Egg
    named: tuple[Named, ...]
    pings: tuple[Pung, ...]
    collects: Collects


class Answered(Reply[Concluded]):
    """What leaves."""


class Operation(Route[Elements, Answered]):
    """Value each element."""


class Parties(Config):
    """The party, the spare held twice, and a business value the deployment does not hold."""

    party: Party
    spare: Spare
    standby: Spare
    word: Word


class Backups(Config):
    """A second deployment."""

    party: Party
