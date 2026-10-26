"""External adapter doubles and payload builders; no engine decisions or assertions."""

import json
from dataclasses import dataclass, field
from decimal import Decimal

from type_construction.program import AttemptId, Frontier, Intent, Observation, Proposal, Result

from .fulfillment import Mail, Payments


@dataclass
class Calls:
    """An external service that records dispatch and answers later."""

    received: list[tuple[Intent, AttemptId]] = field(default_factory=list)

    def __call__(self, intent: Intent, attempt: AttemptId) -> None:
        self.received.append((intent, attempt))


def names(result: Result) -> set[str]:
    return {p.effect.interaction for p in result.ready} if isinstance(result, Frontier) else set()


def proposal(result: Result, interaction: str) -> Proposal:
    assert isinstance(result, Frontier), result
    matches = tuple(p for p in result.ready if p.effect.interaction == interaction)
    assert len(matches) == 1, (interaction, result)
    return matches[0]


def payment(attempt: AttemptId, amount: str, delivery: str = "payment-1") -> Observation:
    return Observation(
        Payments,
        delivery,
        "result",
        payment_json("ORD-7", amount),
        "json",
        about=attempt.effect,
        claims=attempt,
    )


def payment_json(order: str, amount: str, reference: str = " pay-9 ") -> str:
    return json.dumps({"order_id": order, "amount": amount, "reference": reference})


def installment(delivery: str, order: str, amount: str) -> Observation:
    return Observation(
        Payments,
        delivery,
        "result",
        payment_json(order, amount),
        "json",
        through="InstallmentsReported",
    )


def settled(delivery: str, order: str = "ORD-7") -> Observation:
    return Observation(
        Payments,
        delivery,
        "result",
        json.dumps({"order_id": order}),
        "json",
        through="Settled",
    )


def receipted(intent: Intent, attempt: AttemptId) -> Observation:
    return Observation(
        Mail,
        f"receipt-{attempt.number}-{intent.effect.occurrence}",
        "result",
        {"order_id": intent.request.order.root, "amount": Decimal(intent.request.amount.root)},
        about=attempt.effect,
    )
