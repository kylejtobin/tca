"""Construction from occurrences, over the program ``occurrences.py`` is: one class at many
sites, separate collections of one element class, carriers that say which collection, a fixed
pair and a solo line, a record heard as one of two, a child holding its parent's aggregate, and
the same proof whatever order the classes are declared in."""

import sys
from decimal import Decimal
from pathlib import Path
from types import ModuleType

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import StatusCode
from pydantic import BaseModel, ValidationError

from type_construction.engine import (
    Placement,
    Proof,
    answer,
    config,
    construct,
    models,
    proven,
    ran,
    symbolic,
)

from . import fixed, optional, stalls
from . import occurrences as program
from .occurrences import (
    PERFORMED,
    CartShares,
    CartTotal,
    Checkout,
    GiftTotal,
    LineTotal,
    PairTotal,
    PlaceOrder,
    Quote,
    Screen,
    Screened,
    Share,
    SoloTotal,
)

PROGRAM: ModuleType = sys.modules[program.__name__]
"""The program the proof reads."""

ORDER = (
    '{"cart": {"lines": [{"sku": "tea", "quantity": 2}, {"sku": "tea", "quantity": 2}]},'
    ' "gifts": {"lines": [{"sku": "mug", "quantity": 1}]},'
    ' "pair": {"lines": [{"sku": "tea", "quantity": 1}, {"sku": "mug", "quantity": 3}]},'
    ' "solo": {"lines": [{"sku": "pot", "quantity": 1}]}}'
)
"""An order: two equal cart lines, one gift, a pair, and a solo line."""

CART = ("request", "cart", "lines", "[]")
GIFT = ("request", "gifts", "lines", "[]")
FIRST = ("request", "pair", "lines", "[0]")
SECOND = ("request", "pair", "lines", "[1]")
SOLO = ("request", "solo", "lines", "[0]")
"""The sites of each line's scope."""


@pytest.fixture
def parties(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The catalog's prices and a clear screening in the environment; no ``.env``."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CATALOG__PRICES", '{"tea": "2.50", "mug": "4", "pot": "10"}')
    monkeypatch.setenv("FRAUD__SAYS", '{"status": "clear"}')
    PERFORMED.clear()


def exporting() -> InMemorySpanExporter:
    """An exporter receiving every span of the process's tracer provider, which is set once."""
    provider = trace.get_tracer_provider()
    if not isinstance(provider, TracerProvider):
        provider = TracerProvider()
        trace.set_tracer_provider(provider)
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return exporter


def placed() -> dict[tuple[type[object], tuple[str, ...]], Placement]:
    """Every placement of the route, by class and scope."""
    return {(p.cls, p.scope): p for p in proven(PROGRAM).placements(Checkout)}


def test_one_class_constructs_at_every_site_its_premises_bind() -> None:
    found = placed()
    assert {scope for cls, scope in found if cls is LineTotal} == {CART, GIFT, FIRST, SECOND, SOLO}
    assert {scope for cls, scope in found if cls is Quote} == {CART, GIFT, FIRST, SECOND, SOLO}
    assert {scope for cls, scope in found if cls is Share} == {CART, GIFT, FIRST, SECOND, SOLO}
    for scope in (CART, GIFT, FIRST, SECOND, SOLO):
        assert found[LineTotal, scope].singles == {
            "left": ((*scope, "Quote", "heard", "unit"),),
            "right": ((*scope, "quantity"),),
        }


def test_separate_collections_of_one_element_class_stay_separate() -> None:
    found = placed()
    assert found[CartTotal, ()].collections["of"].site == ("request", "cart", "lines")
    assert found[CartTotal, ()].collections["of"].elements == ((*CART, "LineTotal"),)
    assert found[GiftTotal, ()].collections["of"].site == ("request", "gifts", "lines")
    assert found[GiftTotal, ()].collections["of"].elements == ((*GIFT, "LineTotal"),)
    assert found[PairTotal, ()].collections["of"].site == ("request", "pair", "lines")
    assert found[PairTotal, ()].collections["of"].elements == (
        (*FIRST, "LineTotal"),
        (*SECOND, "LineTotal"),
    )
    assert found[SoloTotal, ()].collections["of"].elements == ((*SOLO, "LineTotal"),)
    assert found[CartShares, ()].collections["shares"].site == ("request", "cart", "lines")
    assert found[CartShares, ()].collections["shares"].elements == ((*CART, "Share"),)


def test_a_reference_to_an_existing_premise_is_not_a_new_producer() -> None:
    found = placed()
    assert found[Screened, ()].singles["order"] == (("request",),)
    assert found[Screen, ()].singles["order"] == (("request",),)
    assert found[Share, CART].singles["cart"] == (("CartTotal",),)
    assert found[Share, GIFT].singles["cart"] == (("CartTotal",),)
    assert [cls for cls, _ in found if cls is CartTotal] == [CartTotal]
    assert PlaceOrder not in {cls for cls, _ in found}
    assert found[Screened, ()].singles["clear"] == (("Screen", "heard"),)


def test_the_proof_does_not_depend_on_declaration_order() -> None:
    reversed_program = ModuleType(PROGRAM.__name__)
    for name, value in reversed(list(vars(PROGRAM).items())):
        setattr(reversed_program, name, value)
    forward = {
        (p.cls, p.scope, repr(p.singles), repr(p.collections)) for p in proven(PROGRAM).placed
    }
    backward = {
        (p.cls, p.scope, repr(p.singles), repr(p.collections))
        for p in proven(reversed_program).placed
    }
    assert forward == backward


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_each_carrier_sums_its_own_lines_and_equal_lines_are_two() -> None:
    request = PlaceOrder.model_validate_json(ORDER)
    done = await answer(Checkout, request, config(PROGRAM)(), proven(PROGRAM))
    assert done.reply.model_dump_json() == '{"cart":"10.00","gifts":"4","pair":"14.50","solo":"10"}'
    paid = done.reply.of
    assert isinstance(paid, program.Paid)
    priced = paid.priced
    assert request.cart.lines[0] == request.cart.lines[1]
    assert [t.root for t in priced.cart.of] == [Decimal("5.00"), Decimal("5.00")]
    totals = [*priced.cart.of, *priced.gifts.of, *priced.pair.of, *priced.solo.of]
    assert all(t.root == t.left.root * t.right.root for t in totals)
    assert priced.cart.root == sum(t.root for t in priced.cart.of)
    assert priced.cart.of[0].right is request.cart.lines[0].quantity
    assert priced.cart.of[1].right is request.cart.lines[1].quantity
    assert priced.gifts.of[0].right is request.gifts.lines[0].quantity
    assert priced.pair.of[1].right is request.pair.lines[1].quantity
    assert priced.solo.chosen.right is request.solo.lines[0].quantity
    assert paid.screened.order is request
    assert sorted(PERFORMED) == ["mug", "mug", "pot", "screen", "tea", "tea", "tea"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_a_child_holds_its_parents_aggregate_and_the_parent_collects_the_children() -> None:
    request = PlaceOrder.model_validate_json(ORDER)
    done = await answer(Checkout, request, config(PROGRAM)(), proven(PROGRAM))
    paid = done.reply.of
    assert isinstance(paid, program.Paid)
    priced = paid.priced
    assert len(priced.shares.shares) == 2
    assert all(s.cart is priced.cart for s in priced.shares.shares)
    assert [s.total for s in priced.shares.shares] == list(priced.cart.of)


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_the_other_alternative_heard_makes_the_other_reply(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FRAUD__SAYS", '{"status": "flagged", "reason": "velocity"}')
    request = PlaceOrder.model_validate_json(ORDER)
    done = await answer(Checkout, request, config(PROGRAM)(), proven(PROGRAM))
    assert done.reply.model_dump_json() == '{"reason":"velocity","cart":"10.00"}'


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_empty_collections_sum_to_zero_and_the_fixed_pair_still_constructs() -> None:
    request = PlaceOrder.model_validate_json(
        '{"cart": {"lines": []}, "gifts": {"lines": []},'
        ' "pair": {"lines": [{"sku": "tea", "quantity": 1}, {"sku": "tea", "quantity": 1}]},'
        ' "solo": {"lines": [{"sku": "pot", "quantity": 1}]}}'
    )
    done = await answer(Checkout, request, config(PROGRAM)(), proven(PROGRAM))
    assert done.reply.model_dump_json() == '{"cart":"0","gifts":"0","pair":"5.00","solo":"10"}'


def test_a_fixed_tuple_refuses_the_wrong_count_at_the_request() -> None:
    with pytest.raises(ValidationError) as refusal:
        PlaceOrder.model_validate_json(
            '{"cart": {"lines": []}, "gifts": {"lines": []},'
            ' "pair": {"lines": [{"sku": "tea", "quantity": 1}]},'
            ' "solo": {"lines": [{"sku": "pot", "quantity": 1}]}}'
        )
    assert [(e["type"], e["loc"]) for e in refusal.value.errors()] == [
        ("missing", ("pair", "lines", 1))
    ]


def test_an_optional_field_is_not_evidence_for_a_reply_that_needs_it() -> None:
    with pytest.raises(ValidationError) as refusal:
        proven(optional)
    found = {(e["type"], e["loc"]): e["msg"] for e in refusal.value.errors()}
    assert set(found) == {("conditional", ("Checkout",))}
    assert found["conditional", ("Checkout",)] == (
        "Checkout answers only when Quote.heard.coupon arrives, and what declares it admits its"
        " absence; an absence the business concludes from is a class"
    )


@pytest.mark.asyncio
async def test_a_reply_that_reads_an_optional_field_answers_with_and_without_it(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    program_ = ModuleType(optional.__name__)
    for name, value in vars(optional).items():
        if name not in ("Checkout", "OrderDiscounted", "Discounted", "Discount"):
            setattr(program_, name, value)
    proof = proven(program_)
    request = optional.PlaceOrder.model_validate_json('{"sku": "tea"}')
    monkeypatch.setenv("PARTY__SAYS", '{"amount": "5", "coupon": "TEN"}')
    first = await answer(optional.Price, request, config(program_)(), proof)
    monkeypatch.setenv("PARTY__SAYS", '{"amount": "5"}')
    second = await answer(optional.Price, request, config(program_)(), proof)
    assert first.reply.model_dump_json() == '{"amount":"5","coupon":"TEN"}'
    assert second.reply.model_dump_json() == '{"amount":"5","coupon":null}'


def test_a_fixed_pair_does_not_bind_to_a_collection_of_any_number() -> None:
    with pytest.raises(ValidationError) as refusal:
        proven(fixed)
    found = {(e["type"], e["loc"]): e["msg"] for e in refusal.value.errors()}
    assert set(found) == {("collects", ("Both", "totals"))}
    assert found["collects", ("Both", "totals")] == (
        "Both.totals collects LineTotal as tuple[LineTotal, LineTotal], and the elements of no"
        " collection of that shape hold it; a collection is one level down, under a tuple the"
        " request or a record declares"
    )


def test_conditional_evidence_stays_conditional_through_a_chain_of_constructions() -> None:
    with pytest.raises(ValidationError) as refusal:
        proven(optional)
    (error,) = refusal.value.errors()
    assert (error["type"], error["loc"]) == ("conditional", ("Checkout",))
    placed = {p.cls: p for p in symbolic(optional.Checkout, models(optional)).placed}
    assert placed[optional.Discount].singles["coupon"] == (("Quote", "heard", "coupon"),)
    assert placed[optional.Discounted].singles["discount"] == (("Discount",),)
    assert placed[optional.Checkout].singles["reply"] == (("OrderDiscounted",),)


@pytest.mark.asyncio
async def test_the_run_constructs_a_conditional_chain_only_when_its_premise_arrived(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    found = symbolic(optional.Checkout, models(optional))
    unproven = Proof.model_construct(
        program=optional.__name__,
        classes=models(optional),
        placed=tuple(found.placed),
        waiting=(),
        faulted=(),
    )
    request = optional.PlaceOrder.model_validate_json('{"sku": "tea"}')
    monkeypatch.setenv("PARTY__SAYS", '{"amount": "5", "coupon": "TEN"}')
    done = await ran(optional.Checkout, request, config(optional)(), unproven)
    assert done.route.reply.model_dump_json() == '{"coupon":"TEN"}'
    assert done.root.provenance[("Discount",)] == {
        "quoted": (("Quote", "heard"),),
        "coupon": (("Quote", "heard", "coupon"),),
    }
    assert done.root.provenance[("Discounted",)] == {"discount": (("Discount",),)}
    monkeypatch.setenv("PARTY__SAYS", '{"amount": "5"}')
    with pytest.raises(ValidationError) as refusal:
        await ran(optional.Checkout, request, config(optional)(), unproven)
    assert [(e["type"], e["loc"], e["msg"]) for e in refusal.value.errors()] == [
        (
            "missing",
            ("Discount", "coupon"),
            "no instance fills Discount.coupon at Discount, which holds Coupon",
        )
    ]


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_every_construction_records_the_concrete_occurrences_that_supplied_it() -> None:
    request = PlaceOrder.model_validate_json(ORDER)
    done = await ran(Checkout, request, config(PROGRAM)(), proven(PROGRAM))
    root = done.root
    cart_lines = root.collections[("request", "cart", "lines")]
    assert [s.path for s in cart_lines] == [
        ("request", "cart", "lines", "[0]"),
        ("request", "cart", "lines", "[1]"),
    ]
    assert [s.site for s in cart_lines] == [CART, CART]
    first, second = cart_lines
    assert first.provenance[(*CART, "LineTotal")] == {
        "left": (("request", "cart", "lines", "[0]", "Quote", "heard", "unit"),),
        "right": (("request", "cart", "lines", "[0]", "quantity"),),
    }
    assert second.provenance[(*CART, "LineTotal")] == {
        "left": (("request", "cart", "lines", "[1]", "Quote", "heard", "unit"),),
        "right": (("request", "cart", "lines", "[1]", "quantity"),),
    }
    assert first.owned[(*CART, "LineTotal")] is not second.owned[(*CART, "LineTotal")]
    assert first.owned[(*CART, "LineTotal")] == second.owned[(*CART, "LineTotal")]
    assert root.provenance[("CartTotal",)] == {
        "cart": (("request", "cart"),),
        "of": (
            ("request", "cart", "lines", "[0]", "LineTotal"),
            ("request", "cart", "lines", "[1]", "LineTotal"),
        ),
    }
    gift = root.collections[("request", "gifts", "lines")][0]
    assert first.provenance[(*CART, "Share")]["cart"] == (("CartTotal",),)
    assert gift.provenance[(*GIFT, "Share")]["cart"] == (("CartTotal",),)
    cart_share, gift_share = first.owned[(*CART, "Share")], gift.owned[(*GIFT, "Share")]
    assert isinstance(cart_share, Share)
    assert isinstance(gift_share, Share)
    assert cart_share.cart is gift_share.cart
    assert root.provenance[("Paid",)]["at"] == (("Paid", "at"),)
    assert root.provenance[("Screened",)] == {
        "order": (("request",),),
        "clear": (("Screen", "heard"),),
    }
    assert done.passes == 4


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_spans_name_each_action_occurrence_by_its_concrete_path() -> None:
    exporter = exporting()
    request = PlaceOrder.model_validate_json(ORDER)
    await answer(Checkout, request, config(PROGRAM)(), proven(PROGRAM))
    spans = sorted(
        (
            (s.name, dict(s.attributes or {}))
            for s in exporter.get_finished_spans()
            if s.name != "Checkout"
        ),
        key=lambda found: (found[0], str(found[1].get("tca.site", ""))),
    )
    assert spans == [
        (
            "Quote",
            {
                "tca.party": "Catalog",
                "tca.site": f"{site}.Quote",
                "tca.pass": 1,
                "tca.outcome": "heard",
                "tca.record": "Price",
                "tca.heard": f"{site}.Quote.heard",
            },
        )
        for site in sorted(
            (
                "request.cart.lines.[0]",
                "request.cart.lines.[1]",
                "request.gifts.lines.[0]",
                "request.pair.lines.[0]",
                "request.pair.lines.[1]",
                "request.solo.lines.[0]",
            )
        )
    ] + [
        (
            "Screen",
            {
                "tca.party": "Fraud",
                "tca.site": "Screen",
                "tca.pass": 1,
                "tca.outcome": "heard",
                "tca.record": "Clear",
                "tca.heard": "Screen.heard",
            },
        )
    ]
    (checkout,) = [s for s in exporter.get_finished_spans() if s.name == "Checkout"]
    assert dict(checkout.attributes or {}) == {"tca.request": "PlaceOrder", "tca.passes": 4}
    assert not any("2.50" in str(v) for _, a in spans for v in a.values())


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_a_failing_action_is_noted_with_its_occurrence_and_its_span_records_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exporter = exporting()

    async def failing(self: Quote) -> program.Price:
        """A catalog that cannot price a mug."""
        if self.line.sku.root == "mug":
            down = ConnectionError("no mugs")
            raise down
        return program.Price.model_validate({"price": Decimal("2.50")})

    monkeypatch.setattr(Quote, "perform", failing)
    request = PlaceOrder.model_validate_json(ORDER)
    with pytest.raises(ExceptionGroup) as group:
        await answer(Checkout, request, config(PROGRAM)(), proven(PROGRAM))
    notes = sorted(n for e in group.value.exceptions for n in getattr(e, "__notes__", []))
    assert notes == ["at request.gifts.lines.[0].Quote", "at request.pair.lines.[1].Quote"]
    failed = sorted(
        str((s.attributes or {})["tca.site"])
        for s in exporter.get_finished_spans()
        if s.name == "Quote" and s.status.status_code == StatusCode.ERROR
    )
    assert failed == ["request.gifts.lines.[0].Quote", "request.pair.lines.[1].Quote"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_a_stall_names_the_occurrence_that_did_not_hold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PARTY__SAYS", '{"amount": "25"}')
    request = stalls.Elements.model_validate_json('{"each": [{"name": "a"}, {"name": "a"}]}')
    with pytest.raises(ValidationError) as refusal:
        await answer(stalls.Operation, request, config(stalls)(), proven(stalls))
    assert sorted((e["type"], e["loc"], e["msg"]) for e in refusal.value.errors()) == [
        (
            "relation",
            ("Low",),
            "Low at request.each.[0].Low did not hold: value Amount > bound Limit",
        ),
        (
            "relation",
            ("Low",),
            "Low at request.each.[1].Low did not hold: value Amount > bound Limit",
        ),
    ]


def test_a_refusal_that_is_not_a_refutation_is_titled_with_the_occurrence() -> None:
    placed = Placement(
        route=fixed.Checkout,
        cls=fixed.Both,
        scope=(),
        singles={"cart": (("request", "cart"),)},
        freshly={},
        collections={},
    )
    given: dict[str, BaseModel | tuple[BaseModel, ...]] = {
        "cart": fixed.Cart(lines=()),
        "totals": (),
    }
    with pytest.raises(ValidationError) as refusal:
        construct(placed, given, ("Both",))
    assert refusal.value.title == "Both at Both"
    assert [(e["type"], e["loc"]) for e in refusal.value.errors()] == [
        ("missing", ("totals", 0)),
        ("missing", ("totals", 1)),
    ]
