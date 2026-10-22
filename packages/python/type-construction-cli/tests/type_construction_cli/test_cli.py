"""The command line over the program this module is: a request of every shape the shell
renders, a route, a stand-in party, and nothing else."""

import sys
from decimal import Decimal
from enum import StrEnum
from pathlib import Path
from types import ModuleType
from typing import override

import pytest
from pydantic import Field, computed_field

from type_construction.cli import Given, commands, exits, ran, tree, usage
from type_construction.engine import asked, config, hear, proven
from type_construction.world import (
    Action,
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
    """What the thing is called."""

    root: str = Field(min_length=1)


class Count(Scalar[int]):
    """How many are asked for."""

    root: int = Field(gt=0)


class Amount(Scalar[Decimal]):
    """What is offered."""

    root: Decimal = Field(gt=0)


class Kind(StrEnum):
    """Which kind of thing."""

    ONE = "one"
    TWO = "two"


class City(Scalar[str]):
    """Where the thing is."""

    root: str = Field(min_length=1)


class Place(Value):
    """Where the thing goes."""

    city: City
    """The city it goes to."""


class Tag(Scalar[str]):
    """A word attached to the thing."""

    root: str = Field(min_length=1)


class Label(Scalar[str]):
    """What an element is called."""

    root: str = Field(min_length=1)


class Size(Scalar[int]):
    """How big an element is."""

    root: int = Field(ge=1)


class Element(Value):
    """One of several things asked about."""

    label: Label
    size: Size


class Ask(Request):
    """What is asked."""

    name: Name
    """The thing's name."""
    count: Count
    """How many."""
    amount: Amount
    kind: Kind
    """Which kind."""
    place: Place
    tags: tuple[Tag, ...]
    """Words attached."""
    each: tuple[Element, ...]
    """The elements, any number."""


class Said(Setting[str]):
    """The JSON a stand-in party answers with."""


class Retries(Setting[int]):
    """How many times the party is asked again."""

    root: int = Field(ge=0)


class Party(Connection):
    """A party that answers with the one line the deployment gave it."""

    says: Said
    """What the party says."""
    retries: Retries

    @override
    async def open(self) -> None:
        pass

    @override
    async def close(self) -> None:
        pass


class Word(Scalar[str]):
    """What the party says about an element."""

    root: str = Field(min_length=1)


class Heard(Record):
    """What the party says."""

    word: Word


class Tell[P: Party, T: Record](Action[P, T]):
    """An action toward a stand-in party."""

    @override
    async def perform(self) -> T:
        return hear(self, self.party.says.root)


class Asked(Tell[Party, Heard]):
    """Ask the party about one element."""

    element: Element


class Counted(Fact):
    """An element the party spoke of."""

    element: Element
    heard: Heard


class Concluded(Fact):
    """The ask, and every element spoken of."""

    ask: Ask
    counted: tuple[Counted, ...]


class Told(Reply[Concluded]):
    """What leaves: the name asked about, and the party's words."""

    @computed_field
    @property
    def name(self) -> Name:
        return self.of.ask.name

    @computed_field
    @property
    def words(self) -> tuple[Word, ...]:
        return tuple(c.heard.word for c in self.of.counted)


class Question(Route[Ask, Told]):
    """Ask about a thing and its elements."""


class Parties(Config):
    """The one party."""

    party: Party


PROGRAM: ModuleType = sys.modules[__name__]
"""This module, as the program the command line runs."""

GIVEN = [
    "--name",
    "tea",
    "--count",
    "3",
    "--amount",
    "2.50",
    "--kind",
    "two",
    "--place.city",
    "Boston",
    "--tags",
    "gift",
    "--tags",
    "rush",
    "--each",
    '{"label": "a", "size": 1}',
    "--each",
    '{"label": "b", "size": 2}',
]
"""A complete command line for the route."""


@pytest.fixture
def party(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The party's answer in the environment, and no ``.env`` in the working directory."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PARTY__SAYS", '{"word": "yes"}')
    monkeypatch.setenv("PARTY__RETRIES", "0")


def test_the_program_is_proven_before_anything_is_listed_or_run(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert ran("ask", [], PROGRAM) == 0
    out = capsys.readouterr().out
    assert "usage: ask <route> [options]" in out
    assert "question        Ask about a thing and its elements." in out
    assert "PARTY__SAYS     What the party says." in out
    assert "PARTY__RETRIES  How many times the party is asked again. (>= 0)" in out


def test_a_routes_help_shows_each_option_read_from_the_request(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as left:
        ran("ask", ["question", "--help"], PROGRAM)
    assert left.value.code == 0
    out = capsys.readouterr().out
    assert "What is asked." in out
    assert "--name NAME        The thing's name. (min length 1)" in out
    assert "--count COUNT      How many. (> 0)" in out
    assert "--amount AMOUNT    What is offered. (> 0)" in out
    assert "--kind {one,two}   Which kind." in out
    assert "--place.city CITY  The city it goes to. (min length 1)" in out
    assert "--tags TAG         Words attached. (min length 1)" in out
    assert "--each JSON        The elements, any number." in out


def test_the_parsed_options_rebuild_the_tree_the_request_validates_from() -> None:
    given: Given = {
        "name": "tea",
        "count": "3",
        "amount": "2.50",
        "kind": "two",
        "place.city": "Boston",
        "tags": ["gift", "rush"],
        "each": [{"label": "a", "size": 1}],
    }
    found = tree(given, asked(Question))
    assert found == {
        "name": "tea",
        "count": "3",
        "amount": "2.50",
        "kind": "two",
        "place": {"city": "Boston"},
        "tags": ["gift", "rush"],
        "each": [{"label": "a", "size": 1}],
    }
    request = Ask.model_validate(found, strict=False)
    assert request.count.root == 3
    assert request.amount.root == Decimal("2.50")
    assert request.kind is Kind.TWO
    assert request.each[0].size.root == 1


@pytest.mark.usefixtures("party")
def test_an_option_not_given_is_absent_and_the_request_reports_it_missing(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert exits("ask", ["question", *GIVEN[2:]], PROGRAM) == 1
    err = capsys.readouterr().err
    assert "name" in err
    assert "Field required" in err


@pytest.mark.usefixtures("party")
def test_a_value_outside_a_constraint_exits_1_naming_the_field(
    capsys: pytest.CaptureFixture[str],
) -> None:
    args = ["question", *GIVEN]
    args[args.index("--count") + 1] = "0"
    assert exits("ask", args, PROGRAM) == 1
    err = capsys.readouterr().err
    assert "count" in err
    assert "greater_than" in err


def test_an_unknown_route_exits_2_with_the_route_list(capsys: pytest.CaptureFixture[str]) -> None:
    assert ran("ask", ["nothing"], PROGRAM) == 2
    assert "routes:" in capsys.readouterr().err


@pytest.mark.usefixtures("party")
def test_a_valid_request_reaches_answer_and_the_reply_is_printed(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert ran("ask", ["question", *GIVEN], PROGRAM) == 0
    assert capsys.readouterr().out == '{"name":"tea","words":["yes","yes"]}\n'


def test_the_programs_help_lists_the_deployments_variables_from_the_config() -> None:
    table = commands(proven(PROGRAM))
    assert usage("ask", table, config(PROGRAM)).splitlines()[-2:] == [
        "  PARTY__SAYS     What the party says.",
        "  PARTY__RETRIES  How many times the party is asked again. (>= 0)",
    ]


def test_the_proof_is_computed_once_and_passed_to_the_run() -> None:
    proof = proven(PROGRAM)
    assert proof.path(Counted) == (Element,)
    assert proof.path(Concluded) == ()
