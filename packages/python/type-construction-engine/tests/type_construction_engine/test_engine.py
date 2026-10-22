"""The engine over the program this module is: classes named for what they are to the
framework, two stand-in parties that answer from the environment, and nothing else.

The engine reads a program as the classes its module defines, so this module is the program.
``faults.py`` beside it is a second program, with every fault the proof refuses; ``stalls.py``
a third, whose one outcome a party's answer refutes; ``lifecycle.py`` holds parties that record
their opening and closing, and is not a program."""

import sys
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
    Proof,
    answer,
    asked,
    classes,
    coexist,
    config,
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
    Config,
    Connection,
    Equal,
    Fact,
    Greatest,
    Instant,
    Interval,
    Least,
    Only,
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
    async def open(self) -> None:
        pass

    @override
    async def close(self) -> None:
        pass


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
    async def perform(self) -> T:
        return hear(self, self.party.says.root)


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


def test_the_proof_places_every_class_by_its_fields(proof: Proof) -> None:
    assert proof.path(Elements) == ()
    assert proof.path(Element) == (Element,)
    assert proof.path(Name) == (Element,)
    assert proof.path(Asked) == (Element,)
    assert proof.path(Heard) == (Element,)
    assert proof.path(Amount) == (Element,)
    assert proof.path(Part) == (Element, Part)
    assert proof.path(Share) == (Element, Part)
    assert proof.path(Portion) == (Element, Part)
    assert proof.path(Portions) == (Element,)
    assert proof.path(Largest) == (Element,)
    assert proof.path(Limit) == ()
    assert proof.path(Low) == (Element,)
    assert proof.path(Notify) == (Element,)
    assert proof.path(Noted) == (Element,)
    assert proof.path(Cheap) == (Element,)
    assert proof.path(Total) == ()
    assert proof.path(Concluded) == ()
    assert proof.path(Operation) == ()
    assert proof.waiting == ()
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
    assert type(hear(screen, '{"status": "clear"}')) is Clear
    assert type(hear(screen, '{"status": "flagged", "word": "no"}')) is Flagged


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
    found = {(e["type"], e["loc"]) for e in refusal.value.errors()}
    assert ("missing", ("Concluded", "unheard")) in found
    assert ("cycle", ("Egg",)) in found
    assert ("cycle", ("Chicken",)) in found
    assert ("twice", ("Name",)) in found
    assert ("twice", ("Heard",)) in found
    assert ("twice", ("Party",)) in found
    assert ("unplaceable", ("Twin",)) in found
    assert ("collects", ("Collects",)) in found
    assert ("route", ("Misplaced",)) in found
    assert ("unreached", ("Stray",)) in found
    assert ("unmodeled", ("Bare", "count")) in found
    assert ("boundary", ("Direct", "cheap")) in found
    assert ("boundary", ("Parties", "limit")) in found
    assert ("config", ("type_construction_engine.faults",)) in found
    assert ("ambiguous", ("Either", "which")) in found
    assert ("never", ("Impossible",)) in found
    assert ("never", ("Certain",)) in found
    assert ("never", ("Never",)) in found
    assert ("never", ("Undecided",)) in found
    assert ("undiscriminated", ("Both",)) in found
    assert ("undecided", ("Charge",)) in found
    assert ("cycle", ("Answered",)) not in found
    assert ("undecided", ("Asked",)) not in found
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
    assert found == {("relation", ("Low",), "Low did not hold: value Amount > bound Limit")}


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
            "Largest did not hold: Tuple should have at least 1 item after validation, not 0",
        )
    }


def test_a_selections_shape_is_its_tuple_annotation() -> None:
    with pytest.raises(ValidationError) as refusal:
        Least[Amount](of=())
    assert [(e["type"], e["loc"]) for e in refusal.value.errors()] == [("too_short", ("of",))]
    with pytest.raises(ValidationError) as refusal:
        Only[Element].model_validate({"of": ()})
    assert [(e["type"], e["loc"]) for e in refusal.value.errors()] == [("missing", ("of", 0))]
    with pytest.raises(ValidationError) as refusal:
        Only[Element].model_validate({"of": (Element(name=Name("a")), Element(name=Name("b")))})
    assert [(e["type"], e["loc"]) for e in refusal.value.errors()] == [("too_long", ("of",))]


def test_a_relations_ordering_is_computed_admitted_by_its_literal_and_never_given() -> None:
    low = Low.model_validate({"value": Amount(Decimal(5)), "bound": Limit()})
    assert low.ordering == -1
    assert low.model_dump() == {"value": Decimal(5), "bound": Decimal(10)}
    with pytest.raises(ValidationError) as refusal:
        Low.model_validate({"value": Amount(Decimal(11)), "bound": Limit(), "ordering": 0})
    found = [(e["type"], e["loc"]) for e in refusal.value.errors()]
    assert found == [("literal_error", ("ordering",))]


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_opened_closes_what_it_opened_when_a_later_open_raises() -> None:
    lifecycle.LOG.clear()
    said = lifecycle.Said("{}")
    with pytest.raises(ConnectionError):
        async with opened(
            lifecycle.Opened(fine=lifecycle.Fine(says=said), down=lifecycle.Down(says=said))
        ):
            pass
    assert lifecycle.LOG == ["open:Fine", "open:Down", "close:Fine"]


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
    spans = {s.name: dict(s.attributes or {}) for s in exporter.get_finished_spans()}
    names = [s.name for s in exporter.get_finished_spans()]
    assert names.count("Asked") == 2 and names.count("Operation") == 1
    assert spans["Operation"] == {"tca.request": "Elements", "tca.passes": 4}
    assert spans["Asked"] == {"tca.party": "Party", "tca.record": "Heard"}
    assert not any("2.50" in str(v) for a in spans.values() for v in a.values())


@pytest.mark.asyncio
async def test_a_client_in_a_private_attribute_leaves_the_connection_frozen() -> None:
    class Keyed(Party):
        """A party that holds a client outside its fields."""

        _client: object | None = PrivateAttr(default=None)

        @override
        async def open(self) -> None:
            self._client = object()

        def holds_a_client(self) -> bool:
            """Whether open set the client."""
            return self._client is not None

    keyed = Keyed(says=Said("{}"))
    await keyed.open()
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
