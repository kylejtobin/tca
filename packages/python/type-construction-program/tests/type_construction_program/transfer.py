"""One class in two roles, and one element class in two collections.

A transfer moves an amount from one account to another. Both are an ``Account``; which one the
debit concerns is a business distinction the type does not carry, so the interaction declares
it: the debit request's account is the transfer's source, the credit request's is its target.
An order holds a cart and gifts, each a collection of the one ``Line`` class; each total is over
its own lines, so the program declares which collection each tuple follows. Nothing here is a
subclass made to tell the roles apart.
"""

from decimal import Decimal

from pydantic import Field

from type_construction.program import Binding, Correlation, Interaction, Program, Source
from type_construction.world import Fact, Record, Scalar, Sum, Times, Value


class AccountNumber(Scalar[str]):
    root: str = Field(min_length=1)


class Amount(Scalar[Decimal]):
    root: Decimal = Field(gt=0)


class Reference(Scalar[str]):
    root: str = Field(min_length=1)


class Account(Value):
    number: AccountNumber


class Transfer(Value):
    """The command: move the amount from the source account to the target account."""

    source: Account
    target: Account
    amount: Amount


class DebitRequest(Value):
    account: Account
    amount: Amount


class CreditRequest(Value):
    account: Account
    amount: Amount


class Debited(Record):
    account: AccountNumber = Field(alias="account_number")
    reference: Reference


class Credited(Record):
    account: AccountNumber = Field(alias="account_number")
    reference: Reference


class Legs(Fact):
    """Two sides of one class, each field named for the other's alias: by name, the debit side
    is the source; by alias, the names would swap."""

    debit_side: Account = Field(alias="credit_side")
    credit_side: Account = Field(alias="debit_side")


class Transferred(Fact):
    """The outcome: the transfer, its debit and its credit."""

    transfer: Transfer
    debit: Debited
    credit: Credited


BANK = Source("bank")

DEBIT = Interaction(
    source=BANK,
    sends=DebitRequest,
    receives=(Debited,),
    correlated=(Correlation(received="account", subject="source.number"),),
    bound=(Binding(premise="account", subject="source"),),
)
CREDIT = Interaction(
    source=BANK,
    sends=CreditRequest,
    receives=(Credited,),
    correlated=(Correlation(received="account", subject="target.number"),),
    bound=(Binding(premise="account", subject="target"),),
)
UNBOUND_DEBIT = DEBIT.model_copy(update={"bound": ()})

TRANSFERRING = Program(goal=Transferred, accepts=Transfer, interactions=(DEBIT, CREDIT))
LEGS = Program(
    goal=Legs,
    accepts=Transfer,
    bound=(
        Binding(premise="debit_side", subject="source"),
        Binding(premise="credit_side", subject="target"),
    ),
)

TRANSFER = Transfer(
    source=Account(number=AccountNumber("acc-1")),
    target=Account(number=AccountNumber("acc-2")),
    amount=Amount(Decimal("25.00")),
)


class Sku(Scalar[str]):
    root: str = Field(min_length=1)


class Quantity(Scalar[int]):
    root: int = Field(gt=0)


class UnitPrice(Scalar[Decimal]):
    root: Decimal = Field(gt=0)


class Line(Value):
    sku: Sku
    quantity: Quantity
    price: UnitPrice


class Cart(Value):
    lines: tuple[Line, ...]


class Gifts(Value):
    lines: tuple[Line, ...]


class PlaceOrder(Value):
    """The command: an order of a cart and gifts, each a collection of lines."""

    cart: Cart
    gifts: Gifts


class LineTotal(Times[UnitPrice, Quantity]):
    """What one line costs, wherever the line is."""


class CartTotal(Sum[LineTotal]):
    """What the cart's lines cost together."""


class GiftTotal(Sum[LineTotal]):
    """What the gift lines cost together."""


class Totals(Fact):
    cart: CartTotal
    gifts: GiftTotal


TOTALS = Program(
    goal=Totals,
    accepts=PlaceOrder,
    bound=(
        Binding(premise="cart.of", subject="cart.lines"),
        Binding(premise="gifts.of", subject="gifts.lines"),
    ),
)


def line(sku: str, quantity: int, price: str) -> Line:
    return Line(sku=Sku(sku), quantity=Quantity(quantity), price=UnitPrice(Decimal(price)))


ORDER = PlaceOrder(
    cart=Cart(lines=(line("tea", 2, "2.50"), line("tea", 2, "2.50"))),
    gifts=Gifts(lines=(line("mug", 1, "4.00"),)),
)
"""Two equal cart lines and one gift line."""
