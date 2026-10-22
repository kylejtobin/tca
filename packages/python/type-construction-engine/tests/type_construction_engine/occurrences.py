"""A program in which one class occurs at many sites: a line in a cart, in the gifts, in a fixed
pair and alone; a quote and a line total once per line wherever it is; a sum per carrier, each
over its own lines; a share per line of the cart's total, and the cart's shares collected
again; a screening heard as one of two records. Nothing here is written for the engine: no
identifier, no source, no subclass per collection."""

import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Literal, override

from pydantic import Field, computed_field

from type_construction.engine import hear
from type_construction.world import (
    Action,
    Config,
    Connection,
    Fact,
    Instant,
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


class Sku(Scalar[str]):
    """What a product is called in the catalog."""

    root: str = Field(min_length=1)


class Quantity(Scalar[int]):
    """How many of a product a line asks for."""

    root: int = Field(gt=0)


class UnitPrice(Scalar[Decimal]):
    """What the catalog says one of a product costs."""

    root: Decimal = Field(ge=0)


class Line(Value):
    """One product and how many of it; the same value wherever an order holds lines."""

    sku: Sku
    quantity: Quantity


class Cart(Value):
    """What the customer buys."""

    lines: tuple[Line, ...]


class Gifts(Value):
    """What the customer sends as gifts: lines too, and a separate collection."""

    lines: tuple[Line, ...]


class Pair(Value):
    """Two lines offered together, in order."""

    lines: tuple[Line, Line]


class Solo(Value):
    """One line on its own."""

    lines: tuple[Line]


class PlaceOrder(Request):
    """What arrives: a cart, gifts, a pair and a solo line."""

    cart: Cart
    gifts: Gifts
    pair: Pair
    solo: Solo


class Said(Setting[str]):
    """The JSON a stand-in party answers with."""


class Catalog(Connection):
    """A party that prices a product: its line is a JSON object from sku to price."""

    prices: Said

    @override
    @asynccontextmanager
    async def open(self) -> AsyncGenerator[None]:
        yield


class Fraud(Connection):
    """A party that screens an order with the one line the deployment gave it."""

    says: Said

    @override
    @asynccontextmanager
    async def open(self) -> AsyncGenerator[None]:
        yield


PERFORMED: list[str] = []
"""Each action performed, as the sku it quoted or ``screen``: the test's record of effects."""


class Price(Record):
    """What the catalog says about a line."""

    unit: UnitPrice = Field(alias="price")


class Quote(Action[Catalog, Price]):
    """Ask the catalog what one line's product costs: once per line, in every collection."""

    line: Line

    @override
    async def perform(self) -> Price:
        PERFORMED.append(self.line.sku.root)
        prices: dict[str, str] = json.loads(self.party.prices.root)
        return hear(self, json.dumps({"price": prices[self.line.sku.root]}))


class LineTotal(Times[UnitPrice, Quantity]):
    """What a line costs: its unit price times its quantity; once per line, wherever it is."""


class CartTotal(Sum[LineTotal]):
    """What the cart's lines cost together: the cart says which lines."""

    cart: Cart


class GiftTotal(Sum[LineTotal]):
    """What the gift lines cost together: the gifts say which lines."""

    gifts: Gifts


class PairTotal(Sum[LineTotal]):
    """What the pair costs: exactly its two lines."""

    pair: Pair


class SoloTotal(Only[LineTotal]):
    """The solo line's total: the one there is."""

    solo: Solo


class Share(Fact):
    """A line's total beside the cart's: a child holding its parent's aggregate."""

    total: LineTotal
    cart: CartTotal


class CartShares(Fact):
    """The cart's lines' shares, collected again after the cart's total existed."""

    cart: Cart
    shares: tuple[Share, ...]


class Clear(Record):
    """The screening's yes."""

    status: Literal["clear"]


class Reason(Scalar[str]):
    """Why the screening said no."""

    root: str = Field(min_length=1)


class Flagged(Record):
    """The screening's no."""

    status: Literal["flagged"]
    reason: Reason


class Screen(Action[Fraud, Clear | Flagged]):
    """Ask whether the order is clear."""

    order: PlaceOrder

    @override
    async def perform(self) -> Clear | Flagged:
        PERFORMED.append("screen")
        return hear(self, self.party.says.root)


class Screened(Fact):
    """An order the screening cleared."""

    order: PlaceOrder
    clear: Clear


class Refused(Fact):
    """An order the screening flagged."""

    order: PlaceOrder
    flagged: Flagged


class Priced(Fact):
    """Every total of an order, cleared or not."""

    cart: CartTotal
    gifts: GiftTotal
    pair: PairTotal
    solo: SoloTotal
    shares: CartShares


class Paid(Fact):
    """A cleared order, priced, at a moment."""

    screened: Screened
    priced: Priced
    at: Instant


class Declined(Fact):
    """A flagged order, priced all the same."""

    refused: Refused
    priced: Priced


class Money(Scalar[Decimal]):
    """An amount the caller is told."""


class OrderPaid(Reply[Paid]):
    """What leaves for a cleared order: each total."""

    @computed_field
    @property
    def cart(self) -> Money:
        return Money(self.of.priced.cart.root)

    @computed_field
    @property
    def gifts(self) -> Money:
        return Money(self.of.priced.gifts.root)

    @computed_field
    @property
    def pair(self) -> Money:
        return Money(self.of.priced.pair.root)

    @computed_field
    @property
    def solo(self) -> Money:
        return Money(self.of.priced.solo.chosen.root)


class OrderDeclined(Reply[Declined]):
    """What leaves for a flagged order: the reason, and what it would have cost."""

    @computed_field
    @property
    def reason(self) -> Reason:
        return self.of.refused.flagged.reason

    @computed_field
    @property
    def cart(self) -> Money:
        return Money(self.of.priced.cart.root)


class Checkout(Route[PlaceOrder, OrderPaid | OrderDeclined]):
    """Price an order and screen it."""


class Deployment(Config):
    """The catalog and the screening."""

    catalog: Catalog
    fraud: Fraud
