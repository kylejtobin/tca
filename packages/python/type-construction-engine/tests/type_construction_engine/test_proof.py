"""The occurrence-bound proof against adversarial programs: alternatives at one field proven
never both available only from the actual references bound there, constructions proven
impossible only from their joint premises, and every conclusion checked against what Pydantic
constructs and the run observes. The base program here is one route valuing each element of a
request with a party that answers per element; each test adds the classes its counterexample
needs and reads the program as the module they make."""

import json
from collections.abc import AsyncGenerator, Callable, Iterable
from contextlib import asynccontextmanager
from decimal import Decimal
from pathlib import Path
from types import ModuleType
from typing import Annotated, Literal, override

import pytest
from pydantic import AfterValidator, BaseModel, Field, PrivateAttr, ValidationError

from type_construction.engine import (
    Available,
    Blocked,
    Clash,
    Collected,
    Constructed,
    ConstructedRef,
    Construction,
    Exclusion,
    HeardRef,
    InputRef,
    Joint,
    Proof,
    Ref,
    Refuted,
    Run,
    Scope,
    Unfilled,
    Unknown,
    clash,
    comparisons,
    conditions,
    config,
    exclusions,
    joint,
    models,
    performers,
    proven,
    ran,
    resolve,
    scopes,
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
    Equal,
    Fact,
    Json,
    Only,
    Record,
    Reply,
    Request,
    Route,
    Scalar,
    Selection,
    Setting,
    Shape,
    Under,
    Value,
)

from . import occurrences, stalls, test_engine


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
    """The JSON object from element name to amount a stand-in party answers from."""


class Party(Connection):
    """A party that answers about each element from the line the deployment gave it."""

    says: Said

    @override
    @asynccontextmanager
    async def open(self) -> AsyncGenerator[None]:
        yield


class Amount(Scalar[Decimal]):
    """What the party says an element is worth."""

    root: Decimal = Field(gt=0)


class Heard(Record):
    """What the party says about an element."""

    amount: Amount


class Ask(Action[Party, Heard]):
    """Ask the party about one element: it answers the amount under the element's name."""

    element: Element

    @override
    async def perform(self) -> Json:
        amounts: dict[str, str] = json.loads(self.party.says.root)
        return Json(json.dumps({"amount": amounts[self.element.name.root]}))


class Limit(Scalar[Decimal]):
    """The amount at or under which an element is low: 10 unless another is given."""

    root: Decimal = Decimal(10)


class Low(AtMost[Amount, Limit]):
    """An amount at or under the limit."""


class High(Beyond[Amount, Limit]):
    """An amount over the limit."""


class Cheap(Fact):
    """An element the party valued low."""

    element: Element
    low: Low


class Dear(Fact):
    """An element the party valued high."""

    element: Element
    high: High


class Deployment(Config):
    """The one party."""

    party: Party


CORE: tuple[type[object], ...] = (Name, Element, Elements, Said, Party, Amount, Heard, Ask, Limit)
"""The classes every program here is made from: the request, the party and what it says."""

BASE: tuple[type[object], ...] = (*CORE, Low, High, Cheap, Dear, Deployment)
"""The core with the two relations and the two conclusions they make."""

ELEMENT = ("request", "each", "[]")
"""The site of each element's scope."""

AMOUNT = (*ELEMENT, "Ask", "heard", "amount")
"""The site of the amount the party said about an element."""


def program_of(*members: type[object]) -> ModuleType:
    """A program made of classes defined in this module: the module the engine reads."""
    module = ModuleType(__name__)
    for member in members:
        setattr(module, member.__name__, member)
    return module


def faults_of(program: ModuleType) -> dict[tuple[str, tuple[object, ...]], str]:
    """Every fault the proof refuses a program with, by type and location, with its message."""
    with pytest.raises(ValidationError) as refusal:
        proven(program)
    return {(e["type"], tuple(e["loc"])): e["msg"] for e in refusal.value.errors()}


def unproven[Q: Request, A: Reply[Fact]](program: ModuleType, route: type[Route[Q, A]]) -> Proof:
    """A program's constructions and exclusions as a ``Proof`` the validator did not see: how a
    run is driven over a program the proof refuses, to observe what the proof foresaw."""
    found = symbolic(route, models(program))
    return Proof.model_construct(
        program=program.__name__,
        classes=models(program),
        constructions=tuple(found.constructions),
        waiting=(),
        faulted=(),
        exclusions=exclusions(found.constructions),
        existences=(),
    )


def placed(
    proof: Proof, route: type[BaseModel]
) -> dict[tuple[type[object], tuple[str, ...]], Construction]:
    """Every construction of a route, by class and scope template."""
    return {(c.cls, c.scope): c for c in proof.constructs(route)}


def by_class(proof: Proof) -> dict[type[object], Construction]:
    """Every construction of a proof by its class, for a program constructing each class once."""
    return {c.cls: c for c in proof.constructions}


def exclusion_at(proof: Proof, cls: type[object], name: str) -> Exclusion:
    """The one exclusion the proof concluded at a field of a class."""
    (found,) = (e for e in proof.exclusions if e.construction.cls is cls and e.field == name)
    return found


@pytest.fixture
def party(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Callable[[dict[str, str]], None]:
    """The party's amounts per element name in the environment; no ``.env``."""
    monkeypatch.chdir(tmp_path)

    def saying(amounts: dict[str, str]) -> None:
        monkeypatch.setenv("PARTY__SAYS", json.dumps(amounts))

    return saying


def requested(*names: str) -> Elements:
    """A request of elements with the given names."""
    return Elements.model_validate_json(json.dumps({"each": [{"name": n} for n in names]}))


def agreeing(proof: Proof, root: Scope) -> None:
    """The run's observed state against the proof's established conclusions: nowhere are two
    alternatives the proof excluded both available from the scope their field resolves them
    in, and nothing the proof contradicted was constructed."""
    for e in proof.exclusions:
        if not e.established:
            continue
        template = e.construction.scope
        if not isinstance(e.left, Collected) and e.field in e.construction.collections:
            template = e.left.scope
        for scope in scopes(root):
            if scope.site != template:
                continue
            both = [s for s in (e.left, e.right) if present_in(s, scope)]
            assert len(both) <= 1, (e.construction, e.field, scope.path)
    for x in proof.existences:
        if x.contradicted:
            assert not any(
                isinstance(s.made.get(x.construction), Constructed) for s in scopes(root)
            ), x.construction


def present_in(source: Ref | Collected, scope: Scope) -> bool:
    """Whether a source is available from a scope: a reference that resolves to evidence; a
    collection whose holder does and that the scope sees."""
    if isinstance(source, Collected):
        return isinstance(resolve(source.holder, scope), Available) and (
            scope.collection(source.key) is not None
        )
    return isinstance(resolve(source, scope), Available)


def made_in(root: Scope, cls: type[object]) -> dict[tuple[str, ...], Constructed | Refuted]:
    """What each scope made of each construction of a class, by the occurrence's concrete
    path."""
    return {
        (*s.path, c.cls.__name__): m
        for s in scopes(root)
        for c, m in s.made.items()
        if c.cls is cls
    }


def sites(sources: Iterable[Ref | Collected]) -> set[tuple[str, ...]]:
    """The declared sites of sources."""
    return {s.site for s in sources}


def classed(source: Ref | Collected) -> type[object]:
    """The class a source stands for: a reference's, or a collection's holder's."""
    return source.holder.cls if isinstance(source, Collected) else source.cls


def over(cls: type[BaseModel], value: Ref, bound: Ref) -> ConstructedRef:
    """A reference to a relation constructed in an element's scope over two references."""
    return ConstructedRef(
        Construction(Operation, cls, ELEMENT, {"value": (value,), "bound": (bound,)})
    )


# --- 1. two occurrences of one class in unrelated scopes --------------------------------------


def test_two_occurrences_of_one_action_in_unrelated_scopes_are_two_sources() -> None:
    proof = proven(occurrences)
    found = placed(proof, occurrences.Checkout)
    assert len([c for (cls, _), c in found.items() if cls is occurrences.Quote]) == 5
    assert not any(
        occurrences.Price in (classed(e.left), classed(e.right)) for e in proof.exclusions
    )
    screen = found[occurrences.Screen, ()]
    clear = HeardRef(screen, occurrences.Clear, (), occurrences.Clear)
    flagged = HeardRef(screen, occurrences.Flagged, (), occurrences.Flagged)
    reply = exclusion_at(proof, occurrences.Checkout, "reply")
    assert reply.established
    assert reply.joint.clashes == (Clash("heard", (clear, flagged)),)
    another = Construction(occurrences.Checkout, occurrences.Screen, (), dict(screen.premises))
    elsewhere = HeardRef(another, occurrences.Flagged, (), occurrences.Flagged)
    assert joint((clear, flagged)).impossible
    assert not joint((clear, elsewhere)).impossible
    reason = HeardRef(screen, occurrences.Flagged, ("reason",), occurrences.Reason)
    assert not joint((flagged, reason)).impossible


# --- 2, 7. competing producers; a refuted condition is not its opposite -----------------------


class Valued(Fact):
    """An element valued one way or the other."""

    element: Element
    which: Cheap | Dear


class Concluded(Fact):
    """Every element valued."""

    valued: tuple[Valued, ...]


class Answered(Reply[Concluded]):
    """What leaves."""


class Operation(Route[Elements, Answered]):
    """Value each element."""


TOLD_APART = program_of(*BASE, Valued, Concluded, Answered, Operation)
"""The sound program: two conclusions a relation and its complement tell apart."""


class Other(Fact):
    """An element, and nothing that tells it from a cheap one."""

    element: Element


class Loose(Fact):
    """Cheap, or merely an element: nothing excludes the other."""

    element: Element
    which: Cheap | Other


class LooseEnds(Fact):
    """Every element, loosely."""

    valued: tuple[Loose, ...]


class LooseReply(Reply[LooseEnds]):
    """What leaves."""


class LooseOperation(Route[Elements, LooseReply]):
    """Value each element loosely."""


LOOSE = program_of(
    *CORE, Low, Cheap, Deployment, Other, Loose, LooseEnds, LooseReply, LooseOperation
)
"""The unsound program: a member with no condition beside one with a condition."""


def test_competing_producers_are_accepted_only_where_both_are_never_available() -> None:
    proof = proven(TOLD_APART)
    which = exclusion_at(proof, Valued, "which")
    found = placed(proof, Operation)
    assert (which.left, which.right) == (
        ConstructedRef(found[Cheap, ELEMENT]),
        ConstructedRef(found[Dear, ELEMENT]),
    )
    assert which.established
    assert [c.why for c in which.joint.clashes] == ["ordering"]
    faults = faults_of(LOOSE)
    assert set(faults) == {("ambiguous", ("Loose", "which"))}
    assert faults["ambiguous", ("Loose", "which")] == (
        "Loose.which at request.each.[] may hold both Cheap at request.each.[].Cheap and Other at"
        " request.each.[].Other; with Low at request.each.[].Low holding, nothing excludes either"
    )


@pytest.mark.asyncio
async def test_the_run_finds_both_where_the_proof_found_them_both_available(
    party: Callable[[dict[str, str]], None],
) -> None:
    proof = unproven(LOOSE, LooseOperation)
    which = exclusion_at(proof, Loose, "which")
    assert not which.established
    (cheap, other) = which.left, which.right
    party({"a": "5"})
    done = await ran(LooseOperation, requested("a"), config(LOOSE)(), proof)
    assert isinstance(done, Run)
    (valued,) = done.route.reply.of.valued
    (element,) = (s for s in scopes(done.root) if s.site == ELEMENT)
    assert type(valued.which) is Other
    assert present_in(cheap, element)
    assert present_in(other, element)
    assert done.passes == 2
    claimed = Exclusion(which.construction, which.field, cheap, other, Joint((cheap, other), ()))
    assert claimed.established
    with pytest.raises(AssertionError):
        agreeing(Proof.model_construct(exclusions=(claimed,), existences=()), done.root)
    party({"b": "50"})
    done = await ran(LooseOperation, requested("b"), config(LOOSE)(), proof)
    assert isinstance(done, Run)
    (valued,) = done.route.reply.of.valued
    assert type(valued.which) is Other
    (low,) = made_in(done.root, Low).values()
    assert isinstance(low, Refuted)
    assert made_in(done.root, Cheap) == {}


# --- 3. contradictory shared conditions ------------------------------------------------------


class Both(Fact):
    """An element valued low and high: two conditions over one amount and one limit that never
    hold together, each satisfiable alone."""

    element: Element
    low: Low
    high: High


class Doubled(Fact):
    """Every element, valued both ways."""

    both: tuple[Both, ...]


class DoubledReply(Reply[Doubled]):
    """What leaves."""


class DoubledOperation(Route[Elements, DoubledReply]):
    """Value each element both ways."""


CONTRADICTORY = program_of(
    *CORE, Low, High, Deployment, Both, Doubled, DoubledReply, DoubledOperation
)
"""A program whose fact holds two relations that contradict over the same operands."""


@pytest.mark.asyncio
async def test_premises_satisfiable_alone_and_contradictory_together_never_construct(
    party: Callable[[dict[str, str]], None],
) -> None:
    faults = faults_of(CONTRADICTORY)
    assert faults == {
        ("never", (*ELEMENT, "Both")): (
            "Both at request.each.[].Both never constructs: High at request.each.[].High and"
            " Low at request.each.[].Low admit no ordering in common over the same operands"
        )
    }
    proof = unproven(CONTRADICTORY, DoubledOperation)
    found = by_class(proof)
    assert joint((ConstructedRef(found[Both]),)).impossible
    assert not joint((ConstructedRef(found[Low]),)).impossible
    assert not joint((ConstructedRef(found[High]),)).impossible
    for amount in ("5", "10", "50"):
        party({"a": amount})
        done = await ran(DoubledOperation, requested("a"), config(CONTRADICTORY)(), proof)
        assert isinstance(done, Blocked)
        assert made_in(done.occurrence.scope, Both) == {}
        (cause,) = done.causes
        assert cause.occurrence.construction.cls in {Low, High}


# --- 4. shared sources, and a success the class-global proof refused ---------------------------


def test_shared_source_references_keep_their_identity_and_correlate_their_values() -> None:
    amount = HeardRef(Construction(Operation, Ask, ELEMENT, {}), Heard, ("amount",), Amount)
    limit = InputRef((), ("Limit",), Limit)
    given = InputRef((), ("request", "limit"), Limit)
    low, high = over(Low, amount, limit), over(High, amount, limit)
    other = over(High, amount, given)
    assert clash(frozenset({low, high, amount, limit})) == Clash("ordering", (high, low))
    assert clash(frozenset({low, other, amount, limit, given})) is None
    assert joint((low, high)).impossible
    assert not joint((low, other)).impossible


class Ceiling(Scalar[Decimal]):
    """The amount over which an element is dear: 20 unless another is given."""

    root: Decimal = Decimal(20)


class BelowLimit(Under[Amount, Limit]):
    """An amount under the limit."""


class AboveCeiling(Beyond[Amount, Ceiling]):
    """An amount over the ceiling."""


class Bargain(Fact):
    """An element under the limit."""

    element: Element
    under: BelowLimit


class Luxury(Fact):
    """An element over the ceiling."""

    element: Element
    over: AboveCeiling


class Tiered(Fact):
    """A bargain or a luxury: told apart only by the two constants' defaults at their sites."""

    element: Element
    which: Bargain | Luxury


class Tiers(Fact):
    """Every element tiered."""

    tiered: tuple[Tiered, ...]


class TiersReply(Reply[Tiers]):
    """What leaves."""


class TierOperation(Route[Elements, TiersReply]):
    """Tier each element."""


TIERED = program_of(
    *CORE,
    Deployment,
    Ceiling,
    BelowLimit,
    AboveCeiling,
    Bargain,
    Luxury,
    Tiered,
    Tiers,
    TiersReply,
    TierOperation,
)
"""A sound program the class-global proof refused: the two relations are over two constants
whose classes admit any amount, and only the constants' own sites supply 10 and 20."""


@pytest.mark.asyncio
async def test_two_constants_defaults_at_their_sites_tell_two_relations_apart(
    party: Callable[[dict[str, str]], None],
) -> None:
    proof = proven(TIERED)
    which = exclusion_at(proof, Tiered, "which")
    assert which.established
    (why,) = which.joint.clashes
    assert why.why == "bounds"
    assert sites(why.among) == {
        (*ELEMENT, "BelowLimit"),
        (*ELEMENT, "AboveCeiling"),
        AMOUNT,
        ("Limit",),
        ("Ceiling",),
    }
    for amount, expected in (("5", Bargain), ("25", Luxury)):
        party({"a": amount})
        done = await ran(TierOperation, requested("a"), config(TIERED)(), proof)
        assert isinstance(done, Run)
        (tiered,) = done.route.reply.of.tiered
        assert type(tiered.which) is expected
        agreeing(proof, done.root)
    party({"a": "15"})
    blocked = await ran(TierOperation, requested("a"), config(TIERED)(), proof)
    assert isinstance(blocked, Blocked)
    assert {c.occurrence.construction.cls for c in blocked.causes} == {BelowLimit, AboveCeiling}
    agreeing(proof, blocked.occurrence.scope)


# --- 5. repeated elements keep their own evidence -------------------------------------------


@pytest.mark.asyncio
async def test_different_elements_cannot_exchange_evidence(
    party: Callable[[dict[str, str]], None],
) -> None:
    proof = proven(TOLD_APART)
    found = placed(proof, Operation)
    (world,) = joint((ConstructedRef(found[Cheap, ELEMENT]),)).open
    assert all(isinstance(r, Collected) or r.scope in {(), ELEMENT} for r in world)
    (collection,) = joint((ConstructedRef(found[Concluded, ()]),)).open
    assert sites(collection) == {("Concluded",), ("request",), ("request", "each")}
    party({"a": "5", "b": "50"})
    done = await ran(Operation, requested("a", "b"), config(TOLD_APART)(), proof)
    assert isinstance(done, Run)
    first, second = done.route.reply.of.valued
    assert (type(first.which), type(second.which)) == (Cheap, Dear)
    assert set(made_in(done.root, Cheap)) == {("request", "each", "[0]", "Cheap")}
    assert set(made_in(done.root, Dear)) == {("request", "each", "[1]", "Dear")}
    assert isinstance(made_in(done.root, High)["request", "each", "[0]", "High"], Refuted)
    assert isinstance(made_in(done.root, Low)["request", "each", "[1]", "Low"], Refuted)
    agreeing(proof, done.root)


# --- 6. fixed, variable and empty collections ---------------------------------------------


class Price(Scalar[Decimal]):
    """What a line costs."""

    root: Decimal = Field(gt=0)


class Line(Value):
    """One priced line; the same value wherever an order holds lines."""

    price: Price


class Cart(Value):
    """Any number of lines."""

    lines: tuple[Line, ...]


class Pair(Value):
    """Exactly two lines."""

    lines: tuple[Line, Line]


class Solo(Value):
    """Exactly one line."""

    lines: tuple[Line]


class Order(Request):
    """What arrives: a cart, a pair and a solo line."""

    cart: Cart
    pair: Pair
    solo: Solo


class SoloPrice(Only[Price]):
    """The solo line's price: the one there is."""

    solo: Solo


class SeveralPrices(Selection[Price]):
    """At least two of the cart's prices."""

    of: Annotated[tuple[Price, ...], Shape()] = Field(min_length=2)
    cart: Cart


class PairPrices(Fact):
    """The pair's two prices, by position."""

    pair: Pair
    prices: tuple[Price, Price]


class CartPrices(Fact):
    """The cart's prices, any number, none included."""

    cart: Cart
    prices: tuple[Price, ...]


class Picked(Fact):
    """The solo price, or several of the cart's: two selections over two collections, which no
    count tells apart."""

    which: SoloPrice | SeveralPrices
    pair: PairPrices
    cart: CartPrices


class PicksReply(Reply[Picked]):
    """What leaves."""


class PickOperation(Route[Order, PicksReply]):
    """Pick among lines."""


class Shop(Config):
    """No party."""


PICKED = program_of(
    Price,
    Line,
    Cart,
    Pair,
    Solo,
    Order,
    SoloPrice,
    SeveralPrices,
    PairPrices,
    CartPrices,
    Picked,
    PicksReply,
    PickOperation,
    Shop,
)
"""Two selections over two collections of one element class, which the class-global proof held
exclusive by their counts alone."""


class Lone(Only[Price]):
    """The one price of the pair: a count of one over two positions."""

    pair: Pair


class Lonely(Fact):
    """The pair's one price, which the pair never has."""

    lone: Lone


class LonelyReply(Reply[Lonely]):
    """What leaves."""


class LoneOperation(Route[Order, LonelyReply]):
    """Select one of a pair."""


LONELY = program_of(
    Price, Line, Cart, Pair, Solo, Order, Lone, Lonely, LonelyReply, LoneOperation, Shop
)
"""A selection of one over a collection of two positions."""

CART = ("request", "cart", "lines", "[]")
PAIR = (("request", "pair", "lines", "[0]"), ("request", "pair", "lines", "[1]"))
SOLO = ("request", "solo", "lines", "[0]")
"""The sites of the line scopes."""


def ordered_lines(cart: int) -> Order:
    """An order with a cart of so many lines, a pair and a solo line, each line priced 1."""
    line = {"price": "1"}
    return Order.model_validate_json(
        json.dumps(
            {
                "cart": {"lines": [line] * cart},
                "pair": {"lines": [line, line]},
                "solo": {"lines": [line]},
            }
        )
    )


@pytest.mark.asyncio
async def test_collections_keep_their_cardinality_and_their_own_source(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    proof = unproven(PICKED, PickOperation)
    found = by_class(proof)
    (pair,) = joint((ConstructedRef(found[PairPrices]),)).open
    assert sites(pair) == {
        ("PairPrices",),
        ("request", "pair"),
        ("request", "pair", "lines"),
        *((*p, "price") for p in PAIR),
    }
    (solo,) = joint((ConstructedRef(found[SoloPrice]),)).open
    assert sites(solo) == {
        ("SoloPrice",),
        ("request", "solo"),
        ("request", "solo", "lines"),
        (*SOLO, "price"),
    }
    (cart,) = joint((ConstructedRef(found[CartPrices]),)).open
    assert sites(cart) == {("CartPrices",), ("request", "cart"), ("request", "cart", "lines")}
    (several,) = joint((ConstructedRef(found[SeveralPrices]),)).open
    assert sites(several) == {
        ("SeveralPrices",),
        ("request", "cart"),
        ("request", "cart", "lines"),
        (*CART, "price"),
    }
    assert set(faults_of(PICKED)) == {("ambiguous", ("Picked", "which"))}
    with pytest.raises(ValidationError) as both:
        await ran(PickOperation, ordered_lines(2), Shop(), proof)
    assert [e["msg"] for e in both.value.errors()] == [
        "Picked.which found 2 instances where the proof bound one"
    ]
    for lines in (0, 1):
        done = await ran(PickOperation, ordered_lines(lines), Shop(), proof)
        assert isinstance(done, Run)
        assert type(done.route.reply.of.which) is SoloPrice
        assert len(done.route.reply.of.cart.prices) == lines
        (several_made,) = made_in(done.root, SeveralPrices).values()
        assert isinstance(several_made, Refuted)
    assert faults_of(LONELY) == {
        ("never", ("Lone",)): "Lone at Lone never constructs: Lone at Lone admits no count of 2"
        " elements"
    }
    lonely = unproven(LONELY, LoneOperation)
    blocked = await ran(LoneOperation, ordered_lines(1), Shop(), lonely)
    assert isinstance(blocked, Blocked)
    (cause,) = blocked.causes
    assert cause.occurrence.construction.cls is Lone
    agreeing(lonely, blocked.occurrence.scope)


def test_two_selections_over_one_collection_with_no_count_in_common_are_exclusive() -> None:
    cart = InputRef((), ("request", "cart"), Cart)
    solo = InputRef((), ("request", "solo"), Solo)
    price = InputRef(CART, ("price",), Price)
    lines = Collected(cart, "lines", (price,), None)
    one = ConstructedRef(
        Construction(PickOperation, SoloPrice, (), {"solo": (solo,)}, {"of": (lines,)})
    )
    many = ConstructedRef(
        Construction(PickOperation, SeveralPrices, (), {"cart": (cart,)}, {"of": (lines,)})
    )
    assert clash(frozenset({one, many, cart, solo, lines})) == Clash("count", (many, one))
    assert joint((one, many)).impossible
    other = Collected(solo, "lines", (price,), None)
    apart = ConstructedRef(
        Construction(PickOperation, SoloPrice, (), {"solo": (solo,)}, {"of": (other,)})
    )
    assert clash(frozenset({apart, many, cart, solo, lines, other})) is None
    assert not joint((apart, many)).impossible


# --- 8. optional evidence stays conditional -----------------------------------------------


class Coupon(Scalar[str]):
    """A code the party may offer."""

    root: str = Field(min_length=1)


class Quoted(Record):
    """What the party says: the amount, and perhaps a coupon."""

    amount: Amount
    coupon: Coupon | None = None


class AskQuoted(Action[Party, Quoted]):
    """Ask the party about one element, which may offer a coupon."""

    element: Element

    @override
    async def perform(self) -> Json:
        return Json(self.party.says.root)


class Discount(Fact):
    """An element with a coupon: exists only when the party offered one."""

    element: Element
    coupon: Coupon


class Plain(Fact):
    """An element as quoted, coupon or not."""

    element: Element
    quoted: Quoted


class Offered(Fact):
    """Discounted, or plain: the coupon's absence is not a condition."""

    element: Element
    which: Discount | Plain


class Offers(Fact):
    """Every element, offered."""

    offered: tuple[Offered, ...]


class OfferReply(Reply[Offers]):
    """What leaves."""


class Offer(Route[Elements, OfferReply]):
    """Quote each element with or without a coupon."""


OFFERED = program_of(
    Name,
    Element,
    Elements,
    Said,
    Party,
    Amount,
    Coupon,
    Quoted,
    AskQuoted,
    Discount,
    Plain,
    Offered,
    Offers,
    OfferReply,
    Offer,
    Deployment,
)
"""A route choosing between a conclusion that needs an optional member and one that does not."""


def test_optional_evidence_cannot_become_guaranteed_or_exclusive() -> None:
    faults = faults_of(OFFERED)
    assert set(faults) == {("ambiguous", ("Offered", "which"))}
    proof = unproven(OFFERED, Offer)
    found = by_class(proof)
    coupon = (*ELEMENT, "AskQuoted", "heard", "coupon")
    (coupon_ref,) = found[Discount].premises["coupon"]
    assert isinstance(coupon_ref, HeardRef)
    assert coupon_ref.because == (coupon,)
    assert conditions(found[Discount]) == (coupon,)
    assert conditions(found[Offered]) == ()
    assert conditions(found[Plain]) == ()
    assert conditions(found[Offer]) == ()
    assert not exclusion_at(proof, Offered, "which").established
    assert not joint((ConstructedRef(found[Discount]),)).impossible
    assert not joint((ConstructedRef(found[Plain]),)).impossible
    only = program_of(
        *(c for c in OFFERED.__dict__.values() if isinstance(c, type) and c is not Plain)
    )
    assert faults_of(only) == {
        ("conditional", ("Offer",)): (
            "Offer answers only when request.each.[].AskQuoted.heard.coupon arrives, and what"
            " declares it admits its absence; an absence the business concludes from is a class"
        )
    }
    (route,) = (c for c in unproven(only, Offer).constructions if c.cls is Offer)
    assert conditions(route) == (coupon,)


# --- 9. alternatives keep separate assumptions ----------------------------------------------


class Mixed(Fact):
    """An element with one of two complementary relations: each world of it holds one."""

    element: Element
    tier: Low | High


class Mingled(Fact):
    """Mixed, or merely an element: the two ways Mixed exists must each be weighed against the
    element alone, never merged into one world holding both relations."""

    element: Element
    which: Mixed | Other


class Mingling(Fact):
    """Every element, mingled."""

    mingled: tuple[Mingled, ...]


class MingledReply(Reply[Mingling]):
    """What leaves."""


class MingleOperation(Route[Elements, MingledReply]):
    """Mingle each element."""


MINGLED = program_of(
    *CORE, Low, High, Deployment, Other, Mixed, Mingled, Mingling, MingledReply, MingleOperation
)
"""A program whose unsound acceptance would come from merging a union's alternatives."""


def test_alternative_branches_keep_their_separate_assumptions() -> None:
    faults = faults_of(MINGLED)
    assert set(faults) == {("ambiguous", ("Mingled", "which"))}
    proof = unproven(MINGLED, MingleOperation)
    found = by_class(proof)
    low, high = ConstructedRef(found[Low]), ConstructedRef(found[High])
    assert found[Mixed].premises["tier"] == (low, high)
    which = exclusion_at(proof, Mingled, "which").joint
    (world,) = which.open
    assert which.ways == ((world, None),)
    assert (low in world, high in world) == (True, False)
    assert clash(world | {high}) == Clash("ordering", (high, low))
    assert exclusion_at(proof, Mixed, "tier").established
    assert not joint((ConstructedRef(found[Mixed]),)).impossible


# --- 10. unknown validators and ranges discharge nothing -----------------------------------


class Odd(AtMost[Amount, Limit]):
    """A relation whose ordering another validator passes through: the proof cannot know what
    the field outputs, so the comparison admits nothing it can read."""

    ordering: Annotated[
        Literal[-1, 0], Comparison(("value", "bound")), AfterValidator(lambda v: v)
    ] = Field(default=COMPUTED, exclude=True, repr=False)


def test_an_unknown_validator_discharges_no_obligation() -> None:
    ((compared, admitted),) = comparisons(Odd)
    assert compared == Comparison(("value", "bound"))
    assert isinstance(admitted, Unknown)
    assert Odd(value=Amount(Decimal(5)), bound=Limit()).ordering == -1
    amount = HeardRef(Construction(Operation, Ask, ELEMENT, {}), Heard, ("amount",), Amount)
    limit = InputRef((), ("Limit",), Limit)
    odd, high, low = over(Odd, amount, limit), over(High, amount, limit), over(Low, amount, limit)
    assert joint((low, high)).impossible
    assert not joint((odd, high)).impossible
    assert clash(frozenset({odd, high, amount, limit})) is None


# --- 11. the proof reads declarations, not implementations --------------------------------


class Remembering(Connection):
    """A party of another implementation: a client in a private attribute, opened and closed."""

    says: Said
    _client: list[str] = PrivateAttr(default_factory=list[str])

    @override
    @asynccontextmanager
    async def open(self) -> AsyncGenerator[None]:
        self._client.append("open")
        try:
            yield
        finally:
            self._client.append("closed")


class AskRemembering(Action[Remembering, Heard]):
    """The same question toward the other implementation, answered another way."""

    element: Element

    @override
    async def perform(self) -> Json:
        return Json(json.dumps({"amount": "1", "asked": self.element.name.root}))


class DeploymentRemembering(Config):
    """The other party."""

    party: Remembering


REMEMBERED = program_of(
    Name,
    Element,
    Elements,
    Said,
    Remembering,
    Amount,
    Heard,
    AskRemembering,
    Limit,
    Low,
    High,
    Cheap,
    Dear,
    DeploymentRemembering,
    Valued,
    Concluded,
    Answered,
    Operation,
)
"""The sound program over the other implementation."""

RENAMED: dict[type[object], type[object]] = {
    Remembering: Party,
    AskRemembering: Ask,
    DeploymentRemembering: Deployment,
}
"""Each class of the other implementation as the one it stands in for."""


def test_equivalent_routes_over_different_connection_implementations_prove_alike() -> None:
    def named(cls: type[object]) -> str:
        return RENAMED.get(cls, cls).__name__

    by_name = {c.__name__: c for c in RENAMED}

    def site_of(source: Ref | Collected) -> tuple[str, ...]:
        return tuple(named(by_name[s]) if s in by_name else s for s in source.site)

    def projected(proof: Proof) -> list[object]:
        return [
            *(
                (
                    named(e.construction.cls),
                    e.construction.scope,
                    e.field,
                    named(classed(e.left)),
                    named(classed(e.right)),
                    e.established,
                    [(c.why, tuple(site_of(r) for r in c.among)) for c in e.joint.clashes],
                    [tuple(sorted(site_of(r) for r in w)) for w in e.joint.open],
                )
                for e in proof.exclusions
            ),
            *(
                (named(x.construction.cls), x.construction.scope, x.contradicted, len(x.joint.ways))
                for x in proof.existences
            ),
        ]

    first, second = proven(TOLD_APART), proven(REMEMBERED)
    assert projected(first) == projected(second)
    assert [tuple(map(named, (c.cls,))) for c in first.constructions] == [
        tuple(map(named, (c.cls,))) for c in second.constructions
    ]
    assert any(e.established for e in first.exclusions)


# --- 12. the run never contradicts the proof -----------------------------------------------


@pytest.mark.asyncio
async def test_bounded_runs_never_contradict_established_exclusions(
    party: Callable[[dict[str, str]], None],
) -> None:
    proof = proven(TOLD_APART)
    assert all(e.established for e in proof.exclusions)
    assert not any(x.contradicted for x in proof.existences)
    amounts = ("1", "10", "10.01", "100")
    for first in amounts:
        for second in amounts:
            party({"a": first, "b": second})
            for names in ((), ("a",), ("a", "b")):
                done = await ran(Operation, requested(*names), config(TOLD_APART)(), proof)
                assert isinstance(done, Run)
                agreeing(proof, done.root)
                assert [type(v.which) for v in done.route.reply.of.valued] == [
                    Cheap if Decimal(a) <= 10 else Dear for a in (first, second)[: len(names)]
                ]


def test_an_action_is_decided_only_by_its_own_premises_excluding_the_other_branch() -> None:
    proof = proven(test_engine.PROGRAM)
    found = placed(proof, test_engine.Operation)
    valued = exclusion_at(proof, test_engine.Concluded, "valued")
    assert valued.established
    cheap, dear = valued.left, valued.right
    only_dear = [a for a in performers(dear) if a not in performers(cheap)]
    assert [a.cls for a in only_dear] == [test_engine.Notify]
    assert joint((ConstructedRef(found[test_engine.Notify, ELEMENT]), cheap)).impossible
    assert [a.cls for a in performers(cheap) if a not in performers(dear)] == []


def test_the_proof_keeps_each_conclusion_with_its_ways_and_clashes() -> None:
    proof = proven(TOLD_APART)
    assert {e.construction.cls for e in proof.exclusions} == {Valued}
    assert {x.construction for x in proof.existences} == set(proof.constructions)
    which = exclusion_at(proof, Valued, "which")
    assert which.joint.refs == (which.left, which.right)
    ((world, why),) = which.joint.ways
    assert why is not None
    assert sites(world) >= {
        (*ELEMENT, "Cheap"),
        (*ELEMENT, "Dear"),
        (*ELEMENT, "Low"),
        (*ELEMENT, "High"),
        (*ELEMENT, "Ask"),
        AMOUNT,
        ("Limit",),
        ("deployment", "party"),
    }
    assert which.joint.open == ()


# --- 3, 8. candidates of one class at two sites, and competing collections -------------------


class Yes(Record):
    """The party's yes about an element, with an amount."""

    status: Literal["yes"]
    amount: Amount
    prices: tuple[Price, ...]


class No(Record):
    """The party's no about an element, with an amount of its own."""

    status: Literal["no"]
    amount: Amount
    prices: tuple[Price, ...]


class Judge(Action[Party, Yes | No]):
    """Ask the party to judge one element: it answers the object under the element's name."""

    element: Element

    @override
    async def perform(self) -> Json:
        answers: dict[str, object] = json.loads(self.party.says.root)
        return Json(json.dumps(answers[self.element.name.root]))


class Judged(Fact):
    """An element with the amount the party judged it at, whichever way: ``Amount`` is visible
    at two sites, under each record, and the one action hears one of them."""

    element: Element
    amount: Amount


class Listed(Fact):
    """An element with the prices the party listed, whichever way: two collections, under each
    record, and the one action hears one of them."""

    element: Element
    prices: tuple[Price, ...]


class Judgements(Fact):
    """Every element judged and listed."""

    judged: tuple[Judged, ...]
    listed: tuple[Listed, ...]


class JudgementsReply(Reply[Judgements]):
    """What leaves."""


class JudgeOperation(Route[Elements, JudgementsReply]):
    """Judge each element."""


JUDGED = program_of(
    Name,
    Element,
    Elements,
    Said,
    Party,
    Amount,
    Price,
    Yes,
    No,
    Judge,
    Judged,
    Listed,
    Judgements,
    JudgementsReply,
    JudgeOperation,
    Deployment,
)
"""A sound program the earlier binding refused: one class at two sites, and one element class
collected by two collections, each pair exclusive through the one record the action hears."""

YES: dict[str, object] = {"status": "yes", "amount": "5", "prices": ["1", "2"]}
NO: dict[str, object] = {"status": "no", "amount": "50", "prices": []}
"""What the party may say about an element."""


@pytest.mark.asyncio
async def test_candidates_of_one_class_at_two_sites_are_accepted_when_one_record_is_heard(
    party: Callable[[dict[str, str]], None], monkeypatch: pytest.MonkeyPatch
) -> None:
    proof = proven(JUDGED)
    found = placed(proof, JudgeOperation)
    judge = found[Judge, ELEMENT]
    yes = HeardRef(judge, Yes, ("amount",), Amount)
    no = HeardRef(judge, No, ("amount",), Amount)
    assert found[Judged, ELEMENT].premises["amount"] == (yes, no)
    amount = exclusion_at(proof, Judged, "amount")
    assert (amount.left, amount.right, amount.established) == (yes, no, True)
    assert amount.joint.clashes[0].why == "heard"
    prices = exclusion_at(proof, Listed, "prices")
    assert isinstance(prices.left, Collected)
    assert isinstance(prices.right, Collected)
    assert (prices.left.holder, prices.right.holder) == (
        HeardRef(judge, Yes, (), Yes),
        HeardRef(judge, No, (), No),
    )
    assert prices.established
    assert prices.joint.clashes[0].why == "heard"
    monkeypatch.setenv("PARTY__SAYS", json.dumps({"a": YES, "b": NO}))
    done = await ran(JudgeOperation, requested("a", "b"), config(JUDGED)(), proof)
    assert isinstance(done, Run)
    first, second = done.route.reply.of.judged
    assert (first.amount.root, second.amount.root) == (Decimal(5), Decimal(50))
    listed_a, listed_b = done.route.reply.of.listed
    assert [p.root for p in listed_a.prices] == [Decimal(1), Decimal(2)]
    assert listed_b.prices == ()
    agreeing(proof, done.root)


class Everything(Fact):
    """Every price, from whichever collection: three hold prices, and nothing says which."""

    prices: tuple[Price, ...]


class Everythings(Fact):
    """What was gathered."""

    everything: Everything


class EverythingReply(Reply[Everythings]):
    """What leaves."""


class EverythingOperation(Route[Order, EverythingReply]):
    """Gather every price."""


GATHERED = program_of(
    Price,
    Line,
    Cart,
    Pair,
    Solo,
    Order,
    Everything,
    Everythings,
    EverythingReply,
    EverythingOperation,
    Shop,
)
"""A program whose tuple field three collections of one element class may fill."""


@pytest.mark.asyncio
async def test_competing_collections_are_refused_where_nothing_tells_them_apart(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    faults = faults_of(GATHERED)
    assert set(faults) == {("ambiguous", ("Everything", "prices"))}
    assert faults["ambiguous", ("Everything", "prices")] == (
        "Everything.prices at the root may hold both Price in Cart.lines at request.cart.lines"
        " and Price in Pair.lines at request.pair.lines; nothing available with them excludes"
        " either"
    )
    proof = unproven(GATHERED, EverythingOperation)
    found = by_class(proof)
    assert [c.site for c in found[Everything].collections["prices"]] == [
        ("request", "cart", "lines"),
        ("request", "pair", "lines"),
        ("request", "solo", "lines"),
    ]
    assert len([e for e in proof.exclusions if e.construction.cls is Everything]) == 3
    with pytest.raises(ValidationError) as three:
        await ran(EverythingOperation, ordered_lines(2), Shop(), proof)
    assert [e["msg"] for e in three.value.errors()] == [
        "Everything.prices found 3 collections where the proof bound one"
    ]


# --- the proof stays practical as a program branches ---------------------------------------


class Exactly(Equal[Amount, Limit]):
    """An amount equal to the limit."""


class Tier(Fact):
    """An element under the limit or at it: two alternatives, exclusive by their orderings."""

    element: Element
    tier: BelowLimit | Exactly


def tiered(count: int) -> ModuleType:
    """A program whose one fact holds ``count`` tiers, each a binary choice, beside a fact over
    the ceiling: a choice between the two the proof settles without visiting the ``2**count``
    combinations, since what every combination shares already clashes."""
    tiers = [
        type(
            f"Tier{index}",
            (Tier,),
            {"__module__": __name__, "__doc__": f"Tier {index}."},
        )
        for index in range(count)
    ]
    many = type(
        "Many",
        (Fact,),
        {
            "__annotations__": {"element": Element, **{f"t{i}": t for i, t in enumerate(tiers)}},
            "__module__": __name__,
            "__doc__": "Every tier of an element.",
        },
    )
    either = type(
        "Either",
        (Fact,),
        {
            "__annotations__": {"element": Element, "which": many | Luxury},
            "__module__": __name__,
            "__doc__": "Many tiers, or a luxury.",
        },
    )
    eithers = type(
        "Eithers",
        (Fact,),
        {
            "__annotations__": {"eithers": tuple[either, ...]},  # type: ignore[valid-type]
            "__module__": __name__,
            "__doc__": "Every element, either way.",
        },
    )
    reply = type("EithersReply", (Reply[eithers],), {"__module__": __name__, "__doc__": "Out."})  # type: ignore[valid-type]
    route = type(
        "EithersOperation",
        (Route[Elements, reply],),  # type: ignore[valid-type]
        {"__module__": __name__, "__doc__": "Tier each element."},
    )
    return program_of(
        *CORE,
        Deployment,
        Ceiling,
        BelowLimit,
        Exactly,
        AboveCeiling,
        Luxury,
        *tiers,
        many,
        either,
        eithers,
        reply,
        route,
    )


def test_a_branching_program_proves_without_visiting_every_combination() -> None:
    for count in (1, 4, 8, 12):
        proof = proven(tiered(count))
        (either,) = (e for e in proof.exclusions if e.construction.cls.__name__ == "Either")
        assert either.established
        assert len(either.joint.ways) == 2
        assert {c.why for c in either.joint.clashes} == {"bounds"}
        (many,) = (x for x in proof.existences if x.construction.cls.__name__ == "Many")
        assert not many.contradicted
        assert len(many.joint.ways) == 1
        tiers = [e for e in proof.exclusions if e.field == "tier"]
        assert len(tiers) == count
        assert all(e.established and len(e.joint.ways) == 1 for e in tiers)


# --- previously valid declarations stay valid --------------------------------------------


def test_previously_valid_programs_prove_without_further_modeling() -> None:
    for program in (test_engine.PROGRAM, occurrences, stalls, TOLD_APART, TIERED, JUDGED):
        proof = proven(program)
        assert proof.faulted == ()
        assert all(e.established for e in proof.exclusions)
        assert not any(x.contradicted for x in proof.existences)


@pytest.mark.asyncio
async def test_the_screened_order_runs_agree_with_every_established_exclusion(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CATALOG__PRICES", '{"tea": "2.50", "mug": "4", "pot": "10"}')
    proof = proven(occurrences)
    order = occurrences.PlaceOrder.model_validate_json(
        '{"cart": {"lines": [{"sku": "tea", "quantity": 2}]}, "gifts": {"lines": []},'
        ' "pair": {"lines": [{"sku": "tea", "quantity": 1}, {"sku": "mug", "quantity": 3}]},'
        ' "solo": {"lines": [{"sku": "pot", "quantity": 1}]}}'
    )
    for said, expected in (
        ('{"status": "clear"}', occurrences.OrderPaid),
        ('{"status": "flagged", "reason": "odd"}', occurrences.OrderDeclined),
    ):
        monkeypatch.setenv("FRAUD__SAYS", said)
        done = await ran(occurrences.Checkout, order, config(occurrences)(), proof)
        assert isinstance(done, Run)
        assert type(done.route.reply) is expected
        agreeing(proof, done.root)


# --- conditional availability: absence alone, over alternatives and conjunctions ------------


class Bonus(Scalar[str]):
    """A bonus code the party may offer."""

    root: str = Field(min_length=1)


class Perked(Record):
    """What the party says: the amount, and perhaps a coupon, and perhaps a bonus."""

    amount: Amount
    coupon: Coupon | None = None
    bonus: Bonus | None = None


class AskPerked(Action[Party, Perked]):
    """Ask the party about one element, which may offer perks."""

    element: Element

    @override
    async def perform(self) -> Json:
        answers: dict[str, object] = json.loads(self.party.says.root)
        return Json(json.dumps(answers[self.element.name.root]))


class WithCoupon(Fact):
    """An element with a coupon."""

    element: Element
    coupon: Coupon


class WithBonus(Fact):
    """An element with a bonus."""

    element: Element
    bonus: Bonus


class CouponAgain(Fact):
    """An element with the same coupon, held again."""

    element: Element
    coupon: Coupon


class Perk(Fact):
    """A coupon or a bonus: two optional sources, both of which the party may omit."""

    element: Element
    which: WithCoupon | WithBonus


class PricedPerked(Fact):
    """An element as the party quoted it: unconditional."""

    element: Element
    perked: Perked


class Deal(Fact):
    """A perk and the quote: a conjunction over a disjunction of optional evidence."""

    element: Element
    perk: Perk
    priced: PricedPerked


class Twice(Fact):
    """The coupon through two facts: one source, shared."""

    element: Element
    first: WithCoupon
    second: CouponAgain


class Perks(Fact):
    """Every element's deal and the coupon twice: a collection that may be empty, and whose
    elements, when there are any, need what the party may omit."""

    deals: tuple[Deal, ...]
    twice: tuple[Twice, ...]


class PerksReply(Reply[Perks]):
    """What leaves."""


class PerkOperation(Route[Elements, PerksReply]):
    """Perk each element."""


PERKED = program_of(
    Name,
    Element,
    Elements,
    Said,
    Party,
    Amount,
    Coupon,
    Bonus,
    Perked,
    AskPerked,
    WithCoupon,
    WithBonus,
    CouponAgain,
    Perk,
    PricedPerked,
    Deal,
    Twice,
    Perks,
    PerksReply,
    PerkOperation,
    Deployment,
)
"""A route that answers only when the party offers a coupon or a bonus for every element."""

COUPON = (*ELEMENT, "AskPerked", "heard", "coupon")
BONUS = (*ELEMENT, "AskPerked", "heard", "bonus")
"""The optional sites."""


@pytest.mark.asyncio
async def test_two_optional_sources_absent_together_make_a_route_conditional(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    faults = faults_of(PERKED)
    assert set(faults) == {("conditional", ("PerkOperation",)), ("ambiguous", ("Perk", "which"))}
    assert faults["conditional", ("PerkOperation",)] == (
        "PerkOperation answers only when request.each.[].AskPerked.heard.bonus,"
        " request.each.[].AskPerked.heard.coupon arrive, and what declares it admits its"
        " absence; an absence the business concludes from is a class"
    )
    proof = unproven(PERKED, PerkOperation)
    found = by_class(proof)
    assert conditions(found[WithCoupon]) == (COUPON,)
    assert conditions(found[WithBonus]) == (BONUS,)
    assert conditions(found[Perk]) == (BONUS, COUPON)
    assert conditions(found[PricedPerked]) == ()
    assert conditions(found[Deal]) == (BONUS, COUPON)
    assert conditions(found[Twice]) == (COUPON,)
    assert conditions(found[Perks]) == (BONUS, COUPON)
    assert conditions(found[PerkOperation]) == (BONUS, COUPON)
    treat = Construction(
        PerkOperation,
        Deal,
        ELEMENT,
        {
            "element": found[Deal].premises["element"],
            "which": (ConstructedRef(found[Perk]), ConstructedRef(found[PricedPerked])),
        },
    )
    assert conditions(treat) == ()
    (perks,) = joint((ConstructedRef(found[Perks]),)).open
    assert not any(isinstance(s, ConstructedRef) and s.cls is Deal for s in perks)
    monkeypatch.setenv("PARTY__SAYS", json.dumps({"a": {"amount": "5"}}))
    blocked = await ran(PerkOperation, requested("a"), config(PERKED)(), proof)
    assert isinstance(blocked, Blocked)
    assert {
        (c.occurrence.construction.cls, c.premise[0])
        for c in blocked.causes
        if isinstance(c, Unfilled)
    } == {
        (WithCoupon, "coupon"),
        (WithBonus, "bonus"),
        (CouponAgain, "coupon"),
    }
    monkeypatch.setenv("PARTY__SAYS", json.dumps({"a": {"amount": "5", "coupon": "TEN"}}))
    done = await ran(PerkOperation, requested("a"), config(PERKED)(), proof)
    assert isinstance(done, Run)
    (deal,) = done.route.reply.of.deals
    assert type(deal.perk.which) is WithCoupon
    (twice,) = done.route.reply.of.twice
    assert twice.first.coupon is twice.second.coupon
    empty = await ran(PerkOperation, requested(), config(PERKED)(), proof)
    assert isinstance(empty, Run)
    assert empty.route.reply.of.deals == ()
