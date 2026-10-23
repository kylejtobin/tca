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
from math import inf, isnan, nan
from pathlib import Path
from types import ModuleType
from typing import Annotated, Literal, Self, override

import pytest
from annotated_types import Ge, Gt, Le, Len, Lt, MinLen
from annotated_types import Interval as Range
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from pydantic import (
    AfterValidator,
    AliasChoices,
    AliasPath,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PrivateAttr,
    ValidationError,
    WrapValidator,
    computed_field,
    model_validator,
)
from pydantic_core import PydanticSerializationError

from type_construction.engine import (
    Collected,
    Constructed,
    ConstructedRef,
    Construction,
    HeardRef,
    InputRef,
    Inputs,
    Known,
    Proof,
    Run,
    Unknown,
    answer,
    asked,
    classes,
    config,
    declared,
    exclusions,
    fields,
    hear,
    heard,
    interval,
    interval_at,
    joint,
    models,
    never,
    opened,
    operand,
    outcomes,
    produces,
    proven,
    ran,
    scopes,
    supplied_by,
    symbolic,
)
from type_construction.world import (
    COMPUTED,
    Action,
    AtMost,
    Beyond,
    Comparison,
    Config,
    Connection,
    Derived,
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
    Under,
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
    """Tell the teller about an element valued high: holds the evidence it is performed with, and
    is performed where ``Dear`` needs what it hears."""

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
    (portions,) = placed[Portions, ELEMENT].collections["of"]
    assert (portions.site, portions.name, portions.positions) == (PART[:-1], "parts", None)
    assert portions.holder == heard_
    assert portions.elements == (ConstructedRef(placed[Portion, PART]),)
    assert placed[Dear, ELEMENT].premises["noted"] == (
        HeardRef(placed[Notify, ELEMENT], Noted, (), Noted),
    )
    (total,) = placed[Total, ()].collections["of"]
    assert total.site == ("request", "each")
    assert total.holder == InputRef((), ("request",), Elements)
    assert total.elements == (amount,)
    concluded = placed[Concluded, ()]
    assert concluded.premises == {"total": (ConstructedRef(placed[Total, ()]),)}
    assert [f.name for f in fields(Concluded) if f.fresh] == ["at"]
    assert declared(Concluded, "at").classes == (Instant,)
    (valued,) = concluded.collections["valued"]
    assert valued.site == ("request", "each")
    assert valued.holder == total.holder
    assert valued.elements == (
        ConstructedRef(placed[Cheap, ELEMENT]),
        ConstructedRef(placed[Dear, ELEMENT]),
    )
    assert placed[Operation, ()].premises == {
        "request": (InputRef((), ("request",), Elements),),
        "reply": (ConstructedRef(placed[Answered, ()]),),
    }
    (cheap, _) = valued.elements
    assert isinstance(cheap, ConstructedRef)
    assert cheap.construction is placed[Cheap, ELEMENT]
    refs = [
        r
        for c in placed.values()
        for refs in (
            *c.premises.values(),
            *((col.holder, *col.elements) for cols in c.collections.values() for col in cols),
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
    assert [f.name for f in fields(Low) if f.condition is not None] == ["ordering"]
    assert [f.name for f in fields(Largest) if f.condition is not None] == ["of"]
    assert declared(Only[Element], "of").condition is not None
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
    assert interval(Limit) == Interval()
    assert supplied_by(InputRef((), ("Limit",), Limit)) == Interval(
        low=Decimal(10), high=Decimal(10)
    )
    assert interval(Portion) == Interval(low=Decimal(0))
    assert interval(Total) == Interval(low=Decimal(0))
    assert outcomes(known(interval(Amount)), known(interval(Limit))) == {-1, 0, 1}
    assert outcomes(known(interval(FAULTS.SmallAmount)), known(interval(FAULTS.LargeAmount))) == {
        -1
    }


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
    (valued,) = (e for e in proof.exclusions if e.construction.cls is Concluded)
    placed = {c.cls: c for c in proof.constructs(Operation)}
    assert (valued.field, valued.left, valued.right) == (
        "valued",
        ConstructedRef(placed[Cheap]),
        ConstructedRef(placed[Dear]),
    )
    assert valued.established
    assert [c.why for c in valued.joint.clashes] == ["ordering"]
    assert valued.joint.clashes[0].among == (
        ConstructedRef(placed[High]),
        ConstructedRef(placed[Low]),
    )
    assert all(e.contradicted is False for e in proof.existences)
    faults = symbolic(FAULTS.Operation, models(FAULTS))
    either = {
        (e.left.cls, e.right.cls): e
        for e in exclusions(faults.constructions)
        if not isinstance(e.left, Collected) and not isinstance(e.right, Collected)
    }
    assert not either[FAULTS.AtOrUnder, FAULTS.Exactly].established
    assert either[FAULTS.Priced, FAULTS.Free].established


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
    }
    assert found["ambiguous", ("Named", "name")] == (
        "Named.name at request.each.[] may hold both Name at request.each.[].name and Name at"
        " request.each.[].Asked.heard.name; nothing available with them excludes either"
    )
    assert found["ambiguous", ("Spared", "party")] == (
        "Spared.party at request.each.[] may hold both Spare at deployment.spare and Spare at"
        " deployment.standby; nothing available with them excludes either"
    )
    assert found["ambiguous", ("Total", "of")] == (
        "Total.of at the root may hold both Amount in Elements.each at request.each and Amount"
        " in Elements.others at request.others; nothing available with them excludes either"
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
    provider = trace.get_tracer_provider()
    if not isinstance(provider, TracerProvider):
        provider = TracerProvider()
        trace.set_tracer_provider(provider)
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
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
        ("Operation", {"tca.request": "Elements", "tca.outcome": "answered", "tca.passes": 2}),
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


def accepted(cls: type[Scalar[int]], values: range) -> list[int]:
    """The integers among a range Pydantic admits for a scalar."""
    found: list[int] = []
    for v in values:
        try:
            cls(v)
        except ValidationError:
            continue
        found.append(v)
    return found


def known(found: Interval | Unknown) -> Interval:
    """An interval the analysis knows; a test that needs one fails on what is unknown."""
    assert isinstance(found, Interval), found
    return found


def within(interval: Interval, v: Decimal | int) -> bool:
    """Whether a number lies in an interval."""
    low_ok = interval.low is None or (
        v > interval.low if interval.low_strict else v >= interval.low
    )
    high_ok = interval.high is None or (
        v < interval.high if interval.high_strict else v <= interval.high
    )
    return low_ok and high_ok and not interval.empty


@pytest.mark.parametrize(
    ("declaration", "reversed_", "expected"),
    [
        ((Gt(0), Ge(5)), (Ge(5), Gt(0)), Interval(low=Decimal(5))),
        ((Gt(4), Ge(5)), (Ge(5), Gt(4)), Interval(low=Decimal(5))),
        ((Gt(5), Ge(5)), (Ge(5), Gt(5)), Interval(low=Decimal(6))),
        ((Lt(10), Le(10)), (Le(10), Lt(10)), Interval(high=Decimal(9))),
        ((Lt(10), Le(7)), (Le(7), Lt(10)), Interval(high=Decimal(7))),
        ((Ge(3), Le(3)), (Le(3), Ge(3)), Interval(low=Decimal(3), high=Decimal(3))),
        ((Gt(5), Lt(3)), (Lt(3), Gt(5)), Interval(low=Decimal(6), high=Decimal(2))),
    ],
)
def test_bounds_are_what_pydantic_validates_whatever_the_order_of_the_constraints(
    declaration: tuple[object, ...], reversed_: tuple[object, ...], expected: Interval
) -> None:
    class Forward(Scalar[int]):
        root: Annotated[int, *declaration]

    class Backward(Scalar[int]):
        root: Annotated[int, *reversed_]

    found = declared(Forward, "root").bounds
    assert found == declared(Backward, "root").bounds == expected
    assert interval(Forward) == interval(Backward) == expected
    for cls in (Forward, Backward):
        for v in range(-3, 15):
            assert within(known(found), v) == (v in accepted(cls, range(-3, 15))), (cls, v)


def test_a_repeated_constraint_keeps_what_pydantic_keeps_and_never_narrows_past_it() -> None:
    class LastWins(Scalar[int]):
        root: Annotated[int, Gt(3), Gt(0)]

    class FirstGone(Scalar[int]):
        root: Annotated[int, Gt(0), Gt(3)]

    for cls in (LastWins, FirstGone):
        found = declared(cls, "root").bounds
        admitted = accepted(cls, range(-2, 8))
        assert [v for v in range(-2, 8) if within(known(found), v)] == admitted
    assert declared(LastWins, "root").bounds == Interval(low=Decimal(1))
    assert declared(FirstGone, "root").bounds == Interval(low=Decimal(4))


def test_a_contradictory_scalar_is_empty_and_a_relation_over_it_never_holds() -> None:
    class Nothing(Scalar[Decimal]):
        root: Decimal = Field(gt=5, lt=3)

    class Strict(Scalar[Decimal]):
        root: Decimal = Field(gt=3, le=3)

    class Over(Beyond[Nothing, Limit]):
        """A relation over a scalar no value satisfies."""

    assert known(interval(Nothing)).empty
    assert known(interval(Strict)).empty
    assert not known(interval(Amount)).empty
    assert outcomes(known(interval(Nothing)), known(interval(Limit))) == frozenset()
    assert never(Over) == "holds"
    with pytest.raises(ValidationError):
        Nothing(Decimal(4))
    with pytest.raises(ValidationError):
        Strict(Decimal(3))


def test_a_decimal_bound_keeps_its_strictness_and_a_width_constraint_only_widens() -> None:
    class Open(Scalar[Decimal]):
        root: Decimal = Field(gt=Decimal("0.5"), lt=Decimal("2.5"))

    class Stepped(Scalar[Decimal]):
        root: Decimal = Field(ge=0, le=10, multiple_of=3)

    assert declared(Open, "root").bounds == Interval(
        low=Decimal("0.5"), low_strict=True, high=Decimal("2.5"), high_strict=True
    )
    assert declared(Stepped, "root").bounds == Interval(low=Decimal(0), high=Decimal(10))
    assert Stepped(Decimal(9)).root == 9
    with pytest.raises(ValidationError):
        Stepped(Decimal(8))


def test_a_length_is_what_the_resolved_tuple_schema_admits() -> None:
    class Few(Fact):
        of: Annotated[tuple[Element, ...], Len(2, 4)]

    class LastLength(Fact):
        of: Annotated[tuple[Element, ...], MinLen(3), MinLen(1)]

    class Pair(Fact):
        of: tuple[Element, Element]

    assert declared(Few, "of").length == (2, 4)
    assert declared(LastLength, "of").length == (1, None)
    assert LastLength(of=(Element(name=Name("a")),)).of
    assert declared(Pair, "of").length == (2, 2)
    assert declared(Largest, "of").length == (1, None)
    assert declared(Only[Element], "of").length == (1, 1)
    assert declared(Elements, "each").length == (0, None)


def test_a_records_keys_are_every_alias_pydantic_accepts() -> None:
    class Chosen(Record):
        """A record naming one field by several keys and another by a nested path."""

        amount: Amount = Field(validation_alias=AliasChoices("amount", "amt"))
        word: Word = Field(validation_alias=AliasPath("data", "word"))
        plain: Name

    class Named(Record):
        """A record that validates by field name as well as by alias."""

        model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
        amount: Amount = Field(alias="total")

    assert declared(Chosen, "amount").aliases == {"amount", "amt"}
    assert declared(Chosen, "amount").required_key is None
    assert declared(Chosen, "word").aliases == {"data"}
    assert declared(Chosen, "word").required_key == "data"
    assert declared(Chosen, "plain").required_key == "plain"
    assert declared(Named, "amount").aliases == {"total", "amount"}
    assert declared(Named, "amount").required_key is None
    assert Chosen.model_validate({"amt": Decimal(1), "data": {"word": "w"}, "plain": "p"}).word


def test_a_value_changing_after_validator_and_a_bypassing_wrap_validator_leave_no_bound() -> None:
    class Shifted(Scalar[int]):
        """An integer at least 1, then shifted down past its bound."""

        root: Annotated[int, Ge(1), AfterValidator(lambda v: v - 5)]

    class Bypassed(Scalar[int]):
        """An integer whose wrap validator never reaches its bound."""

        root: Annotated[int, Ge(1), WrapValidator(lambda v, _handler: v)]

    class Over(Beyond[Shifted, Limit]):
        """A relation over an operand whose interval is unknown."""

    assert Shifted(1).root == -4
    assert Bypassed(0).root == 0
    for cls, operation in ((Shifted, "function-after"), (Bypassed, "function-wrap")):
        found = declared(cls, "root").bounds
        assert found == Unknown(operation, ("model", operation))
        assert interval(cls) == found
    assert never(Over) is None
    assert declared(Over, "ordering").output == Known(
        numbers=Interval(low=Decimal(1), high=Decimal(1))
    )


def test_a_before_validator_over_a_native_bound_keeps_the_output_bound_not_input_acceptance() -> (
    None
):
    def refusing(given: object) -> object:
        nothing = f"{given!r} refused before the bound"
        raise ValueError(nothing)

    class Lifted(Scalar[int]):
        """An integer lifted by ten before the bound: inputs under 1 construct."""

        root: Annotated[int, Ge(1), BeforeValidator(lambda v: int(str(v)) + 10)]

    class Refused(Scalar[int]):
        """An integer at least 1 whose before validator refuses every input."""

        root: Annotated[int, Ge(1), BeforeValidator(refusing)]

    assert declared(Lifted, "root").bounds == Interval(low=Decimal(1))
    assert declared(Refused, "root").bounds == Interval(low=Decimal(1))
    assert accepted(Lifted, range(-15, 5)) == list(range(-9, 5))
    assert all(within(Interval(low=Decimal(1)), Lifted(v).root) for v in range(-9, 5))
    assert accepted(Refused, range(-15, 5)) == []


def test_equivalent_compiled_constraints_are_one_summary_whoever_wrote_them() -> None:
    class ByField(Scalar[int]):
        root: int = Field(ge=1, lt=10)

    class ByMetadata(Scalar[int]):
        root: Annotated[int, Lt(10), Ge(1)]

    class ByRange(Scalar[int]):
        root: Annotated[int, Range(ge=1, lt=10)]

    assert {declared(c, "root").output for c in (ByField, ByMetadata, ByRange)} == {
        Known(numbers=Interval(low=Decimal(1), high=Decimal(9)))
    }
    assert {tuple(accepted(c, range(-2, 13))) for c in (ByField, ByMetadata, ByRange)} == {
        tuple(range(1, 10))
    }


def test_an_unknown_interval_proves_nothing_exclusive_and_omits_the_never_diagnostic() -> None:
    class Floor(Scalar[int]):
        root: int = Field(le=10)

    class Ceiling(Scalar[int]):
        root: int = Field(ge=20)

    class Shifted(Scalar[int]):
        root: Annotated[int, Ge(20), AfterValidator(lambda v: v - 100)]

    class Count(Scalar[int]):
        root: int

    class BelowFloor(Under[Count, Floor]):
        """A count under a floor of at most 10."""

    class AboveCeiling(Beyond[Count, Ceiling]):
        """A count over a ceiling of at least 20."""

    class AboveShifted(Beyond[Count, Shifted]):
        """A count over a bound the analysis cannot know."""

    class Lesser(Fact):
        under: BelowFloor

    class Greater(Fact):
        over: AboveCeiling

    class Shifty(Fact):
        over: AboveShifted

    count, floor = (
        InputRef((), ("request", "count"), Count),
        InputRef((), ("request", "floor"), Floor),
    )
    ceiling = InputRef((), ("request", "ceiling"), Ceiling)
    shifted = InputRef((), ("request", "shifted"), Shifted)
    below = Construction(Operation, BelowFloor, (), {"value": (count,), "bound": (floor,)})
    above = Construction(Operation, AboveCeiling, (), {"value": (count,), "bound": (ceiling,)})
    beyond = Construction(Operation, AboveShifted, (), {"value": (count,), "bound": (shifted,)})
    lesser = ConstructedRef(
        Construction(Operation, Lesser, (), {"under": (ConstructedRef(below),)})
    )
    greater = ConstructedRef(
        Construction(Operation, Greater, (), {"over": (ConstructedRef(above),)})
    )
    shifty = ConstructedRef(
        Construction(Operation, Shifty, (), {"over": (ConstructedRef(beyond),)})
    )
    assert joint((lesser, greater)).impossible
    assert [c.why for c in joint((lesser, greater)).clashes] == ["bounds"]
    assert not joint((lesser, shifty)).impossible
    assert never(AboveCeiling) is None
    assert never(AboveShifted) is None
    assert interval(Shifted) == Unknown("function-after", ("model", "function-after"))
    assert AboveShifted(value=Count(1), bound=Shifted(50)).ordering == 1


def test_a_kinds_own_validator_keeps_its_types_bound_and_every_output_lies_in_it(
    proof: Proof,
) -> None:
    assert declared(Low, "ordering").output == Known(
        numbers=Interval(low=Decimal(-1), high=Decimal(0))
    )
    (low,) = (c for c in proof.constructs(Operation) if c.cls is Low)
    (portions,) = (c for c in proof.constructs(Operation) if c.cls is Portions)
    assert operand(Low, "bound") == Interval()
    assert operand(Low, "bound", low) == Interval(low=Decimal(10), high=Decimal(10))
    assert operand(Low, "value", low) == Interval(low=Decimal(0), low_strict=True)
    assert interval_at(portions) == interval(Portions) == Interval(low=Decimal(0))
    assert never(Low, low) is None
    assert declared(Largest, "of").output == Known(lengths=(1, None))
    assert declared(Only[Element], "of").output == Known(lengths=(1, 1))
    assert declared(Portion, "root").output == Known(numbers=Interval(low=Decimal(0)))
    assert interval(Portion) == Interval(low=Decimal(0))
    orderings: set[int] = set()
    for amount in (Decimal("0.5"), Decimal(10), Decimal(11)):
        try:
            orderings.add(Low(value=Amount(amount), bound=Limit()).ordering)
        except ValidationError:
            continue
    assert orderings == {-1, 0}
    with pytest.raises(ValidationError):
        Largest(of=())
    portion = Portion(left=Share(Decimal(1)), right=Amount(Decimal(2)))
    assert len(Largest(of=(portion,)).of) >= 1
    assert len(Only[Element](of=(Element(name=Name("a")),)).of) == 1


def test_extra_outcomes_and_every_branch_are_kept() -> None:
    class Shapes(BaseModel):
        model_config = ConfigDict(validate_default=False)

        maybe: Decimal | None = Field(gt=0)
        count: int = Field(default=-5, ge=1)
        made: int = Field(default_factory=lambda: 7, ge=1)
        either: Annotated[int, Ge(1)] | Annotated[Decimal, Ge(5)]
        tainted: Annotated[int, Ge(1)] | Annotated[Decimal, Ge(5), AfterValidator(lambda v: v)]
        few: tuple[int, ...] = Field(default=(1, 2, 3), max_length=2)

    at = ("model", "model-fields", "model-field")
    assert declared(Shapes, "maybe").output == Known(
        numbers=Interval(low=Decimal(0), low_strict=True), none=True
    )
    assert declared(Shapes, "count").output == Known(numbers=Interval(low=Decimal(-5)))
    assert declared(Shapes, "made").output == Unknown("default_factory", (*at, "default"))
    assert declared(Shapes, "either").output == Known(numbers=Interval(low=Decimal(1)))
    assert declared(Shapes, "tainted").output == Unknown(
        "function-after", (*at, "union", "function-after")
    )
    assert declared(Shapes, "few").output == Known(lengths=(0, 3))
    made = Shapes(maybe=None, either=1, tainted=Decimal(5))
    assert (made.count, made.few) == (-5, (1, 2, 3))


def test_a_number_admitting_nan_is_unknown_and_a_bound_refusing_it_is_known() -> None:
    class Loose(BaseModel):
        value: float
        bounded: float = Field(gt=0)
        exact: Decimal
        finite: float = Field(allow_inf_nan=False)

    at = ("model", "model-fields", "model-field")
    assert declared(Loose, "value").output == Unknown("allow_inf_nan", (*at, "float"))
    assert declared(Loose, "bounded").output == Known(
        numbers=Interval(low=Decimal(0), low_strict=True)
    )
    assert declared(Loose, "exact").output == Known()
    assert declared(Loose, "finite").output == Known()
    fine = {"value": 1.0, "bounded": 1.0, "exact": Decimal(1), "finite": 1.0}
    assert isnan(Loose.model_validate({**fine, "value": nan}).value)
    assert Loose.model_validate({**fine, "bounded": inf}).bounded == inf
    for name, given in (("bounded", nan), ("exact", Decimal("NaN")), ("finite", inf)):
        with pytest.raises(ValidationError):
            Loose.model_validate({**fine, name: given})


def test_a_validator_around_the_model_leaves_its_fields_unknown_and_a_before_one_passes() -> None:
    class Checked(BaseModel):
        amount: int = Field(ge=1)

        @model_validator(mode="after")
        def same(self) -> Self:
            return self

    class Fed(BaseModel):
        amount: int = Field(ge=1)

        @model_validator(mode="before")
        @classmethod
        def feed(cls, data: object) -> object:
            return data

    assert declared(Checked, "amount").output == Unknown("function-after", ("function-after",))
    assert declared(Fed, "amount").output == Known(numbers=Interval(low=Decimal(1)))


def test_a_default_is_the_outcome_only_where_the_site_omits_the_input() -> None:
    class Doubled(Scalar[Decimal]):
        """A scalar whose validated input or default is doubled on the way in."""

        root: Annotated[Decimal, AfterValidator(lambda v: v * 2)] = Decimal(5)

    class Lifted(Scalar[Decimal]):
        """A scalar whose input or default is lifted before its bound admits it."""

        root: Annotated[Decimal, Gt(0), BeforeValidator(lambda v: Decimal(str(v)) + 1)] = Decimal(5)

    class Loose(Scalar[int]):
        """A scalar whose default is not validated: what is written is what is held."""

        model_config = ConfigDict(validate_default=False)
        root: int = Field(default=-5, ge=1)

    def at_site(cls: type[Scalar[Decimal]] | type[Scalar[int]]) -> Interval | Unknown:
        """What the engine's own occurrence of a constant can be: its root omitted."""
        return supplied_by(InputRef((), (cls.__name__,), cls))

    unknown = Unknown("function-after", ("model", "default", "function-after"))
    assert (Limit(Decimal(20)).root, interval(Limit)) == (20, Interval())
    assert (Lifted(Decimal(1)).root, interval(Lifted)) == (
        2,
        Interval(low=Decimal(0), low_strict=True),
    )
    assert (Loose(7).root, interval(Loose)) == (7, Interval(low=Decimal(-5)))
    assert (Doubled(Decimal(1)).root, interval(Doubled)) == (2, unknown)
    assert (Limit().root, at_site(Limit)) == (10, Interval(low=Decimal(10), high=Decimal(10)))
    assert (Lifted().root, at_site(Lifted)) == (6, Interval(low=Decimal(0), low_strict=True))
    assert (Loose().root, at_site(Loose)) == (-5, Interval(low=Decimal(-5), high=Decimal(-5)))
    assert (Doubled().root, at_site(Doubled)) == (10, unknown)
    assert supplied_by(InputRef((), ("request", "limit"), Limit)) == Interval()
    for cls in (Limit, Lifted, Loose):
        assert within(known(at_site(cls)), cls().root)
        assert within(known(interval(cls)), cls().root)


def test_a_before_validator_around_the_model_may_supply_what_a_site_omitted() -> None:
    class Fed(BaseModel):
        amount: int = Field(default=3, ge=1)

        @model_validator(mode="before")
        @classmethod
        def feed(cls, data: object) -> object:
            return {"amount": 50} if data == {} else data

    class Plain(BaseModel):
        amount: int = Field(default=3, ge=1)

    omitted = Inputs(omitted=True)
    nothing = frozenset[type[BaseModel]]()
    assert Fed.model_validate({}).amount == 50
    assert declared(Fed, "amount").output == Known(numbers=Interval(low=Decimal(1)))
    assert declared(Fed, "amount").outputs(nothing, omitted) == Known(
        numbers=Interval(low=Decimal(1))
    )
    assert (Plain().amount, Plain(amount=9).amount) == (3, 9)
    assert declared(Plain, "amount").output == Known(numbers=Interval(low=Decimal(1)))
    assert declared(Plain, "amount").outputs(nothing, omitted) == Known(
        numbers=Interval(low=Decimal(3), high=Decimal(3))
    )


def test_a_relations_impossibility_is_the_sites_claim_where_a_constant_is_bound() -> None:
    class Fee(Scalar[Decimal]):
        """A fee of 5 unless another is given."""

        root: Decimal = Decimal(5)

    class Floor(Scalar[Decimal]):
        """At least 6."""

        root: Decimal = Field(ge=6)

    class Over(Beyond[Fee, Floor]):
        """A fee over a floor."""

    floor = (InputRef((), ("request", "floor"), Floor),)
    from_constant = Construction(
        Operation, Over, (), {"value": (InputRef((), ("Fee",), Fee),), "bound": floor}
    )
    from_request = Construction(
        Operation, Over, (), {"value": (InputRef((), ("request", "fee"), Fee),), "bound": floor}
    )
    assert never(Over) is None
    assert never(Over, from_constant) == "holds"
    assert never(Over, from_request) is None
    assert Over(value=Fee(Decimal(50)), bound=Floor(Decimal(6))).ordering == 1
    with pytest.raises(ValidationError):
        Over(value=Fee(), bound=Floor(Decimal(6)))


def test_a_derived_bound_holds_only_through_the_declared_type_admitting_the_computed_value() -> (
    None
):
    (summing,) = (m for m in Sum.model_fields["root"].metadata if isinstance(m, Derived))

    class Plain(Sum[Amount]):
        """A sum computed and admitted by its declared type, nothing between."""

    class Negated(Sum[Amount]):
        """A sum whose computed value an after validator negates."""

        root: Annotated[Decimal, summing, AfterValidator(lambda v: -v)] = Field(
            default=COMPUTED, exclude=True
        )

    class Turned(Sum[Amount]):
        """A sum whose computed value a before validator turns before the type admits it."""

        root: Annotated[Decimal, BeforeValidator(lambda v: -Decimal(str(v))), summing] = Field(
            default=COMPUTED, exclude=True
        )

    at = ("model", "model-fields", "model-field", "default")
    amounts = (Amount(Decimal(2)), Amount(Decimal(3)))
    assert interval(Plain) == Interval(low=Decimal(0))
    assert Plain(of=amounts).root == 5
    with pytest.raises(ValidationError) as given:
        Plain(of=amounts, root=Decimal(99))
    assert [e["type"] for e in given.value.errors()] == ["computed"]
    assert interval(Negated) == Unknown("function-after", (*at, "function-after"))
    assert Negated(of=amounts).root == -5
    assert interval(Turned) == Interval()
    assert Turned(of=amounts).root == -5
    for cls in (Plain, Turned):
        assert within(known(interval(cls)), cls(of=amounts).root)
    assert interval(Portions) == Interval(low=Decimal(0))
    assert Portions(of=(Portion(left=Share(Decimal(1)), right=Amount(Decimal(2))),)).root == 2


def test_a_relations_conclusion_is_not_drawn_from_a_default_its_validators_change() -> None:
    class Fee(Scalar[Decimal]):
        """A constant written as 5 and constructed as 50."""

        root: Annotated[Decimal, AfterValidator(lambda v: v * 10)] = Decimal(5)

    class Floor(Scalar[Decimal]):
        """At least 6."""

        root: Decimal = Field(ge=6)

    class Over(Beyond[Fee, Floor]):
        """A fee over a floor: held by what constructs, refused by the default as written."""

    assert outcomes(Interval(low=Decimal(5), high=Decimal(5)), known(interval(Floor))) == {-1}
    assert never(Over) is None
    assert Over(value=Fee(), bound=Floor(Decimal(6))).ordering == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_every_value_constructed_in_nested_and_repeated_occurrences_lies_in_its_bound() -> (
    None
):
    request = Elements.model_validate_json(
        '{"each": [{"name": "a"}, {"name": "b"}, {"name": "c"}]}'
    )
    done = await ran(Operation, request, config(PROGRAM)(), proven(PROGRAM))
    assert isinstance(done, Run)
    checked: list[tuple[type[object], Decimal | int]] = []
    for scope in scopes(done.root):
        instances = [
            *((type(i), i) for i in scope.arrived.values()),
            *((c.cls, m.instance) for c, m in scope.made.items() if isinstance(m, Constructed)),
        ]
        for cls, instance in instances:
            root = getattr(instance, "root", None)
            if isinstance(root, bool) or not isinstance(root, (Decimal, int)):
                continue
            assert within(known(interval(cls)), root), (cls, root)
            checked.append((cls, root))
    constant = done.root.arrived[None, ("Limit",)]
    assert isinstance(constant, Limit)
    assert within(known(supplied_by(InputRef((), ("Limit",), Limit))), constant.root)
    assert [c for c, _ in checked].count(Portion) == 6
    assert [c for c, _ in checked].count(Portions) == 3
    assert {c for c, _ in checked} >= {Portion, Portions, Total, Limit, Amount, Share}
