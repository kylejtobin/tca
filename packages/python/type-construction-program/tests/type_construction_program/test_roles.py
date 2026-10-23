"""A type is not its occurrences: one class in two roles, one element class in two collections
(foundations §4.1, §5; acceptance B1 to B3, D3).

The declarations are ``transfer``. The hypothesis under test is the one the first slice held: a
class is obtained one way, and a class found at two places is two classes. The transfer breaks
it: both accounts are an ``Account``, the debit concerns one and the credit the other, and no
subclass is a business distinction. The repair is a declaration: the interaction binds the
request's premise to the place in the input it is obtained from, the program binds a tuple to
the collection it follows, and the evaluator constructs each occurrence from its own place.
Without the binding the program is refused naming the places and the binding that would tell
them apart, not a class to invent.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from type_construction.program import (
    Binding,
    Built,
    Completed,
    Elements,
    InvocationId,
    Program,
    Site,
    accept,
    evaluate,
    intend,
    perform,
)

from . import transfer
from .drive import frontier


def confirmed(account: str, reference: str) -> str:
    return f'{{"account_number": "{account}", "reference": "{reference}"}}'


def test_without_a_binding_two_roles_of_one_class_are_refused_naming_the_binding() -> None:
    with pytest.raises(ValidationError) as refusal:
        Program(
            goal=transfer.Transferred,
            accepts=transfer.Transfer,
            interactions=(transfer.UNBOUND_DEBIT, transfer.CREDIT),
        )
    message = str(refusal.value)
    assert "Transfer.source" in message
    assert "Transfer.target" in message
    assert "Binding(premise=" in message
    assert "DebitRequest.account" in message


def test_each_role_is_its_own_occurrence_and_its_own_operation() -> None:
    program = transfer.TRANSFERRING
    invocation = accept(program, InvocationId("tr"), transfer.TRANSFER)
    opening = frontier(evaluate(program, invocation))
    by_kind = {type(d.request): d for d in opening.dispatch}
    assert set(by_kind) == {transfer.DebitRequest, transfer.CreditRequest}
    debit, credit = by_kind[transfer.DebitRequest], by_kind[transfer.CreditRequest]
    assert isinstance(debit.request, transfer.DebitRequest)
    assert isinstance(credit.request, transfer.CreditRequest)
    assert debit.request.account.number == transfer.AccountNumber("acc-1")
    assert credit.request.account.number == transfer.AccountNumber("acc-2")
    assert isinstance(debit.identity.occurrence, Built)
    assert isinstance(credit.identity.occurrence, Built)
    assert dict(debit.identity.occurrence.parts)["account"] == Site(evidence=0, path=("source",))
    assert dict(credit.identity.occurrence.parts)["account"] == Site(evidence=0, path=("target",))
    assert dict(debit.identity.occurrence.parts)["amount"] == Site(evidence=0, path=("amount",))
    assert dict(credit.identity.occurrence.parts)["amount"] == Site(evidence=0, path=("amount",))

    invocation = intend(invocation, opening.dispatch)
    invocation = perform(program, invocation, debit.identity, confirmed("acc-1", "d-1"))
    invocation = perform(program, invocation, credit.identity, confirmed("acc-2", "c-1"))
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, transfer.Transferred)
    assert result.goal.debit.account == transfer.AccountNumber("acc-1")
    assert result.goal.credit.account == transfer.AccountNumber("acc-2")
    assert result.goal.transfer is invocation.input


def test_a_confirmation_for_the_other_role_does_not_answer_this_one() -> None:
    program = transfer.TRANSFERRING
    invocation = accept(program, InvocationId("tr"), transfer.TRANSFER)
    opening = frontier(evaluate(program, invocation))
    invocation = intend(invocation, opening.dispatch)
    (debit,) = [d for d in opening.dispatch if isinstance(d.request, transfer.DebitRequest)]
    with pytest.raises(Exception, match="Uncorrelated"):
        perform(program, invocation, debit.identity, confirmed("acc-2", "d-1"))


def test_a_binding_to_a_place_holding_another_class_is_refused() -> None:
    with pytest.raises(ValidationError) as refusal:
        Program(
            goal=transfer.Transferred,
            accepts=transfer.Transfer,
            interactions=(
                transfer.DEBIT.model_copy(
                    update={"bound": (Binding(premise="account", subject="amount"),)}
                ),
                transfer.CREDIT,
            ),
        )
    assert "bound to Transfer.amount, which holds" in str(refusal.value)


def test_without_a_binding_one_element_class_in_two_collections_is_refused() -> None:
    with pytest.raises(ValidationError) as refusal:
        Program(goal=transfer.Totals, accepts=transfer.PlaceOrder)
    message = str(refusal.value)
    assert "PlaceOrder.cart.lines.*" in message
    assert "PlaceOrder.gifts.lines.*" in message
    assert "Binding(premise=" in message


def test_each_total_is_over_its_own_lines_and_equal_lines_are_two() -> None:
    program = transfer.TOTALS
    invocation = accept(program, InvocationId("ord"), transfer.ORDER)
    result = evaluate(program, invocation)
    assert isinstance(result, Completed)
    assert isinstance(result.goal, transfer.Totals)
    assert result.goal.cart.root == Decimal("10.00")
    assert result.goal.gifts.root == Decimal("4.00")
    assert [t.root for t in result.goal.cart.of] == [Decimal("5.00"), Decimal("5.00")]
    assert result.goal.cart.of[0] is not result.goal.cart.of[1]
    assert isinstance(result.occurrence, Built)
    parts = dict(result.occurrence.parts)
    cart, gifts = parts["cart"], parts["gifts"]
    assert isinstance(cart, Built)
    assert isinstance(gifts, Built)
    cart_lines, gift_lines = dict(cart.parts)["of"], dict(gifts.parts)["of"]
    assert isinstance(cart_lines, Elements)
    assert isinstance(gift_lines, Elements)
    assert [sites(o) for o in cart_lines.of] == [
        {("cart", "lines", 0, "price"), ("cart", "lines", 0, "quantity")},
        {("cart", "lines", 1, "price"), ("cart", "lines", 1, "quantity")},
    ]
    assert [sites(o) for o in gift_lines.of] == [
        {("gifts", "lines", 0, "price"), ("gifts", "lines", 0, "quantity")}
    ]


def sites(occurrence: Built | Site | Elements) -> set[tuple[str | int, ...]]:
    match occurrence:
        case Site(path=path):
            return {path}
        case Built(parts=parts):
            return {s for _, part in parts for s in sites(part)}
        case Elements(of=of):
            return {s for part in of for s in sites(part)}
