"""Demand and eligibility against adversarial programs and runs: an effect is performed because
the route's answer needs what it hears and its own declared evidence is there, each observed at
``perform`` itself, by subject, timing and evidence. The base program values each element of a
request through a party that answers per element and tells a teller about each element valued
high; each test adds the classes its counterexample needs."""

import asyncio
import json
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from decimal import Decimal
from pathlib import Path
from types import ModuleType
from typing import Annotated, Literal, NamedTuple, Self, cast, override

import pytest
from annotated_types import MaxLen
from pydantic import Field, ValidationError, model_validator

from type_construction import engine
from type_construction.engine import (
    Blocked,
    Constructed,
    Occurrence,
    Proof,
    Refuted,
    Run,
    Scope,
    Undecided,
    config,
    proven,
    ran,
    refused,
    scopes,
)
from type_construction.world import (
    Action,
    AtMost,
    Beyond,
    Config,
    Connection,
    Fact,
    Json,
    Python,
    Record,
    Reply,
    Request,
    Route,
    Scalar,
    Setting,
    Sum,
    Under,
    Value,
)

from . import occurrences, optional
from .test_execution import attributes
from .test_occurrences import ORDER, exporting
from .test_proof import unproven


class Performed(NamedTuple):
    """One ``perform`` call: the action's class, its subject, and the identity of the evidence
    it held."""

    action: type[object]
    subject: str
    evidence: int = 0


PERFORMED: list[Performed] = []
"""Every ``perform`` call, in order."""


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
    """The JSON a stand-in party answers from."""


class Party(Connection):
    """A party that answers about each element from the map the deployment gave it."""

    says: Said

    @override
    @asynccontextmanager
    async def open(self) -> AsyncGenerator[None]:
        yield


class Teller(Party):
    """The party told about dear elements."""


class Amount(Scalar[Decimal]):
    """What the party says an element is worth."""

    root: Decimal = Field(gt=0)


class Heard(Record):
    """What the party says about an element."""

    amount: Amount


class Ask(Action[Party, Heard]):
    """Ask the party about one element: the evidence every later decision needs."""

    element: Element

    @override
    async def perform(self) -> Json:
        amounts: dict[str, str] = json.loads(self.party.says.root)
        PERFORMED.append(Performed(Ask, self.element.name.root))
        if self.element.name.root == "slow":
            await asyncio.sleep(0.01)
        return Json(json.dumps({"amount": amounts[self.element.name.root]}))


class Limit(Scalar[Decimal]):
    """The amount at or under which an element is low."""

    root: Decimal = Decimal(10)


class Low(AtMost[Amount, Limit]):
    """An amount at or under the limit."""


class High(Beyond[Amount, Limit]):
    """An amount over the limit."""


class Word(Scalar[str]):
    """What the teller says."""

    root: str = Field(min_length=1)


class Noted(Record):
    """What the teller says about a dear element."""

    word: Word


class Notify(Action[Teller, Noted]):
    """Tell the teller about an element valued high: its evidence is the high it holds."""

    high: High

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(Notify, str(self.high.value.root), id(self.high)))
        return Json(self.party.says.root)


class Cheap(Fact):
    """An element the party valued low."""

    element: Element
    low: Low


class Dear(Fact):
    """An element the party valued high, which the teller was told about."""

    element: Element
    high: High
    noted: Noted


class Concluded(Fact):
    """Every element valued."""

    valued: tuple[Cheap | Dear, ...]


class Answered(Reply[Concluded]):
    """What leaves."""


class Operation(Route[Elements, Answered]):
    """Value each element and tell the teller about the dear ones."""


class Deployment(Config):
    """The party and the teller."""

    party: Party
    teller: Teller


class Telling(Config):
    """The teller alone."""

    teller: Teller


CORE: tuple[type[object], ...] = (
    Name,
    Element,
    Elements,
    Said,
    Party,
    Teller,
    Amount,
    Heard,
    Ask,
    Limit,
    Low,
    High,
    Word,
    Deployment,
)
"""What every program here is made from."""

REFERENCE: tuple[type[object], ...] = (
    *CORE,
    Noted,
    Notify,
    Cheap,
    Dear,
    Concluded,
    Answered,
    Operation,
)
"""The reference program: ``Ask`` obtains the evidence, ``Low`` or ``High`` decides, ``Dear``
needs what ``Notify`` hears and ``Notify`` holds the ``High`` it is performed with."""

ELEMENT = ("request", "each", "[]")
"""The site of each element's scope."""


def program_of(*members: type[object]) -> ModuleType:
    """A program made of classes defined in this module."""
    module = ModuleType(__name__)
    for member in members:
        setattr(module, member.__name__, member)
    return module


PROGRAM = program_of(*REFERENCE)
"""The reference program, as the engine reads it."""


def faults_of(program: ModuleType) -> dict[tuple[str, tuple[object, ...]], str]:
    """Every fault the proof refuses a program with, by type and location, with its message."""
    with pytest.raises(ValidationError) as refusal:
        proven(program)
    return {(e["type"], tuple(e["loc"])): e["msg"] for e in refusal.value.errors()}


@pytest.fixture
def parties(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Callable[[dict[str, str]], None]:
    """The party's amounts per element name in the environment, the teller's word, no
    ``.env``, and the record of performs cleared."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TELLER__SAYS", '{"word": "dear"}')
    PERFORMED.clear()

    def saying(amounts: dict[str, str]) -> None:
        monkeypatch.setenv("PARTY__SAYS", json.dumps(amounts))

    return saying


def requested(*names: str) -> Elements:
    """A request of elements with the given names."""
    return Elements.model_validate_json(json.dumps({"each": [{"name": n} for n in names]}))


async def valued[A: Reply[Fact]](
    program: ModuleType,
    *names: str,
    route: type[Route[Elements, A]] = Operation,
    proof: Proof | None = None,
) -> Run[Elements, A]:
    """A route of the reference shape run over a program for the named elements, under its
    proof or the one given."""
    proof = proven(program) if proof is None else proof
    done = await ran(route, requested(*names), config(program)(), proof)
    assert isinstance(done, Run)
    return done


def made_in(root: Scope, cls: type[object]) -> dict[tuple[str, ...], Constructed | Refuted]:
    """What each scope made of each construction of a class, by the occurrence's concrete
    path."""
    return {
        (*s.path, c.cls.__name__): m
        for s in scopes(root)
        for c, m in s.made.items()
        if c.cls is cls
    }


def occurrences_of(root: Scope, cls: type[object]) -> list[Occurrence]:
    """Every occurrence of a class the run constructed, in scope order."""
    return [Occurrence(s, c) for s in scopes(root) for c in s.made if c.cls is cls]


def constructed(occurrence: Occurrence) -> Constructed:
    """What a scope made of an occurrence it constructed."""
    made = occurrence.made
    assert isinstance(made, Constructed)
    return made


def notified(done: Run[Elements, Answered]) -> dict[str, High]:
    """The ``High`` each dear element's ``Notify`` was performed with, by element name."""
    found: dict[str, High] = {}
    for v in done.route.reply.of.valued:
        if isinstance(v, Dear):
            found[v.element.name.root] = v.high
    return found


def performed(cls: type[object]) -> list[Performed]:
    """The performs of one action class, in order."""
    return [p for p in PERFORMED if p.action is cls]


def errors_of(blocked: Blocked) -> list[tuple[str, tuple[object, ...], str]]:
    """The causes a blocked run is refused with, as the caller sees them."""
    return [(e["type"], tuple(e["loc"]), e["msg"]) for e in refused(blocked).errors()]


# --- 1. demand and eligibility are two properties: the answer needs the effect, the action -----
# --- holds its evidence ------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_an_effect_is_performed_where_the_answer_needs_it_with_the_evidence_it_holds(
    parties: Callable[[dict[str, str]], None],
) -> None:
    exporter = exporting()
    parties({"a": "5", "b": "50", "c": "12"})
    done = await valued(PROGRAM, "a", "b", "c")
    assert [p.subject for p in performed(Ask)] == ["a", "b", "c"]
    highs = notified(done)
    assert set(highs) == {"b", "c"}
    assert sorted(performed(Notify)) == sorted(
        [Performed(Notify, "50", id(highs["b"])), Performed(Notify, "12", id(highs["c"]))]
    )
    assert PERFORMED.index(performed(Notify)[0]) > max(PERFORMED.index(p) for p in performed(Ask))
    assert set(made_in(done.root, Notify)) == {
        ("request", "each", "[1]", "Notify"),
        ("request", "each", "[2]", "Notify"),
    }
    cheap = made_in(done.root, High)[("request", "each", "[0]", "High")]
    assert isinstance(cheap, Refuted)
    assert done.passes == 3
    spans = exporter.get_finished_spans()
    by_site = {attributes(s)["tca.site"]: s for s in spans if s.name == "Notify"}
    assert set(by_site) == {"request.each.[1].Notify", "request.each.[2].Notify"}
    assert {attributes(s)["tca.pass"] for s in spans if s.name == "Ask"} == {1}
    assert {attributes(s)["tca.pass"] for s in by_site.values()} == {2}


@pytest.mark.asyncio
async def test_effects_are_the_same_whatever_the_declaration_completion_or_invocation_order(
    parties: Callable[[dict[str, str]], None],
) -> None:
    parties({"slow": "50", "b": "5", "c": "20"})

    def trace(done: Run[Elements, Answered]) -> dict[str, tuple[str, int]]:
        """Each dear element's notification: the amount performed with, and how many times the
        very high it holds was performed with."""
        return {
            name: (
                str(high.value.root),
                len([p for p in performed(Notify) if p.evidence == id(high)]),
            )
            for name, high in notified(done).items()
        }

    expected = {"slow": ("50", 1), "c": ("20", 1)}
    for program, names in (
        (PROGRAM, ("slow", "b", "c")),
        (program_of(*reversed(REFERENCE)), ("c", "b", "slow")),
        (PROGRAM, ("slow", "b", "c")),
    ):
        PERFORMED.clear()
        done = await valued(program, *names)
        assert trace(done) == expected
        assert len(performed(Notify)) == 2


class Pinged(Record):
    """What the teller says when pinged."""

    word: Word


class Ping(Action[Teller, Pinged]):
    """Tell the teller about an element: holds the element, nothing of the branch its record
    is needed on, and is supplied from the first pass."""

    element: Element

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(Ping, self.element.name.root))
        return Json(self.party.says.root)


class DearPinged(Fact):
    """An element valued high, pinged about."""

    element: Element
    high: High
    pinged: Pinged


class ConcludedPinged(Fact):
    """Every element valued."""

    valued: tuple[Cheap | DearPinged, ...]


class AnsweredPinged(Reply[ConcludedPinged]):
    """What leaves."""


class PingOperation(Route[Elements, AnsweredPinged]):
    """Value each element and ping about the dear ones."""


PINGED = program_of(
    *CORE, Pinged, Ping, Cheap, DearPinged, ConcludedPinged, AnsweredPinged, PingOperation
)
"""The program whose branch-specific action is supplied before the branch is known."""


@pytest.mark.asyncio
async def test_an_action_supplied_from_the_start_waits_for_the_branch_that_needs_its_record(
    parties: Callable[[dict[str, str]], None],
) -> None:
    proof = proven(PINGED)
    assert proof.faulted == ()
    parties({"a": "5", "b": "50"})
    done = await valued(PINGED, "a", "b", route=PingOperation, proof=proof)
    assert [p.subject for p in performed(Ask)] == ["a", "b"]
    assert [p.subject for p in performed(Ping)] == ["b"]
    assert max(PERFORMED.index(p) for p in performed(Ask)) < PERFORMED.index(performed(Ping)[0])
    assert set(made_in(done.root, Ping)) == {("request", "each", "[1]", "Ping")}
    assert [type(v) for v in done.route.reply.of.valued] == [Cheap, DearPinged]
    PERFORMED.clear()
    parties({"a": "5"})
    cheap = await valued(PINGED, "a", route=PingOperation, proof=proof)
    assert performed(Ping) == []
    assert made_in(cheap.root, Ping) == {}
    assert cheap.passes == 2


class CheapNoted(Fact):
    """An element valued low, which the teller was told about all the same: a consumer that
    needs what ``Notify`` hears where ``Notify`` has no high to hold."""

    element: Element
    low: Low
    noted: Noted


class ConcludedNoted(Fact):
    """Every element valued, the cheap ones told about."""

    valued: tuple[CheapNoted | Dear, ...]


class AnsweredNoted(Reply[ConcludedNoted]):
    """What leaves."""


class NotedOperation(Route[Elements, AnsweredNoted]):
    """Value each element and tell the teller about every one."""


NOTED = program_of(
    *CORE, Noted, Notify, CheapNoted, Dear, ConcludedNoted, AnsweredNoted, NotedOperation
)
"""The reference program with a consumer added that needs ``Notify`` under the cheap branch."""


@pytest.mark.asyncio
async def test_a_consumer_added_demands_an_effect_and_weakens_its_evidence_not_at_all(
    parties: Callable[[dict[str, str]], None],
) -> None:
    assert faults_of(NOTED) == {
        ("never", (*ELEMENT, "CheapNoted")): (
            "CheapNoted at request.each.[].CheapNoted never constructs: High at"
            " request.each.[].High and Low at request.each.[].Low admit no ordering in common"
            " over the same operands"
        )
    }
    proof = unproven(NOTED, NotedOperation)
    parties({"a": "5"})
    blocked = await ran(NotedOperation, requested("a"), config(NOTED)(), proof)
    assert isinstance(blocked, Blocked)
    assert performed(Notify) == []
    assert made_in(blocked.occurrence.scope, Notify) == {}
    assert errors_of(blocked) == [
        (
            "relation",
            ("High",),
            "High at request.each.[0].High did not hold: value Amount at"
            " request.each.[0].Ask.heard.amount < bound Limit at Limit",
        )
    ]
    PERFORMED.clear()
    parties({"a": "50"})
    done = await valued(NOTED, "a", route=NotedOperation, proof=proof)
    assert [p.subject for p in performed(Notify)] == ["50"]
    assert [type(v) for v in done.route.reply.of.valued] == [Dear]


# --- 2. branches: evidence gathered first, one branch's effect after, a choice never guessed ---


class Judging(Party):
    """A party that says yes or no about each element."""


class Yes(Record):
    """The party's yes."""

    status: Literal["yes"]


class No(Record):
    """The party's no."""

    status: Literal["no"]


class Judge(Action[Judging, Yes | No]):
    """Ask the judging party about one element: the evidence the outer choice needs."""

    element: Element

    @override
    async def perform(self) -> Json:
        answers: dict[str, str] = json.loads(self.party.says.root)
        PERFORMED.append(Performed(Judge, self.element.name.root))
        return Json(json.dumps({"status": answers[self.element.name.root]}))


class Receipt(Scalar[str]):
    """What the teller says when charged."""

    root: str = Field(min_length=1)


class Charged(Record):
    """The teller's answer to a charge."""

    receipt: Receipt


class Charge(Action[Teller, Charged]):
    """Charge for an element valued high, whatever the party judged."""

    high: High

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(Charge, str(self.high.value.root), id(self.high)))
        return Json('{"receipt": "paid"}')


class ChargeLoose(Action[Teller, Charged]):
    """Charge for an element: holds the element alone, and is supplied from the first pass."""

    element: Element

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(ChargeLoose, self.element.name.root))
        return Json('{"receipt": "paid"}')


class BigYes(Fact):
    """Judged yes and valued high: charged."""

    element: Element
    yes: Yes
    high: High
    charged: Charged


class SmallYes(Fact):
    """Judged yes and valued low."""

    element: Element
    yes: Yes
    low: Low


class BigNo(Fact):
    """Judged no and valued high: charged all the same."""

    element: Element
    no: No
    high: High
    charged: Charged


class SmallNo(Fact):
    """Judged no and valued low."""

    element: Element
    no: No
    low: Low


class Priced(Fact):
    """Judged yes, big or small."""

    which: BigYes | SmallYes


class Free(Fact):
    """Judged no, big or small."""

    which: BigNo | SmallNo


class Outcome(Fact):
    """Each element's outcome."""

    element: Element
    which: Priced | Free


class Outcomes(Fact):
    """Every element's outcome."""

    outcomes: tuple[Outcome, ...]


class AnsweredOutcomes(Reply[Outcomes]):
    """What leaves."""


class ChargeOperation(Route[Elements, AnsweredOutcomes]):
    """Judge and value each element, charging for the big ones."""


class Judged(Config):
    """The party, the judging party and the teller."""

    party: Party
    judging: Judging
    teller: Teller


NESTED_CORE: tuple[type[object], ...] = (
    *(c for c in CORE if c not in {Deployment, Word}),
    Judging,
    Yes,
    No,
    Judge,
    Receipt,
    Charged,
    BigYes,
    SmallYes,
    BigNo,
    SmallNo,
    Priced,
    Free,
    Outcome,
    Outcomes,
    AnsweredOutcomes,
    ChargeOperation,
    Judged,
)
"""The nested program without its charge."""

NESTED = program_of(*NESTED_CORE, Charge)
"""The program whose charge holds the high it is performed with."""

NESTED_LOOSE = program_of(*NESTED_CORE, ChargeLoose)
"""The same program with the charge holding only the element: supplied before anything is
judged or valued, needed only on the two big leaves."""


@pytest.fixture
def judged(
    parties: Callable[[dict[str, str]], None], monkeypatch: pytest.MonkeyPatch
) -> Callable[[dict[str, str], dict[str, str]], None]:
    """The party's amounts and the judging party's answers per element."""

    def saying(amounts: dict[str, str], answers: dict[str, str]) -> None:
        parties(amounts)
        monkeypatch.setenv("JUDGING__SAYS", json.dumps(answers))

    return saying


@pytest.mark.asyncio
@pytest.mark.parametrize(("program", "charge"), [(NESTED, Charge), (NESTED_LOOSE, ChargeLoose)])
async def test_evidence_is_gathered_first_and_one_branchs_effect_performed_after(
    judged: Callable[[dict[str, str], dict[str, str]], None],
    program: ModuleType,
    charge: type[Action[Teller, Charged]],
) -> None:
    proof = proven(program)
    assert proof.faulted == ()
    judged(
        {"a": "50", "b": "50", "c": "5", "d": "5"}, {"a": "yes", "b": "no", "c": "yes", "d": "no"}
    )
    exporter = exporting()
    done = await ran(ChargeOperation, requested("a", "b", "c", "d"), config(program)(), proof)
    assert isinstance(done, Run)
    spans = exporter.get_finished_spans()
    assert {attributes(s)["tca.pass"] for s in spans if s.name in {"Judge", "Ask"}} == {1}
    assert {attributes(s)["tca.pass"] for s in spans if s.name == charge.__name__} == {2}
    leaves = [type(o.which.which) for o in done.route.reply.of.outcomes]
    assert leaves == [BigYes, BigNo, SmallYes, SmallNo]
    assert [p.subject for p in performed(Judge)] == ["a", "b", "c", "d"]
    assert [p.subject for p in performed(Ask)] == ["a", "b", "c", "d"]
    gathered = max(PERFORMED.index(p) for p in (*performed(Judge), *performed(Ask)))
    assert gathered < min(PERFORMED.index(p) for p in performed(charge))
    assert set(made_in(done.root, charge)) == {
        ("request", "each", "[0]", charge.__name__),
        ("request", "each", "[1]", charge.__name__),
    }
    if charge is Charge:
        highs = {
            id(o.which.which.high): o.element.name.root
            for o in done.route.reply.of.outcomes
            if isinstance(o.which.which, BigYes | BigNo)
        }
        assert sorted(highs[p.evidence] for p in performed(Charge)) == ["a", "b"]
    else:
        assert [p.subject for p in performed(ChargeLoose)] == ["a", "b"]
    assert done.passes == 3


class Mailed(Record):
    """What the teller says to a letter."""

    word: Word


class SendMail(Action[Teller, Mailed]):
    """Write to the teller about an element."""

    element: Element

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(SendMail, self.element.name.root))
        return Json(self.party.says.root)


class Texted(Record):
    """What the teller says to a text."""

    word: Word


class SendText(Action[Teller, Texted]):
    """Text the teller about an element."""

    element: Element

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(SendText, self.element.name.root))
        return Json(self.party.says.root)


class ByMail(Fact):
    """An element written about."""

    element: Element
    mailed: Mailed


class ByText(Fact):
    """An element texted about."""

    element: Element
    texted: Texted


class Sent(Fact):
    """Written or texted about: two effects, and nothing declared says which."""

    element: Element
    which: ByMail | ByText


class AllSent(Fact):
    """Every element sent about."""

    sent: tuple[Sent, ...]


class SentReply(Reply[AllSent]):
    """What leaves."""


class Send(Route[Elements, SentReply]):
    """Send about each element."""


SENDING: tuple[type[object], ...] = (
    Name,
    Element,
    Elements,
    Said,
    Teller,
    Word,
    Mailed,
    SendMail,
    Texted,
    SendText,
)
"""The two ways of sending about an element, toward the teller."""

UNDECIDED = program_of(*SENDING, ByMail, ByText, Sent, AllSent, SentReply, Send, Telling)
"""The program whose one choice is between two effects nothing decides."""


class ByMailLow(Fact):
    """An element valued low, written about."""

    element: Element
    low: Low
    mailed: Mailed


class ByTextHigh(Fact):
    """An element valued high, texted about."""

    element: Element
    high: High
    texted: Texted


class SentDecided(Fact):
    """Written or texted about, as the amount decides."""

    element: Element
    which: ByMailLow | ByTextHigh


class AllSentDecided(Fact):
    """Every element sent about."""

    sent: tuple[SentDecided, ...]


class SentDecidedReply(Reply[AllSentDecided]):
    """What leaves."""


class SendDecided(Route[Elements, SentDecidedReply]):
    """Send about each element the way its amount decides."""


DECIDED = program_of(
    *CORE,
    *SENDING,
    ByMailLow,
    ByTextHigh,
    SentDecided,
    AllSentDecided,
    SentDecidedReply,
    SendDecided,
)
"""The same two effects, each on a branch the party's amount decides."""


@pytest.mark.asyncio
async def test_a_choice_between_effects_is_never_guessed_and_a_decided_one_performs_one(
    parties: Callable[[dict[str, str]], None],
) -> None:
    assert set(faults_of(UNDECIDED)) == {("ambiguous", ("Sent", "which"))}
    parties({"a": "5"})
    blocked = await ran(Send, requested("a"), config(UNDECIDED)(), unproven(UNDECIDED, Send))
    assert isinstance(blocked, Blocked)
    assert PERFORMED == []
    (cause,) = blocked.causes
    assert isinstance(cause, Undecided)
    assert (cause.occurrence.construction.cls, cause.premise) == (Sent, ("which", None))
    assert [(ref.cls, [o.construction.cls for o in a]) for ref, a in cause.alternatives] == [
        (ByMail, [SendMail]),
        (ByText, [SendText]),
    ]
    assert errors_of(blocked) == [
        (
            "undecided",
            ("Sent", "which"),
            "Sent.which at request.each.[0].Sent is decided by nothing before an effect: ByMail at"
            " request.each.[].ByMail needs SendMail at request.each.[0].SendMail performed; ByText"
            " at request.each.[].ByText needs SendText at request.each.[0].SendText performed",
        )
    ]
    proof = proven(DECIDED)
    assert proof.faulted == ()
    for amount, mailed, texted in (("5", ["a"], []), ("50", [], ["a"])):
        PERFORMED.clear()
        parties({"a": amount})
        done = await ran(SendDecided, requested("a"), config(DECIDED)(), proof)
        assert isinstance(done, Run)
        assert [p.subject for p in performed(SendMail)] == mailed
        assert [p.subject for p in performed(SendText)] == texted


# --- 3. occurrence integrity -------------------------------------------------------------------


class Reviewed(Reply[Concluded]):
    """What a second route answers from the same conclusion."""


class Review(Route[Elements, Reviewed]):
    """A second route over the same classes: its constructions are its own."""


TWO_ROUTES = program_of(*REFERENCE, Reviewed, Review)
"""The reference program with a second route over the same classes."""


@pytest.mark.asyncio
async def test_equal_values_reused_objects_siblings_routes_and_invocations_are_their_own(
    parties: Callable[[dict[str, str]], None],
) -> None:
    parties({"x": "50", "y": "5"})
    proof = proven(TWO_ROUTES)
    element = Element(name=Name("x"))
    request = Elements(each=(element, element, Element(name=Name("y"))))
    done = await ran(Operation, request, config(TWO_ROUTES)(), proof)
    assert isinstance(done, Run)
    assert [p.subject for p in performed(Ask)] == ["x", "x", "y"]
    twice = performed(Notify)
    assert [p.subject for p in twice] == ["50", "50"]
    assert twice[0].evidence != twice[1].evidence
    dears = [v for v in done.route.reply.of.valued if isinstance(v, Dear)]
    assert {id(d.high) for d in dears} == {twice[0].evidence, twice[1].evidence}
    assert dears[0].noted is not dears[1].noted
    assert set(made_in(done.root, Notify)) == {
        ("request", "each", "[0]", "Notify"),
        ("request", "each", "[1]", "Notify"),
    }
    first_ask, second_ask, _ = occurrences_of(done.root, Ask)
    for ask in (first_ask, second_ask):
        witness = constructed(ask).supplied.premises["element"].found
        assert witness.instance is element
        assert witness.owner is ask.scope
        assert witness.path == ask.scope.path
        assert (ask.construction, ()) in ask.scope.arrived
    first, second = occurrences_of(done.root, Notify)
    assert constructed(first).supplied.premises["party"].found.path == ("deployment", "teller")
    assert constructed(first).supplied.premises["high"].found.owner is first.scope
    assert constructed(second).supplied.premises["high"].found.owner is second.scope
    PERFORMED.clear()
    reviewed = await ran(Review, requested("x"), config(TWO_ROUTES)(), proof)
    assert isinstance(reviewed, Run)
    assert [p.subject for p in performed(Notify)] == ["50"]
    (own,) = occurrences_of(reviewed.root, Notify)
    assert own.construction in proof.constructs(Review)
    assert own.construction not in proof.constructs(Operation)
    PERFORMED.clear()
    parties({"a": "20", "b": "30"})
    first_run, second_run = await asyncio.gather(
        ran(Operation, requested("a"), config(TWO_ROUTES)(), proof),
        ran(Operation, requested("b"), config(TWO_ROUTES)(), proof),
    )
    assert isinstance(first_run, Run)
    assert isinstance(second_run, Run)
    assert sorted(p.subject for p in performed(Notify)) == ["20", "30"]
    assert {id(h) for h in notified(first_run).values()} == {
        p.evidence for p in performed(Notify) if p.subject == "20"
    }
    assert {id(h) for h in notified(second_run).values()} == {
        p.evidence for p in performed(Notify) if p.subject == "30"
    }


@pytest.mark.asyncio
async def test_two_invocations_sharing_request_and_deployment_objects_perform_their_own(
    parties: Callable[[dict[str, str]], None],
) -> None:
    proof = proven(TWO_ROUTES)
    parties({"a": "20"})
    shared, deployment = requested("a"), config(TWO_ROUTES)()
    assert isinstance(deployment, Deployment)
    one, other = await asyncio.gather(
        ran(Operation, shared, deployment, proof), ran(Operation, shared, deployment, proof)
    )
    assert isinstance(one, Run)
    assert isinstance(other, Run)
    assert [p.subject for p in performed(Notify)] == ["20", "20"]
    (mine,), (theirs,) = occurrences_of(one.root, Notify), occurrences_of(other.root, Notify)
    party_mine = constructed(mine).supplied.premises["party"].found
    party_theirs = constructed(theirs).supplied.premises["party"].found
    assert party_mine.instance is party_theirs.instance is deployment.teller
    assert party_mine.owner is one.root
    assert party_theirs.owner is other.root
    assert party_mine.path == party_theirs.path == ("deployment", "teller")
    assert constructed(mine).instance is not constructed(theirs).instance
    assert (
        mine.scope.arrived[mine.construction, ()]
        is not theirs.scope.arrived[theirs.construction, ()]
    )


@pytest.mark.asyncio
async def test_nested_collections_perform_each_occurrence_once(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CATALOG__PRICES", '{"tea": "2.50", "mug": "4", "pot": "10"}')
    monkeypatch.setenv("FRAUD__SAYS", '{"status": "clear"}')
    occurrences.PERFORMED.clear()
    exporter = exporting()
    request = occurrences.PlaceOrder.model_validate_json(ORDER)
    done = await ran(occurrences.Checkout, request, config(occurrences)(), proven(occurrences))
    assert isinstance(done, Run)
    assert sorted(occurrences.PERFORMED) == ["mug", "mug", "pot", "screen", "tea", "tea", "tea"]
    sites = [
        attributes(s)["tca.site"]
        for s in exporter.get_finished_spans()
        if s.name in {"Quote", "Screen"}
    ]
    assert len(sites) == len(set(sites)) == 7


# --- 4. substitution: another instance, another class, never performed, none of the batch -------


class Swapping(Action[Teller, Noted]):
    """Tell the teller about an element valued high, with a validator that puts another high
    in place of the one supplied when the amount is 60."""

    high: High

    @model_validator(mode="after")
    def swap(self) -> Self:
        if self.high.value.root == 60:
            object.__setattr__(self, "high", High(value=Amount(Decimal(60)), bound=Limit()))
        return self

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(Swapping, str(self.high.value.root), id(self.high)))
        return Json(self.party.says.root)


class Impostor(Action[Teller, Noted]):
    """An action of another class holding a party and a high as ``Masked`` does: in no program,
    constructed by no proof's construction."""

    high: High

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(Impostor, str(self.high.value.root), id(self.high)))
        return Json(self.party.says.root)


class Masked(Action[Teller, Noted]):
    """Tell the teller about an element valued high, with a validator that returns an impostor
    holding the same party and the same high in place of the instance Pydantic constructed when
    the amount is 60."""

    high: High

    @model_validator(mode="after")
    def mask(self) -> Self:
        if self.high.value.root == 60:
            return Impostor(high=self.high, party=self.party)  # type: ignore[return-value]
        return self

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(Masked, str(self.high.value.root), id(self.high)))
        return Json(self.party.says.root)


def telling_through(
    action: type[Action[Teller, Noted]],
) -> tuple[ModuleType, type[Route[Elements, Reply[Fact]]]]:
    """The reference program with its notification made through another action class, and its
    route, which is made here and so is typed by hand."""
    dear = type(
        f"Dear{action.__name__}",
        (Fact,),
        {
            "__annotations__": {"element": Element, "high": High, "noted": Noted},
            "__module__": __name__,
            "__doc__": "An element valued high, told about.",
        },
    )
    concluded = type(
        f"Concluded{action.__name__}",
        (Fact,),
        {
            "__annotations__": {"valued": tuple[Cheap | dear, ...]},  # type: ignore[valid-type]
            "__module__": __name__,
            "__doc__": "Every element valued.",
        },
    )
    answered = type(
        f"Answered{action.__name__}",
        (Reply[concluded],),  # type: ignore[valid-type]
        {"__module__": __name__, "__doc__": "What leaves."},
    )
    route = type(
        f"{action.__name__}Operation",
        (Route[Elements, answered],),  # type: ignore[valid-type]
        {"__module__": __name__, "__doc__": "Value each element."},
    )
    program = program_of(*CORE, Noted, action, Cheap, dear, concluded, answered, route)
    return program, cast("type[Route[Elements, Reply[Fact]]]", route)


type Forgery = Literal["premise", "action"]
"""How the second element's action is forged by its own validator: another instance in place of
the high supplied, or an impostor of another class in place of the action constructed."""

FORGED: dict[Forgery, tuple[type[Action[Teller, Noted]], tuple[str, tuple[str, ...], str]]] = {
    "premise": (
        Swapping,
        (
            "substituted",
            ("Swapping", "high"),
            "Swapping.high at request.each.[1].Swapping holds another instance than the one"
            " supplied for it",
        ),
    ),
    "action": (
        Masked,
        (
            "substituted",
            ("Masked",),
            "Masked at request.each.[1].Masked constructed Impostor, not itself",
        ),
    ),
}
"""Each forgery's action class and the one refusal it meets, at the forged occurrence."""


@pytest.mark.asyncio
@pytest.mark.parametrize("forgery", ["premise", "action"])
@pytest.mark.parametrize("eager", [False, True])
async def test_a_forged_candidate_after_a_valid_one_starts_no_action_of_the_batch(
    parties: Callable[[dict[str, str]], None],
    *,
    forgery: Forgery,
    eager: bool,
) -> None:
    loop = asyncio.get_running_loop()
    factory = loop.get_task_factory()
    if eager:
        loop.set_task_factory(asyncio.eager_task_factory)
    try:
        action, (code, loc, message) = FORGED[forgery]
        program, route = telling_through(action)
        proof = proven(program)
        assert proof.faulted == ()
        parties({"a": "50"})
        done = await ran(route, requested("a"), config(program)(), proof)
        assert isinstance(done, Run)
        assert [p.subject for p in performed(action)] == ["50"]
        PERFORMED.clear()
        parties({"a": "50", "b": "60"})
        with pytest.raises(ValidationError) as failure:
            await ran(route, requested("a", "b"), config(program)(), proof)
        assert [(e["type"], e["loc"], e["msg"]) for e in failure.value.errors()] == [
            (code, loc, message)
        ]
        assert performed(action) == []
        assert performed(Impostor) == []
        assert [p.subject for p in performed(Ask)] == ["a", "b"]
    finally:
        loop.set_task_factory(factory)


# --- 5. admission timing: pending, refuted and unadmitted evidence demands nothing -------------


@pytest.mark.asyncio
async def test_pending_refuted_failed_and_unadmitted_evidence_performs_nothing_after_it(
    parties: Callable[[dict[str, str]], None], monkeypatch: pytest.MonkeyPatch
) -> None:
    parties({"a": "5", "boom": "50", "c": "50"})
    asking = Ask.perform

    async def failing(self: Ask) -> Json:
        if self.element.name.root == "boom":
            PERFORMED.append(Performed(Ask, "boom"))
            down = ConnectionError("party down")
            raise down
        return await asking(self)

    monkeypatch.setattr(Ask, "perform", failing)
    with pytest.raises(ExceptionGroup) as failure:
        await valued(PROGRAM, "a", "boom", "c")
    assert [type(e) for e in failure.value.exceptions] == [ConnectionError]
    assert sorted(p.subject for p in performed(Ask)) == ["a", "boom", "c"]
    assert performed(Notify) == []
    monkeypatch.setattr(Ask, "perform", asking)
    PERFORMED.clear()
    done = await valued(PROGRAM, "a", "c")
    assert [p.subject for p in performed(Notify)] == ["50"]
    (high_a,) = (m for path, m in made_in(done.root, High).items() if path[2] == "[0]")
    assert isinstance(high_a, Refuted)
    assert ("request", "each", "[0]", "Notify") not in made_in(done.root, Notify)
    assert ("request", "each", "[1]", "Notify") in made_in(done.root, Notify)


# --- 6. conditional construction: blocked without an irrelevant effect, and an effect kept -----


class Reading(Scalar[Decimal]):
    """A measurement that arrives."""

    root: Decimal


class Measured(Request):
    """What arrives: one reading."""

    reading: Reading


class Zero(Scalar[Decimal]):
    """The reading under which a reading is negative."""

    root: Decimal = Decimal(0)


class Ten(Scalar[Decimal]):
    """The reading beyond which a reading is over."""

    root: Decimal = Decimal(10)


class Negative(Under[Reading, Zero]):
    """A reading under zero."""


class Within(AtMost[Reading, Ten]):
    """A reading at most ten: holds of every negative reading, and of others."""


class Over(Beyond[Reading, Ten]):
    """A reading over ten."""


class Told(Record):
    """What the teller says."""

    word: Word


class TellWithin(Action[Teller, Told]):
    """Tell the teller of a reading at most ten: supplied for a reading of 5, needed only where
    the reading is negative."""

    within: Within

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(TellWithin, str(self.within.value.root)))
        return Json(self.party.says.root)


class TellNegative(Action[Teller, Told]):
    """Tell the teller of a negative reading."""

    negative: Negative

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(TellNegative, str(self.negative.value.root)))
        return Json(self.party.says.root)


class Below(Fact):
    """A negative reading, told of."""

    negative: Negative
    told: Told


class Above(Fact):
    """A reading over ten."""

    over: Over


class Decided(Fact):
    """Below or above: nothing is concluded of a reading between."""

    which: Below | Above


class DecidedReply(Reply[Decided]):
    """What leaves."""


class Decide(Route[Measured, DecidedReply]):
    """Decide a reading."""


READINGS: tuple[type[object], ...] = (
    Reading,
    Measured,
    Zero,
    Ten,
    Negative,
    Over,
    Said,
    Teller,
    Word,
    Told,
    Below,
    Above,
    Decided,
    DecidedReply,
    Decide,
    Telling,
)
"""The two branches, without the action."""

NONEXHAUSTIVE = program_of(*READINGS, Within, TellWithin)
"""The program whose action holds a reading at most ten, needed only where it is negative: a
reading between is in neither branch, and the action is supplied for it."""

GUARDED = program_of(*READINGS, TellNegative)
"""The same program with the action holding the evidence of the branch that needs it."""


def measured(reading: str) -> Measured:
    """A request of one reading."""
    return Measured(reading=Reading(Decimal(reading)))


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
@pytest.mark.parametrize(
    ("program", "action"), [(NONEXHAUSTIVE, TellWithin), (GUARDED, TellNegative)]
)
async def test_a_route_blocked_in_neither_branch_performs_no_effect_of_either(
    program: ModuleType, action: type[object]
) -> None:
    proof = proven(program)
    assert proof.faulted == ()
    for reading, outcome, told in (("5", Blocked, []), ("-1", Run, ["-1"]), ("50", Run, [])):
        PERFORMED.clear()
        done = await ran(Decide, measured(reading), config(program)(), proof)
        assert isinstance(done, outcome)
        assert [p.subject for p in performed(action)] == told
    blocked = await ran(Decide, measured("5"), config(program)(), proof)
    assert isinstance(blocked, Blocked)
    assert {c.occurrence.construction.cls for c in blocked.causes} == {Negative, Over}


class Quick(Value):
    """A reading to be told of at once."""

    reading: Reading


class Slow(Value):
    """A reading to be told of later."""

    reading: Reading


class Timed(Request):
    """What arrives: a reading, quick or slow."""

    kind: Quick | Slow


class TellTimed(Action[Teller, Told]):
    """Tell the teller of a reading, quick or slow: holds the choice."""

    kind: Quick | Slow

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(TellTimed, type(self.kind).__name__))
        return Json(self.party.says.root)


class TellReading(Action[Teller, Told]):
    """Tell the teller of a reading: holds what both alternatives hold, and is needed under
    either."""

    reading: Reading

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(TellReading, str(self.reading.root)))
        return Json(self.party.says.root)


class ToldQuick(Fact):
    """A quick reading, told of."""

    quick: Quick
    told: Told


class ToldSlow(Fact):
    """A slow reading, told of."""

    slow: Slow
    told: Told


class ToldTimed(Fact):
    """Told of, quick or slow."""

    which: ToldQuick | ToldSlow


class ToldReply(Reply[ToldTimed]):
    """What leaves."""


class Tell(Route[Timed, ToldReply]):
    """Tell of a reading."""


TIMED: tuple[type[object], ...] = (
    Reading,
    Quick,
    Slow,
    Timed,
    Said,
    Teller,
    Word,
    Told,
    ToldQuick,
    ToldSlow,
    ToldTimed,
    ToldReply,
    Tell,
    Telling,
)
"""The two arrival alternatives and their conclusions, without the action."""

HELD = program_of(*TIMED, TellTimed)
"""The program whose action holds the choice among what arrives."""

UNHELD = program_of(*TIMED, TellReading)
"""The same program with the action holding only what both alternatives hold."""


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
@pytest.mark.parametrize(("program", "action"), [(HELD, TellTimed), (UNHELD, TellReading)])
async def test_an_action_needed_under_either_alternative_is_performed_once_under_each(
    program: ModuleType, action: type[object]
) -> None:
    proof = proven(program)
    assert proof.faulted == ()
    for told in (Quick, Slow):
        PERFORMED.clear()
        request = Timed(kind=told(reading=Reading(Decimal(1))))
        done = await ran(Tell, request, config(program)(), proof)
        assert isinstance(done, Run)
        assert [p.action for p in PERFORMED] == [action]
        assert type(done.route.reply.of.which) is (ToldQuick if told is Quick else ToldSlow)


@pytest.mark.asyncio
async def test_an_effect_performed_stays_performed_when_what_needs_it_then_blocks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PARTY__SAYS", '{"amount": "4"}')
    exporter = exporting()
    proof = proven(optional)
    request = optional.PlaceOrder.model_validate_json('{"sku": "tea"}')
    blocked = await ran(optional.Checkout, request, config(optional)(), proof)
    assert isinstance(blocked, Blocked)
    (quote,) = occurrences_of(blocked.occurrence.scope, optional.Quote)
    assert isinstance(quote.made, Constructed)
    heard = blocked.occurrence.scope.arrived[quote.construction, ()]
    assert isinstance(heard, optional.Quoted)
    assert heard.coupon is None
    (span,) = (s for s in exporter.get_finished_spans() if s.name == "Quote")
    assert attributes(span)["tca.outcome"] == "heard"
    assert [(e["type"], e["loc"]) for e in refused(blocked).errors()] == [
        ("missing", ("Discount", "coupon"))
    ]


@pytest.mark.asyncio
async def test_no_element_and_another_implementation_demand_nothing_more(
    parties: Callable[[dict[str, str]], None], monkeypatch: pytest.MonkeyPatch
) -> None:
    parties({})
    empty = await valued(PROGRAM)
    assert PERFORMED == []
    assert empty.route.reply.of.valued == ()
    assert empty.passes == 1
    parties({"a": "50"})
    done = await valued(PROGRAM, "a")
    assert [p.subject for p in performed(Notify)] == ["50"]
    before = set(made_in(done.root, Notify))
    PERFORMED.clear()

    async def telling(self: Notify) -> Python:
        PERFORMED.append(Performed(Notify, str(self.high.value.root), id(self.high)))
        return Python({"word": "dear"})

    monkeypatch.setattr(Notify, "perform", telling)
    again = await valued(PROGRAM, "a")
    assert [p.subject for p in performed(Notify)] == ["50"]
    assert set(made_in(again.root, Notify)) == before
    assert again.route.reply.of.valued[0].noted.word.root == "dear"  # type: ignore[union-attr]


# --- 7. the decision first; the effect that only completes the outcome after -------------------


class Permit(Request):
    """What arrives: a name to admit."""

    name: Name


class Allowed(Record):
    """The judging party's yes."""

    status: Literal["allowed"]


class Denied(Record):
    """The judging party's no."""

    status: Literal["denied"]


class Gate(Action[Judging, Allowed | Denied]):
    """Ask the judging party whether to admit: the effect that produces the decision."""

    permit: Permit

    @override
    async def perform(self) -> Json:
        answers: dict[str, str] = json.loads(self.party.says.root)
        PERFORMED.append(Performed(Gate, self.permit.name.root))
        return Json(json.dumps({"status": answers[self.permit.name.root]}))


class PingPermit(Action[Teller, Pinged]):
    """Ping the teller about a permit: holds the request alone, and is supplied from the
    start."""

    permit: Permit

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(PingPermit, self.permit.name.root))
        return Json(self.party.says.root)


class Admitted(Fact):
    """A permit allowed and pinged about."""

    allowed: Allowed
    pinged: Pinged


class AdmittedReply(Reply[Admitted]):
    """What leaves."""


class Admit(Route[Permit, AdmittedReply]):
    """Admit a permit."""


class Refused(Fact):
    """A permit denied."""

    denied: Denied


class Gated(Fact):
    """Admitted or refused."""

    which: Admitted | Refused


class GatedReply(Reply[Gated]):
    """What leaves."""


class AdmitEither(Route[Permit, GatedReply]):
    """Admit a permit, or refuse it."""


class Gates(Config):
    """The judging party and the teller."""

    judging: Judging
    teller: Teller


GATING: tuple[type[object], ...] = (
    Name,
    Permit,
    Said,
    Judging,
    Teller,
    Word,
    Pinged,
    Allowed,
    Denied,
    Gate,
    PingPermit,
    Admitted,
    Gates,
)
"""The gate, the ping, and the conclusion that needs both."""

ADMIT = program_of(*GATING, AdmittedReply, Admit)
"""The program whose one conclusion needs the gate's yes and the ping's record."""

ADMIT_EITHER = program_of(*GATING, Refused, Gated, GatedReply, AdmitEither)
"""The same program with a fallback for the gate's no."""


@pytest.fixture
def gated(parties: Callable[[dict[str, str]], None], monkeypatch: pytest.MonkeyPatch) -> None:
    """The judging party's answers per permit name."""
    parties({})
    monkeypatch.setenv("JUDGING__SAYS", json.dumps({"yes": "allowed", "no": "denied"}))


@pytest.mark.asyncio
@pytest.mark.usefixtures("gated")
@pytest.mark.parametrize(("program", "route"), [(ADMIT, Admit), (ADMIT_EITHER, AdmitEither)])
async def test_the_gate_is_performed_first_and_the_ping_only_once_the_gate_allowed(
    program: ModuleType, route: type[Route[Permit, Reply[Fact]]]
) -> None:
    exporter = exporting()
    proof = proven(program)
    assert proof.faulted == ()
    done = await ran(route, Permit(name=Name("yes")), config(program)(), proof)
    assert isinstance(done, Run)
    assert [p.action for p in PERFORMED] == [Gate, PingPermit]
    assert done.passes == 3
    passes = {
        s.name: attributes(s)["tca.pass"]
        for s in exporter.get_finished_spans()
        if s.name in {"Gate", "PingPermit"}
    }
    assert (passes["Gate"], passes["PingPermit"]) == (1, 2)
    PERFORMED.clear()
    refused_ = await ran(route, Permit(name=Name("no")), config(program)(), proof)
    assert [p.action for p in PERFORMED] == [Gate]
    if route is Admit:
        assert isinstance(refused_, Blocked)
        assert errors_of(refused_) == [
            (
                "missing",
                ("Admitted", "allowed"),
                "no instance fills Admitted.allowed at Admitted, which holds Allowed; Gate at Gate"
                " heard Denied",
            )
        ]
    else:
        assert isinstance(refused_, Run)
        assert type(refused_.route.reply.of.which) is Refused  # type: ignore[union-attr]


# --- 8. a dormant branch's ordinary construction is never asked for ----------------------------


class Amounts(Request):
    """What arrives: amounts, any number."""

    amounts: tuple[Amount, ...]


class Clear(Record):
    """The judging party's clear."""

    status: Literal["clear"]


class Flagged(Record):
    """The judging party's flag."""

    status: Literal["flagged"]


class Vet(Action[Judging, Clear | Flagged]):
    """Ask the judging party about the amounts."""

    amounts: Amounts

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(Vet, str(len(self.amounts.amounts))))
        return Json(self.party.says.root)


class Total(Sum[Amount]):
    """Every amount, summed."""


class Stats(Fact):
    """Every amount, no more than one: a native constraint, which rejects two amounts as a
    failure of the construction, not a refutation."""

    amounts: Annotated[tuple[Amount, ...], MaxLen(1)]


class Normal(Fact):
    """Amounts cleared, totalled."""

    clear: Clear
    total: Total


class Special(Fact):
    """Amounts flagged, with their stats."""

    flagged: Flagged
    stats: Stats


class Vetted(Fact):
    """Normal or special, as the judging party says."""

    which: Normal | Special


class VettedReply(Reply[Vetted]):
    """What leaves."""


class Vetting(Route[Amounts, VettedReply]):
    """Vet amounts."""


class Vets(Config):
    """The judging party."""

    judging: Judging


VETTED = program_of(
    Amount,
    Amounts,
    Said,
    Judging,
    Clear,
    Flagged,
    Vet,
    Total,
    Stats,
    Normal,
    Special,
    Vetted,
    VettedReply,
    Vetting,
    Vets,
)
"""A route whose dormant branch holds a construction that would fail over the request."""


@pytest.mark.asyncio
async def test_a_dormant_branchs_failing_construction_is_never_asked_for_and_a_selected_ones_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    PERFORMED.clear()
    proof = proven(VETTED)
    assert proof.faulted == ()
    request = Amounts(amounts=(Amount(Decimal(1)), Amount(Decimal(2))))
    with pytest.raises(ValidationError) as failure:
        Stats(amounts=request.amounts)
    assert [(e["type"], e["loc"]) for e in failure.value.errors()] == [("too_long", ("amounts",))]
    monkeypatch.setenv("JUDGING__SAYS", '{"status": "clear"}')
    done = await ran(Vetting, request, config(VETTED)(), proof)
    assert isinstance(done, Run)
    assert type(done.route.reply.of.which) is Normal
    assert done.route.reply.of.which.total.root == 3  # type: ignore[union-attr]
    assert made_in(done.root, Stats) == {}
    assert [p.action for p in PERFORMED] == [Vet]
    monkeypatch.setenv("JUDGING__SAYS", '{"status": "flagged"}')
    with pytest.raises(ValidationError) as failed:
        await ran(Vetting, request, config(VETTED)(), proof)
    assert failed.value.title == "Stats"
    assert failed.value.__notes__ == ["at Stats"]
    assert [(e["type"], e["loc"]) for e in failed.value.errors()] == [("too_long", ("amounts",))]


# --- 9. shared occurrences are evaluated once, however many fields reach them -----------------


class Seed(Scalar[Decimal]):
    """What a chain of facts grows from."""

    root: Decimal


class Seeded(Request):
    """What arrives: a seed."""

    seed: Seed


class Alone(Config):
    """No party."""


def chained(depth: int) -> tuple[ModuleType, type[Route[Seeded, Reply[Fact]]]]:
    """A program whose facts form a chain of diamonds: each holds the one before it at two
    fields, so a tree expansion visits ``2 ** depth`` occurrences and a graph ``depth``."""
    steps: list[type[Fact]] = [
        type(
            "Step0",
            (Fact,),
            {"__annotations__": {"seed": Seed}, "__module__": __name__, "__doc__": "The first."},
        )
    ]
    for index in range(1, depth + 1):
        steps.append(
            type(
                f"Step{index}",
                (Fact,),
                {
                    "__annotations__": {"left": steps[-1], "right": steps[-1]},
                    "__module__": __name__,
                    "__doc__": f"Step {index}: the one before, held twice.",
                },
            )
        )
    reply = type("ClimbedReply", (Reply[steps[-1]],), {"__module__": __name__, "__doc__": "Out."})  # type: ignore[valid-type]
    route = type(
        "Climb",
        (Route[Seeded, reply],),  # type: ignore[valid-type]
        {"__module__": __name__, "__doc__": "Climb the chain."},
    )
    program = program_of(Seed, Seeded, Alone, *steps, reply, route)
    return program, cast("type[Route[Seeded, Reply[Fact]]]", route)


@pytest.mark.asyncio
async def test_a_chain_of_diamonds_is_evaluated_as_a_graph_not_expanded_as_a_tree(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    binding = engine.bound
    bindings: list[int] = []

    def counting(construction: engine.Construction, scope: Scope) -> engine.Bound:
        bindings.append(1)
        return binding(construction, scope)

    monkeypatch.setattr(engine, "bound", counting)
    counts: dict[int, int] = {}
    for depth in (4, 8, 16):
        program, route = chained(depth)
        bindings.clear()
        done = await ran(route, Seeded(seed=Seed(Decimal(1))), Alone(), proven(program))
        assert isinstance(done, Run)
        assert done.passes == 1
        assert len(done.root.made) == depth + 3
        counts[depth] = len(bindings)
    assert counts[16] - counts[8] == 2 * (counts[8] - counts[4])
    assert counts[16] <= 2 * (16 + 3)
