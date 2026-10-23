"""Pure evaluation of one invocation: the next justified work, from the history alone.

``evaluate`` takes a program and an invocation and returns one of three results. ``Completed``
holds the constructed goal. ``Frontier`` holds the requests justified now, the receives
outstanding, and the requests demanded but withheld, with why. ``Blocked`` holds structured
reasons why the goal cannot be constructed from the declared sources however much evidence
arrives: a declared condition refuted over the evidence, a source that answered with another
member than the premise needs, a construction that failed, alternatives that both hold, or a
choice between effects that nothing declared decides.

Demand is rooted in the goal and an effect is justified only when it is necessary (foundations
§7.1, §7.2). Two rules, both over the graph the declarations compile to, and neither a property
of any one node:

- **Necessity across alternatives.** Where more than one member of a union is still live, a
  request is justified only if every live member needs it. A request one member needs and
  another does not is withheld as ``Unchosen``; if nothing else can advance the invocation,
  that is a block, not a wait: the declarations have not said which effect to perform.
- **Decisions precede dependent effects.** A premise is undecided while evidence still to come
  may refute it: a receive whose source may answer with another member, a declared condition
  over an open premise, a selection over an unclosed collection. While any premise of a
  conjunction is undecided, the requests under its decided premises are withheld as
  ``Deferred``, and only the requests that resolve the undecided premises are dispatched. This
  holds whether or not another branch exists for the refuted case: a single remaining branch is
  not an established branch.

Independent necessary work stays concurrent: two decided premises dispatch together, and two
undecided premises dispatch their deciding requests together.

Construction is by occurrence, not by class. Each node of the graph is one construction
relationship; evaluation is scoped, binding each collection in play to one element, and a node
is constructed once per scope it varies over, so two places that obtain a value the same way
share one occurrence and two elements with equal content do not. A constructed value's
occurrence is the occurrences of its premises, which is what identifies the effect a request
intends.

Evaluation constructs pure values through Pydantic, with ``Refusals`` as the validation context
so that a refutable kind's own refusal is told from a malformed construction. It reads no clock,
performs no effect and allocates no identity that is not derived from the history. An attempt
that failed leaves its intent dispatchable under the same identity. An attempt whose outcome is
uncertain leaves it outstanding and not dispatchable; which is right is the capability's
recovery contract, not a business conclusion.
"""

from dataclasses import dataclass, replace
from typing import cast

from pydantic import BaseModel, ConfigDict, Field, SerializeAsAny, ValidationError, model_validator

from type_construction.world import Refusals, Refutable

from .declaration import (
    EACH,
    All,
    Choice,
    Collection,
    Each,
    Found,
    Heard,
    Interaction,
    Location,
    Made,
    Node,
    Program,
    Source,
    constant,
    fallible,
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
    closed_by,
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


class Undecidable(BaseModel):
    """The live members of an alternative each need an effect the others do not, nothing
    declared decides between them, and nothing else can advance the invocation. The evaluator
    does not choose."""

    model_config = RESULT

    premise: str
    members: tuple[type[BaseModel], ...]
    operations: tuple[str, ...]

    def __hash__(self) -> int:
        return hash((self.premise, self.members, self.operations))


type Reason = Refutation | AnsweredOtherwise | Malformed | Indeterminate | Undecidable


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


class Deferred(BaseModel):
    """A request whose premises are available and whose result the goal needs, withheld because
    a premise of the same conjunction is undecided: evidence still to come may refute it, and
    then the request would have been performed for nothing. ``until`` names those premises."""

    model_config = RESULT

    identity: EffectIdentity
    request: SerializeAsAny[BaseModel]
    until: tuple[str, ...]


class Unchosen(BaseModel):
    """A request one live member of an alternative needs and another does not, withheld because
    the declarations have not decided between them."""

    model_config = RESULT

    identity: EffectIdentity
    request: SerializeAsAny[BaseModel]
    premise: str
    among: tuple[type[BaseModel], ...]


type Withheld = Deferred | Unchosen


class Completed(BaseModel):
    """The goal is constructed, from the occurrences named."""

    model_config = RESULT

    goal: SerializeAsAny[BaseModel]
    occurrence: Occurrence


class Frontier(BaseModel):
    """The next justified work: requests to dispatch now, receives outstanding, and requests
    demanded but withheld, each with why."""

    model_config = RESULT

    dispatch: tuple[Dispatch, ...] = ()
    awaiting: tuple[Awaiting, ...] = ()
    withheld: tuple[Withheld, ...] = ()

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
    """The premise is not yet constructed, and declared work may supply it. ``undecided`` names
    the premises under it that evidence still to come may refute; empty, the premise is decided
    and only pending."""

    dispatch: dict[EffectIdentity, Dispatch]
    withheld: dict[EffectIdentity, Withheld]
    awaiting: dict[object, Awaiting]
    undecided: tuple[str, ...] = ()

    def needs(self) -> dict[EffectIdentity, Dispatch]:
        """Every request this premise needs performed, dispatched or deferred."""
        deferred = {
            identity: Dispatch(identity=identity, request=w.request, attempt=1)
            for identity, w in self.withheld.items()
            if isinstance(w, Deferred)
        }
        return {**deferred, **self.dispatch}


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


def undecided(outcome: Outcome, path: str) -> Open:
    """An open outcome marked undecided at this premise, if not already undecided deeper."""
    if not isinstance(outcome, Open):
        msg = f"{path}: only an open premise is undecided"
        raise TypeError(msg)
    return outcome if outcome.undecided else replace(outcome, undecided=(path,))


def conjoined(parts: list[tuple[str, Outcome]]) -> Open | Refuted | Stuck | None:
    """How several premises' outcomes combine when all are needed: a malformed construction
    outranks a refutation, which outranks open work; ``None`` when every one is available.
    While any premise is undecided, the requests under the decided premises are deferred until
    it is: they are demanded, but not yet justified."""
    stuck = [r for _, o in parts if isinstance(o, Stuck) for r in o.reasons]
    if stuck:
        return Stuck(distinct(stuck))
    refuted = [r for _, o in parts if isinstance(o, Refuted) for r in o.reasons]
    if refuted:
        return Refuted(distinct(refuted))
    opens = [o for _, o in parts if isinstance(o, Open)]
    if not opens:
        return None
    pending = tuple(dict.fromkeys(p for o in opens for p in o.undecided))
    dispatch: dict[EffectIdentity, Dispatch] = {}
    withheld: dict[EffectIdentity, Withheld] = {}
    awaiting: dict[object, Awaiting] = {}
    for o in opens:
        awaiting |= o.awaiting
        withheld |= o.withheld
        if pending and not o.undecided:
            for identity, d in o.dispatch.items():
                withheld[identity] = Deferred(identity=identity, request=d.request, until=pending)
        else:
            dispatch |= o.dispatch
    for identity in dispatch:
        withheld.pop(identity, None)
    return Open(dispatch, withheld, awaiting, pending)


def chosen(path: str, members: list[tuple[type[BaseModel], Outcome]]) -> Outcome:
    """How alternatives combine: one constructed member is the premise; two are indeterminate;
    among live open members, a request is justified only if every one needs it, and a request
    one needs and another does not is unchosen. The alternative is undecided only while every
    live member is: a member nothing can refute will hold whatever the others do."""
    available = [(m, o) for m, o in members if isinstance(o, Available)]
    if len(available) == 1:
        return available[0][1]
    if available:
        return Stuck((Indeterminate(premise=path, members=tuple(m for m, _ in available)),))
    stuck = [r for _, o in members if isinstance(o, Stuck) for r in o.reasons]
    if stuck:
        return Stuck(distinct(stuck))
    opens = [(m, o) for m, o in members if isinstance(o, Open)]
    if not opens:
        refuted = [r for _, o in members if isinstance(o, Refuted) for r in o.reasons]
        return Refuted(distinct(refuted))
    if len(opens) == 1:
        return opens[0][1]
    return live(path, opens)


def live(path: str, opens: list[tuple[type[BaseModel], Open]]) -> Open:
    """How several live open members of an alternative combine: a request every member needs is
    necessary and dispatched when every member dispatches it; a request one member needs and
    another does not is unchosen."""
    members = tuple(m for m, _ in opens)
    needs = [o.needs() for _, o in opens]
    necessary = set(needs[0]).intersection(*(set(n) for n in needs[1:]))
    dispatch: dict[EffectIdentity, Dispatch] = {}
    withheld: dict[EffectIdentity, Withheld] = {}
    awaiting: dict[object, Awaiting] = {}
    for _, o in opens:
        awaiting |= o.awaiting
        for identity, w in o.withheld.items():
            if identity in necessary or not isinstance(w, Deferred):
                withheld.setdefault(identity, w)
        for identity, d in o.needs().items():
            if identity not in necessary:
                withheld[identity] = Unchosen(
                    identity=identity, request=d.request, premise=path, among=members
                )
    for identity in necessary:
        if all(identity in o.dispatch for _, o in opens):
            dispatch[identity] = next(o.dispatch[identity] for _, o in opens)
            withheld.pop(identity, None)
    pending = tuple(dict.fromkeys(p for _, o in opens for p in o.undecided))
    if not all(o.undecided for _, o in opens):
        pending = ()
    return Open(dispatch, withheld, awaiting, pending)


def awaiting(interaction: Interaction, how: Awaiting, which: object) -> Open:
    """An open outcome awaiting one receive occurrence."""
    return Open({}, {}, {(interaction.source, interaction.receives, type(how), which): how})


class Evaluator:
    """One evaluation of one invocation; see ``evaluate``."""

    def __init__(self, program: Program, invocation: Invocation) -> None:
        self.program = program
        self.invocation = invocation
        self.graph = program.graph
        self.memo: dict[tuple[Node, Scope], Outcome] = {}

    def construct(self, node: Node, path: str, scope: Scope) -> Outcome:
        """The outcome of constructing one node in one scope, once per evaluation. The scope is
        reduced to the collections the node varies over, so two places that obtain a value the
        same way share one occurrence."""
        relevant = self.graph.varies[node]
        key = (node, tuple(b for b in scope if b[0] in relevant))
        if key in self.memo:
            return self.memo[key]
        outcome = self._construct(node, path, scope)
        self.memo[key] = outcome
        return outcome

    def _construct(self, node: Node, path: str, scope: Scope) -> Outcome:
        match node:
            case Choice(members):
                outcomes = [
                    (m, self.construct(n, f"{path}.{m.__name__}", scope)) for m, n in members
                ]
                return chosen(path, outcomes)
            case Heard():
                return self._received(node, path, scope)
            case Found():
                return self._located(node, path, scope)
            case Made():
                return self._composed(node, path, scope)
            case All():
                return self._accumulated(node, path, scope)
            case Each():
                return self._mapped(node, path, scope)

    def _received(self, node: Heard, path: str, scope: Scope) -> Outcome:
        """One record from a source, in this scope: the evidence answering this scope's request
        or correlated to this scope's element, else the work that supplies it. The receive is
        undecided while the source may still answer with another member."""
        interaction, kind = node.interaction, node.kind
        said = self.invocation.said(interaction)
        decision = len(interaction.receives) > 1
        if interaction.many:
            site = bound(scope, Collection(kind, ()))
            if site is None:
                msg = f"{path}: {kind.__name__} is one of many and no element is bound"
                raise RuntimeError(msg)
            (mine,) = [e for e in said if e.id == site.evidence]
            return self._answer(mine, kind, path)
        if node.request is None:
            element = self._element(interaction, scope)
            mine = self._one(path, [e for e in said if e.element == element])
            if mine is not None:
                return self._answer(mine, kind, path)
            how = Unsolicited(
                receives=interaction.receives, source=interaction.source, element=element
            )
            waiting = awaiting(interaction, how, element)
            return undecided(waiting, path) if decision else waiting
        return self._solicited(node, node.request, path, scope)

    def _solicited(self, node: Heard, sent: Node, path: str, scope: Scope) -> Outcome:
        """The answer to this scope's request, or the request's own outcome: the send to
        dispatch, the wait after an attempt, or the premises the request still lacks."""
        interaction, kind = node.interaction, node.kind
        decision = len(interaction.receives) > 1
        sends = interaction.sends
        if sends is None:
            msg = f"{path}: a request node without a send"
            raise RuntimeError(msg)
        request = self.construct(sent, f"{path}.{sends.__name__}", scope)
        if isinstance(request, Open):
            return undecided(request, path) if decision else request
        if not isinstance(request, Available):
            return request
        if not isinstance(request.value, BaseModel):
            msg = f"{path}: a request is a declared class"
            raise TypeError(msg)
        identity = EffectIdentity(
            invocation=self.invocation.id, operation=qualified(sends), occurrence=request.occurrence
        )
        said = self.invocation.said(interaction)
        mine = self._one(path, [e for e in said if e.answers == identity])
        if mine is not None:
            return self._answer(mine, kind, path)
        elements = tuple(site for over, site in scope if over in self.graph.varies[sent])
        outstanding = self._outstanding(interaction, identity, request.value, elements, path)
        return undecided(outstanding, path) if decision else outstanding

    def _one(self, path: str, evidence: list[Evidence]) -> Evidence | None:
        """The one piece of evidence admitted for a receive occurrence, or none. Admission
        admits at most one; two is a protocol defect, not a choice to make here."""
        if len(evidence) > 1:
            msg = f"{path}: {len(evidence)} answers admitted for one receive occurrence"
            raise RuntimeError(msg)
        return evidence[0] if evidence else None

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
        self,
        interaction: Interaction,
        identity: EffectIdentity,
        request: BaseModel,
        elements: tuple[Site, ...],
        path: str,
    ) -> Open:
        """A solicited receive nothing has satisfied: the send to dispatch, or the wait."""
        attempts = self.invocation.attempts(identity)
        last: Attempted | None = attempts[-1] if attempts else None
        if last is None or isinstance(last.outcome, Failed):
            dispatch = Dispatch(
                identity=identity, request=request, attempt=len(attempts) + 1, elements=elements
            )
            return Open({identity: dispatch}, {}, {})
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

    def _accumulated(self, node: All, path: str, scope: Scope) -> Outcome:
        """Every item a source says, available once the declared closing evidence is."""
        interaction = node.interaction
        closer = interaction.closed_by
        if closer is None:
            msg = f"{path}: a collection from {interaction.source.root} has no closure"
            raise TypeError(msg)
        element = self._element(interaction, scope)
        said = self._said(interaction, element)
        if closed_by(self.invocation, interaction, element) is not None:
            values = tuple(e.value for e in said)
            return Available(values, Elements(of=tuple(Site(evidence=e.id) for e in said)))
        how = Unclosed(element=node.kind, source=interaction.source, closing=closer, held=len(said))
        match self.construct(node.closer, f"{path}.closed_by", scope):
            case Open() as outcome:
                merged = conjoined([(path, outcome), (path, awaiting(interaction, how, element))])
                if merged is None:
                    msg = f"{path}: open premises combined to nothing"
                    raise RuntimeError(msg)
                return merged
            case Available():
                msg = f"{path}: {closer.__name__} is available and no closing evidence is admitted"
                raise RuntimeError(msg)
            case Refuted() | Stuck() as outcome:
                return outcome

    def _said(self, interaction: Interaction, element: Site | None) -> tuple[Evidence, ...]:
        """What a collection source has said for one element of the input, or for the
        invocation when its correlation enters no collection."""
        return tuple(e for e in self.invocation.said(interaction) if e.element == element)

    def _elements(self, node: Each, path: str, scope: Scope) -> Outcome:
        """The elements of the collection a tuple follows, with their sites: the records a
        collection source has said so far for this element, or a tuple found in the input or in
        a record."""
        over = node.over
        if node.closure is not None:
            interaction = node.closure.interaction
            said = self._said(interaction, self._element(interaction, scope))
            values = tuple(e.value for e in said)
            return Available(values, Elements(of=tuple(Site(evidence=e.id) for e in said)))
        return self._located(Found(Location(over.container, over.path), node.holder), path, scope)

    def _mapped(self, node: Each, path: str, scope: Scope) -> Outcome:
        """One construction per element of the collection the class varies over. The tuple is
        final only when the collection is: a collection source's tuple stays open until its
        closing evidence, while each element's work proceeds; and while it is open, elements
        still to come may be refuted if any element can be."""
        elements = self._elements(node, f"{path}.{node.over.container.__name__}", scope)
        if not isinstance(elements, Available):
            return elements
        if not isinstance(elements.occurrence, Elements):
            msg = f"{path}: {node.over} is not a collection"
            raise TypeError(msg)
        parts: list[tuple[str, Outcome]] = []
        for index, site in enumerate(elements.occurrence.of):
            if not isinstance(site, Site):
                msg = f"{path}: an element of {node.over} is not at a site"
                raise TypeError(msg)
            each = binding(scope, node.over, site)
            at = f"{path}[{index}]"
            parts.append((at, self.construct(node.element, at, each)))
        if node.closure is not None:
            sealed = self.construct(node.closure, path, scope)
            if isinstance(sealed, Open) and self.graph.refutable[node.element]:
                sealed = undecided(sealed, f"{path}[{EACH}]")
            parts.append((path, sealed))
        pending = conjoined(parts)
        if pending is not None:
            return pending
        built = [o for _, o in parts[: len(elements.occurrence.of)] if isinstance(o, Available)]
        values = tuple(o.value for o in built)
        return Available(values, Elements(of=tuple(o.occurrence for o in built)))

    def _located(self, node: Found, path: str, scope: Scope) -> Outcome:
        """A value found at a declared location: inside the input or a received record, entering
        each collection on the way at the element the scope binds."""
        location = node.location
        if node.held is None:
            value: object = self.invocation.input
            site = Site(evidence=0)
        else:
            held = self.construct(node.held, f"{path}.{location.container.__name__}", scope)
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

    def _composed(self, node: Made, path: str, scope: Scope) -> Outcome:
        """A class constructed from its premises through Pydantic. A class whose construction may
        refuse, over an open premise, is undecided: the condition, validator or computation may
        not hold once the premise is, and the compiler does not read its body to know."""
        kind = node.kind
        if constant(kind):
            return Available(kind(), Built(kind=qualified(kind)))
        given: dict[str, object] = {}
        occurrences: list[tuple[str, Occurrence]] = []
        parts: list[tuple[str, Outcome]] = []
        for name, premise in node.premises:
            outcome = self.construct(premise, f"{path}.{name}", scope)
            parts.append((f"{path}.{name}", outcome))
            if isinstance(outcome, Available):
                given[name] = outcome.value
                occurrences.append((name, outcome.occurrence))
        pending = conjoined(parts)
        if isinstance(pending, Open) and fallible(kind):
            return undecided(pending, path)
        if pending is not None:
            return pending
        occurrence = Built(kind=qualified(kind), parts=tuple(occurrences))
        return self._validated(kind, given, occurrence, path)

    def _validated(
        self, kind: type[BaseModel], given: dict[str, object], occurrence: Built, path: str
    ) -> Outcome:
        """The class validated by Pydantic over its constructed premises, supplied by field name
        since they are the fields' values and not a party's payload, so a field's alias keeps
        its native meaning at the boundary and does not bar construction: available, refuted by
        its own declared condition, or malformed."""
        refusals = Refusals()
        try:
            value = kind.model_validate(given, context=refusals, by_name=True)
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


def undecidable(withheld: dict[EffectIdentity, Withheld]) -> tuple[Reason, ...]:
    """The unchosen effects as the reasons an invocation that can do nothing else is blocked."""
    by_premise: dict[tuple[str, tuple[type[BaseModel], ...]], list[str]] = {}
    for identity, w in withheld.items():
        if isinstance(w, Unchosen):
            by_premise.setdefault((w.premise, w.among), []).append(identity.operation)
    return tuple(
        Undecidable(premise=premise, members=among, operations=tuple(sorted(operations)))
        for (premise, among), operations in by_premise.items()
    )


def evaluate(program: Program, invocation: Invocation) -> Evaluation:
    """The next justified work of an invocation, from its history."""
    graph = program.graph
    outcome = Evaluator(program, invocation).construct(graph.root, program.goal.__name__, ())
    match outcome:
        case Available(value, occurrence):
            if not isinstance(value, BaseModel):
                msg = "a goal is a declared class"
                raise TypeError(msg)
            return Completed(goal=value, occurrence=occurrence)
        case Open(dispatch, withheld, awaited):
            if dispatch or awaited:
                return Frontier(
                    dispatch=tuple(dispatch.values()),
                    awaiting=tuple(awaited.values()),
                    withheld=tuple(withheld.values()),
                )
            reasons = undecidable(withheld)
            if not reasons:
                msg = "an open goal with nothing to dispatch, await or choose"
                raise RuntimeError(msg)
            return Blocked(reasons=reasons)
        case Refuted(reasons) | Stuck(reasons):
            return Blocked(reasons=reasons)
