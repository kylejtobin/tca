"""The two moves a test makes against an invocation, and nothing that chooses for it.

A test supplies what the outside world said and asserts what the evaluator derived. It never
constructs a conclusion, picks a branch, or names the work: ``performing`` commits whatever the
evaluator dispatched, requires that it was exactly one request, and records the given answer to
it; ``delivered`` is a delivery from a source with a payload. Which request was dispatched is
asserted by the test after the fact.
"""

from type_construction.program import (
    Delivery,
    DeliveryId,
    Dispatch,
    EffectIdentity,
    Evaluation,
    Frontier,
    Invocation,
    Program,
    Source,
    evaluate,
    intend,
    perform,
)


def frontier(evaluation: Evaluation) -> Frontier:
    """The evaluation, which the test expects to be a frontier."""
    assert isinstance(evaluation, Frontier), evaluation
    return evaluation


def only(program: Program, invocation: Invocation) -> tuple[Invocation, Dispatch]:
    """The one dispatch the evaluator proposes, committed."""
    proposed = frontier(evaluate(program, invocation))
    assert len(proposed.dispatch) == 1, proposed
    return intend(invocation, proposed.dispatch), proposed.dispatch[0]


def performing(
    program: Program, invocation: Invocation, answer: str
) -> tuple[Invocation, Dispatch]:
    """Commit the one dispatch the evaluator proposes and record the party's answer to it."""
    invocation, dispatch = only(program, invocation)
    return perform(program, invocation, dispatch.identity, answer), dispatch


def delivered(
    source: Source, delivery: str, payload: str, answers: EffectIdentity | None = None
) -> Delivery:
    """A delivery from a source."""
    return Delivery(source=source, id=DeliveryId(delivery), payload=payload, answers=answers)
