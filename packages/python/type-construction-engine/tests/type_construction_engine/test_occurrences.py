"""Construction from occurrences, over the program ``occurrences.py`` is: one class at many
sites, separate collections of one element class, carriers that say which collection, a fixed
pair and a solo line, a record heard as one of two, a child holding its parent's aggregate, and
the same proof whatever order the classes are declared in."""

import sys
from decimal import Decimal
from pathlib import Path
from types import ModuleType

import pytest
from pydantic import ValidationError

from type_construction.engine import Placement, answer, config, proven

from . import fixed, optional
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
