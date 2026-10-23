"""A program whose party may omit a coupon from what it says, and whose reply needs the
discount the coupon makes: the proof must not take the coupon as present, since the record the
action hears admits its absence. ``Priced`` and ``Told`` are the legitimate use: the reply
reads the coupon the party gave, or nothing."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import override

from pydantic import Field, computed_field

from type_construction.world import (
    Action,
    Config,
    Connection,
    Fact,
    Json,
    Record,
    Reply,
    Request,
    Route,
    Scalar,
    Setting,
)


class Sku(Scalar[str]):
    """What a product is called."""

    root: str = Field(min_length=1)


class Amount(Scalar[Decimal]):
    """What the party says a product costs."""

    root: Decimal = Field(gt=0)


class Coupon(Scalar[str]):
    """A code the party may offer."""

    root: str = Field(min_length=1)


class PlaceOrder(Request):
    """What arrives: a product."""

    sku: Sku


class Said(Setting[str]):
    """The JSON a stand-in party answers with."""


class Party(Connection):
    """A party that answers with the one line the deployment gave it."""

    says: Said

    @override
    @asynccontextmanager
    async def open(self) -> AsyncGenerator[None]:
        yield


class Quoted(Record):
    """What the party says: the amount, and perhaps a coupon."""

    amount: Amount
    coupon: Coupon | None = None


class Quote(Action[Party, Quoted]):
    """Ask the party about the product."""

    order: PlaceOrder

    @override
    async def perform(self) -> Json:
        return Json(self.party.says.root)


class Discount(Fact):
    """A quote with a coupon: exists only when the party offered one."""

    quoted: Quoted
    coupon: Coupon


class Discounted(Fact):
    """What a discounted order concludes."""

    discount: Discount


class OrderDiscounted(Reply[Discounted]):
    """What leaves: the coupon used."""

    @computed_field
    @property
    def coupon(self) -> Coupon:
        return self.of.discount.coupon


class Checkout(Route[PlaceOrder, OrderDiscounted]):
    """A route that cannot answer when the party offers no coupon."""


class Priced(Fact):
    """An order as the party quoted it."""

    quoted: Quoted


class Told(Reply[Priced]):
    """What leaves: the amount, and the coupon offered or none."""

    @computed_field
    @property
    def amount(self) -> Amount:
        return self.of.quoted.amount

    @computed_field
    @property
    def coupon(self) -> Coupon | None:
        return self.of.quoted.coupon


class Price(Route[PlaceOrder, Told]):
    """A route that answers whatever the party says."""


class Deployment(Config):
    """The one party."""

    party: Party
