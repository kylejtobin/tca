"""A program whose fact requires exactly two line totals from a cart of any number of lines:
the proof must not bind a fixed pair to a collection that guarantees no count, since Pydantic
refuses the fact at the request that has three."""

from decimal import Decimal

from pydantic import Field, computed_field

from type_construction.world import (
    Config,
    Fact,
    Reply,
    Request,
    Route,
    Scalar,
    Times,
    Value,
)


class Quantity(Scalar[int]):
    """How many of a product a line asks for."""

    root: int = Field(gt=0)


class UnitPrice(Scalar[Decimal]):
    """What one of a product costs, as the line says."""

    root: Decimal = Field(ge=0)


class Line(Value):
    """One product, priced, and how many."""

    quantity: Quantity
    price: UnitPrice


class Cart(Value):
    """Any number of lines."""

    lines: tuple[Line, ...]


class PlaceOrder(Request):
    """What arrives: a cart."""

    cart: Cart


class LineTotal(Times[UnitPrice, Quantity]):
    """What a line costs."""


class Both(Fact):
    """Exactly two line totals, from a cart that may hold any number."""

    cart: Cart
    totals: tuple[LineTotal, LineTotal]


class Paired(Reply[Both]):
    """What leaves: the first total."""

    @computed_field
    @property
    def first(self) -> UnitPrice:
        return UnitPrice(self.of.totals[0].root)


class Checkout(Route[PlaceOrder, Paired]):
    """Price the pair."""


class Deployment(Config):
    """No party: every value arrives."""
