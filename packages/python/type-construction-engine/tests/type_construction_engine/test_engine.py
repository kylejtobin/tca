"""The engine over the program this module is: classes named for what they are to the
framework, a stand-in party that answers from the environment, and nothing else.

The engine reads a program as the classes its module defines, so this module is the program.
``faults.py`` beside it is a second program, with the faults the proof refuses."""

import sys
from decimal import Decimal
from pathlib import Path
from types import ModuleType
from typing import override

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from pydantic import Field, PrivateAttr, ValidationError, computed_field

from type_construction.engine import (
    answer,
    asked,
    classes,
    coexist,
    config,
    descends,
    feasible,
    hear,
    heard,
    never,
    opened,
    produced,
    prove,
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
    First,
    Greatest,
    Least,
    Only,
    Record,
    Reply,
    Request,
    Route,
    Scalar,
    Setting,
    Sum,
    Value,
)

from . import faults as faults_module


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


class Amount(Scalar[Decimal]):
    """What the party says an element is worth."""

    root: Decimal = Field(gt=0)


class Heard(Record):
    """What the party says about an element."""

    amount: Amount


class Tell[P: Party, T: Record](Action[P, T]):
    """An action toward a stand-in party: hears the line the party was given."""

    @override
    async def perform(self) -> T:
        return hear(self, self.party.says.root)


class Asked(Tell[Party, Heard]):
    """Ask the party about one element."""

    element: Element


class Limit(Scalar[Decimal]):
    """The amount at or under which an element is low."""

    root: Decimal = Decimal(10)


class Low(AtMost[Amount, Limit]):
    """An amount at or under the limit."""

    bound: Limit = Limit()


class High(Beyond[Amount, Limit]):
    """An amount over the limit."""

    bound: Limit = Limit()


class Cheap(Fact):
    """An element the party valued low."""

    element: Element
    low: Low


class Dear(Fact):
    """An element the party valued high."""

    element: Element
    high: High


class Total(Sum[Amount]):
    """Every element's amount, summed."""


class Concluded(Fact):
    """Every element valued, and the total."""

    valued: tuple[Cheap | Dear, ...]
    total: Total


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
    """The one party."""

    party: Party


PROGRAM: ModuleType = sys.modules[__name__]
"""This module, as the program the engine reads."""

FAULTS: ModuleType = faults_module
"""The program beside this one, with the faults the proof refuses."""


@pytest.fixture
def party(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The party's answer in the environment, and no ``.env`` in the working directory."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PARTY__SAYS", '{"amount": "2.50"}')


async def operate(elements: str) -> Concluded:
    """The fact the route concludes for the elements, given as the request's JSON."""
    request = Elements.model_validate_json(elements)
    route = await answer(Operation, request, config(PROGRAM)(), PROGRAM)
    return route.reply.of


def test_the_program_is_proven() -> None:
    proven(PROGRAM)


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


def test_a_computed_field_produces_the_classes_its_return_type_names() -> None:
    class Picked(Fact):
        """A fact whose computed field returns one of two scalars."""

        amount: Amount

        @computed_field
        @property
        def which(self) -> Amount | Limit:
            return self.amount

    assert produced(Picked) == {"which": (Amount, Limit)}


def test_the_proof_is_what_joins_from_the_request() -> None:
    joined = prove(Operation, PROGRAM)
    assert {Elements, Element, Name, Party, Asked, Heard, Amount, Low, High, Cheap, Dear} <= joined
    assert {Total, Concluded, Answered, Capped, Operation} <= joined


def test_scope_is_read_as_the_element_a_class_descends_from() -> None:
    assert descends(Cheap, PROGRAM) == {Element}
    assert descends(Asked, PROGRAM) == {Element}
    assert descends(Amount, PROGRAM) == {Element}
    assert descends(Total, PROGRAM) == frozenset()
    assert descends(Operation, PROGRAM) == frozenset()


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_each_element_is_valued_in_its_own_run_and_collected_in_order() -> None:
    done = await operate('{"each": [{"name": "a"}, {"name": "b"}]}')
    assert [type(v).__name__ for v in done.valued] == ["Cheap", "Cheap"]
    assert [v.element.name.root for v in done.valued] == ["a", "b"]
    assert done.total.root == Decimal("5.00")


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_the_relation_that_holds_decides_the_outcome(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PARTY__SAYS", '{"amount": "25"}')
    done = await operate('{"each": [{"name": "a"}]}')
    assert type(done.valued[0]) is Dear


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_no_element_collects_the_empty_tuple_and_sums_to_zero() -> None:
    done = await operate('{"each": []}')
    assert done.valued == ()
    assert done.total.root == Decimal(0)


def test_a_relation_that_cannot_hold_or_cannot_refuse_is_read_from_the_bounds() -> None:
    assert never(FAULTS.Impossible) == "holds"
    assert never(FAULTS.Certain) == "refuses"
    assert never(FAULTS.Never) == "holds"
    assert never(Low) is None
    assert never(Cheap) is None


def test_two_facts_told_apart_by_complementary_relations_cannot_both_hold() -> None:
    assert not coexist(Cheap, Dear, PROGRAM)
    assert coexist(Cheap, Cheap, PROGRAM)


def test_two_facts_told_apart_by_overlapping_relations_can_both_hold() -> None:
    assert coexist(FAULTS.AtOrUnder, FAULTS.Exactly, FAULTS)


def test_the_solver_decides_difference_constraints_with_strictness() -> None:
    zero, x = object(), object()
    assert feasible([(zero, x, (Decimal(5), 0)), (x, zero, (Decimal(-5), 0))])
    assert not feasible([(zero, x, (Decimal(5), 0)), (x, zero, (Decimal(-5), -1))])


def test_the_proof_refuses_every_fault_at_once() -> None:
    with pytest.raises(ValidationError) as refusal:
        proven(FAULTS)
    found = {(e["type"], e["loc"]) for e in refusal.value.errors()}
    assert ("unused", ("Stray",)) in found
    assert ("undecidable", ("Undecided",)) in found
    assert ("relation", ("Impossible",)) in found
    assert ("relation", ("Certain",)) in found
    assert ("relation", ("Never",)) in found
    assert ("overlap", ("Either", "which")) in found
    assert ("hearer", ("Heard",)) in found
    assert ("party", ("Party",)) in found
    assert ("cycle", ("Egg",)) in found
    assert ("cycle", ("Chicken",)) in found
    assert ("scope", ("Misplaced",)) in found
    assert ("scope", ("Collects", "every")) in found
    assert ("scope", ("Heard",)) in found
    assert ("unused", ("Heard",)) not in found
    assert ("carrier", ("Name",)) in found
    assert ("missing", ("Concluded", "unheard")) in found
    assert FAULTS.Egg.model_fields["chicken"].annotation is FAULTS.Chicken


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_a_stalled_run_names_the_relation_that_did_not_hold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    said = '{"amount": "25", "name": "a", "tags": []}'
    monkeypatch.setenv("PARTY__SAYS", said)
    monkeypatch.setenv("BACKUP__SAYS", said)
    with pytest.raises(ValidationError) as refusal:
        request = FAULTS.Elements.model_validate_json(
            '{"each": [{"name": "a"}], "small": "50", "large": "150"}'
        )
        await answer(FAULTS.Operation, request, config(FAULTS)(), FAULTS)
    found = {(e["type"], e["loc"], e["msg"]) for e in refusal.value.errors()}
    assert ("relation", ("Low",), "Low did not hold: Amount exceeds Limit") in found


def test_a_selection_with_nothing_to_choose_from_refuses_with_relation() -> None:
    for kind in (Least[Amount], Greatest[Amount], First[Element], Only[Element]):
        with pytest.raises(ValidationError) as refusal:
            kind(of=())
        assert [e["type"] for e in refusal.value.errors()] == ["relation"]


class Fine(Party):
    """A party that opens."""

    @override
    async def open(self) -> None:
        LOG.append("open:Fine")

    @override
    async def close(self) -> None:
        LOG.append("close:Fine")


class Down(Party):
    """A party whose open raises."""

    @override
    async def open(self) -> None:
        LOG.append("open:Down")
        down = ConnectionError("down")
        raise down


class Later(Party):
    """A party opened after the first."""

    @override
    async def open(self) -> None:
        LOG.append("open:Later")

    @override
    async def close(self) -> None:
        LOG.append("close:Later")


class Opened(Config):
    """A deployment whose second party is down."""

    fine: Fine
    down: Down


class Lifecycle(Config):
    """A deployment of two parties that record their opening and closing."""

    fine: Fine
    later: Later


LOG: list[str] = []
"""What the parties' open and close wrote."""


@pytest.mark.asyncio
@pytest.mark.usefixtures("party")
async def test_opened_closes_what_it_opened_when_a_later_open_raises() -> None:
    LOG.clear()
    said = Said("{}")
    with pytest.raises(ConnectionError):
        async with opened(Opened(fine=Fine(says=said), down=Down(says=said))):
            pass
    assert LOG == ["open:Fine", "open:Down", "close:Fine"]


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
    LOG.clear()
    said = Said("{}")
    async with opened(Lifecycle(fine=Fine(says=said), later=Later(says=said))):
        LOG.append("answer")
        await operate('{"each": [{"name": "a"}]}')
        LOG.append("answer")
        await operate('{"each": [{"name": "a"}]}')
    assert LOG == ["open:Fine", "open:Later", "answer", "answer", "close:Later", "close:Fine"]


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
    assert spans["Operation"] == {"tca.request": "Elements", "tca.passes": 3}
    assert spans["Asked"] == {"tca.party": "Party", "tca.record": "Heard"}
    assert not any("2.50" in str(v) for a in spans.values() for v in a.values())


def test_the_proof_is_read_once_per_process() -> None:
    assert prove(Operation, PROGRAM) is prove(Operation, PROGRAM)
    assert proven(PROGRAM) is None
    assert proven(PROGRAM) is None


def test_a_scalar_over_int_has_no_value_between_two_integers() -> None:
    class Unit(Scalar[int]):
        """An integer over 0 and under 2: exactly 1."""

        root: int = Field(gt=0, lt=2)

    class One(Scalar[int]):
        """An integer that is 1."""

        root: int = Field(ge=1, le=1)

    class Same(Equal[Unit, One]):
        """Two integers that can only be 1."""

    assert never(Same) == "refuses"


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
async def test_a_computed_field_whose_scalar_refuses_propagates_the_refusal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PARTY__SAYS", '{"amount": "25"}')
    with pytest.raises(ValidationError) as refusal:
        await operate('{"each": [{"name": "a"}, {"name": "b"}]}')
    assert [(e["type"], e["loc"]) for e in refusal.value.errors()] == [("less_than_equal", ())]
