"""Pure evaluation of one invocation: the next justified work, from the history alone.

``evaluate`` takes a program and an invocation and returns one of three results. ``Completed``
holds the constructed goal. ``Frontier`` holds the requests justified now, each with the
derivation that justifies it, the receives outstanding, and the requests demanded but withheld,
with why. ``Blocked`` holds structured reasons why the goal cannot be constructed from the
declared sources however much evidence arrives: a declared condition refuted over the evidence,
a source that answered with another member than the premise needs, a construction that failed,
alternatives that both hold, or a choice between effects that nothing declared decides.

Demand is rooted in the goal and propagated through the declared construction relationships
(foundations §7.1). Three rules, all over the graph the declarations compile to:

- **A product is joint construction.** A class demands every one of its premises, and the
  requests that supply them are dispatched as soon as their own premises are there, together.
  Nothing orders one field before another: not a validator on the class or on a field, not a
  constraint, not a source that may answer otherwise. A validator on a class that also holds an
  effect is a postcondition of that class, judged when the class constructs, never prior
  authorization for the effect. Packaging, a wrapper, a flattening, an opaque or a readable
  formulation of the same check, changes nothing about what is demanded (decision 0003, law 3).

- **A conditional is ordered demand.** ``When[C, R]`` demands ``C`` first, through its own
  complete native construction, and demands ``R`` only once ``C`` is constructed. Until then
  the operations under ``R`` are ``Pending``, named with the conditional and its condition. If
  ``C`` is refused, nothing under ``R`` is ever demanded and the conditional is refused with it.
  The work that establishes ``C`` is justified by ``C``'s own demand and needs its own premises
  like any other; being useful to a decision exempts it from nothing (§7.3). Where every use of
  an operation requires something, that something is a premise of its request, and no consumer
  weakens it (§7.4).

- **An alternative demands what every live member needs.** Where more than one member of a
  union is still live, a request is justified only if every live member demands it. A request
  one member demands and another does not is withheld as ``Unchosen``; if nothing else can
  advance the invocation, that is a block, not a wait: the declarations have not said which
  effect to perform. A member refuted by the evidence is no longer live, and what the remaining
  member demands is demanded (§7.2).

Each request in a frontier carries its ``Derivation``: every path by which it is demanded, from
the premise demanding the receive it answers up through the conditionals whose conditions were
established on the way, each with the occurrence of the established condition, and the revision
of the history this was derived from. The derivation is not computed after the fact: a request
is proposed at the premise that demands it, under the conditions in force there, and that is
what the derivation records. A construction two places demand is constructed once and demanded
twice, and its requests carry both paths; a conditional path does not appear until its condition
is established.

Construction is native and complete. A class constructs through Pydantic from its constructed
premises, with ``Refusals`` as the validation context so that a refutable kind's own refusal is
told from a malformed construction, and nothing is judged before that: no constraint is run on
a field alone, no validator is set aside, no fragment is rebuilt from an annotation. What
Pydantic accepts with a padding before-validator, or a revalidated element reading the context,
the evaluator accepts, because it only ever asks Pydantic the question the declaration asks.

Evidence is owned by the history. Evaluation constructs from its own copy of each piece of
evidence and, at the end, checks the copies still equal the history; a construction that
altered a premise, through a validator that mutates what it is given, makes the evaluation
``Blocked`` as ``Impure`` rather than a conclusion built on altered evidence. A validator that
returns a replacement is native behaviour: the constructed value holds the replacement and the
history holds what was admitted.

Construction is by occurrence, not by class. Each node of the graph is one construction
relationship; evaluation is scoped, binding each collection in play to one element, and a node
is constructed once per scope it varies over, so two places that obtain a value the same way
share one occurrence and two elements with equal content do not. A constructed value's
occurrence is the occurrences of its premises, which is what identifies the effect a request
intends. It reads no clock, performs no effect and allocates no identity that is not derived
from the history. An attempt that failed leaves its intent dispatchable under the same
identity. An attempt whose outcome is uncertain leaves it outstanding and not dispatchable;
which is right is the capability's recovery contract, not a business conclusion.
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
    Conditional,
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


class Impure(BaseModel):
    """A construction altered the evidence it was given: after evaluation, the evaluator's copy
    of the evidence named no longer equals the history. A validator that mutates what it is
    given is not supported, and a conclusion built over altered premises is not reported."""

    model_config = RESULT

    evidence: tuple[int, ...]

    def __hash__(self) -> int:
        return hash(self.evidence)


type Reason = Refutation | AnsweredOtherwise | Malformed | Indeterminate | Undecidable | Impure


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


class Pending(BaseModel):
    """The result of a conditional is not yet demanded: its condition is open. ``premise`` is
    the conditional, ``condition`` the premise it waits for, and ``operations`` the requests the
    conditional gates, those demanded under its result and not under its condition, none of
    which is constructed or proposed until the condition is established."""

    model_config = RESULT

    premise: str
    condition: str
    operations: tuple[str, ...]


class Unchosen(BaseModel):
    """A request one live member of an alternative needs and another does not, withheld because
    the declarations have not decided between them."""

    model_config = RESULT

    identity: EffectIdentity
    request: SerializeAsAny[BaseModel]
    premise: str
    among: tuple[type[BaseModel], ...]


type Withheld = Pending | Unchosen


class Activation(BaseModel):
    """A condition established on the way to a request: the conditional at ``conditional``
    demanded its result because the class at ``condition`` was constructed, at the occurrence
    named."""

    model_config = RESULT

    conditional: str
    condition: str
    occurrence: Occurrence

    def __hash__(self) -> int:
        return hash((self.conditional, self.condition, self.occurrence))


class Demand(BaseModel):
    """One path by which a request is demanded: ``consumer`` is the premise demanding the receive
    the request answers, and ``activations`` the conditions established between the goal and
    it, outermost first. Empty, the demand is unconditional from the goal."""

    model_config = RESULT

    consumer: str
    activations: tuple[Activation, ...] = ()

    def __hash__(self) -> int:
        return hash((self.consumer, self.activations))


class Derivation(BaseModel):
    """Why a request in the frontier is justified: every path by which the goal demands it, and
    the revision of the history this was derived from. The request itself and the occurrences
    of its premises are the dispatch and its identity."""

    model_config = RESULT

    identity: EffectIdentity
    demands: tuple[Demand, ...] = Field(min_length=1)
    revision: int


class Completed(BaseModel):
    """The goal is constructed, from the occurrences named."""

    model_config = RESULT

    goal: SerializeAsAny[BaseModel]
    occurrence: Occurrence


class Frontier(BaseModel):
    """The next justified work: requests to dispatch now, each with its derivation, receives
    outstanding, and requests demanded but withheld, each with why."""

    model_config = RESULT

    dispatch: tuple[Dispatch, ...] = ()
    awaiting: tuple[Awaiting, ...] = ()
    withheld: tuple[Withheld, ...] = ()
    derived: tuple[Derivation, ...] = ()
    """The derivation of each request in ``dispatch``, in the same order."""

    @model_validator(mode="after")
    def _some(self) -> Frontier:
        if not self.dispatch and not self.awaiting:
            msg = "a frontier with nothing to dispatch and nothing awaited is not a frontier"
            raise ValueError(msg)
        if [d.identity for d in self.derived] != [d.identity for d in self.dispatch]:
            msg = "every request dispatched has its derivation, and nothing else has"
            raise ValueError(msg)
        return self

    def why(self, identity: EffectIdentity) -> Derivation:
        """The derivation of the request with this identity."""
        for derivation in self.derived:
            if derivation.identity == identity:
                return derivation
        msg = f"{identity} is not dispatched in this frontier"
        raise KeyError(msg)


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
class Proposal:
    """A request proposed for dispatch, with every path that demands it so far."""

    dispatch: Dispatch
    demands: tuple[Demand, ...]


@dataclass(frozen=True)
class Open:
    """The premise is not yet constructed, and declared work may supply it: requests proposed,
    requests withheld, receives awaited."""

    dispatch: dict[EffectIdentity, Proposal]
    withheld: dict[object, Withheld]
    awaiting: dict[object, Awaiting]


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

type Context = tuple[Activation, ...]
"""The conditions established between the goal and the premise being constructed."""


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


def proposed(
    into: dict[EffectIdentity, Proposal], more: dict[EffectIdentity, Proposal]
) -> dict[EffectIdentity, Proposal]:
    """The proposals of two outcomes together: one request demanded by both carries every path
    that demands it, once each."""
    merged = dict(into)
    for identity, proposal in more.items():
        if identity in merged:
            demands = tuple(dict.fromkeys((*merged[identity].demands, *proposal.demands)))
            merged[identity] = Proposal(merged[identity].dispatch, demands)
        else:
            merged[identity] = proposal
    return merged


def under(path: str, prefix: str) -> bool:
    """Whether a path is the prefix or continues it at a field or an element."""
    return path == prefix or (path.startswith(prefix) and path[len(prefix)] in ".[")


def moved(path: str, old: str, new: str) -> str:
    """The path with the prefix at which a shared construction was first demanded replaced by
    the prefix at which it is demanded now."""
    if not under(path, old):
        msg = f"{path} is not under {old}"
        raise RuntimeError(msg)
    return new + path[len(old) :]


def demanded_again(outcome: Open, old: str, new: str, outer: int, context: Context) -> Open:
    """A shared construction's outcome as demanded from a second place: the same work, with the
    demands of this place in force. Each proposal's paths are moved from the first place to this
    one; the conditions in force at the first place are replaced by those in force here, and the
    conditions established inside the construction are kept, moved. The first place's demands
    stay with the first place; the two meet where the goal holds both."""

    def activation(a: Activation) -> Activation:
        return Activation(
            conditional=moved(a.conditional, old, new),
            condition=moved(a.condition, old, new),
            occurrence=a.occurrence,
        )

    def demand(d: Demand) -> Demand:
        inner = tuple(activation(a) for a in d.activations[outer:])
        return Demand(consumer=moved(d.consumer, old, new), activations=(*context, *inner))

    dispatch = {
        identity: Proposal(p.dispatch, tuple(demand(d) for d in p.demands))
        for identity, p in outcome.dispatch.items()
    }
    withheld: dict[object, Withheld] = {}
    for key, w in outcome.withheld.items():
        match w:
            case Pending(premise=premise, condition=condition, operations=operations):
                there = moved(premise, old, new)
                withheld[there] = Pending(
                    premise=there, condition=moved(condition, old, new), operations=operations
                )
            case Unchosen():
                withheld[key] = Unchosen(
                    identity=w.identity,
                    request=w.request,
                    premise=moved(w.premise, old, new),
                    among=w.among,
                )
    return Open(dispatch, withheld, outcome.awaiting)


type Part = tuple[str, Outcome]
"""One premise of a conjunction: its path and its outcome."""


def conjoined(parts: list[Part]) -> Open | Refuted | Stuck | None:
    """How several premises' outcomes combine when all are needed: a malformed construction
    outranks a refutation, which outranks open work; ``None`` when every one is available, and
    then the class constructs. Open premises are joint: every request each proposes is proposed,
    with every path that demands it, and nothing is ordered between them."""
    stuck = [r for _, o in parts if isinstance(o, Stuck) for r in o.reasons]
    if stuck:
        return Stuck(distinct(stuck))
    refuted = [r for _, o in parts if isinstance(o, Refuted) for r in o.reasons]
    if refuted:
        return Refuted(distinct(refuted))
    opens = [o for _, o in parts if isinstance(o, Open)]
    if not opens:
        return None
    dispatch: dict[EffectIdentity, Proposal] = {}
    withheld: dict[object, Withheld] = {}
    awaiting: dict[object, Awaiting] = {}
    for o in opens:
        dispatch = proposed(dispatch, o.dispatch)
        withheld |= o.withheld
        awaiting |= o.awaiting
    for identity in dispatch:
        withheld.pop(identity, None)
    return Open(dispatch, withheld, awaiting)


def chosen(path: str, members: list[tuple[type[BaseModel], Outcome]]) -> Outcome:
    """How alternatives combine: one constructed member is the premise; two are indeterminate;
    among live open members, a request is justified only if every one needs it, and a request
    one needs and another does not is unchosen."""
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
    """How several live open members of an alternative combine: a request every member proposes
    is necessary and proposed, demanded by every member's path; a request one member proposes
    and another does not is unchosen. What a member holds pending or unchosen inside it stays
    so."""
    members = tuple(m for m, _ in opens)
    necessary = set(opens[0][1].dispatch).intersection(*(set(o.dispatch) for _, o in opens[1:]))
    dispatch: dict[EffectIdentity, Proposal] = {}
    withheld: dict[object, Withheld] = {}
    awaiting: dict[object, Awaiting] = {}
    for _, o in opens:
        awaiting |= o.awaiting
        for key, w in o.withheld.items():
            withheld.setdefault(key, w)
        for identity, p in o.dispatch.items():
            if identity in necessary:
                dispatch = proposed(dispatch, {identity: p})
            else:
                withheld[identity] = Unchosen(
                    identity=identity, request=p.dispatch.request, premise=path, among=members
                )
    for identity in dispatch:
        withheld.pop(identity, None)
    return Open(dispatch, withheld, awaiting)


def awaiting(interaction: Interaction, how: Awaiting, which: object) -> Open:
    """An open outcome awaiting one receive occurrence."""
    return Open({}, {}, {(interaction.source, interaction.receives, type(how), which): how})


class Evaluator:
    """One evaluation of one invocation; see ``evaluate``."""

    def __init__(self, program: Program, invocation: Invocation) -> None:
        self.program = program
        self.invocation = invocation
        self.graph = program.graph
        self.memo: dict[tuple[Node, Scope], tuple[Outcome, str, int]] = {}
        self.view: dict[int, BaseModel] = {0: invocation.input.model_copy(deep=True)}
        for evidence in invocation.evidence:
            self.view[evidence.id] = evidence.value.model_copy(deep=True)

    def altered(self) -> tuple[int, ...]:
        """The evidence whose copy no longer equals the history after evaluation."""
        originals = {0: self.invocation.input, **{e.id: e.value for e in self.invocation.evidence}}
        return tuple(i for i, copy in self.view.items() if copy != originals[i])

    def construct(self, node: Node, path: str, scope: Scope, context: Context) -> Outcome:
        """The outcome of constructing one node in one scope, once per evaluation. The scope is
        reduced to the collections the node varies over, so two places that obtain a value the
        same way share one occurrence. A second place that demands a construction already made
        gets the same outcome demanded from its own place: its own path, under the conditions
        in force there, so that two consumers' demands are never merged by the sharing."""
        relevant = self.graph.varies[node]
        key = (node, tuple(b for b in scope if b[0] in relevant))
        if key in self.memo:
            outcome, first, outer = self.memo[key]
            if isinstance(outcome, Open):
                return demanded_again(outcome, first, path, outer, context)
            return outcome
        outcome = self._construct(node, path, scope, context)
        self.memo[key] = (outcome, path, len(context))
        return outcome

    def _construct(self, node: Node, path: str, scope: Scope, context: Context) -> Outcome:
        match node:
            case Choice():
                outcome = self._chosen(node, path, scope, context)
            case Heard():
                outcome = self._received(node, path, scope, context)
            case Found():
                outcome = self._located(node, path, scope, context)
            case Made():
                outcome = self._composed(node, path, scope, context)
            case All():
                outcome = self._accumulated(node, path, scope, context)
            case Each():
                outcome = self._mapped(node, path, scope, context)
            case Conditional():
                outcome = self._conditional(node, path, scope, context)
        return outcome

    def _chosen(self, node: Choice, path: str, scope: Scope, context: Context) -> Outcome:
        """An alternative: each member constructed, and combined by ``chosen``."""
        outcomes = [
            (m, self.construct(n, f"{path}.{m.__name__}", scope, context)) for m, n in node.members
        ]
        return chosen(path, outcomes)

    def _conditional(self, node: Conditional, path: str, scope: Scope, context: Context) -> Outcome:
        """A conditional premise: the condition first, through its own construction; while it is
        open, the result is pending and nothing under it is demanded; refused, the conditional
        is refused; constructed, the result is demanded under one more activation, and the
        conditional constructs natively from both."""
        condition = self.construct(node.condition, f"{path}.condition", scope, context)
        match condition:
            case Available(value, occurrence):
                activation = Activation(
                    conditional=path, condition=f"{path}.condition", occurrence=occurrence
                )
                result = self.construct(
                    node.result, f"{path}.result", scope, (*context, activation)
                )
                if not isinstance(result, Available):
                    return result
                given = {"condition": value, "result": result.value}
                built = Built(
                    kind=qualified(node.kind),
                    parts=(("condition", occurrence), ("result", result.occurrence)),
                )
                return self._validated(node.kind, given, built, path)
            case Open():
                pending = Pending(
                    premise=path, condition=f"{path}.condition", operations=self.graph.gated[node]
                )
                return replace(condition, withheld={**condition.withheld, path: pending})
            case Refuted() | Stuck():
                return condition

    def _received(self, node: Heard, path: str, scope: Scope, context: Context) -> Outcome:
        """One record from a source, in this scope: the evidence answering this scope's request
        or correlated to this scope's element, else the work that supplies it."""
        interaction, kind = node.interaction, node.kind
        said = self.invocation.said(interaction)
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
            return awaiting(interaction, how, element)
        return self._solicited(node, node.request, path, scope, context)

    def _solicited(
        self, node: Heard, sent: Node, path: str, scope: Scope, context: Context
    ) -> Outcome:
        """The answer to this scope's request, or the request's own outcome: the send to
        dispatch, demanded at this premise under the conditions in force, the wait after an
        attempt, or the premises the request still lacks."""
        interaction, kind = node.interaction, node.kind
        sends = interaction.sends
        if sends is None:
            msg = f"{path}: a request node without a send"
            raise RuntimeError(msg)
        request = self.construct(sent, f"{path}.{sends.__name__}", scope, context)
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
        demand = Demand(consumer=path, activations=context)
        return self._outstanding(interaction, identity, request.value, elements, demand)

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
        """The evidence as this evaluation's copy of it, if it is what the premise needs."""
        value = self.view[evidence.id]
        if isinstance(value, kind):
            return Available(value, Site(evidence=evidence.id))
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
        demand: Demand,
    ) -> Open:
        """A solicited receive nothing has satisfied: the send to dispatch, proposed with the
        demand that justifies it, or the wait."""
        attempts = self.invocation.attempts(identity)
        last: Attempted | None = attempts[-1] if attempts else None
        if last is None or isinstance(last.outcome, Failed):
            dispatch = Dispatch(
                identity=identity, request=request, attempt=len(attempts) + 1, elements=elements
            )
            return Open({identity: Proposal(dispatch, (demand,))}, {}, {})
        after = self._after(interaction, identity, last, demand.consumer)
        return awaiting(interaction, after, identity)

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

    def _accumulated(self, node: All, path: str, scope: Scope, context: Context) -> Outcome:
        """Every item a source says, available once the declared closing evidence is."""
        interaction = node.interaction
        closer = interaction.closed_by
        if closer is None:
            msg = f"{path}: a collection from {interaction.source.root} has no closure"
            raise TypeError(msg)
        element = self._element(interaction, scope)
        said = self._said(interaction, element)
        if closed_by(self.invocation, interaction, element) is not None:
            values = tuple(self.view[e.id] for e in said)
            return Available(values, Elements(of=tuple(Site(evidence=e.id) for e in said)))
        how = Unclosed(element=node.kind, source=interaction.source, closing=closer, held=len(said))
        match self.construct(node.closer, f"{path}.closed_by", scope, context):
            case Open() as outcome:
                waiting = awaiting(interaction, how, element)
                merged = conjoined([(path, outcome), (path, waiting)])
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

    def _elements(self, node: Each, path: str, scope: Scope, context: Context) -> Outcome:
        """The elements of the collection a tuple follows, with their sites: the records a
        collection source has said so far for this element, or a tuple found in the input or in
        a record."""
        over = node.over
        if node.closure is not None:
            interaction = node.closure.interaction
            said = self._said(interaction, self._element(interaction, scope))
            values = tuple(self.view[e.id] for e in said)
            return Available(values, Elements(of=tuple(Site(evidence=e.id) for e in said)))
        found = Found(Location(over.container, over.path), node.holder)
        return self._located(found, path, scope, context)

    def _mapped(self, node: Each, path: str, scope: Scope, context: Context) -> Outcome:
        """One construction per element of the collection the class varies over. The tuple is
        final only when the collection is: a collection source's tuple stays open until its
        closing evidence, while each element's work proceeds."""
        elements = self._elements(node, f"{path}.{node.over.container.__name__}", scope, context)
        if not isinstance(elements, Available):
            return elements
        if not isinstance(elements.occurrence, Elements):
            msg = f"{path}: {node.over} is not a collection"
            raise TypeError(msg)
        parts: list[Part] = []
        for index, site in enumerate(elements.occurrence.of):
            if not isinstance(site, Site):
                msg = f"{path}: an element of {node.over} is not at a site"
                raise TypeError(msg)
            each = binding(scope, node.over, site)
            at = f"{path}[{index}]"
            parts.append((at, self.construct(node.element, at, each, context)))
        if node.closure is not None:
            sealed = self.construct(node.closure, path, scope, context)
            parts.append((f"{path}[{EACH}]", sealed))
        pending = conjoined(parts)
        if pending is not None:
            return pending
        built = [o for _, o in parts[: len(elements.occurrence.of)] if isinstance(o, Available)]
        values = tuple(o.value for o in built)
        return Available(values, Elements(of=tuple(o.occurrence for o in built)))

    def _located(self, node: Found, path: str, scope: Scope, context: Context) -> Outcome:
        """A value found at a declared location: inside the input or a received record, entering
        each collection on the way at the element the scope binds."""
        location = node.location
        if node.held is None:
            value: object = self.view[0]
            site = Site(evidence=0)
        else:
            held = self.construct(
                node.held, f"{path}.{location.container.__name__}", scope, context
            )
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

    def _composed(self, node: Made, path: str, scope: Scope, context: Context) -> Outcome:
        """A class constructed from its premises through Pydantic, once every premise is there:
        joint construction, nothing judged before it. A constant is constructed the same way,
        since a default is validated too."""
        kind = node.kind
        if constant(kind):
            return self._validated(kind, None, Built(kind=qualified(kind)), path)
        given: dict[str, object] = {}
        occurrences: list[tuple[str, Occurrence]] = []
        parts: list[Part] = []
        for name, premise in node.premises:
            at = f"{path}.{name}"
            outcome = self.construct(premise, at, scope, context)
            if isinstance(outcome, Available):
                given[name] = outcome.value
                occurrences.append((name, outcome.occurrence))
            parts.append((at, outcome))
        pending = conjoined(parts)
        if pending is None:
            occurrence = Built(kind=qualified(kind), parts=tuple(occurrences))
            return self._validated(kind, given, occurrence, path)
        return pending

    def _validated(
        self, kind: type[BaseModel], given: dict[str, object] | None, occurrence: Built, path: str
    ) -> Outcome:
        """The class validated by Pydantic over its constructed premises, supplied by field name
        and read by field name only: they are the fields' values, not a party's payload, so an
        alias keeps its native meaning at the boundary and takes no part here, and a field whose
        alias is another field's name receives its own premise. A constant, given nothing, is
        constructed from its defaults, which are validated too. Available, refuted by its own
        declared condition, or malformed."""
        refusals = Refusals()
        try:
            if given is None:
                value = kind()
            else:
                value = kind.model_validate(given, context=refusals, by_alias=False, by_name=True)
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


def undecidable(withheld: dict[object, Withheld]) -> tuple[Reason, ...]:
    """The unchosen effects as the reasons an invocation that can do nothing else is blocked."""
    by_premise: dict[tuple[str, tuple[type[BaseModel], ...]], list[str]] = {}
    for w in withheld.values():
        if isinstance(w, Unchosen):
            by_premise.setdefault((w.premise, w.among), []).append(w.identity.operation)
    return tuple(
        Undecidable(premise=premise, members=among, operations=tuple(sorted(operations)))
        for (premise, among), operations in by_premise.items()
    )


def evaluate(program: Program, invocation: Invocation) -> Evaluation:
    """The next justified work of an invocation, from its history."""
    graph = program.graph
    evaluator = Evaluator(program, invocation)
    outcome = evaluator.construct(graph.root, program.goal.__name__, (), ())
    altered = evaluator.altered()
    if altered:
        return Blocked(reasons=(Impure(evidence=altered),))
    match outcome:
        case Available(value, occurrence):
            if not isinstance(value, BaseModel):
                msg = "a goal is a declared class"
                raise TypeError(msg)
            return Completed(goal=value, occurrence=occurrence)
        case Open(dispatch, withheld, awaited):
            if dispatch or awaited:
                return Frontier(
                    dispatch=tuple(p.dispatch for p in dispatch.values()),
                    awaiting=tuple(awaited.values()),
                    withheld=tuple(withheld.values()),
                    derived=tuple(
                        Derivation(identity=i, demands=p.demands, revision=invocation.revision)
                        for i, p in dispatch.items()
                    ),
                )
            reasons = undecidable(withheld)
            if not reasons:
                msg = "an open goal with nothing to dispatch, await or choose"
                raise RuntimeError(msg)
            return Blocked(reasons=reasons)
        case Refuted(reasons) | Stuck(reasons):
            return Blocked(reasons=reasons)
