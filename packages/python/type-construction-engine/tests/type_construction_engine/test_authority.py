"""Effect authorization against adversarial programs and runs: an effect is performed because
its exact occurrence was constructed from the evidence the proof established justifies it,
observed at ``perform`` itself, by subject, timing and evidence, never through the
authorization's own reads. The base program values each element of a request through a party
that answers per element and tells a teller about each element valued high; each test adds the
classes its counterexample needs."""

import asyncio
import json
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from decimal import Decimal
from inspect import signature
from pathlib import Path
from types import ModuleType
from typing import Literal, NamedTuple, Self, override

import pytest
from pydantic import BaseModel, Field, ValidationError, model_validator

from type_construction import engine
from type_construction.engine import (
    Blocked,
    Constructed,
    Execution,
    Invocation,
    Occurrence,
    Proof,
    Refuted,
    Run,
    Scope,
    config,
    performed_in_span,
    proven,
    ran,
    scopes,
    unauthorized,
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
    Value,
)

from . import occurrences, optional
from .test_execution import attributes
from .test_occurrences import ORDER, exporting


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
    """Tell the teller about an element valued high: made from the evidence that decides it."""

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
"""The reference program: ``Ask`` obtains the evidence, ``Low`` or ``High`` decides, ``Notify``
holds the ``High`` that justifies it."""

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


# --- 1, 4. the correct branch, from evidence obtained before the choice ---------------------


@pytest.mark.asyncio
async def test_notify_is_performed_only_for_the_element_whose_own_high_evidence_exists(
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
    spans = exporter.get_finished_spans()
    by_site = {attributes(s)["tca.site"]: s for s in spans if s.name == "Notify"}
    assert set(by_site) == {"request.each.[1].Notify", "request.each.[2].Notify"}
    asks = {attributes(s)["tca.pass"] for s in spans if s.name == "Ask"}
    assert asks == {1}
    assert {attributes(s)["tca.pass"] for s in by_site.values()} == {2}
    proof = proven(PROGRAM)
    by_action = {j.action.cls: j for j in proof.justifications}
    assert set(by_action) == {Ask, Notify}
    assert all(j.established for j in by_action.values())
    assert by_action[Ask].joint.ways == ()


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


# --- 2. a branch-specific action missing its deciding premise ------------------------------


class Pinged(Record):
    """What the teller says when pinged."""

    word: Word


class Ping(Action[Teller, Pinged]):
    """Tell the teller about an element: holds the element, not what decides the branch."""

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


UNGUARDED = program_of(
    *CORE, Pinged, Ping, Cheap, DearPinged, ConcludedPinged, AnsweredPinged, PingOperation
)
"""The program whose branch-specific action holds nothing that decides the branch."""


def test_a_branch_specific_action_without_its_deciding_premise_is_refused_at_startup() -> None:
    PERFORMED.clear()
    faults = faults_of(UNGUARDED)
    assert set(faults) == {("undecided", ("Ping",))}
    assert faults["undecided", ("Ping",)] == (
        "Ping at request.each.[] is performed when ConcludedPinged.valued holds Cheap at"
        " request.each.[].Cheap as when it holds DearPinged at request.each.[].DearPinged; High at"
        " request.each.[].High, which DearPinged at request.each.[].DearPinged needs, would decide"
        " it, and Ping holds nothing that does"
    )
    assert PERFORMED == []


# --- 3. an action under several alternatives, accepted only when its evidence covers them ----


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
    """Charge for an element valued high, whatever the party judged: holds the evidence that
    decides the inner choice under either outer alternative."""

    high: High

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(Charge, str(self.high.value.root), id(self.high)))
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
    Priced,
    Free,
    Outcome,
    Outcomes,
    AnsweredOutcomes,
    ChargeOperation,
    Judged,
)
"""The nested program without its charge and the four leaves."""

NESTED = program_of(*NESTED_CORE, Charge, BigYes, SmallYes, BigNo, SmallNo)
"""The program whose charge is used under both outer alternatives, and holds what decides
the inner choice under each."""


class ChargeLoose(Action[Teller, Charged]):
    """Charge for an element: holds nothing that decides the inner choice."""

    element: Element

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(ChargeLoose, self.element.name.root))
        return Json('{"receipt": "paid"}')


NESTED_LOOSE = program_of(*NESTED_CORE, ChargeLoose, BigYes, SmallYes, BigNo, SmallNo)
"""The same program with the charge holding only the element: reachable under both outer
alternatives, and used under neither's small leaf."""


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
async def test_an_action_under_several_alternatives_is_accepted_only_where_its_evidence_covers_them(
    judged: Callable[[dict[str, str], dict[str, str]], None],
) -> None:
    faults = faults_of(NESTED_LOOSE)
    assert set(faults) == {("undecided", ("ChargeLoose",))}
    assert faults["undecided", ("ChargeLoose",)] == (
        "ChargeLoose at request.each.[] is performed when Priced.which holds SmallYes at"
        " request.each.[].SmallYes as when it holds BigYes at request.each.[].BigYes; High at"
        " request.each.[].High, which BigYes at request.each.[].BigYes needs, would decide it, and"
        " ChargeLoose holds nothing that does"
    )
    proof = proven(NESTED)
    by_action = {j.action.cls: j for j in proof.justifications}
    assert all(j.established for j in by_action.values())
    assert by_action[Judge].joint.ways == ()
    assert by_action[Charge].joint.open == ()
    judged(
        {"a": "50", "b": "50", "c": "5", "d": "5"}, {"a": "yes", "b": "no", "c": "yes", "d": "no"}
    )
    done = await ran(ChargeOperation, requested("a", "b", "c", "d"), config(NESTED)(), proof)
    assert isinstance(done, Run)
    leaves = [type(o.which.which) for o in done.route.reply.of.outcomes]
    assert leaves == [BigYes, BigNo, SmallYes, SmallNo]
    highs = {
        id(o.which.which.high): o.element.name.root
        for o in done.route.reply.of.outcomes
        if isinstance(o.which.which, BigYes | BigNo)
    }
    assert sorted(highs[p.evidence] for p in performed(Charge)) == ["a", "b"]
    assert all(p.subject == "50" for p in performed(Charge))
    assert [p.subject for p in performed(Judge)] == ["a", "b", "c", "d"]
    assert max(PERFORMED.index(p) for p in performed(Judge)) < min(
        PERFORMED.index(p) for p in performed(Charge)
    )


# --- 5. occurrence integrity ------------------------------------------------------------------


class Reviewed(Reply[Concluded]):
    """What a second route answers from the same conclusion."""


class Review(Route[Elements, Reviewed]):
    """A second route over the same classes: its constructions are its own."""


TWO_ROUTES = program_of(*REFERENCE, Reviewed, Review)
"""The reference program with a second route over the same classes."""


@pytest.mark.asyncio
async def test_equal_values_reused_objects_siblings_routes_and_invocations_keep_their_authority(
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
    first = occurrences_of(done.root, Notify)[0]
    made = first.made
    assert isinstance(made, Constructed)
    assert made.supplied.premises["party"].found.path == ("deployment", "teller")
    assert made.supplied.premises["high"].found.path == ("request", "each", "[0]", "High")
    assert unauthorized(Invocation(Operation, proof, done.root, set()), first) is None
    assert unauthorized(Invocation(Operation, proof, done.root, {first}), first) == (
        "it was performed in this invocation already"
    )
    assert unauthorized(Invocation(Review, proof, done.root, set()), first) == (
        "its construction is not in the proof of Review"
    )
    (cheap,) = (s for s in scopes(done.root) if s.path == ("request", "each", "[2]"))
    foreign = Occurrence(cheap, first.construction)
    assert unauthorized(Invocation(Operation, proof, done.root, set()), foreign) == (
        "its scope made no action of it"
    )
    elsewhere = Scope(ELEMENT, ("request", "each", "[0]"), None)
    elsewhere.made[first.construction] = made
    assert unauthorized(
        Invocation(Operation, proof, done.root, set()), Occurrence(elsewhere, first.construction)
    ) == ("its scope is not one this invocation opened at its site")
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


# --- 6. substitution --------------------------------------------------------------------------


class Swapping(Action[Teller, Noted]):
    """Tell the teller about an element valued high, with a validator that puts another high
    in place of the one supplied."""

    high: High

    @model_validator(mode="after")
    def swap(self) -> Self:
        object.__setattr__(self, "high", High(value=Amount(Decimal(99)), bound=Limit()))
        return self

    @override
    async def perform(self) -> Json:
        PERFORMED.append(Performed(Swapping, str(self.high.value.root), id(self.high)))
        return Json(self.party.says.root)


class DearSwapped(Fact):
    """An element valued high, told about through the swapping action."""

    element: Element
    high: High
    noted: Noted


class ConcludedSwapped(Fact):
    """Every element valued."""

    valued: tuple[Cheap | DearSwapped, ...]


class AnsweredSwapped(Reply[ConcludedSwapped]):
    """What leaves."""


class SwapOperation(Route[Elements, AnsweredSwapped]):
    """Value each element through the swapping action."""


SWAPPING = program_of(
    *CORE, Noted, Swapping, Cheap, DearSwapped, ConcludedSwapped, AnsweredSwapped, SwapOperation
)
"""The program whose action substitutes its own premise."""


@pytest.mark.asyncio
async def test_a_substituted_premise_a_foreign_action_or_a_mismatched_pair_is_never_performed(
    parties: Callable[[dict[str, str]], None],
) -> None:
    assert list(signature(performed_in_span).parameters) == ["execution", "pass_"]
    assert Execution._fields == ("occurrence", "action", "supplied")
    parties({"a": "50"})
    with pytest.raises(ValidationError) as failure:
        await valued(SWAPPING, "a", route=SwapOperation)
    assert [(e["type"], e["loc"], e["msg"]) for e in failure.value.errors()] == [
        (
            "substituted",
            ("Swapping", "high"),
            "Swapping.high at request.each.[0].Swapping holds another instance than the one"
            " supplied for it",
        )
    ]
    assert performed(Swapping) == []
    parties({"a": "50", "b": "60"})
    proof = proven(PROGRAM)
    done = await valued(PROGRAM, "a", "b", proof=proof)
    first, second = occurrences_of(done.root, Notify)
    made_first, made_second = first.made, second.made
    assert isinstance(made_first, Constructed)
    assert isinstance(made_second, Constructed)
    fresh = Invocation(Operation, proof, done.root, set())
    assert unauthorized(fresh, first) is None
    first.scope.made[first.construction] = Constructed(made_second.instance, made_first.supplied)
    assert unauthorized(fresh, first) == "high hold other instances than were supplied"
    first.scope.made[first.construction] = Constructed(made_second.instance, made_second.supplied)
    assert unauthorized(fresh, first) == "high no longer dereferences to what supplied it"
    high = made_first.supplied.premises["high"].found.instance
    assert isinstance(high, High)
    assert isinstance(made_first.instance, Notify)
    handmade = Notify(high=high, party=made_first.instance.party)
    first.scope.made[first.construction] = Constructed(handmade, made_first.supplied)
    assert unauthorized(fresh, first) is None
    assert handmade is not made_first.instance
    first.scope.made[first.construction] = made_first
    with pytest.raises(ValidationError) as refused:
        engine.authorized(Invocation(Operation, proof, done.root, {first}), first)
    assert [(e["type"], e["loc"], e["msg"]) for e in refused.value.errors()] == [
        (
            "unauthorized",
            ("Notify",),
            "Notify at request.each.[0].Notify is not performed: it was performed in this"
            " invocation already",
        )
    ]


# --- 7. admission timing ----------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pending_refuted_failed_and_unadmitted_evidence_authorizes_nothing(
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


# --- 8. the batch is preflighted before any task is created ----------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize("eager", [False, True])
async def test_an_invalid_candidate_after_a_valid_one_starts_no_action_of_the_batch(
    parties: Callable[[dict[str, str]], None], monkeypatch: pytest.MonkeyPatch, *, eager: bool
) -> None:
    loop = asyncio.get_running_loop()
    factory = loop.get_task_factory()
    if eager:
        loop.set_task_factory(asyncio.eager_task_factory)
    try:
        parties({"a": "50", "b": "60"})
        done = await valued(PROGRAM, "a", "b")
        assert sorted(p.subject for p in performed(Notify)) == ["50", "60"]
        PERFORMED.clear()
        constructing = engine.construct
        witnessing = engine.witnessed
        notifies: list[BaseModel] = []

        def forging(occurrence: Occurrence, given: engine.Given) -> BaseModel | ValidationError:
            found = constructing(occurrence, given)
            if occurrence.construction.cls is Notify and isinstance(found, BaseModel):
                notifies.append(found)
                return notifies[0]
            return found

        def unchecked(
            occurrence: Occurrence,
            instance: BaseModel,
            supplied: engine.Bound,
        ) -> Constructed:
            return Constructed(instance, supplied)

        monkeypatch.setattr(engine, "construct", forging)
        monkeypatch.setattr(engine, "witnessed", unchecked)
        with pytest.raises(ValidationError) as failure:
            await valued(PROGRAM, "a", "b")
        assert [(e["type"], e["loc"], e["msg"]) for e in failure.value.errors()] == [
            (
                "unauthorized",
                ("Notify",),
                "Notify at request.each.[1].Notify is not performed: high hold other instances"
                " than were supplied",
            )
        ]
        assert len(notifies) == 2
        assert performed(Notify) == []
        assert [p.subject for p in performed(Ask)] == ["a", "b"]
        monkeypatch.setattr(engine, "construct", constructing)
        monkeypatch.setattr(engine, "witnessed", witnessing)
        assert isinstance(done, Run)
    finally:
        loop.set_task_factory(factory)


# --- 10. conditional programs and other capability implementations ---------------------------


@pytest.mark.asyncio
async def test_a_conditional_program_still_blocks_and_another_implementation_changes_nothing(
    parties: Callable[[dict[str, str]], None], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PARTY__SAYS", '{"amount": "4"}')
    proof = proven(optional)
    assert all(j.established for j in proof.justifications)
    request = optional.PlaceOrder.model_validate_json('{"sku": "tea"}')
    done = await ran(optional.Checkout, request, config(optional)(), proof)
    assert isinstance(done, Blocked)
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
    assert {j.action.cls for j in proven(PROGRAM).justifications if j.established} == {Ask, Notify}
