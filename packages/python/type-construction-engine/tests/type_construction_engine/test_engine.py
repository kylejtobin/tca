"""The engine over the program this module is: classes named for what they are to the
framework, two stand-in parties that answer from the environment, and nothing else.

The engine reads a program as the classes its module defines, so this module is the program.
``faults.py`` beside it is a second program, with every fault the proof refuses; ``stalls.py``
a third, whose one outcome a party's answer refutes; ``lifecycle.py`` holds parties that record
their opening and closing, and is not a program."""

import asyncio
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from decimal import Decimal
from pathlib import Path
from types import ModuleType
from typing import Literal, override

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from pydantic import Field, PrivateAttr, ValidationError, computed_field
from pydantic_core import PydanticSerializationError

from type_construction.engine import (
    ConstructedRef,
    HeardRef,
    InputRef,
    Proof,
    answer,
    asked,
    classes,
    coexist,
    config,
    declared,
    fields,
    hear,
    heard,
    interval,
    models,
    never,
    opened,
    outcomes,
    produces,
    proven,
)
from type_construction.world import (
    Action,
    AtMost,
    Beyond,
    Comparison,
    Config,
    Connection,
    Equal,
    Fact,
    Greatest,
    Instant,
    Interval,
    Json,
    Least,
    Only,
    Python,
    Record,
    Reply,
    Request,
    Route,
    Scalar,
    Setting,
    Sum,
    Times,
    Value,
)

from . import faults as faults_module
from . import lifecycle
from . import stalls as stalls_module


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
    """A party that answers every question with the one line the deployment gave it."""

    says: Said

    @override
    @asynccontextmanager
    async def open(self) -> AsyncGenerator[None]:
        yield


class Teller(Party):
    """A second party, with a line of its own."""


class Amount(Scalar[Decimal]):
    """What the party says an element is worth."""

    root: Decimal = Field(gt=0)


class Share(Scalar[Decimal]):
    """How much of an element one part is."""

    root: Decimal = Field(gt=0, le=1)


class Part(Value):
    """One part of an element, of which the party says several."""

    share: Share


class Heard(Record):
    """What the party says about an element: its amount, and its parts."""

    amount: Amount
    parts: tuple[Part, ...]


class Tell[P: Party, T: Record](Action[P, T]):
    """An action toward a stand-in party: hears the line the party was given."""

    @override
    async def perform(self) -> Json:
        return Json(self.party.says.root)


class Asked(Tell[Party, Heard]):
    """Ask the party about one element."""

    element: Element


class Portion(Times[Share, Amount]):
    """What one part of an element is worth: its share of the amount."""


class Portions(Sum[Portion]):
    """Every part's portion, summed."""


class Largest(Greatest[Portion]):
    """The part worth most."""


class Limit(Scalar[Decimal]):
    """The amount at or under which an element is low."""

    root: Decimal = Decimal(10)


class Low(AtMost[Amount, Limit]):
    """An amount at or under the limit."""


class High(Beyond[Amount, Limit]):
    """An amount over the limit."""


class Word(Scalar[str]):
    """What the teller says about a dear element."""

    root: str = Field(min_length=1)


class Noted(Record):
    """What the teller says."""

    word: Word


class Notify(Tell[Teller, Noted]):
    """Tell the teller about an element valued high."""

    high: High


class Cheap(Fact):
    """An element the party valued low."""

    element: Element
    low: Low
    portions: Portions
    largest: Largest


class Dear(Fact):
    """An element the party valued high, which the teller was told about."""

    element: Element
    high: High
    portions: Portions
    largest: Largest
    noted: Noted


class Total(Sum[Amount]):
    """Every element's amount, summed."""


class Concluded(Fact):
    """Every element valued, and the total, at a moment."""

    valued: tuple[Cheap | Dear, ...]
    total: Total
    at: Instant


class Capped(Scalar[Decimal]):
    """What leaves as the total: at most 30."""

    root: Decimal = Field(le=30)


class Answered(Reply[Concluded]):
    """What leaves: the total, capped."""

    @computed_field
    @property
    def total(self) -> Capped:
        return Capped(self.of.total.root)


class Operation(Route[Elements, Answered]):
    """Value each element and total them."""


class Parties(Config):
    """The party and the teller."""

    party: Party
    teller: Teller


PROGRAM: ModuleType = sys.modules[__name__]
"""This module, as the program the engine reads."""

FAULTS: ModuleType = faults_module
"""The program beside this one, with the faults the proof refuses."""

STALLS: ModuleType = stalls_module
"""The program beside this one whose one outcome a party's answer refutes."""

SAYS = '{"amount": "2.50", "parts": [{"share": "0.5"}, {"share": "0.5"}]}'
"""The party's line: an amount under the limit, in two equal parts."""


@pytest.fixture
def party(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The parties' answers in the environment, and no ``.env`` in the working directory."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PARTY__SAYS", SAYS)
    monkeypatch.setenv("TELLER__SAYS", '{"word": "dear"}')


@pytest.fixture
def proof() -> Proof:
    """The program's proof."""
    return proven(PROGRAM)


async def operate(elements: str) -> Answered:
    """The reply the route answers for the elements, given as the request's JSON."""
    request = Elements.model_validate_json(elements)
    route = await answer(Operation, request, config(PROGRAM)(), proven(PROGRAM))
    return route.reply


ELEMENT = ("request", "each", "[]")
"""The site of each element's scope."""

PART = (*ELEMENT, "Asked", "heard", "parts", "[]")
"""The site of each part's scope, under the record the party said about the element."""


def test_the_proof_places_every_class_at_the_sites_its_fields_bind(proof: Proof) -> None:
    placed = {(c.cls, c.scope): c for c in proof.constructs(Operation)}
    assert set(placed) == {
        (Asked, ELEMENT),
        (Low, ELEMENT),
        (High, ELEMENT),
        (Notify, ELEMENT),
        (Portion, PART),
        (Portions, ELEMENT),
        (Largest, ELEMENT),
        (Cheap, ELEMENT),
        (Dear, ELEMENT),
        (Total, ()),
        (Concluded, ()),
        (Answered, ()),
        (Operation, ()),
    }
    heard_ = HeardRef(placed[Asked, ELEMENT], Heard, (), Heard)
    amount = heard_.held(Amount, "amount")
    assert amount.site == (*ELEMENT, "Asked", "heard", "amount")
    assert placed[Asked, ELEMENT].premises == {
        "party": (InputRef((), ("deployment", "party"), Party),),
        "element": (InputRef(ELEMENT, (), Element),),
    }
    assert placed[Low, ELEMENT].premises == {
        "value": (amount,),
        "bound": (InputRef((), ("Limit",), Limit),),
    }
    assert placed[Portion, PART].premises == {
        "left": (heard_.element(Part, "parts", "[]").held(Share, "share"),),
        "right": (amount,),
    }
    assert placed[Portion, PART].premises["left"][0].site == (*PART, "share")
    portions = placed[Portions, ELEMENT].collections["of"]
    assert (portions.site, portions.name, portions.positions) == (PART[:-1], "parts", None)
    assert portions.holder == heard_
    assert portions.elements == (ConstructedRef(placed[Portion, PART]),)
    assert placed[Dear, ELEMENT].premises["noted"] == (
        HeardRef(placed[Notify, ELEMENT], Noted, (), Noted),
    )
    total = placed[Total, ()].collections["of"]
    assert total.site == ("request", "each")
    assert total.holder == InputRef((), ("request",), Elements)
    assert total.elements == (amount,)
    concluded = placed[Concluded, ()]
    assert concluded.premises == {"total": (ConstructedRef(placed[Total, ()]),)}
    assert [f.name for f in fields(Concluded) if f.fresh] == ["at"]
    assert declared(Concluded, "at").classes == (Instant,)
    assert concluded.collections["valued"].site == ("request", "each")
    assert concluded.collections["valued"].holder == total.holder
    assert concluded.collections["valued"].elements == (
        ConstructedRef(placed[Cheap, ELEMENT]),
        ConstructedRef(placed[Dear, ELEMENT]),
    )
    assert placed[Operation, ()].premises == {
        "request": (InputRef((), ("request",), Elements),),
        "reply": (ConstructedRef(placed[Answered, ()]),),
    }
    (cheap, _) = concluded.collections["valued"].elements
    assert isinstance(cheap, ConstructedRef)
    assert cheap.construction is placed[Cheap, ELEMENT]
    refs = [
        r
        for c in placed.values()
        for refs in (
            *c.premises.values(),
            *((col.holder, *col.elements) for col in c.collections.values()),
        )
        for r in refs
    ]
    producers = [r.construction for r in refs if isinstance(r, ConstructedRef)]
    actions = [r.action for r in refs if isinstance(r, HeardRef)]
    assert producers and actions
    assert all(any(p is c for c in placed.values()) for p in producers)
    assert all(any(a is c for c in placed.values()) for a in actions)
    assert all(c in proof.constructions for c in placed.values())


def test_the_published_graph_is_sealed_and_its_identities_are_shared(proof: Proof) -> None:
    constructions = proof.constructs(Operation)
    assert all(c.sealed for c in constructions)
    (low,) = (c for c in constructions if c.cls is Low)
    with pytest.raises(AttributeError, match="sealed"):
        low.rebound(low)
    with pytest.raises(AttributeError, match="sealed"):
        low.premises = {}
    with pytest.raises(TypeError):
        low.premises["value"] = ()  # type: ignore[index]
    (portions,) = (c for c in constructions if c.cls is Portions)
    with pytest.raises(TypeError):
        portions.collections["of"] = portions.collections["of"]  # type: ignore[index]
    again = proven(PROGRAM).constructs(Operation)
    assert [c.cls for c in again] == [c.cls for c in constructions]
    assert all(a is not b for a, b in zip(again, constructions, strict=True))


def test_a_declaration_is_read_through_one_view(proof: Proof) -> None:
    valued = declared(Concluded, "valued")
    assert (valued.is_tuple, valued.fixed, valued.positions) == (True, False, None)
    assert valued.classes == (Cheap, Dear)
    assert valued.item_classes == ((Cheap, Dear),)
    assert (valued.step(0), valued.step(3)) == ("[]", "[]")
    assert valued.shape == "tuple[Cheap | Dear, ...]"
    assert not valued.premise and not valued.fresh and valued.required
    ordering = declared(Low, "ordering")
    assert ordering.condition is ordering.computation
    assert isinstance(ordering.condition, Comparison)
    assert not ordering.required and not ordering.premise
    assert declared(Largest, "of").length == (1, None)
    assert declared(Only[Element], "of").length == (1, 1)
    assert declared(Only[Element], "of").positions == 1
    assert declared(Low, "value").premise
    assert declared(Low, "bound").classes == (Limit,)
    assert declared(Heard, "parts").is_tuple
    assert [f.name for f in fields(Low)] == ["value", "bound", "ordering"]
    assert declared(Amount, "root").bounds == Interval(low=Decimal(0), low_strict=True)
    assert declared(Low, "ordering").condition is not None
    assert Low.conditions() == {"ordering"}
    assert Largest.conditions() == {"of"}
    assert Cheap.model_fields.keys() == {f.name for f in fields(Cheap)}
    assert proof.constructs(Operation)
    assert proof.sites(Operation, Portion) == ((*PART, "Portion"),)
    assert proof.waiting == ()
    assert proof.faulted == ()
    assert proof.constants == (Limit,)


def test_a_programs_classes_are_the_ones_its_module_defines() -> None:
    found = classes(PROGRAM)
    assert Asked in found
    assert Tell not in found
    assert Tell[Party, Heard] not in found
    assert Fact not in found


def test_a_routes_request_and_an_actions_records_are_read_from_their_parameters() -> None:
    assert asked(Operation) is Elements
    assert heard(Asked) == (Heard,)

    class Other(Record):
        """A second record the party may say."""

        tag: Name

    class Either(Tell[Party, Heard | Other]):
        """An action hearing one of two records."""

        element: Element

    assert heard(Either) == (Heard, Other)


def test_a_record_union_is_heard_as_the_member_the_text_constructs() -> None:
    class Clear(Record):
        """The party's yes."""

        status: Literal["clear"]

    class Flagged(Record):
        """The party's no."""

        status: Literal["flagged"]
        word: Word

    class Screen(Tell[Party, Clear | Flagged]):
        """Ask the party whether an element is clear."""

        element: Element

    screen = Screen(party=Party(says=Said("{}")), element=Element(name=Name("a")))
    assert type(hear(screen, Json('{"status": "clear"}'))) is Clear
    assert type(hear(screen, Json('{"status": "flagged", "word": "no"}'))) is Flagged
    assert type(hear(screen, Python({"status": "clear"}))) is Clear
    flagged = Flagged(status="flagged", word=Word("no"))
    assert hear(screen, Python(flagged)) is flagged
    with pytest.raises(ValidationError) as refusal:
        hear(screen, Python(Heard(amount=Amount(Decimal(1)), parts=())))
    assert {e["type"] for e in refusal.value.errors()} == {"model_type"}
    with pytest.raises(ValidationError) as refusal:
        hear(screen, Json('{"status": "clear", "word": "no"}'))
    assert [(e["type"], e["loc"]) for e in refusal.value.errors()] == [
        ("extra_forbidden", ("Clear", "word")),
        ("literal_error", ("Flagged", "status")),
    ]


def test_a_computed_field_names_the_classes_it_constructs() -> None:
    class Picked(Fact):
        """A fact whose computed field returns one of two scalars."""

        amount: Amount

        @computed_field
        @property
        def which(self) -> Amount | Limit:
            return self.amount

    assert produces(Picked) == {"which": (Amount, Limit)}


def test_the_classes_a_route_builds_are_those_its_reply_leads_to(proof: Proof) -> None:
    built = proof.built(Operation)
    assert set(built) == {
        Asked,
        Portion,
        Portions,
        Largest,
        Low,
        High,
        Notify,
        Cheap,
        Dear,
        Total,
        Concluded,
        Answered,
        Operation,
    }
    assert Heard not in built
    assert Limit not in built


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_each_element_is_valued_in_its_own_scope_and_its_parts_in_theirs() -> None:
    done = await operate('{"each": [{"name": "a"}, {"name": "b"}]}')
    assert [type(v).__name__ for v in done.of.valued] == ["Cheap", "Cheap"]
    assert [v.element.name.root for v in done.of.valued] == ["a", "b"]
    assert [v.portions.root for v in done.of.valued] == [Decimal("2.500"), Decimal("2.500")]
    assert [v.largest.chosen.root for v in done.of.valued] == [Decimal("1.250"), Decimal("1.250")]
    assert done.of.total.root == Decimal("5.00")
    assert done.model_dump_json() == '{"total":"5.00"}'


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_the_relation_that_holds_decides_the_outcome_and_its_effect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PARTY__SAYS", '{"amount": "25", "parts": [{"share": "1"}]}')
    done = await operate('{"each": [{"name": "a"}]}')
    (valued,) = done.of.valued
    assert type(valued) is Dear
    assert valued.noted.word.root == "dear"
    assert valued.high.ordering == 1
    assert valued.portions.root == Decimal(25)
    assert done.model_dump_json() == '{"total":"25"}'


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_a_fresh_scalar_is_constructed_for_each_holder() -> None:
    first = await operate('{"each": []}')
    second = await operate('{"each": []}')
    assert first.of.at.root.tzinfo is not None
    assert first.of.at.root < second.of.at.root
    with pytest.raises(ValidationError) as refusal:
        Concluded.model_validate({"valued": (), "total": Total(of=())})
    assert [(e["type"], e["loc"]) for e in refusal.value.errors()] == [("missing", ("at",))]


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_no_element_collects_the_empty_tuple_and_sums_to_zero() -> None:
    done = await operate('{"each": []}')
    assert done.of.valued == ()
    assert done.of.total.root == Decimal(0)


def test_a_relation_that_cannot_hold_or_cannot_refuse_is_read_from_the_intervals() -> None:
    assert never(FAULTS.Impossible) == "holds"
    assert never(FAULTS.Certain) == "refuses"
    assert never(FAULTS.Never) == "holds"
    assert never(FAULTS.Undecided) == "refuses"
    assert never(Low) is None
    assert never(Cheap) is None


def test_an_interval_is_read_from_the_bounds_the_default_or_the_operation() -> None:
    assert interval(Amount) == Interval(low=Decimal(0), low_strict=True)
    assert interval(Share) == Interval(low=Decimal(0), low_strict=True, high=Decimal(1))
    assert interval(Limit) == Interval(low=Decimal(10), high=Decimal(10))
    assert interval(Portion) == Interval(low=Decimal(0))
    assert interval(Total) == Interval(low=Decimal(0))
    assert outcomes(interval(Amount), interval(Limit)) == {-1, 0, 1}
    assert outcomes(interval(FAULTS.SmallAmount), interval(FAULTS.LargeAmount)) == {-1}


def test_a_scalar_over_int_has_no_value_between_two_integers() -> None:
    class Unit(Scalar[int]):
        """An integer over 0 and under 2: exactly 1."""

        root: int = Field(gt=0, lt=2)

    class One(Scalar[int]):
        """An integer that is 1."""

        root: int = Field(ge=1, le=1)

    class Same(Equal[Unit, One]):
        """Two integers that can only be 1."""

    assert interval(Unit) == Interval(low=Decimal(1), high=Decimal(1))
    assert never(Same) == "refuses"


def test_two_facts_told_apart_by_complementary_relations_are_proven_exclusive(
    proof: Proof,
) -> None:
    assert not coexist(Cheap, Dear, proof.classes)
    assert coexist(Cheap, Cheap, proof.classes)
    assert coexist(FAULTS.AtOrUnder, FAULTS.Exactly, models(FAULTS))


def test_the_proof_refuses_every_fault_at_once() -> None:
    with pytest.raises(ValidationError) as refusal:
        proven(FAULTS)
    found = {(e["type"], e["loc"]): e["msg"] for e in refusal.value.errors()}
    assert set(found) == {
        ("missing", ("Concluded", "unheard")),
        ("cycle", ("Egg",)),
        ("cycle", ("Chicken",)),
        ("ambiguous", ("Named", "name")),
        ("ambiguous", ("Spared", "party")),
        ("ambiguous", ("Total", "of")),
        ("ambiguous", ("Either", "which")),
        ("unplaceable", ("Twin",)),
        ("collects", ("Collects", "every")),
        ("route", ("Misplaced",)),
        ("unreached", ("Stray",)),
        ("unreached", ("Direct",)),
        ("unmodeled", ("Bare", "count")),
        ("boundary", ("Direct", "cheap")),
        ("boundary", ("Parties", "word")),
        ("config", ("type_construction_engine.faults",)),
        ("never", ("Impossible",)),
        ("never", ("Certain",)),
        ("never", ("Never",)),
        ("never", ("Undecided",)),
        ("undiscriminated", ("Both",)),
        ("undecided", ("Charge",)),
    }
    assert found["ambiguous", ("Named", "name")] == (
        "Named.name has two sources: Name is at 2 sites here: request.each.[].name,"
        " request.each.[].Asked.heard.name; hold what tells them apart"
    )
    assert found["ambiguous", ("Spared", "party")] == (
        "Spared.party has two sources: Spare is at 2 sites here: deployment.spare,"
        " deployment.standby; hold what tells them apart"
    )
    assert found["ambiguous", ("Total", "of")] == (
        "Total.of has two sources: Amount is collected by 2: request.each, request.others; hold"
        " what tells them apart"
    )
    assert found["unplaceable", ("Twin",)] == (
        "Twin.element, Twin.second are never visible from one scope; a class over two sibling"
        " elements is an element of its own"
    )
    assert found["route", ("Misplaced",)].startswith(
        "Misplaced would exist once per request.each.[]"
    )
    assert FAULTS.Egg.model_fields["chicken"].annotation is FAULTS.Chicken


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_a_stalled_run_names_the_relation_that_did_not_hold_with_the_ordering(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PARTY__SAYS", '{"amount": "25"}')
    request = STALLS.Elements.model_validate_json('{"each": [{"name": "a"}]}')
    with pytest.raises(ValidationError) as refusal:
        await answer(STALLS.Operation, request, config(STALLS)(), proven(STALLS))
    found = {(e["type"], e["loc"], e["msg"]) for e in refusal.value.errors()}
    assert found == {
        (
            "relation",
            ("Low",),
            "Low at request.each.[0].Low did not hold: value Amount at"
            " request.each.[0].Asked.heard.amount > bound Limit at Limit",
        )
    }


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_a_stalled_run_names_the_selection_with_nothing_to_choose(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PARTY__SAYS", '{"amount": "2.50", "parts": []}')
    with pytest.raises(ValidationError) as refusal:
        await operate('{"each": [{"name": "a"}]}')
    found = {(e["type"], e["loc"], e["msg"]) for e in refusal.value.errors()}
    assert found == {
        (
            "relation",
            ("Largest",),
            "Largest at request.each.[0].Largest did not hold: Tuple should have at least 1 item"
            " after validation, not 0",
        ),
        (
            "relation",
            ("High",),
            "High at request.each.[0].High did not hold: value Amount at"
            " request.each.[0].Asked.heard.amount < bound Limit at Limit",
        ),
    }


def test_a_selections_shape_is_its_tuple_annotation() -> None:
    with pytest.raises(ValidationError) as refusal:
        Least[Amount](of=())
    assert [(e["type"], e["loc"], e["msg"]) for e in refusal.value.errors()] == [
        ("refuted", ("of",), "Tuple should have at least 1 item after validation, not 0")
    ]
    with pytest.raises(ValidationError) as refusal:
        Only[Element].model_validate({"of": ()})
    assert [(e["type"], e["loc"], e.get("ctx")) for e in refusal.value.errors()] == [
        ("refuted", ("of",), {"why": "Field required", "count": 0})
    ]
    with pytest.raises(ValidationError) as refusal:
        Only[Element].model_validate({"of": (Element(name=Name("a")), Element(name=Name("b")))})
    assert [(e["type"], e["loc"], e.get("ctx")) for e in refusal.value.errors()] == [
        (
            "refuted",
            ("of",),
            {"why": "Tuple should have at most 1 item after validation, not 2", "count": 2},
        )
    ]
    with pytest.raises(ValidationError) as refusal:
        Only[Element].model_validate({})
    assert [(e["type"], e["loc"]) for e in refusal.value.errors()] == [("missing", ("of",))]
    with pytest.raises(ValidationError) as refusal:
        Only[Element].model_validate({"of": (Name("a"),)})
    assert [e["type"] for e in refusal.value.errors()] == ["model_type"]


def test_a_relations_ordering_is_computed_admitted_by_its_literal_and_never_given() -> None:
    low = Low.model_validate({"value": Amount(Decimal(5)), "bound": Limit()})
    assert low.ordering == -1
    assert low.model_dump() == {"value": Decimal(5), "bound": Decimal(10)}
    with pytest.raises(ValidationError) as refusal:
        Low.model_validate({"value": Amount(Decimal(11)), "bound": Limit(), "ordering": 0})
    found = [(e["type"], e["loc"]) for e in refusal.value.errors()]
    assert found == [("computed", ("ordering",))]
    with pytest.raises(ValidationError) as refusal:
        Low.model_validate({"value": Amount(Decimal(5)), "bound": Limit(), "ordering": -1})
    found = [(e["type"], e["loc"]) for e in refusal.value.errors()]
    assert found == [("computed", ("ordering",))]


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_an_open_that_fails_releases_what_it_acquired_and_what_opened_before_it() -> None:
    lifecycle.LOG.clear()
    said = lifecycle.Said("{}")
    with pytest.raises(ConnectionError):
        async with opened(
            lifecycle.Opened(fine=lifecycle.Fine(says=said), down=lifecycle.Down(says=said))
        ):
            pass
    assert lifecycle.LOG == ["open:Fine", "open:Down", "close:Down", "close:Fine"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_a_cancellation_during_an_open_releases_it_and_what_opened_before_it() -> None:
    lifecycle.LOG.clear()
    said = lifecycle.Said("{}")

    async def starting() -> None:
        async with opened(
            lifecycle.Hanging(fine=lifecycle.Fine(says=said), slow=lifecycle.Slow(says=said))
        ):
            lifecycle.LOG.append("body")

    server = asyncio.ensure_future(starting())
    while lifecycle.LOG != ["open:Fine", "open:Slow"]:
        await asyncio.sleep(0)
    server.cancel()
    with pytest.raises(asyncio.CancelledError):
        await server
    assert lifecycle.LOG == ["open:Fine", "open:Slow", "close:Slow", "close:Fine"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_a_failing_action_cancels_the_pass_and_propagates_in_a_group(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def failing(self: Tell[Party, Record]) -> Record:
        """A perform whose party is down."""
        down = ConnectionError("party down")
        raise down

    monkeypatch.setattr(Tell, "perform", failing)
    with pytest.raises(ExceptionGroup) as group:
        await operate('{"each": [{"name": "a"}, {"name": "b"}]}')
    assert [type(e) for e in group.value.exceptions] == [ConnectionError, ConnectionError]


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_connections_open_once_before_answers_and_close_once_after_in_reverse() -> None:
    lifecycle.LOG.clear()
    said = lifecycle.Said("{}")
    async with opened(
        lifecycle.Lifecycle(fine=lifecycle.Fine(says=said), later=lifecycle.Later(says=said))
    ):
        lifecycle.LOG.append("answer")
        await operate('{"each": [{"name": "a"}]}')
        lifecycle.LOG.append("answer")
        await operate('{"each": [{"name": "a"}]}')
    assert lifecycle.LOG == [
        "open:Fine",
        "open:Later",
        "answer",
        "answer",
        "close:Later",
        "close:Fine",
    ]


def test_an_action_or_a_connection_without_a_library_kind_cannot_be_constructed() -> None:
    class Bare(Action[Party, Heard]):
        """An action with no perform."""

        element: Element

    class Mute(Connection):
        """A connection with no open or close."""

        says: Said

    with pytest.raises(TypeError, match="Bare"):
        Bare(party=Party(says=Said("{}")), element=Element(name=Name("a")))  # type: ignore[abstract]
    with pytest.raises(TypeError, match="Mute"):
        Mute(says=Said("{}"))  # type: ignore[abstract]


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_an_answer_is_one_span_per_route_and_one_per_performed_action() -> None:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    await operate('{"each": [{"name": "a"}, {"name": "b"}]}')
    spans = sorted(
        ((s.name, dict(s.attributes or {})) for s in exporter.get_finished_spans()),
        key=lambda found: (found[0], str(found[1].get("tca.site", ""))),
    )
    assert spans == [
        *(
            (
                "Asked",
                {
                    "tca.party": "Party",
                    "tca.site": f"request.each.[{i}].Asked",
                    "tca.pass": 1,
                    "tca.outcome": "heard",
                    "tca.record": "Heard",
                    "tca.heard": f"request.each.[{i}].Asked.heard",
                },
            )
            for i in (0, 1)
        ),
        ("Operation", {"tca.request": "Elements", "tca.outcome": "answered", "tca.passes": 4}),
    ]
    assert not any("2.50" in str(v) for _, a in spans for v in a.values())


@pytest.mark.asyncio
async def test_a_client_in_a_private_attribute_leaves_the_connection_frozen() -> None:
    class Keyed(Party):
        """A party that holds a client outside its fields."""

        _client: object | None = PrivateAttr(default=None)

        @override
        @asynccontextmanager
        async def open(self) -> AsyncGenerator[None]:
            self._client = object()
            yield

        def holds_a_client(self) -> bool:
            """Whether open set the client."""
            return self._client is not None

    keyed = Keyed(says=Said("{}"))
    async with keyed.open():
        assert keyed.holds_a_client()
        with pytest.raises(ValidationError) as refusal:
            keyed.says = Said("x")  # type: ignore[misc]
        assert [e["type"] for e in refusal.value.errors()] == ["frozen_instance"]
        assert keyed.model_dump_json() == '{"says":"{}"}'
        assert isinstance(hash(keyed), int)


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_a_replys_word_that_refuses_refuses_when_the_reply_is_serialized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PARTY__SAYS", '{"amount": "25", "parts": [{"share": "1"}]}')
    done = await operate('{"each": [{"name": "a"}, {"name": "b"}]}')
    assert done.of.total.root == Decimal(50)
    with pytest.raises(PydanticSerializationError, match="less_than_equal") as refusal:
        done.model_dump_json()
    assert "1 validation error for Capped" in str(refusal.value)
