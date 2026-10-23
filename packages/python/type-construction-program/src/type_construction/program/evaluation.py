"""Pure evaluation of one invocation: the next justified work, from the history alone.

``evaluate`` takes a program and an invocation and returns one of three results. ``Completed``
holds the constructed goal. ``Frontier`` holds the dispatches the host may perform now and the
receives that are outstanding; either may be empty, not both. ``Blocked`` holds structured
reasons why the goal cannot be constructed from the declared sources however much evidence
arrives: a declared condition refuted over the evidence, a source that answered with another
member than the premise needs, a construction that failed, or alternatives that both hold.

Four conditions, three results. Actionable and waiting are not exclusive states of an
invocation: one invocation may have a request to send and a receive outstanding at once, so they
are the two parts of one frontier rather than two variants.

Evaluation constructs pure values through Pydantic, with ``Refusals`` as the validation context
so that a refutable kind's own refusal is told from a malformed construction. It reads no clock,
performs no effect, allocates no identity that is not derived from the history, and memoizes
one construction per premise annotation within one evaluation. An attempt that failed leaves
its intent dispatchable under the same identity. An attempt whose outcome is uncertain leaves it
outstanding and not dispatchable; which is right is the capability's recovery contract, not a
business conclusion.

This evaluator binds a premise to evidence by the premise's declared class and the program's
declared locations, which the program validated to be unique. It is the depth the contract
experiments need. Occurrence binding where one class is demanded at two sites of one invocation
is outcome 2.
"""

from dataclasses import dataclass
from typing import cast

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SerializeAsAny,
    ValidationError,
    model_validator,
)

from type_construction.world import Refusals, Refutable

from .declaration import (
    Interaction,
    Location,
    Program,
    Source,
    alternatives,
    collection,
    constant,
    premises,
    qualified,
)
from .invocation import (
    Acknowledged,
    Answered,
    Attempted,
    Dispatch,
    EffectIdentity,
    Evidence,
    Failed,
    Invocation,
    Uncertain,
)

RESULT = ConfigDict(frozen=True, strict=True, extra="forbid", validate_default=True)
"""Configuration for an evaluation result: strict, frozen, no undeclared fields."""


class Refutation(BaseModel):
    """A declared condition did not hold over validated evidence."""

    model_config = RESULT

    premise: str
    kind: type[BaseModel]
    refused: tuple[str, ...]


class AnsweredOtherwise(BaseModel):
    """The source answered with another of its declared records than this premise needs."""

    model_config = RESULT

    premise: str
    expected: type[BaseModel]
    answered: type[BaseModel]
    evidence: int


class Malformed(BaseModel):
    """Construction from available evidence failed for a reason that is not a declared
    condition: a defect of the program or of the evidence, not a business conclusion."""

    model_config = RESULT

    premise: str
    kind: type[BaseModel]
    errors: tuple[str, ...]


class Indeterminate(BaseModel):
    """More than one alternative constructed; the declaration does not say which holds."""

    model_config = RESULT

    premise: str
    members: tuple[type[BaseModel], ...]


type Reason = Refutation | AnsweredOtherwise | Malformed | Indeterminate


class Solicited(BaseModel):
    """A send was performed; the source has not said the result. With ``acknowledged``, the
    source accepted the request and will say it later."""

    model_config = RESULT

    receives: tuple[type[BaseModel], ...]
    source: Source
    identity: EffectIdentity
    attempt: int
    acknowledged: SerializeAsAny[BaseModel] | None = None


class Unsolicited(BaseModel):
    """Nothing is sent; a correlated delivery from the source supplies the premise."""

    model_config = RESULT

    receives: tuple[type[BaseModel], ...]
    source: Source


class Unresolved(BaseModel):
    """An attempt's outcome is unknown. The intent is not dispatched again here; the capability's
    recovery contract resolves it."""

    model_config = RESULT

    identity: EffectIdentity
    attempt: int
    reason: str


class Unclosed(BaseModel):
    """The source may say more; the premise holds every item it says, so it waits for the
    declared closing evidence. ``held`` is how many items have been said so far."""

    model_config = RESULT

    element: type[BaseModel]
    source: Source
    closing: type[BaseModel]
    held: int


type Awaiting = Solicited | Unsolicited | Unresolved | Unclosed


class Completed(BaseModel):
    """The goal is constructed."""

    model_config = RESULT

    goal: SerializeAsAny[BaseModel]


class Frontier(BaseModel):
    """The next justified work: requests to dispatch now, and receives outstanding."""

    model_config = RESULT

    dispatch: tuple[Dispatch, ...] = ()
    awaiting: tuple[Awaiting, ...] = ()

    @model_validator(mode="after")
    def _some(self) -> Frontier:
        if not self.dispatch and not self.awaiting:
            msg = "a frontier with nothing to dispatch and nothing awaited is not a frontier"
            raise ValueError(msg)
        return self


class Blocked(BaseModel):
    """The goal cannot be constructed from the declared sources, for these reasons."""

    model_config = RESULT

    reasons: tuple[Reason, ...] = Field(min_length=1)


type Evaluation = Completed | Frontier | Blocked


@dataclass(frozen=True)
class Available:
    """The premise is constructed, from the evidence at these history positions."""

    value: object
    premises: frozenset[int]


@dataclass(frozen=True)
class Open:
    """The premise is not yet constructed, and declared work may supply it."""

    dispatch: dict[EffectIdentity, Dispatch]
    awaiting: dict[object, Awaiting]

    def merged(self, other: Open) -> Open:
        return Open({**self.dispatch, **other.dispatch}, {**self.awaiting, **other.awaiting})


@dataclass(frozen=True)
class Refuted:
    """A declared condition did not hold, or the source answered otherwise; no further evidence
    constructs this premise."""

    reasons: tuple[Reason, ...]


@dataclass(frozen=True)
class Stuck:
    """Construction cannot proceed for a reason that is not a business conclusion."""

    reasons: tuple[Reason, ...]


type Outcome = Available | Open | Refuted | Stuck


def distinct(reasons: list[Reason]) -> tuple[Reason, ...]:
    """The reasons once each, in first-seen order: a premise refuted once is reported once,
    however many paths reach it."""
    return tuple(dict.fromkeys(reasons))


def awaiting(interaction: Interaction, how: Awaiting) -> Open:
    """An open outcome awaiting one receive."""
    return Open({}, {(interaction.source, interaction.receives, type(how)): how})


class Evaluator:
    """One evaluation of one invocation; see ``evaluate``."""

    def __init__(self, program: Program, invocation: Invocation) -> None:
        self.program = program
        self.invocation = invocation
        self.memo: dict[object, Outcome] = {}

    def construct(self, annotation: object, path: str) -> Outcome:
        """The outcome of constructing one premise annotation, once per evaluation."""
        if annotation in self.memo:
            return self.memo[annotation]
        outcome = self._construct(annotation, path)
        self.memo[annotation] = outcome
        return outcome

    def _construct(self, annotation: object, path: str) -> Outcome:
        members = alternatives(annotation)
        if members is not None:
            return self._alternatives(members, path)
        shape = collection(annotation)
        if shape is not None:
            return self._collection(annotation, shape[0], path)
        if not (isinstance(annotation, type) and issubclass(annotation, BaseModel)):
            msg = f"{path}: {annotation!r} passed program validation and is not a premise"
            raise TypeError(msg)
        interaction = self.program.receiving(annotation)
        if interaction is not None:
            return self._received(interaction, annotation, path)
        location = self.program.analysis.located.get(annotation)
        if location is not None:
            return self._located(location, path)
        return self._composed(annotation, path)

    def _alternatives(self, members: tuple[type[BaseModel], ...], path: str) -> Outcome:
        outcomes = [(m, self.construct(m, f"{path}.{m.__name__}")) for m in members]
        available = [(m, o) for m, o in outcomes if isinstance(o, Available)]
        if len(available) == 1:
            return available[0][1]
        if available:
            held = tuple(m for m, _ in available)
            return Stuck((Indeterminate(premise=path, members=held),))
        stuck = [o for _, o in outcomes if isinstance(o, Stuck)]
        if stuck:
            return Stuck(distinct([r for o in stuck for r in o.reasons]))
        opens = [o for _, o in outcomes if isinstance(o, Open)]
        if opens:
            merged = Open({}, {})
            for o in opens:
                merged = merged.merged(o)
            return merged
        return Refuted(
            distinct([r for _, o in outcomes if isinstance(o, Refuted) for r in o.reasons])
        )

    def _said(self, interaction: Interaction) -> tuple[Evidence, ...]:
        return self.invocation.said(interaction)

    def _received(self, interaction: Interaction, kind: type[BaseModel], path: str) -> Outcome:
        said = self._said(interaction)
        if said:
            evidence = said[0]
            if isinstance(evidence.value, kind):
                return Available(evidence.value, frozenset({evidence.id}))
            reason = AnsweredOtherwise(
                premise=path, expected=kind, answered=type(evidence.value), evidence=evidence.id
            )
            return Refuted((reason,))
        return self._outstanding(interaction, path)

    def _outstanding(self, interaction: Interaction, path: str) -> Outcome:
        """A receive nothing has satisfied: the send to dispatch, or the wait."""
        if interaction.sends is None:
            how = Unsolicited(receives=interaction.receives, source=interaction.source)
            return awaiting(interaction, how)
        request = self.construct(interaction.sends, f"{path}.{interaction.sends.__name__}")
        if not isinstance(request, Available):
            return request
        if not isinstance(request.value, BaseModel):
            msg = f"{path}: a request is a declared class"
            raise TypeError(msg)
        identity = EffectIdentity(
            invocation=self.invocation.id,
            operation=qualified(interaction.sends),
            premises=tuple(sorted(request.premises)),
        )
        attempts = self.invocation.attempts(identity)
        last: Attempted | None = attempts[-1] if attempts else None
        if last is None or isinstance(last.outcome, Failed):
            dispatch = Dispatch(identity=identity, request=request.value, attempt=len(attempts) + 1)
            return Open({identity: dispatch}, {})
        return awaiting(interaction, self._after(interaction, identity, last, path))

    def _after(
        self, interaction: Interaction, identity: EffectIdentity, last: Attempted, path: str
    ) -> Awaiting:
        """What is awaited after an attempt that neither failed nor was answered."""
        match last.outcome:
            case Acknowledged(receipt=receipt):
                return Solicited(
                    receives=interaction.receives,
                    source=interaction.source,
                    identity=identity,
                    attempt=last.number,
                    acknowledged=receipt,
                )
            case Uncertain(reason=reason):
                return Unresolved(identity=identity, attempt=last.number, reason=reason)
            case Answered() | Failed():
                msg = f"{path}: attempt {last.number} was {type(last.outcome).__name__}"
                raise RuntimeError(msg)

    def _collection(self, annotation: object, element: type[BaseModel], path: str) -> Outcome:
        interaction = self.program.receiving(element)
        if interaction is not None:
            return self._accumulated(interaction, element, path)
        location = self.program.analysis.located.get(annotation)
        if location is None:
            msg = f"{path}: {annotation!r} passed program validation without a location"
            raise TypeError(msg)
        return self._located(location, path)

    def _accumulated(
        self, interaction: Interaction, element: type[BaseModel], path: str
    ) -> Outcome:
        """Every item a source says, available once the declared closing evidence is."""
        closer = interaction.closed_by
        if closer is None:
            msg = f"{path}: a collection from {interaction.source.root} has no closure"
            raise TypeError(msg)
        said = self._said(interaction)
        closing = [e for e in self.invocation.evidence if isinstance(e.value, closer)]
        if closing:
            values = tuple(e.value for e in said)
            return Available(values, frozenset(e.id for e in said) | {closing[0].id})
        how = Unclosed(element=element, source=interaction.source, closing=closer, held=len(said))
        match self.construct(closer, f"{path}.closed_by"):
            case Open() as outcome:
                return outcome.merged(awaiting(interaction, how))
            case Available():
                msg = f"{path}: {closer.__name__} is available and no closing evidence is admitted"
                raise RuntimeError(msg)
            case Refuted() | Stuck() as outcome:
                return outcome

    def _located(self, location: Location, path: str) -> Outcome:
        """A value found at a declared location: inside the input, a received record, or each
        element of a received collection."""
        if location.container is self.program.accepts:
            container: Outcome = Available(self.invocation.input, frozenset({0}))
        elif location.projected:
            container = self.construct(
                tuple[location.container, ...], f"{path}.{location.container.__name__}"
            )
        else:
            container = self.construct(location.container, f"{path}.{location.container.__name__}")
        if not isinstance(container, Available):
            return container
        if location.projected:
            if not isinstance(container.value, tuple):
                msg = f"{path}: a projected location is over a collection"
                raise TypeError(msg)
            elements = cast("tuple[object, ...]", container.value)
            return Available(tuple(_at(e, location.path) for e in elements), container.premises)
        return Available(_at(container.value, location.path), container.premises)

    def _composed(self, kind: type[BaseModel], path: str) -> Outcome:
        """A class constructed from its premises through Pydantic."""
        if constant(kind):
            return Available(kind(), frozenset())
        given: dict[str, object] = {}
        used: set[int] = set()
        opens: list[Open] = []
        refuted: list[Reason] = []
        stuck: list[Reason] = []
        for name, annotation in premises(kind):
            outcome = self.construct(annotation, f"{path}.{name}")
            match outcome:
                case Available(value, ids):
                    given[name] = value
                    used |= ids
                case Open():
                    opens.append(outcome)
                case Refuted(reasons):
                    refuted.extend(reasons)
                case Stuck(reasons):
                    stuck.extend(reasons)
        if stuck:
            return Stuck(distinct(stuck))
        if refuted:
            return Refuted(distinct(refuted))
        if opens:
            merged = Open({}, {})
            for o in opens:
                merged = merged.merged(o)
            return merged
        return self._validated(kind, given, frozenset(used), path)

    def _validated(
        self, kind: type[BaseModel], given: dict[str, object], used: frozenset[int], path: str
    ) -> Outcome:
        """The class validated by Pydantic over its constructed premises: available, refuted by
        its own declared condition, or malformed."""
        refusals = Refusals()
        try:
            value = kind.model_validate(given, context=refusals)
        except ValidationError as refusal:
            messages = tuple(e["msg"] for e in refusal.errors())
            if issubclass(kind, Refutable) and kind.refuted(refusal, refusals):
                return Refuted((Refutation(premise=path, kind=kind, refused=messages),))
            return Stuck((Malformed(premise=path, kind=kind, errors=messages),))
        return Available(value, used)


def _at(value: object, path: tuple[str, ...]) -> object:
    for name in path:
        value = getattr(value, name)
    return value


def evaluate(program: Program, invocation: Invocation) -> Evaluation:
    """The next justified work of an invocation, from its history."""
    outcome = Evaluator(program, invocation).construct(program.goal, program.goal.__name__)
    match outcome:
        case Available(value, _):
            if not isinstance(value, BaseModel):
                msg = "a goal is a declared class"
                raise TypeError(msg)
            return Completed(goal=value)
        case Open(dispatch, awaited):
            return Frontier(dispatch=tuple(dispatch.values()), awaiting=tuple(awaited.values()))
        case Refuted(reasons) | Stuck(reasons):
            return Blocked(reasons=reasons)
