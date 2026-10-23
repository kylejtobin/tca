"""One invocation's recorded history, and the protocol by which it grows.

An invocation is one accepted pursuit of a program's goal. Its history is append-only: the
accepted input, each piece of admitted evidence, each effect intent committed before dispatch,
and each attempt's outcome. The position of an entry in the history is its identity within the
invocation; the evaluator reads the history and nothing else.

An occurrence is where a value comes from, not what class it has. A ``Site`` is a value found
in the history: the evidence it is in and the path to it, element indices included, so the two
lines of one order are two occurrences however equal their content. A ``Built`` is a value
constructed from premises: the class and the occurrence of each premise. ``Elements`` is a
collection of occurrences. An ``EffectIdentity`` is one logical external operation: the
invocation, the request class sent, and the occurrence of the request. It is derived, so the
same history yields the same identity; it is recorded, because dispatch follows the record.
Attempts of one identity are numbered; a retry is a new attempt, not a new identity. A request
built from a different element, or from different evidence, is a different operation; a request
built from the same occurrences is the same one, however many premises hold it.

The functions here are the host protocol in its smallest form. ``accept`` opens an invocation.
``intend`` commits the evaluator's proposed dispatches before anything is sent. Every claim about
the world then passes through one admission, whether it arrives as a delivery (``admit``) or comes
back inside an attempt (``perform``): the receive is selected by the request the claim answers or
by its declared correlation, the payload is validated as what that receive says, a repeated claim
is one claim and a conflicting one is refused, every declared equality is checked, a claim for a
solicited receive must answer a request this invocation committed, and a receive that says
nothing more refuses. A returned payload is not evidence until it passes the same admission a
delivery does. ``acknowledge``, ``failed`` and ``uncertain`` record what else an attempt produced,
as the capability reports it: a receipt, which satisfies no premise; a failure that did not
happen; or an outcome that is not known. Which of these came back is the capability's report, not
an inference from the payload's shape: a receipt may have the shape of a result. Nothing here
calls an external system, reads a clock, or decides a business branch.

These are in-memory records for contract experiments. They are not a durable codec, and nothing
here demonstrates recovery, concurrency or worker ownership.
"""

from typing import cast

from pydantic import BaseModel, ConfigDict, Field, SerializeAsAny, TypeAdapter, ValidationError

from type_construction.world import Scalar

from .declaration import EACH, Correlation, Interaction, Program, Source, steps

RECORDED = ConfigDict(frozen=True, strict=True, extra="forbid", validate_default=True)
"""Configuration for a recorded entry: strict, frozen, no undeclared fields."""


class InvocationId(Scalar[str]):
    """One accepted pursuit of a goal."""

    root: str = Field(min_length=1)


class DeliveryId(Scalar[str]):
    """A delivery's transport identity, as the source and transport establish it. Two deliveries
    with one identity are one claim."""

    root: str = Field(min_length=1)


class Site(BaseModel):
    """A value found in the history: the evidence it is in and the path to it, with field names
    and element indices. Two elements of one collection are two sites."""

    model_config = RECORDED

    evidence: int
    path: tuple[str | int, ...] = ()

    def __hash__(self) -> int:
        return hash((self.evidence, self.path))

    def within(self, *more: str | int) -> Site:
        """The site further along the path."""
        return Site(evidence=self.evidence, path=(*self.path, *more))


class Built(BaseModel):
    """A value constructed from premises: the class and the occurrence of each premise, in
    field order. A constant, constructed from nothing, has no parts."""

    model_config = RECORDED

    kind: str
    parts: tuple[tuple[str, "Occurrence"], ...] = ()

    def __hash__(self) -> int:
        return hash((self.kind, self.parts))


class Elements(BaseModel):
    """A collection of occurrences, in element order."""

    model_config = RECORDED

    of: tuple["Occurrence", ...]

    def __hash__(self) -> int:
        return hash(self.of)


type Occurrence = Site | Built | Elements
"""Where a value comes from: found at a site, built from premises, or a collection of them."""


class EffectIdentity(BaseModel):
    """One logical external operation of one invocation.

    The invocation keeps two invocations' operations apart. The request class keeps two
    intended operations apart when their request bodies are equal. The occurrence of the
    request keeps apart two requests built from different elements or different evidence,
    equal or not in content, and makes one of two requests built from the same occurrences.
    Nothing about the request's payload, or any attempt, is part of it.
    """

    model_config = RECORDED

    invocation: InvocationId
    operation: str
    """The durable name of the request class sent."""
    occurrence: Occurrence
    """How the request was constructed: the occurrence of each premise."""

    def __hash__(self) -> int:
        return hash((self.invocation.root, self.operation, self.occurrence))


class Delivered(BaseModel):
    """Evidence came in a delivery."""

    model_config = RECORDED

    delivery: DeliveryId


class Returned(BaseModel):
    """Evidence came back inside an attempt of a send."""

    model_config = RECORDED

    identity: EffectIdentity
    attempt: int


class Delivery(BaseModel):
    """An external claim presented for admission: who says it, its transport identity, the
    payload as received, and, when the party echoes it, the intent it answers."""

    model_config = RECORDED

    source: Source
    id: DeliveryId
    payload: str
    """The payload as JSON text; admission validates it in JSON mode."""
    answers: EffectIdentity | None = None


class Claim(BaseModel):
    """What admission judges, whatever brought it: the party, how it came, the payload as the
    party gave it, and the request it answers when that is known."""

    model_config = RECORDED

    source: Source
    origin: Delivered | Returned
    payload: str
    answers: EffectIdentity | None = None


class Evidence(BaseModel):
    """An admitted record: the value, its source, where it came from, the intent it answers when
    it answers one, and the input element it correlates to when its correlation enters a
    collection. Its ``id`` is its position in the history."""

    model_config = RECORDED

    id: int
    source: Source
    value: SerializeAsAny[BaseModel]
    origin: Delivered | Returned
    answers: EffectIdentity | None = None
    element: Site | None = None


class Accepted(BaseModel):
    """The input the invocation was accepted with; always at position 0."""

    model_config = RECORDED

    input: SerializeAsAny[BaseModel]


class Admitted(BaseModel):
    """A piece of evidence was admitted."""

    model_config = RECORDED

    evidence: Evidence


class Intended(BaseModel):
    """An effect intent was committed, before dispatch. ``elements`` are the input elements the
    request was constructed for, when it is one of many."""

    model_config = RECORDED

    identity: EffectIdentity
    request: SerializeAsAny[BaseModel]
    elements: tuple[Site, ...] = ()


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
    ``attempt``, constructed for the input ``elements`` when it is one of many."""

    model_config = RECORDED

    identity: EffectIdentity
    request: SerializeAsAny[BaseModel]
    attempt: int = Field(ge=1)
    elements: tuple[Site, ...] = ()


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
    def committed(self) -> tuple[Intended, ...]:
        """Every committed intent, in order."""
        return tuple(e for e in self.history if isinstance(e, Intended))

    @property
    def intents(self) -> dict[EffectIdentity, BaseModel]:
        """Every committed intent and its request."""
        return {e.identity: e.request for e in self.committed}

    def answered(self, identity: EffectIdentity) -> Evidence | None:
        """The evidence that answers an intent, if any."""
        for e in self.evidence:
            if e.answers == identity:
                return e
        return None

    def intended(self, identity: EffectIdentity) -> Intended:
        """The committed intent with this identity."""
        for e in self.committed:
            if e.identity == identity:
                return e
        raise Refusal(Unintended(identity=identity))

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
    """More than one declared receive of the source admits the payload, or more than one element
    of the input matches its correlation, or more than one committed request could be the one
    the payload answers."""

    model_config = RECORDED

    source: Source
    admitted: tuple[type[BaseModel], ...]
    elements: tuple[Site, ...] = ()
    intents: tuple[EffectIdentity, ...] = ()


class Uncorrelated(BaseModel):
    """The delivery is not tied to this invocation: a declared equality does not hold at any
    element, or the payload is what a solicited receive says, the receive has no field
    correlation or varies per element, and the delivery names no intent."""

    model_config = RECORDED

    received: type[BaseModel]
    correlation: Correlation | None
    found: SerializeAsAny[BaseModel] | None = None
    expected: tuple[SerializeAsAny[BaseModel], ...] = ()


class Unrequested(BaseModel):
    """The payload is what a solicited receive says, and this invocation has committed no request
    it could answer: the source said it, and this program did not ask. It is not evidence for a
    premise obtained by asking."""

    model_config = RECORDED

    received: type[BaseModel]
    sends: type[BaseModel]


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
    """A second payload under an origin already admitted, differing from the first."""

    model_config = RECORDED

    delivery: Delivered | Returned
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
    | Unrequested
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


def at(value: object, path: str) -> object:
    """The value at a dotted field path that enters no collection."""
    for name in steps(path):
        value = getattr(value, name)
    return value


def everywhere(value: object, site: Site, path: tuple[str, ...]) -> list[tuple[object, Site]]:
    """Every value at a path that may enter collections, each with its site."""
    if not path:
        return [(value, site)]
    name, *rest = path
    if name == EACH:
        if not isinstance(value, tuple):
            msg = f"{site!r}: {EACH} enters a collection, and this is not one"
            raise TypeError(msg)
        elements: list[tuple[object, Site]] = []
        for index, item in enumerate(cast("tuple[object, ...]", value)):
            elements.extend(everywhere(item, site.within(index), tuple(rest)))
        return elements
    return everywhere(getattr(value, name), site.within(name), tuple(rest))


def correlated(
    program: Program, invocation: Invocation, interaction: Interaction, value: BaseModel
) -> Site | None:
    """Check each declared equality between the received value and the accepted input, and
    return the one input element the record is tied to when a subject path enters a collection.
    Equality at no element is uncorrelated; at more than one, ambiguous: the declaration does
    not tell those elements apart."""
    element: Site | None = None
    for correlation in interaction.correlated:
        found = at(value, correlation.received)
        candidates = everywhere(invocation.input, Site(evidence=0), steps(correlation.subject))
        matching = [site for expected, site in candidates if expected == found]
        if not matching:
            raise Refusal(
                Uncorrelated(
                    received=type(value),
                    correlation=correlation,
                    found=found if isinstance(found, BaseModel) else None,
                    expected=tuple(e for e, _ in candidates if isinstance(e, BaseModel)),
                )
            )
        if not program.subject_collections(correlation):
            continue
        if len(matching) > 1:
            kinds = (type(value),)
            raise Refusal(
                Ambiguous(source=interaction.source, admitted=kinds, elements=tuple(matching))
            )
        (site,) = matching
        chosen = Site(evidence=0, path=site.path[: steps(correlation.subject).index(EACH) + 1])
        if element is not None and element != chosen:
            kinds = (type(value),)
            raise Refusal(
                Ambiguous(source=interaction.source, admitted=kinds, elements=(element, chosen))
            )
        element = chosen
    return element


def requested(
    program: Program, invocation: Invocation, interaction: Interaction, element: Site | None
) -> EffectIdentity:
    """The one committed, unanswered request of an interaction that a claim correlated to
    ``element`` could answer. None is ``Unrequested``: the source said it, this program did not
    ask. More than one is ``Ambiguous``: the declaration ties the claim to no one of them. When
    every request it could answer is answered, the claim is for the answered one, and closure
    judges it as a second answer."""
    sends = interaction.sends
    if sends is None:
        msg = "an unsolicited receive answers no request"
        raise TypeError(msg)
    mine = [
        i.identity
        for i in invocation.committed
        if program.sending(i.identity.operation) is interaction
        and (element is None or element in i.elements)
    ]
    candidates = [identity for identity in mine if invocation.answered(identity) is None]
    if not candidates and mine:
        return mine[-1]
    if not candidates:
        raise Refusal(Unrequested(received=interaction.receives[0], sends=sends))
    if len(candidates) > 1:
        kinds = (interaction.receives[0],)
        intents = tuple(candidates)
        raise Refusal(Ambiguous(source=interaction.source, admitted=kinds, intents=intents))
    return candidates[0]


def closed(invocation: Invocation, interaction: Interaction, arriving: Evidence) -> Evidence | None:
    """Refuse a receive that says nothing more, or return the earlier evidence a claim repeats.

    A collection source is closed by its declared closing evidence. A solicited receive takes one
    answer per request: the same answer again, from a second delivery or from the attempt that
    performed the request, is that one answer; a different answer to an answered request is
    refused. An unsolicited receive is one record per element it correlates to, or per
    invocation."""
    kind = type(arriving.value)
    if interaction.closed_by is not None:
        closing = [e for e in invocation.evidence if isinstance(e.value, interaction.closed_by)]
        if closing:
            raise Refusal(Closed(received=kind, by=closing[0].id))
        return None
    if interaction.sends is not None:
        prior = invocation.answered(arriving.answers) if arriving.answers is not None else None
        if prior is None:
            return None
        if prior.value == arriving.value:
            return prior
        raise Refusal(Closed(received=kind, by=prior.id))
    said = invocation.said(interaction)
    if arriving.element is not None:
        said = tuple(e for e in said if e.element == arriving.element)
    if said:
        raise Refusal(Closed(received=kind, by=said[0].id))
    return None


def selected(
    program: Program, invocation: Invocation, claim: Claim
) -> tuple[Interaction, BaseModel]:
    """The one receive a claim is for and the payload validated as what it says."""
    at_source = [i for i in program.interactions if i.source == claim.source]
    if claim.answers is not None:
        sent = program.sending(claim.answers.operation)
        if sent is None or sent not in at_source or claim.answers not in invocation.intents:
            raise Refusal(UnknownIntent(received=None, answers=claim.answers))
        eligible = [sent]
    else:
        eligible = [i for i in at_source if i.sends is None or i.correlated]
    candidates: list[tuple[Interaction, BaseModel]] = []
    errors: list[str] = []
    for interaction in eligible:
        admitted, refused = validated(claim.payload, interaction.receives)
        candidates.extend((interaction, value) for value in admitted)
        errors.extend(refused)
    if not candidates:
        elsewhere = [i for i in at_source if i not in eligible]
        said = [type(v) for i in elsewhere for v in validated(claim.payload, i.receives)[0]]
        if said and claim.answers is not None:
            raise Refusal(UnknownIntent(received=said[0], answers=claim.answers))
        if said:
            raise Refusal(Uncorrelated(received=said[0], correlation=None))
        tried = tuple(kind for i in eligible for kind in i.receives)
        raise Refusal(Unmatched(source=claim.source, tried=tried, errors=tuple(errors)))
    if len(candidates) > 1:
        kinds = tuple(type(value) for _, value in candidates)
        raise Refusal(Ambiguous(source=claim.source, admitted=kinds))
    return candidates[0]


def admissible(program: Program, invocation: Invocation, claim: Claim) -> Evidence:
    """Judge one claim and return the evidence it is, new at the next position of the history,
    or the earlier evidence it repeats. Raise ``Refusal`` otherwise.

    The receive is selected by the declared tie, then the payload is validated as what that
    receive says. A claim naming the request it answers is for the interaction that sent that
    request, which must be committed here; shape alone cannot select among a source's records,
    since two may have one shape. A claim naming no request is for the source's unsolicited
    receives and its solicited receives with a field correlation; it must validate as exactly one
    of what they say. A claim already admitted under its origin is one claim: the same payload is
    the same evidence, a different one is a conflict. Every declared correlation must hold, at
    exactly one element where the subject is in a collection. A claim for a solicited receive
    answers one committed request, named or the one its correlation selects; with none it is not
    evidence, whatever its source said. A receive that says nothing more refuses.
    """
    interaction, value = selected(program, invocation, claim)
    for prior in invocation.evidence:
        if prior.origin == claim.origin:
            if prior.value == value:
                return prior
            raise Refusal(Conflict(delivery=claim.origin, prior=prior.id))
    element = correlated(program, invocation, interaction, value)
    answers = claim.answers
    if interaction.sends is not None:
        if answers is None:
            if program.varying(interaction) and element is None:
                raise Refusal(Uncorrelated(received=type(value), correlation=None))
            answers = requested(program, invocation, interaction, element)
        elif element is not None and element not in invocation.intended(answers).elements:
            raise Refusal(
                Ambiguous(source=claim.source, admitted=(type(value),), elements=(element,))
            )
    evidence = Evidence(
        id=invocation.revision,
        source=claim.source,
        value=value,
        origin=claim.origin,
        answers=answers,
        element=element,
    )
    repeated = closed(invocation, interaction, evidence)
    return evidence if repeated is None else repeated


def admit(program: Program, invocation: Invocation, delivery: Delivery) -> Invocation:
    """Admit a delivery as evidence through ``admissible``, or refuse it. A delivery that repeats
    admitted evidence changes nothing."""
    claim = Claim(
        source=delivery.source,
        origin=Delivered(delivery=delivery.id),
        payload=delivery.payload,
        answers=delivery.answers,
    )
    evidence = admissible(program, invocation, claim)
    if evidence.id < invocation.revision:
        return invocation
    return invocation._with(Admitted(evidence=evidence))  # pyright: ignore[reportPrivateUsage]


def intend(invocation: Invocation, dispatches: tuple[Dispatch, ...]) -> Invocation:
    """Commit each proposed dispatch's intent that is not yet committed."""
    for dispatch in dispatches:
        if dispatch.identity not in invocation.intents:
            entry = Intended(
                identity=dispatch.identity, request=dispatch.request, elements=dispatch.elements
            )
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
    """Record that an attempt of a committed intent returned the result. The result passes the
    same admission a delivery does, as a claim answering the intent; admitted, it becomes
    evidence in the same step as the attempt. Refused, nothing is recorded: the attempt returned
    something that is not evidence for this invocation, and the host decides what that makes of
    the attempt.

    The capability reports whether what came back is the result or a receipt; this function
    is the report of a result. The payload's shape cannot establish that, since a receipt may
    have the shape of a result."""
    number = _attempting(invocation, identity)
    interaction = program.sending(identity.operation)
    if interaction is None:
        raise Refusal(Unintended(identity=identity))
    claim = Claim(
        source=interaction.source,
        origin=Returned(identity=identity, attempt=number),
        payload=result,
        answers=identity,
    )
    evidence = admissible(program, invocation, claim)
    if evidence.id == invocation.revision:
        invocation = invocation._with(Admitted(evidence=evidence))  # pyright: ignore[reportPrivateUsage]
    attempt = Attempted(identity=identity, number=number, outcome=Answered(evidence=evidence.id))
    return invocation._with(attempt)  # pyright: ignore[reportPrivateUsage]


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
