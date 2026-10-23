"""The runtime where it can break: a pass's actions in flight together, one of them failing
or answering text that does not validate while the others wait, a deadline or a shutdown
arriving mid-pass, two answers interleaving on one deployment, and the connections' closes
when the answer failed, when a close raises and when a cancellation lands during shutdown."""

import asyncio
import json
from collections.abc import AsyncGenerator, Callable, Coroutine, Mapping, Sequence
from contextlib import asynccontextmanager
from decimal import Decimal
from pathlib import Path
from typing import Annotated, Any, Literal, TypeIs

import pytest
from opentelemetry.sdk.trace import ReadableSpan
from pydantic import BaseModel, Field, ValidationError, ValidatorFunctionWrapHandler, WrapValidator
from pydantic_core import PydanticCustomError

from type_construction import engine
from type_construction.engine import (
    Collected,
    Constructed,
    ConstructedRef,
    Construction,
    Given,
    HeardRef,
    InputRef,
    Occurrence,
    Proof,
    Ref,
    Run,
    Scope,
    answer,
    config,
    construct,
    models,
    opened,
    proven,
    ran,
    scopes,
    symbolic,
)
from type_construction.world import (
    COMPUTED,
    REFUTED,
    AtMost,
    Comparison,
    Connection,
    Json,
    Only,
    Python,
    Record,
    Refusals,
    Refutable,
    Scalar,
)

from . import blockers, deadlock, fixed, stalls
from . import occurrences as program
from . import test_engine as valued
from .occurrences import PERFORMED, Checkout, PlaceOrder, Quote, Screen
from .test_occurrences import ORDER, exporting

PRICES = {"tea": "2.50", "mug": "4", "pot": "10"}
"""What the catalog says each product costs."""

LOG: list[str] = []
"""What the parties' open and close wrote, in order."""

OPENED: list[int] = []
"""The identity of each connection ``open`` was called on."""

HELD: list[int] = []
"""The identity of the party each performed action held."""

QUOTES = (
    "request.cart.lines.[0].Quote, request.cart.lines.[1].Quote, request.gifts.lines.[0].Quote,"
    " request.pair.lines.[0].Quote, request.pair.lines.[1].Quote"
)
"""The five quotes cancelled when the solo line's fails, in the order they were constructed;
the screening, constructed at the root before them, comes first when it is cancelled too."""


class Flight:
    """What the test holds over a pass's actions: a gate they wait at, an event set once the
    expected number wait there at once, and which were cancelled while waiting."""

    def __init__(self, expected: int) -> None:
        self.expected = expected
        self.gate = asyncio.Event()
        self.full = asyncio.Event()
        self.waiting = 0
        self.cancelled: list[str] = []

    async def held(self, name: str) -> None:
        """Wait at the gate as one named action, noting a cancellation that lands here."""
        self.waiting += 1
        if self.waiting == self.expected:
            self.full.set()
        try:
            await self.gate.wait()
        except asyncio.CancelledError:
            self.cancelled.append(name)
            raise
        finally:
            self.waiting -= 1


type Perform[A, T] = Callable[[A], Coroutine[Any, Any, T]]
"""A ``perform`` the test puts on an action class."""


def quoting(flight: Flight, *, breaking: str | None = None) -> Perform[Quote, Json | Python]:
    """A catalog's ``perform``: each quote waits at the flight's gate; the one for the
    breaking product instead yields once, so its siblings are waiting, and then fails, with
    the party down for ``boom``, answering text that is no price for ``junk``, and returning
    a record of another class, already validated, for ``alien``."""

    async def perform(self: Quote) -> Json | Python:
        sku = self.line.sku.root
        HELD.append(id(self.party))
        if sku == breaking == "boom":
            await asyncio.sleep(0)
            down = ConnectionError("catalog down")
            raise down
        if sku == breaking == "junk":
            await asyncio.sleep(0)
            return Json('{"price": "a lot"}')
        if sku == breaking == "alien":
            await asyncio.sleep(0)
            return Python(program.Clear(status="clear"))
        await flight.held(sku)
        return Json(json.dumps({"price": PRICES[sku]}))

    return perform


def screening(flight: Flight) -> Perform[Screen, Json]:
    """A screening's ``perform`` that waits at the flight's gate."""

    async def perform(self: Screen) -> Json:
        HELD.append(id(self.party))
        await flight.held("screen")
        return Json(self.party.says.root)

    return perform


def recording(
    monkeypatch: pytest.MonkeyPatch,
    cls: type[Connection],
    *,
    closing: asyncio.Event | None = None,
    broken: bool = False,
) -> None:
    """Put an ``open`` on a party class that records its entry and its exit: the exit signals
    ``closing`` and then waits until cancelled, or raises when ``broken``."""

    @asynccontextmanager
    async def open_(self: Connection) -> AsyncGenerator[None]:
        LOG.append(f"open:{cls.__name__}")
        OPENED.append(id(self))
        try:
            yield
        finally:
            LOG.append(f"close:{cls.__name__}")
            if closing is not None:
                closing.set()
                await asyncio.Event().wait()
            if broken:
                gone = OSError("socket already gone")
                raise gone

    monkeypatch.setattr(cls, "open", open_)


@pytest.fixture
def parties(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Both programs' parties in the environment, no ``.env``, the records cleared, and the
    occurrences program's parties recording their opening and closing."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CATALOG__PRICES", json.dumps(PRICES))
    monkeypatch.setenv("FRAUD__SAYS", '{"status": "clear"}')
    monkeypatch.setenv("PARTY__SAYS", "{}")
    monkeypatch.setenv("TELLER__SAYS", "{}")
    PERFORMED.clear()
    LOG.clear()
    OPENED.clear()
    HELD.clear()
    recording(monkeypatch, program.Catalog)
    recording(monkeypatch, program.Fraud)


def grouped(failure: BaseException | None) -> TypeIs[ExceptionGroup[Exception]]:
    """Whether a failure is the group a pass's actions raised in."""
    return isinstance(failure, ExceptionGroup)


def admitted(route: ReadableSpan) -> list[str]:
    """The paths of the records admitted on a route's span, in order; a failed run's span also
    carries the API's ``exception`` event."""
    return [str((e.attributes or {})["tca.heard"]) for e in route.events if e.name == "admitted"]


def by_name(spans: Sequence[ReadableSpan], name: str) -> list[ReadableSpan]:
    """The spans with a name."""
    return [s for s in spans if s.name == name]


def attributes(span: ReadableSpan) -> dict[str, object]:
    """A span's attributes."""
    return dict(span.attributes or {})


def site(span: ReadableSpan) -> str:
    """The occurrence a span was performed at."""
    return str(attributes(span)["tca.site"])


def trace_of(span: ReadableSpan) -> int:
    """The trace a span is in."""
    assert span.context is not None
    return span.context.trace_id


def parented(spans: Sequence[ReadableSpan], route: ReadableSpan) -> bool:
    """Whether every span is a child of the route's."""
    assert route.context is not None
    return all(s.parent is not None and s.parent.span_id == route.context.span_id for s in spans)


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_a_close_that_raises_after_a_failed_answer_closes_the_rest_and_keeps_the_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recording(monkeypatch, program.Fraud, broken=True)
    flight = Flight(6)
    monkeypatch.setattr(Quote, "perform", quoting(flight, breaking="boom"))
    monkeypatch.setattr(Screen, "perform", screening(flight))
    deployment = config(program)()
    request = PlaceOrder.model_validate_json(ORDER.replace('"pot"', '"boom"'))
    with pytest.raises(OSError, match="socket already gone") as failed:
        async with opened(deployment):
            await answer(Checkout, request, deployment, proven(program))
    assert LOG == ["open:Catalog", "open:Fraud", "close:Fraud", "close:Catalog"]
    group = failed.value.__context__
    assert grouped(group)
    (down,) = group.exceptions
    assert isinstance(down, ConnectionError)
    assert down.__notes__ == ["at request.solo.lines.[0].Quote"]
    assert group.__notes__ == [f"heard none; cancelled Screen, {QUOTES}; admitted none"]
    assert sorted(flight.cancelled) == ["mug", "mug", "screen", "tea", "tea", "tea"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_a_cancellation_that_lands_during_shutdown_does_not_keep_the_rest_open(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    closing = asyncio.Event()
    recording(monkeypatch, program.Fraud, closing=closing)
    flight = Flight(7)
    monkeypatch.setattr(Quote, "perform", quoting(flight))
    monkeypatch.setattr(Screen, "perform", screening(flight))
    deployment = config(program)()
    request = PlaceOrder.model_validate_json(ORDER)

    async def serving() -> None:
        async with opened(deployment):
            await answer(Checkout, request, deployment, proven(program))

    server = asyncio.ensure_future(serving())
    await flight.full.wait()
    server.cancel()
    await closing.wait()
    server.cancel()
    with pytest.raises(asyncio.CancelledError):
        await server
    assert LOG == ["open:Catalog", "open:Fraud", "close:Fraud", "close:Catalog"]
    assert len(flight.cancelled) == 7
    assert flight.waiting == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_a_deadline_cancels_the_pass_in_flight_and_the_opened_deployment_answers_again(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exporter = exporting()
    flight = Flight(7)
    monkeypatch.setattr(Quote, "perform", quoting(flight))
    monkeypatch.setattr(Screen, "perform", screening(flight))
    deployment = config(program)()
    assert isinstance(deployment, program.Deployment)
    proof = proven(program)
    request = PlaceOrder.model_validate_json(ORDER)
    async with opened(deployment):
        with pytest.raises(TimeoutError):
            async with asyncio.timeout(0.05):
                await answer(Checkout, request, deployment, proof)
        assert len(flight.cancelled) == 7
        assert flight.waiting == 0
        assert LOG == ["open:Catalog", "open:Fraud"]
        flight.gate.set()
        HELD.clear()
        done = await ran(Checkout, request, deployment, proof)
    assert isinstance(done, Run)
    assert LOG == ["open:Catalog", "open:Fraud", "close:Fraud", "close:Catalog"]
    assert done.route.reply.model_dump_json() == (
        '{"cart":"10.00","gifts":"4","pair":"14.50","solo":"10"}'
    )
    assert done.passes == 4
    assert len(HELD) == 7
    assert set(HELD) == set(OPENED) == {id(deployment.catalog), id(deployment.fraud)}
    quotes = [
        made.instance
        for scope in scopes(done.root)
        for construction, made in scope.made.items()
        if construction.cls is Quote and isinstance(made, Constructed)
    ]
    assert len(quotes) == 6
    assert all(isinstance(q, Quote) and q.party is deployment.catalog for q in quotes)
    cancelled, answered = by_name(exporter.get_finished_spans(), "Checkout")
    assert attributes(cancelled) == {"tca.request": "PlaceOrder", "tca.outcome": "cancelled"}
    assert cancelled.status.status_code.name == "UNSET"
    assert admitted(cancelled) == []
    assert attributes(answered) == {
        "tca.request": "PlaceOrder",
        "tca.outcome": "answered",
        "tca.passes": 4,
    }
    assert sorted(admitted(answered)) == sorted(
        f"{s}.heard" for s in ("Screen", *QUOTES.split(", "), "request.solo.lines.[0].Quote")
    )


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
@pytest.mark.parametrize(
    ("breaking", "failure", "errors"),
    [
        ("boom", ConnectionError, []),
        ("junk", ValidationError, [("decimal_parsing", ("price",))]),
        ("alien", ValidationError, [("model_type", ())]),
    ],
)
async def test_one_action_failing_mid_pass_cancels_its_siblings_and_the_group_holds_it_alone(
    monkeypatch: pytest.MonkeyPatch,
    breaking: str,
    failure: type[Exception],
    errors: list[tuple[str, tuple[str, ...]]],
) -> None:
    exporter = exporting()
    flight = Flight(5)
    monkeypatch.setattr(Quote, "perform", quoting(flight, breaking=breaking))
    request = PlaceOrder.model_validate_json(ORDER.replace('"pot"', f'"{breaking}"'))
    with pytest.raises(ExceptionGroup) as group:
        await answer(Checkout, request, config(program)(), proven(program))
    (failed,) = group.value.exceptions
    assert type(failed) is failure
    assert failed.__notes__ == ["at request.solo.lines.[0].Quote"]
    assert group.value.__notes__ == [f"heard Screen; cancelled {QUOTES}; admitted none"]
    if isinstance(failed, ValidationError):
        assert [(e["type"], e["loc"]) for e in failed.errors()] == errors
        assert failed.title == "Price"
    assert sorted(flight.cancelled) == ["mug", "mug", "tea", "tea", "tea"]
    assert flight.waiting == 0
    assert PERFORMED == ["screen"]
    spans = exporter.get_finished_spans()
    (route,) = by_name(spans, "Checkout")
    assert attributes(route) == {"tca.request": "PlaceOrder", "tca.outcome": "failed"}
    assert route.status.status_code.name == "ERROR"
    assert admitted(route) == []
    actions = [s for s in spans if s.name != "Checkout"]
    assert len(actions) == 7
    assert parented(actions, route)
    (broken,) = [s for s in actions if s.status.status_code.name == "ERROR"]
    assert site(broken) == "request.solo.lines.[0].Quote"
    assert attributes(broken)["tca.outcome"] == "failed"
    (screen,) = by_name(actions, "Screen")
    assert attributes(screen)["tca.outcome"] == "heard"
    assert attributes(screen)["tca.record"] == "Clear"
    quotes = [s for s in actions if s is not broken and s is not screen]
    assert {attributes(s)["tca.outcome"] for s in quotes} == {"cancelled"}
    assert all("tca.record" not in attributes(s) for s in quotes)


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_two_answers_interleaving_across_passes_keep_their_evidence_and_traces_apart(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exporter = exporting()
    asked = Flight(3)
    notified = asyncio.Event()

    async def telling(self: valued.Tell[valued.Party, Record]) -> Json:
        """A party that values an element at what its name says, and a teller that waits."""
        if isinstance(self, valued.Asked):
            name = self.element.name.root
            await asked.held(name)
            return Json(json.dumps({"amount": name, "parts": [{"share": "1"}]}))
        await notified.wait()
        return Json('{"word": "dear"}')

    monkeypatch.setattr(valued.Tell, "perform", telling)
    deployment = config(valued.PROGRAM)()
    proof = proven(valued.PROGRAM)
    cheap = valued.Elements.model_validate_json('{"each": [{"name": "2"}, {"name": "3"}]}')
    dear = valued.Elements.model_validate_json('{"each": [{"name": "25"}]}')
    first = asyncio.ensure_future(ran(valued.Operation, cheap, deployment, proof))
    second = asyncio.ensure_future(ran(valued.Operation, dear, deployment, proof))
    await asked.full.wait()
    asked.gate.set()
    done = await first
    assert not second.done()
    notified.set()
    later = await second
    assert isinstance(done, Run)
    assert isinstance(later, Run)
    assert done.route.reply.model_dump_json() == '{"total":"5"}'
    assert later.route.reply.model_dump_json() == '{"total":"25"}'
    assert done.route.request is cheap
    assert later.route.request is dear
    assert [type(v).__name__ for v in done.route.reply.of.valued] == ["Cheap", "Cheap"]
    (valued_dear,) = later.route.reply.of.valued
    assert isinstance(valued_dear, valued.Dear)
    assert valued_dear.element is dear.each[0]
    assert valued_dear.high.value.root == Decimal(25)
    spans = exporter.get_finished_spans()
    routes = {trace_of(s): s for s in by_name(spans, "Operation")}
    assert len(routes) == 2
    for s in spans:
        if s.name != "Operation":
            assert parented([s], routes[trace_of(s)])
    (notify,) = by_name(spans, "Notify")
    assert attributes(notify)["tca.pass"] == 2
    assert {attributes(s)["tca.outcome"] for s in spans if s.name != "Operation"} == {"heard"}
    for trace, route in routes.items():
        assert attributes(route)["tca.outcome"] == "answered"
        assert sorted(admitted(route)) == sorted(
            f"{site(s)}.heard" for s in spans if trace_of(s) == trace and s.name != "Operation"
        )
    traced = sorted(
        sorted(site(s) for s in spans if trace_of(s) == trace and s.name != "Operation")
        for trace in routes
    )
    assert traced == [
        ["request.each.[0].Asked", "request.each.[0].Notify"],
        ["request.each.[0].Asked", "request.each.[1].Asked"],
    ]
    assert (done.passes, later.passes) == (4, 4)


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_a_refused_run_is_the_businesss_no_on_the_route_span_not_a_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exporter = exporting()
    monkeypatch.setenv("PARTY__SAYS", '{"amount": "25"}')
    request = stalls.Elements.model_validate_json('{"each": [{"name": "a"}]}')
    with pytest.raises(ValidationError) as refusal:
        await answer(stalls.Operation, request, config(stalls)(), proven(stalls))
    assert [e["type"] for e in refusal.value.errors()] == ["relation"]
    spans = exporter.get_finished_spans()
    (route,) = by_name(spans, "Operation")
    assert attributes(route) == {"tca.request": "Elements", "tca.outcome": "refused"}
    assert route.status.status_code.name == "UNSET"
    assert [e.name for e in route.events] == ["admitted"]
    assert admitted(route) == ["request.each.[0].Asked.heard"]
    (asked,) = by_name(spans, "Asked")
    assert attributes(asked)["tca.outcome"] == "heard"


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_a_premise_the_party_decided_against_refuses_the_run_at_that_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exporter = exporting()
    monkeypatch.setenv("FRAUD__SAYS", '{"status": "flagged", "reason": "velocity"}')
    request = PlaceOrder.model_validate_json(ORDER)
    with pytest.raises(ValidationError) as refusal:
        await answer(program.Cleared, request, config(program)(), proven(program))
    assert [(e["type"], e["loc"], e["msg"]) for e in refusal.value.errors()] == [
        (
            "missing",
            ("Screened", "clear"),
            "no instance fills Screened.clear at Screened, which holds Clear; Screen at Screen"
            " heard Flagged",
        )
    ]
    (route,) = by_name(exporter.get_finished_spans(), "Cleared")
    assert attributes(route) == {"tca.request": "PlaceOrder", "tca.outcome": "refused"}
    assert len(admitted(route)) == 7
    assert "Screen.heard" in admitted(route)


@pytest.mark.asyncio
async def test_a_construction_that_is_not_refutable_refusing_is_a_failure_not_the_businesss_no(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    exporter = exporting()
    found = symbolic(fixed.Checkout, models(fixed))
    (line_total,) = (c for c in found.constructions if c.cls is fixed.LineTotal)
    cart = InputRef((), ("request", "cart"), fixed.Cart)
    both = Construction(
        fixed.Checkout,
        fixed.Both,
        (),
        premises={"cart": (cart,)},
        collections={"totals": (Collected(cart, "lines", (ConstructedRef(line_total),), None),)},
    )
    paired = Construction(
        fixed.Checkout, fixed.Paired, (), premises={"of": (ConstructedRef(both),)}
    )
    checkout = Construction(
        fixed.Checkout,
        fixed.Checkout,
        (),
        premises={
            "request": (InputRef((), ("request",), fixed.PlaceOrder),),
            "reply": (ConstructedRef(paired),),
        },
    )
    unproven = Proof.model_construct(
        program=fixed.__name__,
        classes=models(fixed),
        constructions=(*found.constructions, both, paired, checkout),
        waiting=(),
        faulted=(),
    )
    request = fixed.PlaceOrder.model_validate_json(
        '{"cart": {"lines": [{"quantity": 1, "price": "1"}, {"quantity": 1, "price": "1"},'
        ' {"quantity": 1, "price": "1"}]}}'
    )
    with pytest.raises(ValidationError) as failure:
        await answer(fixed.Checkout, request, config(fixed)(), unproven)
    assert failure.value.title == "Both"
    assert failure.value.__notes__ == ["at Both"]
    assert [(e["type"], e["loc"]) for e in failure.value.errors()] == [("too_long", ("totals",))]
    (route,) = by_name(exporter.get_finished_spans(), "Checkout")
    assert attributes(route) == {"tca.request": "PlaceOrder", "tca.outcome": "failed"}
    assert route.status.status_code.name == "ERROR"


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_a_premise_refuted_in_one_scope_is_reported_there_and_nowhere_else(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exporter = exporting()

    async def valuing(self: stalls.Tell[stalls.Party, Record]) -> Json:
        """A party that values an element at what its name says."""
        assert isinstance(self, stalls.Asked)
        return Json(json.dumps({"amount": self.element.name.root}))

    monkeypatch.setattr(stalls.Tell, "perform", valuing)
    request = stalls.Elements.model_validate_json(
        '{"each": [{"name": "2"}, {"name": "25"}, {"name": "3"}]}'
    )
    with pytest.raises(ValidationError) as refusal:
        await answer(stalls.Operation, request, config(stalls)(), proven(stalls))
    assert [(e["type"], e["loc"], e["msg"]) for e in refusal.value.errors()] == [
        (
            "relation",
            ("Low",),
            "Low at request.each.[1].Low did not hold: value Amount at"
            " request.each.[1].Asked.heard.amount > bound Limit at Limit",
        )
    ]
    (route,) = by_name(exporter.get_finished_spans(), "Operation")
    assert attributes(route)["tca.outcome"] == "refused"
    assert len(admitted(route)) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("says", "amount", "expected"),
    [
        (
            '{"status": "flagged", "reason": "velocity"}',
            "25",
            [
                (
                    "missing",
                    ("Screened", "clear"),
                    "no instance fills Screened.clear at Screened, which holds Clear; Screen at"
                    " Screen heard Flagged",
                ),
                (
                    "relation",
                    ("Low",),
                    "Low at Low did not hold: value Amount at request.amount > bound Limit at"
                    " Limit",
                ),
            ],
        ),
        (
            '{"status": "flagged", "reason": "velocity"}',
            "5",
            [
                (
                    "missing",
                    ("Screened", "clear"),
                    "no instance fills Screened.clear at Screened, which holds Clear; Screen at"
                    " Screen heard Flagged",
                ),
            ],
        ),
        (
            '{"status": "clear"}',
            "25",
            [
                (
                    "relation",
                    ("Low",),
                    "Low at Low did not hold: value Amount at request.amount > bound Limit at"
                    " Limit",
                ),
            ],
        ),
        ('{"status": "clear"}', "5", []),
    ],
)
async def test_each_premise_blocking_the_route_is_named_whatever_the_others_are(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    says: str,
    amount: str,
    expected: list[tuple[str, tuple[str, ...], str]],
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("FRAUD__SAYS", says)
    request = blockers.Ask.model_validate_json(f'{{"amount": "{amount}"}}')
    if not expected:
        done = await answer(blockers.Approve, request, config(blockers)(), proven(blockers))
        assert done.reply.of.low.value is request.amount
        return
    with pytest.raises(ValidationError) as refusal:
        await answer(blockers.Approve, request, config(blockers)(), proven(blockers))
    assert [(e["type"], e["loc"], e["msg"]) for e in refusal.value.errors()] == expected


def placing(cls: type[BaseModel], **premises: Ref) -> Construction:
    """A construction of a class at the root, its single fields bound to one reference each."""
    return Construction(
        deadlock.Hatch, cls, (), premises={name: (ref,) for name, ref in premises.items()}
    )


@pytest.mark.asyncio
async def test_occurrences_waiting_on_one_another_are_a_failure_not_the_businesss_no(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    exporter = exporting()
    with pytest.raises(ValidationError) as refused:
        proven(deadlock)
    assert {e["type"] for e in refused.value.errors()} == {"cycle"}
    assert {("cycle", ("Egg",)), ("cycle", ("Chicken",))} <= {
        (e["type"], e["loc"]) for e in refused.value.errors()
    }
    ask = InputRef((), ("request",), deadlock.Ask)
    egg = placing(deadlock.Egg, ask=ask)
    chicken = placing(deadlock.Chicken, egg=ConstructedRef(egg))
    egg.premises = {"chicken": (ConstructedRef(chicken),), "ask": (ask,)}
    hatched = placing(deadlock.Hatched, egg=ConstructedRef(egg))
    told = placing(deadlock.Told, of=ConstructedRef(hatched))
    hatch = placing(deadlock.Hatch, request=ask, reply=ConstructedRef(told))
    unproven = Proof.model_construct(
        program=deadlock.__name__,
        classes=models(deadlock),
        constructions=(egg, chicken, hatched, told, hatch),
        waiting=(),
        faulted=(),
    )
    request = deadlock.Ask.model_validate_json('{"name": "a"}')
    with pytest.raises(ValidationError) as failure:
        await answer(deadlock.Hatch, request, config(deadlock)(), unproven)
    assert [(e["type"], e["loc"], e["msg"]) for e in failure.value.errors()] == [
        ("deadlock", ("Hatch",), "Hatch at Hatch waits for Told at Told, and nothing constructs"),
        (
            "deadlock",
            ("Told",),
            "Told at Told waits for Hatched at Hatched, and nothing constructs",
        ),
        (
            "deadlock",
            ("Hatched",),
            "Hatched at Hatched waits for Egg at Egg, and nothing constructs",
        ),
        ("deadlock", ("Egg",), "Egg at Egg waits for Chicken at Chicken, and nothing constructs"),
        (
            "deadlock",
            ("Chicken",),
            "Chicken at Chicken waits for Egg at Egg, and nothing constructs",
        ),
    ]
    (route,) = by_name(exporter.get_finished_spans(), "Hatch")
    assert attributes(route) == {"tca.request": "Ask", "tca.outcome": "failed"}


ELEMENT = ("request", "each", "[]")
"""The site of each element's scope in the stalls and engine programs."""


def test_a_refutable_kind_is_refuted_by_its_declared_condition_only() -> None:
    element = Scope(ELEMENT, ("request", "each", "[0]"), Scope((), (), None))
    asked = Construction(stalls.Operation, stalls.Asked, ELEMENT)
    heard = HeardRef(asked, stalls.Heard, (), stalls.Heard)
    low = Occurrence(
        element,
        Construction(
            stalls.Operation,
            stalls.Low,
            ELEMENT,
            premises={
                "value": (heard.held(stalls.Amount, "amount", optional=False),),
                "bound": (InputRef((), ("Limit",), stalls.Limit),),
            },
        ),
    )
    assert low.path == ("request", "each", "[0]", "Low")
    refuted = construct(low, {"value": stalls.Amount(Decimal(11)), "bound": stalls.Limit()})
    assert isinstance(refuted, ValidationError)
    assert [(e["type"], e["loc"], e["msg"], e.get("ctx")) for e in refuted.errors()] == [
        (
            "refuted",
            ("ordering",),
            "value > bound",
            {
                "left": "value",
                "right": "bound",
                "left_class": "Amount",
                "right_class": "Limit",
                "sign": ">",
                "ordering": 1,
                "refusal": 0,
            },
        )
    ]
    malformed: list[dict[str, BaseModel]] = [
        {"value": stalls.Amount(Decimal(11))},
        {"value": stalls.Amount(Decimal(5)), "bound": stalls.Limit(), "ordering": -1},  # type: ignore[dict-item]
        {"value": stalls.Limit(), "bound": stalls.Limit()},
    ]
    for given in malformed:
        with pytest.raises(ValidationError) as failure:
            construct(low, given)  # type: ignore[arg-type]
        assert failure.value.title == "Low"
        assert failure.value.__notes__ == ["at request.each.[0].Low"]
    valuing = Construction(valued.Operation, valued.Asked, ELEMENT)
    record = HeardRef(valuing, valued.Heard, (), valued.Heard)
    portion = Construction(valued.Operation, valued.Portion, (*record.site, "parts", "[]"))
    largest = Occurrence(
        element,
        Construction(
            valued.Operation,
            valued.Largest,
            ELEMENT,
            collections={"of": (Collected(record, "parts", (ConstructedRef(portion),), None),)},
        ),
    )
    (of,) = largest.construction.collections["of"]
    assert of.site == (*ELEMENT, "Asked", "heard", "parts")
    refuted = construct(largest, {"of": ()})
    assert isinstance(refuted, ValidationError)
    assert [(e["type"], e["loc"], e.get("ctx")) for e in refuted.errors()] == [
        (
            "refuted",
            ("of",),
            {
                "why": "Tuple should have at least 1 item after validation, not 0",
                "count": 0,
                "refusal": 0,
            },
        )
    ]
    for malformed_of in ({}, {"of": (valued.Limit(),)}):
        with pytest.raises(ValidationError) as failure:
            construct(largest, malformed_of)  # type: ignore[arg-type]
        assert failure.value.title == "Largest"
        assert failure.value.__notes__ == ["at request.each.[0].Largest"]
    assert [e["type"] for e in failure.value.errors()] == ["model_type"]
    solo_ = InputRef((), ("request", "solo"), program.Solo)
    line_total = Construction(
        program.Checkout, program.LineTotal, ("request", "solo", "lines", "[0]")
    )
    only = Occurrence(
        Scope((), (), None),
        Construction(
            program.Checkout,
            program.SoloTotal,
            (),
            premises={"solo": (solo_,)},
            collections={"of": (Collected(solo_, "lines", (ConstructedRef(line_total),), 1),)},
        ),
    )
    assert only.path == ("SoloTotal",)
    solo = program.Solo(lines=(program.Line(sku=program.Sku("a"), quantity=program.Quantity(1)),))
    total = program.LineTotal(left=program.UnitPrice(Decimal(1)), right=program.Quantity(1))
    refuted = construct(only, {"solo": solo, "of": ()})
    assert isinstance(refuted, ValidationError)
    assert [(e["type"], e["loc"], e.get("ctx")) for e in refuted.errors()] == [
        ("refuted", ("of",), {"why": "Field required", "count": 0, "refusal": 0})
    ]
    refuted = construct(only, {"solo": solo, "of": (total, total)})
    assert isinstance(refuted, ValidationError)
    assert [(e["type"], e["loc"], e.get("ctx")) for e in refuted.errors()] == [
        (
            "refuted",
            ("of",),
            {
                "why": "Tuple should have at most 1 item after validation, not 2",
                "count": 2,
                "refusal": 0,
            },
        )
    ]
    assert isinstance(construct(only, {"solo": solo, "of": (total,)}), program.SoloTotal)
    for malformed_only in ({"solo": solo}, {"solo": solo, "of": (solo,)}):
        with pytest.raises(ValidationError) as failure:
            construct(only, malformed_only)  # type: ignore[arg-type]
        assert failure.value.__notes__ == ["at SoloTotal"]


def forged(value: object, handler: ValidatorFunctionWrapHandler) -> object:
    """A validator that is not a declared condition yet raises the condition's error type."""
    raise PydanticCustomError(REFUTED, "forged", {"refusal": 0})


class Tagged(Scalar[str]):
    """A tag a forged validator refuses."""

    root: str = Field(min_length=1)


class Forging(AtMost[stalls.Amount, stalls.Limit]):
    """A relation with a field that forges the condition's error outside any condition."""

    tag: Annotated[Tagged, WrapValidator(forged)]


class Forger(Refutable):
    """A refutable kind whose own condition field is wrapped by a validator forging the
    condition's error at that very field, before the condition can run."""

    value: stalls.Amount
    bound: stalls.Limit
    ordering: Annotated[Literal[-1, 0], Comparison(("value", "bound")), WrapValidator(forged)] = (
        Field(default=COMPUTED, exclude=True)
    )


def refusal_of(cls: type[Refutable], given: Given) -> tuple[ValidationError, Refusals]:
    """A refutable kind's refusal of what was given, validated with its own refusals record."""
    refusals = Refusals()
    with pytest.raises(ValidationError) as refusal:
        cls.model_validate(given, context=refusals)
    return refusal.value, refusals


def test_a_refutation_is_only_what_the_kinds_own_conditions_refuse() -> None:
    held: Given = {"value": stalls.Amount(Decimal(1)), "bound": stalls.Limit()}
    over: Given = {"value": stalls.Amount(Decimal(11)), "bound": stalls.Limit()}
    refusal, refusals = refusal_of(Forging, {**held, "tag": Tagged("t")})
    assert [(e["type"], e["loc"]) for e in refusal.errors()] == [("refuted", ("tag",))]
    assert refusals.noted == []
    assert not Forging.refuted(refusal, refusals)
    refusal, refusals = refusal_of(Forging, {**over, "tag": Tagged("t")})
    assert [(e["type"], e["loc"]) for e in refusal.errors()] == [
        ("refuted", ("ordering",)),
        ("refuted", ("tag",)),
    ]
    assert [name for name, _ in refusals.noted] == ["ordering"]
    assert not Forging.refuted(refusal, refusals)
    refusal, refusals = refusal_of(Forger, over)
    assert [(e["type"], e["loc"], e.get("ctx")) for e in refusal.errors()] == [
        ("refuted", ("ordering",), {"refusal": 0})
    ]
    assert refusals.noted == []
    assert not Forger.refuted(refusal, refusals)
    refusal, refusals = refusal_of(stalls.Low, over)
    assert [name for name, _ in refusals.noted] == ["ordering"]
    assert stalls.Low.refuted(refusal, refusals)
    assert not stalls.Low.refuted(refusal, Refusals())
    refusal, refusals = refusal_of(stalls.Low, {"value": stalls.Limit(), "bound": stalls.Limit()})
    assert [e["type"] for e in refusal.errors()] == ["is_instance_of", "uncomputed"]
    assert refusals.noted == []
    assert not stalls.Low.refuted(refusal, refusals)
    forging = Occurrence(Scope((), (), None), Construction(stalls.Operation, Forging, ()))
    with pytest.raises(ValidationError) as failure:
        construct(forging, {**over, "tag": Tagged("t")})
    assert failure.value.__notes__ == ["at Forging"]
    forger = Occurrence(Scope((), (), None), Construction(stalls.Operation, Forger, ()))
    with pytest.raises(ValidationError) as failure:
        construct(forger, over)
    assert failure.value.__notes__ == ["at Forger"]
    cheap = Occurrence(Scope((), (), None), Construction(stalls.Operation, stalls.Cheap, ()))
    nested: dict[str, object] = {
        "element": stalls.Element(name=stalls.Name("a")),
        "low": dict(over),
    }
    with pytest.raises(ValidationError) as failure:
        construct(cheap, nested)  # type: ignore[arg-type]
    assert [(e["type"], e["loc"]) for e in failure.value.errors()] == [
        ("refuted", ("low", "ordering"))
    ]
    assert failure.value.__notes__ == ["at Cheap"]


class Sole(Only[stalls.Element]):
    """One element, chosen among elements."""


def test_a_mixed_refusal_is_a_failure_and_a_pure_one_a_refutation() -> None:
    elements = (stalls.Element(name=stalls.Name("a")), stalls.Element(name=stalls.Name("b")))
    refusal, refusals = refusal_of(Sole, {"of": elements})
    assert [e["type"] for e in refusal.errors()] == ["refuted"]
    assert Sole.refuted(refusal, refusals)
    refusal, refusals = refusal_of(Sole, {"of": (stalls.Name("a"),)})
    assert [e["type"] for e in refusal.errors()] == ["model_type"]
    assert refusals.noted == []
    assert not Sole.refuted(refusal, refusals)


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_one_resolver_serves_construction_and_explanation_and_only_a_blocked_run_explains(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resolved: list[Ref] = []
    explained: list[engine.Occurrence] = []
    resolving, explaining = engine.resolve, engine.causes

    def counting(ref: Ref, scope: Scope) -> engine.State:
        """``resolve`` that records each reference dereferenced, in a pass or at the end."""
        resolved.append(ref)
        return resolving(ref, scope)

    def noting(
        occurrence: engine.Occurrence,
        unresolved: engine.Unresolved,
        blocked: Mapping[engine.Occurrence, tuple[engine.Cause, ...]],
    ) -> tuple[engine.Cause, ...]:
        """``causes`` that records each occurrence explained."""
        explained.append(occurrence)
        return explaining(occurrence, unresolved, blocked)

    monkeypatch.setattr(engine, "resolve", counting)
    monkeypatch.setattr(engine, "causes", noting)
    request = PlaceOrder.model_validate_json(ORDER)
    proof = proven(program)
    retained = {
        r
        for route in (Checkout, program.Cleared)
        for c in proof.constructs(route)
        for refs in (
            *c.premises.values(),
            *((col.holder, *col.elements) for cols in c.collections.values() for col in cols),
        )
        for r in refs
    }
    done = await ran(Checkout, request, config(program)(), proof)
    assert isinstance(done, Run)
    assert done.passes == 4
    assert resolved
    assert all(r in retained for r in resolved)
    assert explained == []
    resolved.clear()
    monkeypatch.setenv("FRAUD__SAYS", '{"status": "flagged", "reason": "velocity"}')
    blocked = await ran(program.Cleared, request, config(program)(), proof)
    assert isinstance(blocked, engine.Blocked)
    assert all(r in retained for r in resolved)
    (screened,) = (c for c in proof.constructs(program.Cleared) if c.cls is program.Screened)
    (screen,) = (c for c in proof.constructs(program.Cleared) if c.cls is program.Screen)
    assert explained
    assert all(o.scope is blocked.occurrence.scope for o in explained)
    (cause,) = blocked.causes
    assert isinstance(cause, engine.Unfilled)
    assert cause.ref is screened.premises["clear"][0]
    assert cause.occurrence.construction is screened
    assert isinstance(cause.state, engine.Heard)
    assert cause.state.action.construction is screen
    assert cause.state.record is blocked.occurrence.scope.arrived[screen, ()]
    assert isinstance(cause.state.record, program.Flagged)


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_an_action_that_cancels_itself_fails_the_pass_and_admits_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exporter = exporting()
    flight = Flight(6)
    monkeypatch.setattr(Quote, "perform", quoting(flight))

    async def quitting(self: Screen) -> Json:
        """A screening that cancels its own task once its siblings are waiting."""
        await flight.full.wait()
        task = asyncio.current_task()
        assert task is not None
        task.cancel()
        await asyncio.sleep(0)
        return Json(self.party.says.root)

    monkeypatch.setattr(Screen, "perform", quitting)
    request = PlaceOrder.model_validate_json(ORDER)

    async def releasing() -> None:
        await flight.full.wait()
        await asyncio.sleep(0)
        flight.gate.set()

    release = asyncio.ensure_future(releasing())
    with pytest.raises(RuntimeError) as failure:
        await answer(Checkout, request, config(program)(), proven(program))
    await release
    said = str(failure.value)
    assert said.startswith("an action of pass 1 cancelled itself; heard ")
    assert said.endswith("; cancelled Screen; admitted none")
    assert all(path in said for path in (*QUOTES.split(", "), "request.solo.lines.[0].Quote"))
    assert flight.cancelled == []
    spans = exporter.get_finished_spans()
    (route,) = by_name(spans, "Checkout")
    assert attributes(route) == {"tca.request": "PlaceOrder", "tca.outcome": "failed"}
    assert route.status.status_code.name == "ERROR"
    assert route.status.description == "RuntimeError"
    assert admitted(route) == []
    assert [(e.name, dict(e.attributes or {})) for e in route.events] == [
        ("exception", {"exception.type": "builtins.RuntimeError"})
    ]
    (screen,) = by_name(spans, "Screen")
    assert attributes(screen)["tca.outcome"] == "cancelled"
    assert screen.status.status_code.name == "UNSET"
    assert {attributes(s)["tca.outcome"] for s in by_name(spans, "Quote")} == {"heard"}


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_a_failed_actions_span_names_the_failure_and_carries_nothing_the_party_said(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exporter = exporting()
    flight = Flight(5)
    leaked = '{"price": "a lot", "token": "sk-live-123"}'

    async def leaking(self: Quote) -> Json:
        """A catalog whose answer for one product is no price and carries a token."""
        sku = self.line.sku.root
        if sku == "junk":
            await asyncio.sleep(0)
            return Json(leaked)
        await flight.held(sku)
        return Json(json.dumps({"price": PRICES[sku]}))

    monkeypatch.setattr(Quote, "perform", leaking)
    request = PlaceOrder.model_validate_json(ORDER.replace('"pot"', '"junk"'))
    with pytest.raises(ExceptionGroup) as group:
        await answer(Checkout, request, config(program)(), proven(program))
    (failed,) = group.value.exceptions
    assert isinstance(failed, ValidationError)
    assert {e["input"] for e in failed.errors()} == {"a lot", "sk-live-123"}
    spans = exporter.get_finished_spans()
    (route,) = by_name(spans, "Checkout")
    (broken,) = [s for s in spans if s.name == "Quote" and s.status.status_code.name == "ERROR"]
    assert route.status.description == "ExceptionGroup"
    assert broken.status.description == "ValidationError"
    assert [(e.name, dict(e.attributes or {})) for e in broken.events] == [
        ("exception", {"exception.type": "pydantic_core._pydantic_core.ValidationError"})
    ]
    assert [e.name for e in route.events] == ["exception"]
    exported = [
        *(str(v) for s in spans for v in attributes(s).values()),
        *(str(v) for s in spans for e in s.events for v in (e.attributes or {}).values()),
        *(str(s.status.description) for s in spans),
    ]
    assert not any("a lot" in found or "sk-live" in found for found in exported)
