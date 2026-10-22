"""The runtime where it can break: a pass's actions in flight together, one of them failing
or answering text that does not validate while the others wait, a deadline or a shutdown
arriving mid-pass, two answers interleaving on one deployment, and the connections' closes
when the answer failed, when a close raises and when a cancellation lands during shutdown."""

import asyncio
import json
from collections.abc import AsyncGenerator, Callable, Coroutine, Sequence
from contextlib import asynccontextmanager
from decimal import Decimal
from pathlib import Path
from typing import Any, TypeIs

import pytest
from opentelemetry.sdk.trace import ReadableSpan
from pydantic import ValidationError

from type_construction.engine import answer, config, hear, opened, proven, ran, scopes
from type_construction.world import Connection, Record

from . import occurrences as program
from . import stalls
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


def quoting(flight: Flight, *, breaking: str | None = None) -> Perform[Quote, program.Price]:
    """A catalog's ``perform``: each quote waits at the flight's gate; the one for the
    breaking product instead yields once, so its siblings are waiting, and then fails, with
    the party down for ``boom`` and answering text that is no price for ``junk``."""

    async def perform(self: Quote) -> program.Price:
        sku = self.line.sku.root
        HELD.append(id(self.party))
        if sku == breaking == "boom":
            await asyncio.sleep(0)
            down = ConnectionError("catalog down")
            raise down
        if sku == breaking == "junk":
            await asyncio.sleep(0)
            return hear(self, '{"price": "a lot"}')
        await flight.held(sku)
        return hear(self, json.dumps({"price": PRICES[sku]}))

    return perform


def screening(flight: Flight) -> Perform[Screen, program.Clear | program.Flagged]:
    """A screening's ``perform`` that waits at the flight's gate."""

    async def perform(self: Screen) -> program.Clear | program.Flagged:
        HELD.append(id(self.party))
        await flight.held("screen")
        return hear(self, self.party.says.root)

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
    """The paths of the records admitted on a route's span, in order; a failed or refused run's
    span also carries the API's ``exception`` event."""
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
    assert group.__notes__ == [f"cancelled Screen, {QUOTES}"]
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
    assert LOG == ["open:Catalog", "open:Fraud", "close:Fraud", "close:Catalog"]
    assert done.route.reply.model_dump_json() == (
        '{"cart":"10.00","gifts":"4","pair":"14.50","solo":"10"}'
    )
    assert done.passes == 4
    assert len(HELD) == 7
    assert set(HELD) == set(OPENED) == {id(deployment.catalog), id(deployment.fraud)}
    quotes = [
        instance
        for scope in scopes(done.root)
        for owned, instance in scope.owned.items()
        if owned[-1] == "Quote"
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
    ("breaking", "failure"), [("boom", ConnectionError), ("junk", ValidationError)]
)
async def test_one_action_failing_mid_pass_cancels_its_siblings_and_the_group_holds_it_alone(
    monkeypatch: pytest.MonkeyPatch, breaking: str, failure: type[Exception]
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
    assert group.value.__notes__ == [f"cancelled {QUOTES}"]
    if isinstance(failed, ValidationError):
        assert [(e["type"], e["loc"]) for e in failed.errors()] == [("decimal_parsing", ("price",))]
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

    async def telling(self: valued.Tell[valued.Party, Record]) -> Record:
        """A party that values an element at what its name says, and a teller that waits."""
        if isinstance(self, valued.Asked):
            name = self.element.name.root
            await asked.held(name)
            return hear(self, json.dumps({"amount": name, "parts": [{"share": "1"}]}))
        await notified.wait()
        return hear(self, '{"word": "dear"}')

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
    assert admitted(route) == ["request.each.[0].Asked.heard"]
    (asked,) = by_name(spans, "Asked")
    assert attributes(asked)["tca.outcome"] == "heard"
