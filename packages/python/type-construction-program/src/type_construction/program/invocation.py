"""One invocation's recorded history, and the protocol by which it grows.

An invocation is one accepted pursuit of a program's goal. Its history is append-only: the
accepted input, each piece of admitted evidence, each effect intent committed before dispatch,
and each attempt's outcome. The position of an entry in the history is its identity within the
invocation; the evaluator reads the history and nothing else.

The functions here are the host protocol in its smallest form. ``accept`` opens an invocation.
``admit`` validates a delivery against the program's declared receives, ties it to the invocation
by the declared correlation or by the intent it answers, refuses what is closed, duplicated or
conflicting, and records it as evidence. ``intend`` commits the evaluator's proposed dispatches
before anything is sent. ``perform``, ``acknowledge``, ``failed`` and ``uncertain`` record what
one attempt produced, as the capability reports it: the result, which becomes evidence in the
same step; a receipt, which does not; a failure that did not happen; or an outcome that is not
known. Which of these came back is the capability's report, not an inference from the payload's
shape: a receipt may have the shape of a result. Nothing here calls an external
system, reads a clock, or decides a business branch.

An ``EffectIdentity`` is one logical external operation: the invocation, the request class
sent, and the evidence the request was constructed from. It is derived, so the same history
yields the same identity; it is recorded, because dispatch follows the record. Attempts of one
identity are numbered; a retry is a new attempt, not a new identity.

These are in-memory records for contract experiments. They are not a durable codec, and nothing
here demonstrates recovery, concurrency or worker ownership.
"""

from pydantic import BaseModel, ConfigDict, Field, SerializeAsAny, TypeAdapter, ValidationError

from type_construction.world import Scalar

from .declaration import Correlation, Interaction, Program, Source, at

RECORDED = ConfigDict(frozen=True, strict=True, extra="forbid", validate_default=True)
"""Configuration for a recorded entry: strict, frozen, no undeclared fields."""


class InvocationId(Scalar[str]):
    """One accepted pursuit of a goal."""

    root: str = Field(min_length=1)


class DeliveryId(Scalar[str]):
    """A delivery's transport identity, as the source and transport establish it. Two deliveries
    with one identity are one claim."""

    root: str = Field(min_length=1)


class EffectIdentity(BaseModel):
    """One logical external operation of one invocation.

    The invocation keeps two invocations' operations apart. The request class keeps two
    intended operations apart when their request bodies are equal. The premises, the history
    positions of the evidence the request was constructed from, make a request constructed
    from new evidence a new operation. Nothing about the request's payload, or any attempt, is
    part of it.
    """

    model_config = RECORDED

    invocation: InvocationId
    operation: str
    """The durable name of the request class sent."""
    premises: tuple[int, ...]
    """The history positions of the evidence the request was constructed from, ascending."""

    def __hash__(self) -> int:
        """Hashable by its three parts, so that it keys the intents and attempts it names."""
        return hash((self.invocation.root, self.operation, self.premises))


class Delivery(BaseModel):
    """An external claim presented for admission: who says it, its transport identity, the
    payload as received, and, when the party echoes it, the intent it answers."""

    model_config = RECORDED

    source: Source
    id: DeliveryId
    payload: str
    """The payload as JSON text; admission validates it in JSON mode."""
    answers: EffectIdentity | None = None


class Delivered(BaseModel):
    """Evidence came in a delivery."""

    model_config = RECORDED

    delivery: DeliveryId


class Returned(BaseModel):
    """Evidence came back inside an attempt of a send."""

    model_config = RECORDED

    identity: EffectIdentity
    attempt: int


class Evidence(BaseModel):
    """An admitted record: the value, its source, where it came from, and the intent it
    answers when it answers one. Its ``id`` is its position in the history."""

    model_config = RECORDED

    id: int
    source: Source
    value: SerializeAsAny[BaseModel]
    origin: Delivered | Returned
    answers: EffectIdentity | None = None


class Accepted(BaseModel):
    """The input the invocation was accepted with; always at position 0."""

    model_config = RECORDED

    input: SerializeAsAny[BaseModel]


class Admitted(BaseModel):
    """A piece of evidence was admitted."""

    model_config = RECORDED

    evidence: Evidence


class Intended(BaseModel):
    """An effect intent was committed, before dispatch."""

    model_config = RECORDED

    identity: EffectIdentity
    request: SerializeAsAny[BaseModel]


class Answered(BaseModel):
    """The attempt returned the result; it is the evidence at ``evidence``."""

    model_config = RECORDED

    evidence: int


class Acknowledged(BaseModel):
    """The attempt returned a receipt: the party accepted the request and will say the result
    later. The receipt satisfies no premise."""

    model_config = RECORDED

    receipt: SerializeAsAny[BaseModel]


class Failed(BaseModel):
    """The attempt did not reach the party, or the party refused it: it did not happen."""

    model_config = RECORDED

    reason: str


class Uncertain(BaseModel):
    """The attempt's outcome is not known: it may have happened. Nothing here decides whether
    to retry; that is the capability's recovery contract."""

    model_config = RECORDED

    reason: str


class Attempted(BaseModel):
    """One physical attempt of one logical effect, and what it produced."""

    model_config = RECORDED

    identity: EffectIdentity
    number: int = Field(ge=1)
    outcome: Answered | Acknowledged | Failed | Uncertain


type Entry = Accepted | Admitted | Intended | Attempted


class Dispatch(BaseModel):
    """What the evaluator proposes the host perform: one request under one identity, as attempt
    ``attempt``."""

    model_config = RECORDED

    identity: EffectIdentity
    request: SerializeAsAny[BaseModel]
    attempt: int = Field(ge=1)


class Invocation(BaseModel):
    """One invocation: its identity and its history. Every function below returns a new
    invocation with one more entry, or the same one, or raises ``Refusal``."""

    model_config = RECORDED

    id: InvocationId
    history: tuple[Entry, ...] = Field(min_length=1)

    @property
    def input(self) -> BaseModel:
        """The accepted input."""
        first = self.history[0]
        if not isinstance(first, Accepted):
            msg = "a history begins with its accepted input"
            raise TypeError(msg)
        return first.input

    @property
    def revision(self) -> int:
        """How many entries the history holds."""
        return len(self.history)

    @property
    def evidence(self) -> tuple[Evidence, ...]:
        """Every admitted piece of evidence, in admission order."""
        return tuple(e.evidence for e in self.history if isinstance(e, Admitted))

    @property
    def intents(self) -> dict[EffectIdentity, BaseModel]:
        """Every committed intent and its request."""
        return {e.identity: e.request for e in self.history if isinstance(e, Intended)}

    def attempts(self, identity: EffectIdentity) -> tuple[Attempted, ...]:
        """The attempts of one identity, in order."""
        return tuple(e for e in self.history if isinstance(e, Attempted) and e.identity == identity)

    def said(self, interaction: Interaction) -> tuple[Evidence, ...]:
        """The evidence an interaction's source has said, in admission order."""
        return tuple(e for e in self.evidence if interaction.says(type(e.value)))

    def _with(self, entry: Entry) -> Invocation:
        return Invocation(id=self.id, history=(*self.history, entry))


class NotAccepted(BaseModel):
    """The input is not an instance of what the program accepts."""

    model_config = RECORDED

    expected: type[BaseModel]
    given: type[BaseModel]


class Unmatched(BaseModel):
    """No receive declared for the source admits the payload."""

    model_config = RECORDED

    source: Source
    tried: tuple[type[BaseModel], ...]
    errors: tuple[str, ...]


class Ambiguous(BaseModel):
    """More than one declared receive of the source admits the payload."""

    model_config = RECORDED

    source: Source
    admitted: tuple[type[BaseModel], ...]


class Uncorrelated(BaseModel):
    """The delivery is not tied to this invocation: a declared equality does not hold, or the
    payload is what a solicited receive with no field correlation says and the delivery names
    no intent."""

    model_config = RECORDED

    received: type[BaseModel]
    correlation: Correlation | None
    found: SerializeAsAny[BaseModel] | None = None
    expected: SerializeAsAny[BaseModel] | None = None


class UnknownIntent(BaseModel):
    """The delivery answers an intent this invocation never committed, or one no interaction
    with this source sent."""

    model_config = RECORDED

    received: type[BaseModel] | None
    answers: EffectIdentity


class Closed(BaseModel):
    """The receive says nothing more: it was satisfied, or its declared closing evidence was
    admitted, at the evidence named."""

    model_config = RECORDED

    received: type[BaseModel]
    by: int


class Conflict(BaseModel):
    """A second payload under a delivery identity already admitted, differing from the first."""

    model_config = RECORDED

    delivery: DeliveryId
    prior: int


class Unintended(BaseModel):
    """An attempt was recorded for an identity with no committed intent."""

    model_config = RECORDED

    identity: EffectIdentity


class Settled(BaseModel):
    """An attempt was recorded for an identity the party already answered."""

    model_config = RECORDED

    identity: EffectIdentity
    evidence: int


class Unrecognized(BaseModel):
    """An attempt's reported result is not a declared result, or its reported receipt is not the
    declared receipt, or the interaction declares none."""

    model_config = RECORDED

    identity: EffectIdentity
    tried: tuple[type[BaseModel], ...]
    errors: tuple[str, ...]


type Reason = (
    NotAccepted
    | Unmatched
    | Ambiguous
    | Uncorrelated
    | UnknownIntent
    | Closed
    | Conflict
    | Unintended
    | Settled
    | Unrecognized
)


class Refusal(Exception):  # noqa: N818  a refusal is a boundary decision, not an error
    """The protocol refused to record something, for the structured reason it carries. The
    history is unchanged. It is raised, as Pydantic raises ``ValidationError``, so that a caller
    who does not handle it cannot proceed as if the record were made."""

    def __init__(self, reason: Reason) -> None:
        super().__init__(repr(reason))
        self.reason: Reason = reason


def accept(program: Program, identity: InvocationId, given: BaseModel) -> Invocation:
    """Open an invocation of the program with its accepted input."""
    if not isinstance(given, program.accepts):
        raise Refusal(NotAccepted(expected=program.accepts, given=type(given)))
    return Invocation(id=identity, history=(Accepted(input=given),))


def validated(
    payload: str, kinds: tuple[type[BaseModel], ...]
) -> tuple[list[BaseModel], tuple[str, ...]]:
    """The payload validated in JSON mode as each kind that admits it, and the errors of those
    that do not."""
    admitted: list[BaseModel] = []
    errors: list[str] = []
    for kind in kinds:
        try:
            admitted.append(TypeAdapter(kind).validate_json(payload))
        except ValidationError as refusal:
            errors.append(f"{kind.__name__}: " + "; ".join(e["msg"] for e in refusal.errors()))
    return admitted, tuple(errors)


def correlated(invocation: Invocation, interaction: Interaction, value: BaseModel) -> None:
    """Check each declared equality between the received value and the accepted input."""
    for correlation in interaction.correlated:
        found = at(value, correlation.received)
        expected = at(invocation.input, correlation.subject)
        if found != expected:
            raise Refusal(
                Uncorrelated(
                    received=type(value),
                    correlation=correlation,
                    found=found if isinstance(found, BaseModel) else None,
                    expected=expected if isinstance(expected, BaseModel) else None,
                )
            )


def closed(
    program: Program, invocation: Invocation, interaction: Interaction, kind: type[BaseModel]
) -> None:
    """Refuse a receive that says nothing more: one held as a single record and already said,
    or one whose declared closing evidence is admitted."""
    said = invocation.said(interaction)
    if program.analysis.held.get(kind, None) is None and said:
        raise Refusal(Closed(received=kind, by=said[0].id))
    if interaction.closed_by is not None:
        closing = [e for e in invocation.evidence if isinstance(e.value, interaction.closed_by)]
        if closing:
            raise Refusal(Closed(received=kind, by=closing[0].id))


def admit(program: Program, invocation: Invocation, delivery: Delivery) -> Invocation:
    """Admit a delivery as evidence, or refuse it.

    The receive is selected by the declared tie, then the payload is validated as what that
    receive says. A delivery naming the intent it answers is for the interaction that sent that
    intent, which must be committed here; shape alone cannot select among a source's records,
    since two may have one shape. A delivery naming no intent is for the source's unsolicited
    receives and its solicited receives with a field correlation; it must validate as exactly
    one of what they say. A delivery already admitted under its identity is one claim: the same
    payload changes nothing, a different one is a conflict. Every declared correlation must
    hold, and a receive that says nothing more refuses.
    """
    at_source = [i for i in program.interactions if i.source == delivery.source]
    if delivery.answers is not None:
        sent = program.sending(delivery.answers.operation)
        if sent is None or sent not in at_source or delivery.answers not in invocation.intents:
            raise Refusal(UnknownIntent(received=None, answers=delivery.answers))
        eligible = [sent]
    else:
        eligible = [i for i in at_source if i.sends is None or i.correlated]
    candidates: list[tuple[Interaction, BaseModel]] = []
    errors: list[str] = []
    for interaction in eligible:
        admitted, refused = validated(delivery.payload, interaction.receives)
        candidates.extend((interaction, value) for value in admitted)
        errors.extend(refused)
    if not candidates:
        elsewhere = [i for i in at_source if i not in eligible]
        said = [type(v) for i in elsewhere for v in validated(delivery.payload, i.receives)[0]]
        if said and delivery.answers is not None:
            raise Refusal(UnknownIntent(received=said[0], answers=delivery.answers))
        if said:
            raise Refusal(Uncorrelated(received=said[0], correlation=None))
        tried = tuple(kind for i in eligible for kind in i.receives)
        raise Refusal(Unmatched(source=delivery.source, tried=tried, errors=tuple(errors)))
    if len(candidates) > 1:
        kinds = tuple(type(value) for _, value in candidates)
        raise Refusal(Ambiguous(source=delivery.source, admitted=kinds))
    interaction, value = candidates[0]
    for prior in invocation.evidence:
        if prior.origin == Delivered(delivery=delivery.id):
            if prior.value == value:
                return invocation
            raise Refusal(Conflict(delivery=delivery.id, prior=prior.id))
    correlated(invocation, interaction, value)
    closed(program, invocation, interaction, type(value))
    evidence = Evidence(
        id=invocation.revision,
        source=delivery.source,
        value=value,
        origin=Delivered(delivery=delivery.id),
        answers=delivery.answers,
    )
    return invocation._with(Admitted(evidence=evidence))  # pyright: ignore[reportPrivateUsage]


def intend(invocation: Invocation, dispatches: tuple[Dispatch, ...]) -> Invocation:
    """Commit each proposed dispatch's intent that is not yet committed."""
    for dispatch in dispatches:
        if dispatch.identity not in invocation.intents:
            entry = Intended(identity=dispatch.identity, request=dispatch.request)
            invocation = invocation._with(entry)  # pyright: ignore[reportPrivateUsage]
    return invocation


def _attempting(invocation: Invocation, identity: EffectIdentity) -> int:
    """The number of the next attempt of a committed, unanswered intent."""
    if identity not in invocation.intents:
        raise Refusal(Unintended(identity=identity))
    for attempt in invocation.attempts(identity):
        if isinstance(attempt.outcome, Answered):
            raise Refusal(Settled(identity=identity, evidence=attempt.outcome.evidence))
    return len(invocation.attempts(identity)) + 1


def perform(
    program: Program, invocation: Invocation, identity: EffectIdentity, result: str
) -> Invocation:
    """Record that an attempt of a committed intent returned the result: it becomes evidence
    answering the intent, in the same step as the attempt.

    The capability reports whether what came back is the result or a receipt; this function
    is the report of a result. The payload's shape cannot establish that, since a receipt may
    have the shape of a result."""
    number = _attempting(invocation, identity)
    interaction = program.sending(identity.operation)
    if interaction is None:
        raise Refusal(Unintended(identity=identity))
    results, errors = validated(result, interaction.receives)
    if len(results) > 1:
        kinds = tuple(type(value) for value in results)
        raise Refusal(Ambiguous(source=interaction.source, admitted=kinds))
    if not results:
        raise Refusal(Unrecognized(identity=identity, tried=interaction.receives, errors=errors))
    evidence = Evidence(
        id=invocation.revision,
        source=interaction.source,
        value=results[0],
        origin=Returned(identity=identity, attempt=number),
        answers=identity,
    )
    attempt = Attempted(identity=identity, number=number, outcome=Answered(evidence=evidence.id))
    return invocation._with(Admitted(evidence=evidence))._with(attempt)  # pyright: ignore[reportPrivateUsage]


def acknowledge(
    program: Program, invocation: Invocation, identity: EffectIdentity, receipt: str
) -> Invocation:
    """Record that an attempt of a committed intent returned the declared receipt: the party
    accepted the request and will say the result later. The receipt is recorded against the
    attempt; no evidence is admitted and the receive stays outstanding."""
    number = _attempting(invocation, identity)
    interaction = program.sending(identity.operation)
    if interaction is None:
        raise Refusal(Unintended(identity=identity))
    if interaction.acknowledges is None:
        raise Refusal(Unrecognized(identity=identity, tried=(), errors=()))
    receipts, errors = validated(receipt, (interaction.acknowledges,))
    if not receipts:
        tried = (interaction.acknowledges,)
        raise Refusal(Unrecognized(identity=identity, tried=tried, errors=errors))
    attempt = Attempted(identity=identity, number=number, outcome=Acknowledged(receipt=receipts[0]))
    return invocation._with(attempt)  # pyright: ignore[reportPrivateUsage]


def failed(invocation: Invocation, identity: EffectIdentity, reason: str) -> Invocation:
    """Record that an attempt did not happen."""
    number = _attempting(invocation, identity)
    attempt = Attempted(identity=identity, number=number, outcome=Failed(reason=reason))
    return invocation._with(attempt)  # pyright: ignore[reportPrivateUsage]


def uncertain(invocation: Invocation, identity: EffectIdentity, reason: str) -> Invocation:
    """Record that an attempt's outcome is not known."""
    number = _attempting(invocation, identity)
    attempt = Attempted(identity=identity, number=number, outcome=Uncertain(reason=reason))
    return invocation._with(attempt)  # pyright: ignore[reportPrivateUsage]
