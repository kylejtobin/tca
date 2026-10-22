"""A program with the faults the proof refuses, and a relation with no other outcome: a class
nothing holds, a record no action hears, a scalar two carriers hold, a relation kind that
declares no constraints, relations the bounds decide, a union two relations cannot tell apart,
a record two actions hear, a party the config holds twice, two classes that hold each other
through a forward reference the engine resolves, a route that descends from an element, a
collection of a once-per-run class, a record heard per element that holds a collection, and
an outcome with no complement."""

from decimal import Decimal
from typing import Self, override

from pydantic import Field, model_validator

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
    Value,
    refused,
)


class Name(Scalar[str]):
    """What an element is called."""

    root: str = Field(min_length=1)


class Element(Value):
    """One thing the request holds several of."""

    name: Name


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
    """What arrives: the elements, and two bounded amounts."""

    each: tuple[Element, ...]
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


class Tag(Scalar[str]):
    """A word the party attaches to an element."""

    root: str = Field(min_length=1)


class Heard(Record):
    """What the party says about an element, with a collection a record heard per element may
    not hold, and the element's name, which Element carries too."""

    amount: Amount
    name: Name
    tags: tuple[Tag, ...]


class Tell[P: Party, T: Record](Action[P, T]):
    """An action toward a stand-in party."""

    @override
    async def perform(self) -> T:
        return hear(self, self.party.says.root)


class Asked(Tell[Party, Heard]):
    """Ask the party about one element."""

    element: Element


class Reasked(Tell[Party, Heard]):
    """A second action hearing the same record."""

    element: Element


class Limit(Scalar[Decimal]):
    """The amount at or under which an element is low."""

    root: Decimal = Decimal(10)


class Low(AtMost[Amount, Limit]):
    """An amount at or under the limit, with no complement declared."""

    bound: Limit = Limit()


class Cheap(Fact):
    """An element the party valued low; the only outcome."""

    element: Element
    low: Low


class Impossible(Beyond[SmallAmount, LargeAmount]):
    """A small amount beyond a large one: never holds."""


class Certain(AtMost[SmallAmount, LargeAmount]):
    """A small amount at most a large one: never refuses."""


class Never(Equal[SmallAmount, LargeAmount]):
    """A small amount equal to a large one: never holds."""


class AtOrUnder(AtMost[Amount, Limit]):
    """An amount at or under the limit."""

    bound: Limit = Limit()


class Exactly(Equal[Amount, Limit]):
    """An amount equal to the limit, which is also at or under it."""

    bound: Limit = Limit()


class Either(Fact):
    """Two outcomes the proof can see both holding."""

    element: Element
    which: AtOrUnder | Exactly


class Near[A: Numeric, B: Numeric](Relation):
    """A relation kind that declares no constraints: undecidable to the proof."""

    value: A
    bound: B

    @model_validator(mode="after")
    def holds(self) -> Self:
        if abs(Decimal(self.value.root) - Decimal(self.bound.root)) > 1:
            refusal = refused("{value} is not near {bound}", self.value, self.bound)
            raise refusal
        return self


class Undecided(Near[Amount, Limit]):
    """An amount near the limit."""

    bound: Limit = Limit()


class Stray(Scalar[str]):
    """A scalar nothing holds."""

    root: str = Field(min_length=1)


class Egg(Fact):
    """A fact that holds a fact that holds it."""

    chicken: "Chicken"  # noqa: UP037
    elements: Elements


class Chicken(Fact):
    """The other half of the cycle."""

    egg: Egg


class Word(Scalar[str]):
    """What a record no action hears would say."""

    root: str = Field(min_length=1)


class Unheard(Record):
    """A record no action hears."""

    word: Word


class Wrong(Fact):
    """A reply's fact that holds an element directly."""

    cheap: Cheap


class AnsweredWrong(Reply[Wrong]):
    """A reply that would exist once per element."""


class Misplaced(Route[Elements, AnsweredWrong]):
    """A route that descends from an element."""


class Concluded(Fact):
    """Every element valued low, with every fault the proof refuses held once or collected."""

    valued: tuple[Cheap, ...]
    certain: Certain
    impossible: Impossible
    never: Never
    either: tuple[Either, ...]
    undecided: tuple[Undecided, ...]
    unheard: Unheard


class Collects(Fact):
    """A collection of a class that exists once per run."""

    every: tuple[Concluded, ...]


class Answered(Reply[Concluded]):
    """What leaves."""


class Operation(Route[Elements, Answered]):
    """Value each element."""


class Parties(Config):
    """The party, held twice."""

    party: Party
    backup: Party
