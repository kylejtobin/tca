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
- **Decisions precede dependent effects.** What controls an open premise is kept apart in
  ``Control``. A *declared* decision is one the business stated: a source that may answer with
  another record, a declared refutable condition. A *constraint* is native metadata Pydantic
  itself interprets, located on a field and checked by the evaluator, through Pydantic, as soon
  as that field's value is there. In a conjunction the strongest control open governs: only the
  requests under premises at that control are dispatched, since their results are what resolves
  it and a control cannot require its own inputs as prior authority, and the rest are withheld
  as ``Deferred`` naming what they wait on. This holds whether or not another branch exists for
  the refuted case: a single remaining branch is not an established branch.
- **Unproven construction is neither a control nor a grant.** A validator, computation or
  revalidation the compiler locates but cannot interpret is resolved only by constructing. The
  evaluator does not order effects by it, since that order would be invented from the model's
  shape and not from a declared relationship, and does not treat the effects under it as
  evidence-gathering, since that would be authority from ignorance. A class with such a part,
  still open, is reported in the frontier as ``Unproven`` beside the effects it did not stop;
  the relationship, if the business means one, is declared by making the class a premise of the
  action (foundations §7.4), and then the action waits for it as for any premise. A plain class
  is under no control and reported as nothing: that is the absence of anything recognized, not
  a proof it constructs, and a construction that fails is reported when it fails.

Independent necessary work stays concurrent: two premises nothing can refuse dispatch
together, and two declared decisions dispatch their deciding requests together.

Evidence is owned by the history. Evaluation constructs from its own copy of each piece of
evidence and, at the end, checks the copies still equal the history; a construction that
altered a premise, through a validator that mutates what it is given, makes the evaluation
``Blocked`` as ``Impure`` rather than a conclusion built on altered evidence.

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
from typing import Annotated, cast

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SerializeAsAny,
    TypeAdapter,
    ValidationError,
    model_validator,
)

from type_construction.world import Refusals, Refutable

from .declaration import (
    EACH,
    All,
    Choice,
    Collection,
    Control,
    Each,
    Found,
    Heard,
    Interaction,
    Location,
    Made,
    Node,
    Program,
    Source,
    collection,
    constant,
    constrained,
    constraint,
    opaque,
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


class Deferred(BaseModel):
    """A request whose premises are available and whose result the goal needs, withheld because
    a premise of the same conjunction may yet be refused: by evidence still to come, or by a
    native constraint at construction, and then the request would have been performed for
    nothing. ``until`` names those premises."""

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


class Unproven(BaseModel):
    """A construction with a validator, computation or revalidation the evaluator cannot
    interpret, still open while the requests named were dispatched beside it. If the business
    means those requests to wait for it, it declares the class a premise of their request."""

    model_config = RESULT

    premise: str
    kind: type[BaseModel]
    beside: tuple[str, ...]

    def __hash__(self) -> int:
        return hash((self.premise, self.kind, self.beside))


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
    unproven: tuple[Unproven, ...] = ()

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
    """The premise is not yet constructed, and declared work may supply it. ``pending`` names
    the premises under it still under a control and which, see ``Control``; empty, no decision
    the evaluator knows of controls the premise."""

    dispatch: dict[EffectIdentity, Dispatch]
    withheld: dict[EffectIdentity, Withheld]
    awaiting: dict[object, Awaiting]
    pending: tuple[tuple[str, Control], ...] = ()
    unproven: tuple[tuple[str, type[BaseModel], frozenset[EffectIdentity]], ...] = ()
    """The open constructions under this premise whose outcome cannot be read, each with the
    requests dispatched beside it so far."""

    def tier(self) -> Control:
        """The strongest control over this premise."""
        return max((d for _, d in self.pending), default=Control.NONE)

    def paths(self, tier: Control) -> tuple[str, ...]:
        """The pending premises at one tier."""
        return tuple(p for p, d in self.pending if d == tier)

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


def controlled(outcome: Outcome, path: str, how: Control) -> Open:
    """An open outcome under the given control at this premise, added to what is pending deeper,
    unless already pending there at least as strongly."""
    if not isinstance(outcome, Open):
        msg = f"{path}: only an open premise is pending"
        raise TypeError(msg)
    if how == Control.NONE or outcome.tier() >= how:
        return outcome
    return replace(outcome, pending=(*outcome.pending, (path, how)))


type Part = tuple[str, Outcome, Control]
"""One premise of a conjunction: its path, its outcome, and how the construction holding it
may refuse it on its own account, beyond what is pending inside it."""


def conjoined(parts: list[Part]) -> Open | Refuted | Stuck | None:
    """How several premises' outcomes combine when all are needed: a malformed construction
    outranks a refutation, which outranks open work; ``None`` when every one is available.

    Each open premise is under the strongest control of what is pending inside it and of what
    the holding construction judges it by. The conjunction's governing control is the strongest
    among them. Only the requests under premises at the governing control are dispatched: their
    results are what resolves it, and a control cannot require its own inputs as prior
    authority. Requests under the others are deferred until those premises are resolved:
    demanded, not yet justified. With nothing pending, every request is dispatched."""
    stuck = [r for _, o, _ in parts if isinstance(o, Stuck) for r in o.reasons]
    if stuck:
        return Stuck(distinct(stuck))
    refuted = [r for _, o, _ in parts if isinstance(o, Refuted) for r in o.reasons]
    if refuted:
        return Refuted(distinct(refuted))
    opens = [(path, controlled(o, path, own)) for path, o, own in parts if isinstance(o, Open)]
    if not opens:
        return None
    governing = max(o.tier() for _, o in opens)
    pending = tuple(dict.fromkeys(p for _, o in opens for p in o.pending))
    until = tuple(dict.fromkeys(p for _, o in opens for p in o.paths(governing)))
    dispatch: dict[EffectIdentity, Dispatch] = {}
    withheld: dict[EffectIdentity, Withheld] = {}
    awaiting: dict[object, Awaiting] = {}
    for _, o in opens:
        awaiting |= o.awaiting
        withheld |= o.withheld
        if o.tier() < governing:
            for identity, d in o.dispatch.items():
                withheld[identity] = Deferred(identity=identity, request=d.request, until=until)
        else:
            dispatch |= o.dispatch
    for identity in dispatch:
        withheld.pop(identity, None)
    unread: dict[tuple[str, type[BaseModel]], frozenset[EffectIdentity]] = {}
    for _, o in opens:
        for path, kind, beside in o.unproven:
            elsewhere = frozenset(dispatch) - frozenset(o.dispatch)
            unread[path, kind] = unread.get((path, kind), frozenset()) | beside | elsewhere
    unproven = tuple((path, kind, beside) for (path, kind), beside in unread.items())
    return Open(dispatch, withheld, awaiting, pending, unproven)


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
    another does not is unchosen. The alternative may be refused only if every live member may,
    so what is pending is what the members have pending, at the weakest tier among them."""
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
    weakest = min(o.tier() for _, o in opens)
    pending = tuple(
        dict.fromkeys(
            (path, min(how, weakest)) for _, o in opens for path, how in o.pending if weakest
        )
    )
    unproven = tuple(dict.fromkeys(u for _, o in opens for u in o.unproven))
    return Open(dispatch, withheld, awaiting, pending, unproven)


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
        self.view: dict[int, BaseModel] = {0: invocation.input.model_copy(deep=True)}
        for evidence in invocation.evidence:
            self.view[evidence.id] = evidence.value.model_copy(deep=True)

    def altered(self) -> tuple[int, ...]:
        """The evidence whose copy no longer equals the history after evaluation."""
        originals = {0: self.invocation.input, **{e.id: e.value for e in self.invocation.evidence}}
        return tuple(i for i, copy in self.view.items() if copy != originals[i])

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
            return controlled(waiting, path, Control.DECLARED) if decision else waiting
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
            return controlled(request, path, Control.DECLARED) if decision else request
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
        return controlled(outstanding, path, Control.DECLARED) if decision else outstanding

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
            values = tuple(self.view[e.id] for e in said)
            return Available(values, Elements(of=tuple(Site(evidence=e.id) for e in said)))
        how = Unclosed(element=node.kind, source=interaction.source, closing=closer, held=len(said))
        match self.construct(node.closer, f"{path}.closed_by", scope):
            case Open() as outcome:
                waiting = awaiting(interaction, how, element)
                merged = conjoined([(path, outcome, Control.NONE), (path, waiting, Control.NONE)])
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
            values = tuple(self.view[e.id] for e in said)
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
        parts: list[Part] = []
        for index, site in enumerate(elements.occurrence.of):
            if not isinstance(site, Site):
                msg = f"{path}: an element of {node.over} is not at a site"
                raise TypeError(msg)
            each = binding(scope, node.over, site)
            at = f"{path}[{index}]"
            parts.append((at, self.construct(node.element, at, each), Control.NONE))
        if node.closure is not None:
            sealed = self.construct(node.closure, path, scope)
            still = self.graph.control[node.element]
            parts.append((f"{path}[{EACH}]", sealed, still))
        pending = conjoined(parts)
        if pending is not None:
            return pending
        built = [o for _, o, _ in parts[: len(elements.occurrence.of)] if isinstance(o, Available)]
        values = tuple(o.value for o in built)
        return Available(values, Elements(of=tuple(o.occurrence for o in built)))

    def _located(self, node: Found, path: str, scope: Scope) -> Outcome:
        """A value found at a declared location: inside the input or a received record, entering
        each collection on the way at the element the scope binds."""
        location = node.location
        if node.held is None:
            value: object = self.view[0]
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
        """A class constructed from its premises through Pydantic. Each open premise is under the
        control this class puts on it: a declared condition over every premise, a native
        constraint on its field, or none the evaluator can read. A premise already available is
        checked against its own field's native constraints at once, through Pydantic, so a
        constraint the class states is respected before any effect beside it, not only when the
        whole class constructs; a callback is never run early, and a refutable class's
        constraints are its declared condition, judged by constructing it so that its refusal is
        classified as its own. A class with a part the evaluator cannot read, still open, is
        reported unproven. A constant is constructed the same way, since a default is validated
        too."""
        kind = node.kind
        if constant(kind):
            return self._validated(kind, None, Built(kind=qualified(kind)), path)
        given: dict[str, object] = {}
        occurrences: list[tuple[str, Occurrence]] = []
        parts: list[Part] = []
        bounded = constrained(kind)
        for name, premise in node.premises:
            outcome = self.construct(premise, f"{path}.{name}", scope)
            own = Control.NONE
            if issubclass(kind, Refutable):
                own = Control.DECLARED
            elif name in bounded:
                own = Control.CONSTRAINT
            if isinstance(outcome, Available):
                errors = None if issubclass(kind, Refutable) else checked(kind, name, outcome.value)
                if errors is not None:
                    reason = Malformed(premise=f"{path}.{name}", kind=kind, errors=errors)
                    outcome = Stuck((reason,))
                else:
                    given[name] = outcome.value
                    occurrences.append((name, outcome.occurrence))
            parts.append((f"{path}.{name}", outcome, own))
        pending = conjoined(parts)
        if isinstance(pending, Open) and opaque(kind) != frozenset():
            unread = (path, kind, frozenset[EffectIdentity]())
            return replace(pending, unproven=(*pending.unproven, unread))
        if pending is not None:
            return pending
        occurrence = Built(kind=qualified(kind), parts=tuple(occurrences))
        return self._validated(kind, given, occurrence, path)

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


def checked(kind: type[BaseModel], name: str, value: object) -> tuple[str, ...] | None:
    """The errors a field's own native constraints raise over an available premise, or ``None``
    when the field has none or they hold. The field's annotation with its constraint metadata, a
    bound, a length, a fixed tuple size, is what Pydantic will apply to the field at
    construction; applying it here through Pydantic is the same judgement, made as soon as the
    premise is there. Callbacks in the metadata, validators declared by decorator and model
    validators run only at construction and are not run here: their outcome stays unproven."""
    info = kind.model_fields[name]
    bounds = tuple(m for m in info.metadata if constraint(m))
    fixed = collection(info.annotation)
    if not bounds and (fixed is None or fixed[1] is None):
        return None
    judged: object = info.annotation
    if bounds:
        judged = Annotated[(info.annotation, *bounds)]  # pyright: ignore[reportInvalidTypeArguments, reportInvalidTypeForm]
    try:
        TypeAdapter(judged).validate_python(value, strict=True)
    except ValidationError as refusal:
        return tuple(e["msg"] for e in refusal.errors())
    return None


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
    evaluator = Evaluator(program, invocation)
    outcome = evaluator.construct(graph.root, program.goal.__name__, ())
    altered = evaluator.altered()
    if altered:
        return Blocked(reasons=(Impure(evidence=altered),))
    match outcome:
        case Available(value, occurrence):
            if not isinstance(value, BaseModel):
                msg = "a goal is a declared class"
                raise TypeError(msg)
            return Completed(goal=value, occurrence=occurrence)
        case Open(dispatch, withheld, awaited, _, unread):
            if dispatch or awaited:
                return Frontier(
                    dispatch=tuple(dispatch.values()),
                    awaiting=tuple(awaited.values()),
                    withheld=tuple(withheld.values()),
                    unproven=tuple(
                        Unproven(
                            premise=path,
                            kind=kind,
                            beside=tuple(sorted(i.operation for i in beside if i in dispatch)),
                        )
                        for path, kind, beside in unread
                    ),
                )
            reasons = undecidable(withheld)
            if not reasons:
                msg = "an open goal with nothing to dispatch, await or choose"
                raise RuntimeError(msg)
            return Blocked(reasons=reasons)
        case Refuted(reasons) | Stuck(reasons):
            return Blocked(reasons=reasons)
