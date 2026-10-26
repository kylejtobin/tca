"""The same order paid in installments: an evolving source closed by declaration.

The provider reports each installment for the order as it arrives and reports settlement when
no more will come. Each installment is acknowledged to the customer as soon as it is admitted.
The total paid, whether a single payment settled the order and whether the installments cover
the total are conclusions over the closed tuple, and only over the closed tuple. The same
generic declarations as ``fulfillment`` are used; nothing is added to the engine for it."""

from typing import Annotated

from pydantic import Field

from type_construction.program import (
    EACH,
    Bound,
    Correlate,
    Goal,
    Interaction,
    Members,
    PerMember,
    Premises,
    Program,
    Receive,
)
from type_construction.world import AtLeast, Fact, Only, Record, Sum, Value

from .fulfillment import Mail, Order, OrderId, Paid, PaymentReported, Payments, Total


class SettlementReported(Fact):
    """What the provider says when no more installments will come for an order."""

    order: OrderId = Field(alias="order_id")


class InstallmentsReported(Receive[PaymentReported]):
    """The provider reports each installment for the order, unasked."""

    source = Payments
    correlation = (Correlate(result=("order",), premise=Bound("order", "id")),)


class Settled(Receive[SettlementReported]):
    """The provider reports that the order's installments are complete."""

    source = Payments
    correlation = (Correlate(result=("order",), premise=Bound("order", "id")),)


class ReceiptRequest(Value):
    """What the mailbox is asked: to acknowledge one installment."""

    order: Annotated[OrderId, Bound("order", "id")]
    amount: Annotated[Paid, Bound("member", "amount")]


class Receipted(Fact):
    """That the customer was told of one installment."""

    order: OrderId = Field(alias="order_id")
    amount: Paid


class SendReceipt(Interaction[ReceiptRequest, Receipted]):
    """Tell the customer one installment arrived; safe to repeat."""

    source = Mail
    correlation = (
        Correlate(result=("order",), request=("order",)),
        Correlate(result=("amount",), request=("amount",)),
    )
    recovery = "retry"


class PaidTotal(Sum[Paid]):
    """What the installments paid together."""


class Covered(AtLeast[PaidTotal, Total]):
    """The installments cover the total."""


class Single(Only[PaymentReported]):
    """The order was settled by exactly one payment."""


class Settlement(Record):
    """The outcome: the order, its installments once settled, each acknowledged, their total,
    and that they cover the order."""

    order: Order
    installments: Annotated[
        tuple[PaymentReported, ...], Members(reported=InstallmentsReported, closed_by=Settled)
    ]
    receipts: Annotated[tuple[Receipted, ...], PerMember("installments")]
    paid: Annotated[PaidTotal, Premises(of=Bound("installments", EACH, "amount"))]
    covered: Annotated[Covered, Premises(value=Bound("paid"), bound=Bound("order", "total"))]


class SingleSettlement(Record):
    """The outcome when the order must have been paid at once."""

    order: Order
    installments: Annotated[
        tuple[PaymentReported, ...], Members(reported=InstallmentsReported, closed_by=Settled)
    ]
    single: Annotated[Single, Premises(of=Bound("installments"))]


SETTLE = Goal(Settlement, accepts=("order",))
"""Settle one order's installments."""

SETTLEMENT = Program(SETTLE, (InstallmentsReported, Settled, SendReceipt), artifact="settlement@1")
"""The installments program artifact."""

SINGLE = Program(
    Goal(SingleSettlement, accepts=("order",)), (InstallmentsReported, Settled), artifact="single@1"
)
"""The single-payment program artifact."""
