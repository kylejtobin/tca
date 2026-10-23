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

Construction is by occurrence, not by class. A premise found in the input or in a received record
is the value at that site; a premise found inside a collection is one value per element, and a
tuple of a constructed class is one construction per element of the collection its premises vary
over. Evaluation is scoped: a scope binds each collection in play to one element, and a premise
is constructed once per scope it varies over, so that two sites that depend on the same element
share one occurrence and two elements with equal content do not. A constructed value's
occurrence is the occurrences of its premises, which is what identifies the effect a request
intends: a request built from a different element is a different operation, however equal its
body.

Evaluation constructs pure values through Pydantic, with ``Refusals`` as the validation context
so that a refutable kind's own refusal is told from a malformed construction. It reads no clock,
performs no effect and allocates no identity that is not derived from the history. An attempt
that failed leaves its intent dispatchable under the same identity. An attempt whose outcome is
uncertain leaves it outstanding and not dispatchable; which is right is the capability's
recovery contract, not a business conclusion.
"""

from dataclasses import dataclass
from typing import cast

from pydantic import BaseModel, ConfigDict, Field, SerializeAsAny, ValidationError, model_validator

from type_construction.world import Refusals, Refutable

from .declaration import (
    EACH,
    Collection,
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
    Built,
    Dispatch,
    EffectIdentity,
    Elements,
    Evidence,
    Failed,
    Invocation,
    Occurrence,
    Site,
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

    def __hash__(self) -> int:
        return hash((self.premise, self.kind, self.refused))


class AnsweredOtherwise(BaseModel):
    """The source answered with another of its declared records than this premise needs."""

    model_config = RESULT

    premise: str
    expected: type[BaseModel]
    answered: type[BaseModel]
    evidence: int

    def __hash__(self) -> int:
        return hash((self.premise, self.expected, self.answered, self.evidence))


class Malformed(BaseModel):
    """Construction from available evidence failed for a reason that is not a declared
    condition: a defect of the program or of the evidence, not a business conclusion."""

    model_config = RESULT

    premise: str
    kind: type[BaseModel]
    errors: tuple[str, ...]

    def __hash__(self) -> int:
        return hash((self.premise, self.kind, self.errors))


class Indeterminate(BaseModel):
    """More than one alternative constructed; the declaration does not say which holds."""

    model_config = RESULT

    premise: str
    members: tuple[type[BaseModel], ...]

    def __hash__(self) -> int:
        return hash((self.premise, self.members))


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
    """Nothing is sent; a correlated delivery from the source supplies the premise. With
    ``element``, the delivery must correlate to that element of the input."""

    model_config = RESULT

    receives: tuple[type[BaseModel], ...]
    source: Source
    element: Site | None = None


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
    """The goal is constructed, from the occurrences named."""

    model_config = RESULT

    goal: SerializeAsAny[BaseModel]
    occurrence: Occurrence


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
    """The premise is constructed: its value and its occurrence."""

    value: object
    occurrence: Occurrence


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

type Scope = tuple[tuple[Collection, Site], ...]
"""The element each collection in play is bound to, ordered by the collection's name."""


def distinct(reasons: list[Reason]) -> tuple[Reason, ...]:
    """The reasons once each, in first-seen order: a premise refuted once is reported once,
    however many paths reach it."""
    return tuple(dict.fromkeys(reasons))


def bound(scope: Scope, over: Collection) -> Site | None:
    """The element a collection is bound to in a scope, if any."""
    for each, site in scope:
        if each == over:
            return site
    return None


def binding(scope: Scope, over: Collection, site: Site) -> Scope:
    """The scope with one more collection bound."""
    return tuple(sorted((*scope, (over, site)), key=lambda b: str(b[0])))


def combined(outcomes: list[Outcome]) -> Open | Refuted | Stuck | None:
    """How several premises' outcomes combine when all are needed: a malformed construction
    outranks a refutation, which outranks open work; ``None`` when every one is available."""
    stuck = [r for o in outcomes if isinstance(o, Stuck) for r in o.reasons]
    if stuck:
        return Stuck(distinct(stuck))
    refuted = [r for o in outcomes if isinstance(o, Refuted) for r in o.reasons]
    if refuted:
        return Refuted(distinct(refuted))
    opens = [o for o in outcomes if isinstance(o, Open)]
    if opens:
        merged = Open({}, {})
        for o in opens:
            merged = merged.merged(o)
        return merged
    return None


def awaiting(interaction: Interaction, how: Awaiting, which: object) -> Open:
    """An open outcome awaiting one receive occurrence."""
    return Open({}, {(interaction.source, interaction.receives, type(how), which): how})


class Evaluator:
    """One evaluation of one invocation; see ``evaluate``."""

    def __init__(self, program: Program, invocation: Invocation) -> None:
        self.program = program
        self.invocation = invocation
        self.memo: dict[tuple[object, Scope], Outcome] = {}

    def construct(self, annotation: object, path: str, scope: Scope) -> Outcome:
        """The outcome of constructing one premise annotation in one scope, once per
        evaluation. The scope is reduced to the collections the premise varies over, so two
        sites reaching one occurrence share it."""
        relevant = self.program.analysis.varying(annotation, frozenset(c for c, _ in scope))
        key = (annotation, tuple(b for b in scope if b[0] in relevant))
        if key in self.memo:
            return self.memo[key]
        outcome = self._construct(annotation, path, scope)
        self.memo[key] = outcome
        return outcome

    def _construct(self, annotation: object, path: str, scope: Scope) -> Outcome:
        members = alternatives(annotation)
        if members is not None:
            return self._alternatives(members, path, scope)
        shape = collection(annotation)
        if shape is not None:
            return self._collection(annotation, shape[0], path, scope)
        if not (isinstance(annotation, type) and issubclass(annotation, BaseModel)):
            msg = f"{path}: {annotation!r} passed program validation and is not a premise"
            raise TypeError(msg)
        interaction = self.program.receiving(annotation)
        if interaction is not None:
            return self._received(interaction, annotation, path, scope)
        location = self.program.analysis.located.get(annotation)
        if location is not None:
            return self._located(location, path, scope)
        return self._composed(annotation, path, scope)

    def _alternatives(
        self, members: tuple[type[BaseModel], ...], path: str, scope: Scope
    ) -> Outcome:
        outcomes = [(m, self.construct(m, f"{path}.{m.__name__}", scope)) for m in members]
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

    def _received(
        self, interaction: Interaction, kind: type[BaseModel], path: str, scope: Scope
    ) -> Outcome:
        """One record from a source, in this scope: the evidence answering this scope's intent
        or correlated to this scope's element, else the work that supplies it."""
        said = self.invocation.said(interaction)
        if interaction.many:
            site = bound(scope, Collection(kind, ()))
            if site is None:
                msg = f"{path}: {kind.__name__} is one of many and no element is bound"
                raise RuntimeError(msg)
            (mine,) = [e for e in said if e.id == site.evidence]
            return self._answer(mine, kind, path)
        if interaction.sends is None:
            element = self._element(interaction, scope)
            mine = [e for e in said if e.element == element]
            if mine:
                return self._answer(mine[0], kind, path)
            how = Unsolicited(
                receives=interaction.receives, source=interaction.source, element=element
            )
            return awaiting(interaction, how, element)
        sends = interaction.sends
        request = self.construct(sends, f"{path}.{sends.__name__}", scope)
        varies = self.program.analysis.varying(sends, frozenset(c for c, _ in scope))
        unscoped = [e for e in said if e.answers is None and e.element is None]
        if varies:
            unscoped = []
        if not isinstance(request, Available):
            return self._answer(unscoped[0], kind, path) if unscoped else request
        if not isinstance(request.value, BaseModel):
            msg = f"{path}: a request is a declared class"
            raise TypeError(msg)
        identity = EffectIdentity(
            invocation=self.invocation.id,
            operation=qualified(sends),
            occurrence=request.occurrence,
        )
        mine = [e for e in said if e.answers == identity] or unscoped
        if mine:
            return self._answer(mine[0], kind, path)
        return self._outstanding(interaction, identity, request.value, path)

    def _element(self, interaction: Interaction, scope: Scope) -> Site | None:
        """The input element an unsolicited receive is tied to in this scope, if its
        correlation enters a collection."""
        over = self.program.element_collection(interaction)
        if over is None:
            return None
        site = bound(scope, over)
        if site is None:
            msg = f"{over} is not bound where {interaction.receives[0].__name__} is demanded"
            raise RuntimeError(msg)
        return site

    def _answer(self, evidence: Evidence, kind: type[BaseModel], path: str) -> Outcome:
        if isinstance(evidence.value, kind):
            return Available(evidence.value, Site(evidence=evidence.id))
        reason = AnsweredOtherwise(
            premise=path, expected=kind, answered=type(evidence.value), evidence=evidence.id
        )
        return Refuted((reason,))

    def _outstanding(
        self, interaction: Interaction, identity: EffectIdentity, request: BaseModel, path: str
    ) -> Outcome:
        """A solicited receive nothing has satisfied: the send to dispatch, or the wait."""
        attempts = self.invocation.attempts(identity)
        last: Attempted | None = attempts[-1] if attempts else None
        if last is None or isinstance(last.outcome, Failed):
            dispatch = Dispatch(identity=identity, request=request, attempt=len(attempts) + 1)
            return Open({identity: dispatch}, {})
        return awaiting(interaction, self._after(interaction, identity, last, path), identity)

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

    def _collection(
        self, annotation: object, element: type[BaseModel], path: str, scope: Scope
    ) -> Outcome:
        """Every element of a collection: all a source says once closed, a tuple found in the
        input or a record, or one construction per element of the collection the class varies
        over."""
        interaction = self.program.receiving(element)
        if interaction is not None:
            return self._accumulated(interaction, element, path, scope)
        location = self.program.analysis.located.get(annotation)
        if location is not None:
            return self._located(location, path, scope)
        over = self.program.analysis.mapped.get(annotation)
        if over is None:
            msg = f"{path}: {annotation!r} passed program validation without a way to be obtained"
            raise TypeError(msg)
        return self._mapped(element, over, path, scope)

    def _accumulated(
        self, interaction: Interaction, element: type[BaseModel], path: str, scope: Scope
    ) -> Outcome:
        """Every item a source says, available once the declared closing evidence is."""
        closer = interaction.closed_by
        if closer is None:
            msg = f"{path}: a collection from {interaction.source.root} has no closure"
            raise TypeError(msg)
        said = self.invocation.said(interaction)
        closing = [e for e in self.invocation.evidence if isinstance(e.value, closer)]
        if closing:
            values = tuple(e.value for e in said)
            return Available(values, Elements(of=tuple(Site(evidence=e.id) for e in said)))
        how = Unclosed(element=element, source=interaction.source, closing=closer, held=len(said))
        match self.construct(closer, f"{path}.closed_by", scope):
            case Open() as outcome:
                return outcome.merged(awaiting(interaction, how, None))
            case Available():
                msg = f"{path}: {closer.__name__} is available and no closing evidence is admitted"
                raise RuntimeError(msg)
            case Refuted() | Stuck() as outcome:
                return outcome

    def _elements(self, over: Collection, path: str, scope: Scope) -> Outcome:
        """The elements of a collection as a tuple with their sites: the records a collection
        source has said so far, or a tuple found in the input or a record."""
        interaction = self.program.receiving(over.container)
        if interaction is not None and not over.path:
            said = self.invocation.said(interaction)
            values = tuple(e.value for e in said)
            return Available(values, Elements(of=tuple(Site(evidence=e.id) for e in said)))
        return self._located(Location(over.container, over.path), path, scope)

    def _mapped(self, kind: type[BaseModel], over: Collection, path: str, scope: Scope) -> Outcome:
        """One construction of a class per element of the collection it varies over. The tuple
        is final only when the collection is: a collection source's tuple stays open until its
        closing evidence, while each element's work proceeds."""
        elements = self._elements(over, f"{path}.{over.container.__name__}", scope)
        if not isinstance(elements, Available):
            return elements
        if not isinstance(elements.occurrence, Elements):
            msg = f"{path}: {over} is not a collection"
            raise TypeError(msg)
        outcomes: list[Outcome] = []
        for index, site in enumerate(elements.occurrence.of):
            if not isinstance(site, Site):
                msg = f"{path}: an element of {over} is not at a site"
                raise TypeError(msg)
            each = binding(scope, over, site)
            outcomes.append(self.construct(kind, f"{path}[{index}]", each))
        built = [o for o in outcomes if isinstance(o, Available)]
        interaction = self.program.receiving(over.container)
        if interaction is not None and not over.path:
            outcomes.append(self._accumulated(interaction, over.container, path, scope))
        pending = combined(outcomes)
        if pending is not None:
            return pending
        values = tuple(o.value for o in built)
        return Available(values, Elements(of=tuple(o.occurrence for o in built)))

    def _located(self, location: Location, path: str, scope: Scope) -> Outcome:
        """A value found at a declared location: inside the input or a received record, entering
        each collection on the way at the element the scope binds."""
        if location.container is self.program.accepts:
            value: object = self.invocation.input
            site = Site(evidence=0)
        else:
            container = location.container
            held = self.construct(container, f"{path}.{container.__name__}", scope)
            if not isinstance(held, Available):
                return held
            if not isinstance(held.occurrence, Site):
                msg = f"{path}: a received record is at a site"
                raise TypeError(msg)
            value, site = held.value, held.occurrence
        for k, step in enumerate(location.path):
            if step != EACH:
                value = getattr(value, step)
                site = site.within(step)
                continue
            element = bound(scope, Collection(location.container, location.path[:k]))
            if element is None:
                msg = f"{path}: {location} varies and no element is bound"
                raise RuntimeError(msg)
            index = element.path[-1]
            if not isinstance(index, int):
                msg = f"{path}: {location} does not enter a collection at step {k}"
                raise TypeError(msg)
            value = items(value)[index]
            site = site.within(index)
        if isinstance(value, tuple):
            found = items(cast("object", value))
            sites = tuple(site.within(i) for i in range(len(found)))
            return Available(found, Elements(of=sites))
        return Available(value, site)

    def _composed(self, kind: type[BaseModel], path: str, scope: Scope) -> Outcome:
        """A class constructed from its premises through Pydantic."""
        if constant(kind):
            return Available(kind(), Built(kind=qualified(kind)))
        given: dict[str, object] = {}
        parts: list[tuple[str, Occurrence]] = []
        outcomes: list[Outcome] = []
        for name, annotation in premises(kind):
            outcome = self.construct(annotation, f"{path}.{name}", scope)
            outcomes.append(outcome)
            if isinstance(outcome, Available):
                given[name] = outcome.value
                parts.append((name, outcome.occurrence))
        pending = combined(outcomes)
        if pending is not None:
            return pending
        occurrence = Built(kind=qualified(kind), parts=tuple(parts))
        return self._validated(kind, given, occurrence, path)

    def _validated(
        self, kind: type[BaseModel], given: dict[str, object], occurrence: Built, path: str
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
        return Available(value, occurrence)


def items(value: object) -> tuple[object, ...]:
    """A tuple's items, as the unknown objects they are."""
    if not isinstance(value, tuple):
        msg = f"{value!r} is not a collection"
        raise TypeError(msg)
    return tuple(cast("tuple[object, ...]", value))


def evaluate(program: Program, invocation: Invocation) -> Evaluation:
    """The next justified work of an invocation, from its history."""
    outcome = Evaluator(program, invocation).construct(program.goal, program.goal.__name__, ())
    match outcome:
        case Available(value, occurrence):
            if not isinstance(value, BaseModel):
                msg = "a goal is a declared class"
                raise TypeError(msg)
            return Completed(goal=value, occurrence=occurrence)
        case Open(dispatch, awaited):
            return Frontier(dispatch=tuple(dispatch.values()), awaiting=tuple(awaited.values()))
        case Refuted(reasons) | Stuck(reasons):
            return Blocked(reasons=reasons)
