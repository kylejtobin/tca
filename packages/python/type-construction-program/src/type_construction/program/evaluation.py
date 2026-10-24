"""Pure evaluation of one invocation: the next justified work, from the history alone.

``evaluate`` takes a program and an invocation and returns one of three results. ``Completed``
holds the constructed goal. ``Frontier`` holds the requests justified now, the receives
outstanding, and the requests demanded but withheld, with why. ``Blocked`` holds structured
reasons why the goal cannot be constructed from the declared sources however much evidence
arrives: a declared condition refuted over the evidence, a source that answered with another
member than the premise needs, a construction that failed, alternatives that both hold, a
choice between effects that nothing declared decides, or requests withheld behind judgements
that nothing can make before them.

Demand is rooted in the goal and an effect is justified only when it is necessary (foundations
§7.1, §7.2). Three rules, all over the graph the declarations compile to, and none a property
of any one node:

- **Necessity across alternatives.** Where more than one member of a union is still live, a
  request is justified only if every live member needs it. A request one member needs and
  another does not is withheld as ``Unchosen``; if nothing else can advance the invocation,
  that is a block, not a wait: the declarations have not said which effect to perform.

- **Decisions precede the effects that depend on them.** Each open premise of a conjunction
  carries the judgements still to be made on it, at the places they are declared
  (``Judgement``): a source that may answer otherwise or a refutable condition (``Decided``),
  a native constraint at a field (``Bounded``), or a validator, default or schema the
  evaluator cannot read (``Unread``). A request's result either feeds a judgement, when the
  premise it supplies is under one, or it does not, and then performing it decides nothing:
  its demand through the conjunction assumes every open judgement of the conjunction resolves
  in its favour. So a request under a premise nothing can refuse waits for every judgement
  the conjunction has open, named in ``Deferred``; requests whose results feed judgements
  the evaluator reads are dispatched together, since each is the declared means of a decision
  the goal needs, a decision cannot require its own inputs as prior authority (§7.3), and the
  declarations order none of them before another (§7.2).

- **An unread judgement grants nothing and settles nothing.** What a validator the evaluator
  cannot read means is unknown: it may refuse, or it may be an identity. The effects beside
  it are derived by taking both cases. A request feeding a readable decision is dispatched
  either way, so it is dispatched. A request under a premise nothing can refuse must wait if
  the unread part can refuse, so it waits, and ``Deferred`` names the unread judgement: the
  dependency is unresolved, not established. A request feeding only an unread judgement,
  beside a readable one, would be a deciding request if the unread part decides and a
  dependent one if it does not, so it waits for the readable decision, again named as
  unresolved. Beside premises nothing can refuse it is dispatched, since it would be either
  way. Beside another unread judgement neither reading settles the order: both requests wait,
  and if nothing else can advance the invocation that is reported as ``Undetermined``, naming
  the judgements and the requests, for the business to declare the condition readably or to
  put the judgement at a construction boundary before the effect (§8.2). Less knowledge never
  releases an effect, and never invents an order.

Independent necessary work stays concurrent: two premises nothing can refuse dispatch
together, and two readable decisions dispatch their deciding requests together.

A native constraint is judged before its class constructs only where that is the same
judgement Pydantic makes at construction (``early``): the field's value is there and nothing
omitted, a callback at the field, a decorated validator, a model validator before or around
field validation, a custom schema, can change the verdict. Otherwise the constraint is judged
only when the class constructs, natively, and until then it is an open judgement like any
other. A conclusion the evaluator cannot establish stays unknown; it is never made by running
Pydantic on a fragment with the business's own validators stripped away.

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
    Bounded,
    Choice,
    Collection,
    Decided,
    Each,
    Found,
    Heard,
    Interaction,
    Judgement,
    Location,
    Made,
    Node,
    Program,
    Refusability,
    Source,
    Unread,
    at_field,
    constant,
    early,
    native,
    qualified,
    refusability,
    strongest,
    unread,
    weakest,
    whole,
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


class Undetermined(BaseModel):
    """Requests demanded and constructible are withheld behind judgements, and nothing else can
    advance the invocation. Either the judgements are made only by constructing what needs
    those very requests, or the evaluator cannot read them well enough to establish whether
    the requests decide them or depend on them. The declarations do not determine the order
    and the evaluator does not choose. ``judgements`` names them where they are declared;
    ``operations`` the requests withheld. A declared relation the evaluator reads, or a
    construction boundary that makes the judgement before the effect, resolves it."""

    model_config = RESULT

    judgements: tuple[Judgement, ...]
    operations: tuple[str, ...]

    def __hash__(self) -> int:
        return hash((self.judgements, self.operations))


class Impure(BaseModel):
    """A construction altered the evidence it was given: after evaluation, the evaluator's copy
    of the evidence named no longer equals the history. A validator that mutates what it is
    given is not supported, and a conclusion built over altered premises is not reported."""

    model_config = RESULT

    evidence: tuple[int, ...]

    def __hash__(self) -> int:
        return hash(self.evidence)


type Reason = (
    Refutation | AnsweredOtherwise | Malformed | Indeterminate | Undecidable | Undetermined | Impure
)


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
    a premise of the same conjunction may yet be refused and the request's result does not
    decide that. ``behind`` names the judgements it waits for, where they are declared.

    With ``unread`` empty the dependency is established: the request decides nothing the
    evaluator can read and the judgements behind it are read decisions. Otherwise it is
    unresolved: an unread judgement, on the request's own premise or among those behind it,
    may be a condition the request must wait for or an identity that binds it to nothing, and
    the evaluator cannot tell which. It waits, and names what it cannot read.
    """

    model_config = RESULT

    identity: EffectIdentity
    request: SerializeAsAny[BaseModel]
    behind: tuple[Judgement, ...]
    unread: tuple[Unread, ...] = ()

    @property
    def until(self) -> tuple[str, ...]:
        """The premises whose judgements the request waits for, once each."""
        return tuple(dict.fromkeys(j.premise for j in self.behind))


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
    """The premise is not yet constructed, and declared work may supply it. ``judgements`` are
    the places under it still to be judged, where they are declared; ``refusable`` is what
    they establish about the premise as a whole: for a conjunction the strongest, for an
    alternative the weakest of its live members."""

    dispatch: dict[EffectIdentity, Dispatch]
    withheld: dict[EffectIdentity, Withheld]
    awaiting: dict[object, Awaiting]
    judgements: tuple[Judgement, ...] = ()
    refusable: Refusability = Refusability.ASSURED

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


def once(judgements: tuple[Judgement, ...]) -> tuple[Judgement, ...]:
    """The judgements once each, in first-seen order."""
    return tuple(dict.fromkeys(judgements))


def bound(scope: Scope, over: Collection) -> Site | None:
    """The element a collection is bound to in a scope, if any."""
    for each, site in scope:
        if each == over:
            return site
    return None


def binding(scope: Scope, over: Collection, site: Site) -> Scope:
    """The scope with one more collection bound."""
    return tuple(sorted((*scope, (over, site)), key=lambda b: str(b[0])))


def judged(outcome: Open, *judgements: Judgement) -> Open:
    """The open outcome with judgements added at this premise."""
    if not judgements:
        return outcome
    return replace(
        outcome,
        judgements=once((*outcome.judgements, *judgements)),
        refusable=strongest(outcome.refusable, *(refusability(j) for j in judgements)),
    )


type Part = tuple[str, Outcome, tuple[Judgement, ...]]
"""One premise of a conjunction: its path, its outcome, and the judgements the holding class
makes at that premise's field which are still to be made."""


@dataclass(frozen=True)
class Standing:
    """One premise of a conjunction that is open, or available and still judged at its field, as
    the conjunction sees it: the judgements on it, and what they establish about it."""

    path: str
    outcome: Open | None
    own: tuple[Judgement, ...]

    @property
    def judgements(self) -> tuple[Judgement, ...]:
        inner = () if self.outcome is None else self.outcome.judgements
        return once((*self.own, *inner))

    @property
    def refusable(self) -> Refusability:
        inner = Refusability.ASSURED if self.outcome is None else self.outcome.refusable
        return strongest(inner, *(refusability(j) for j in self.own))

    def deferred(
        self, behind: tuple[Judgement, ...], unresolved: tuple[Unread, ...]
    ) -> dict[EffectIdentity, Withheld]:
        """The requests dispatched under this premise, withheld behind the judgements named."""
        if self.outcome is None:
            return {}
        return {
            identity: Deferred(
                identity=identity, request=d.request, behind=behind, unread=unresolved
            )
            for identity, d in self.outcome.dispatch.items()
        }


def conjoined(parts: list[Part]) -> Open | Refuted | Stuck | None:
    """How several premises' outcomes combine when all are needed: a malformed construction
    outranks a refutation, which outranks open work; ``None`` when every one is available, and
    then the class constructs, which is what makes any judgement still open at a field.

    Otherwise the requests dispatched under each open premise are kept or withheld by the
    rules in the module docstring, derived from the judgements still open across the
    conjunction. Requests feeding a readable decision stand. Requests under a premise nothing
    can refuse wait for every open judgement. Requests feeding only an unread judgement stand
    when nothing else in the conjunction may refuse, wait for readable decisions as
    unresolved, and wait for other unread judgements as unresolved too; in that last case
    nothing may stand, and the block that follows names what was not established. A judgement
    two premises share, one construction occurrence demanded at both, is not another judgement:
    a request feeding it under one premise feeds it under the other.
    """
    stuck = [r for _, o, _ in parts if isinstance(o, Stuck) for r in o.reasons]
    if stuck:
        return Stuck(distinct(stuck))
    refuted = [r for _, o, _ in parts if isinstance(o, Refuted) for r in o.reasons]
    if refuted:
        return Refuted(distinct(refuted))
    standings = [
        Standing(path, o if isinstance(o, Open) else None, own)
        for path, o, own in parts
        if isinstance(o, Open) or own
    ]
    opens = [s for s in standings if s.outcome is not None]
    if not opens:
        return None
    governing = strongest(*(s.refusable for s in standings))
    withheld: dict[EffectIdentity, Withheld] = {}
    awaiting: dict[object, Awaiting] = {}
    for s in opens:
        if s.outcome is not None:
            awaiting |= s.outcome.awaiting
            withheld |= s.outcome.withheld
    if governing == Refusability.READABLE:
        dispatch, deferred = decided(standings, opens)
    elif governing == Refusability.UNREAD:
        dispatch, deferred = unsettled(standings, opens)
    else:
        dispatch = {k: d for s in opens if s.outcome for k, d in s.outcome.dispatch.items()}
        deferred = {}
    withheld |= deferred
    for identity in dispatch:
        withheld.pop(identity, None)
    judgements = once(tuple(j for s in standings for j in s.judgements))
    return Open(dispatch, withheld, awaiting, judgements, governing)


type Kept = tuple[dict[EffectIdentity, Dispatch], dict[EffectIdentity, Withheld]]
"""The requests a conjunction dispatches and the requests it withholds."""


def decided(standings: list[Standing], opens: list[Standing]) -> Kept:
    """A readable decision governs: requests feeding one stand; the rest wait for every
    judgement of the deciding premises, as unresolved where any of those, or their own, is
    unread."""
    deciding = [s for s in standings if s.refusable == Refusability.READABLE]
    decisions = once(tuple(j for s in deciding for j in s.judgements))
    dispatch: dict[EffectIdentity, Dispatch] = {}
    withheld: dict[EffectIdentity, Withheld] = {}
    for s in opens:
        if s.outcome is not None and s.refusable == Refusability.READABLE:
            dispatch |= s.outcome.dispatch
        else:
            withheld |= s.deferred(decisions, unread((*decisions, *s.judgements)))
    return dispatch, withheld


def unsettled(standings: list[Standing], opens: list[Standing]) -> Kept:
    """Only unread judgements are open: a request feeding the one unread judgement stands, since
    it would under either reading of it; a request feeding one unread judgement beside another
    waits for the other, since one reading has it depend on it; a request feeding none waits
    for them all."""
    unsettled = [s for s in standings if s.refusable == Refusability.UNREAD]
    dispatch: dict[EffectIdentity, Dispatch] = {}
    withheld: dict[EffectIdentity, Withheld] = {}
    for s in opens:
        others = once(
            tuple(
                j
                for u in unsettled
                if u is not s
                for j in unread(u.judgements)
                if j not in s.judgements
            )
        )
        if s.outcome is not None and s.refusable == Refusability.UNREAD and not others:
            dispatch |= s.outcome.dispatch
        else:
            withheld |= s.deferred(others, unread((*others, *s.judgements)))
    return dispatch, withheld


def chosen(path: str, members: list[tuple[type[BaseModel], Outcome]]) -> Outcome:
    """How alternatives combine: one constructed member is the premise; two are indeterminate;
    among live open members, a request is justified only if every one needs it, and a request
    one needs and another does not is unchosen. The alternative may be refused only if every
    live member may be: a member nothing can refute will hold whatever the others do."""
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
    another does not is unchosen. The judgements open are the members'; what they establish
    about the alternative is the weakest among the members, since it is refused only if every
    member is."""
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
    judgements = once(tuple(j for _, o in opens for j in o.judgements))
    return Open(dispatch, withheld, awaiting, judgements, weakest(*(o.refusable for _, o in opens)))


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
        a decision while the source may still answer with another member."""
        interaction, kind = node.interaction, node.kind
        said = self.invocation.said(interaction)
        decision = Decided(premise=path) if len(interaction.receives) > 1 else None
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
            return judged(waiting, decision) if decision else waiting
        return self._solicited(node, node.request, path, scope)

    def _solicited(self, node: Heard, sent: Node, path: str, scope: Scope) -> Outcome:
        """The answer to this scope's request, or the request's own outcome: the send to
        dispatch, the wait after an attempt, or the premises the request still lacks."""
        interaction, kind = node.interaction, node.kind
        decision = Decided(premise=path) if len(interaction.receives) > 1 else None
        sends = interaction.sends
        if sends is None:
            msg = f"{path}: a request node without a send"
            raise RuntimeError(msg)
        request = self.construct(sent, f"{path}.{sends.__name__}", scope)
        if isinstance(request, Open):
            return judged(request, decision) if decision else request
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
        return judged(outstanding, decision) if decision else outstanding

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
                merged = conjoined([(path, outcome, ()), (path, waiting, ())])
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
        still to come are judged as each element is, by the judgements located in the element's
        construction."""
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
            parts.append((at, self.construct(node.element, at, each), ()))
        if node.closure is not None:
            sealed = self.construct(node.closure, path, scope)
            parts.append((f"{path}[{EACH}]", sealed, self.graph.judgements[node.element]))
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
        """A class constructed from its premises through Pydantic. Each premise carries the
        judgements the class makes at its field: a native constraint, judged through Pydantic
        as soon as the premise is there where nothing omitted can change the verdict, else
        left to construction; and what the evaluator cannot read, always left to construction.
        The class's judgements on the whole, its declared condition or an unread part, are
        what its parent sees it refusable by. A constant is constructed the same way, since a
        default is validated too."""
        kind = node.kind
        if constant(kind):
            return self._validated(kind, None, Built(kind=qualified(kind)), path)
        given: dict[str, object] = {}
        occurrences: list[tuple[str, Occurrence]] = []
        parts: list[Part] = []
        for name, premise in node.premises:
            at = f"{path}.{name}"
            outcome = self.construct(premise, at, scope)
            own = at_field(kind, name, at)
            if isinstance(outcome, Available):
                if any(isinstance(j, Bounded) for j in own) and early(kind, name):
                    errors = checked(kind, name, outcome.value)
                    if errors is not None:
                        outcome = Stuck((Malformed(premise=at, kind=kind, errors=errors),))
                    own = tuple(j for j in own if not isinstance(j, Bounded))
                if isinstance(outcome, Available):
                    given[name] = outcome.value
                    occurrences.append((name, outcome.occurrence))
            parts.append((at, outcome, own))
        pending = conjoined(parts)
        if pending is None:
            occurrence = Built(kind=qualified(kind), parts=tuple(occurrences))
            return self._validated(kind, given, occurrence, path)
        if isinstance(pending, Open):
            return judged(pending, *whole(kind, path))
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


def checked(kind: type[BaseModel], name: str, value: object) -> tuple[str, ...] | None:
    """The errors a field's native constraints raise over an available premise, or ``None``
    when they hold. Sound only where ``early`` holds: then the field's annotation with its
    constraint metadata is exactly what Pydantic applies to the field at construction, under
    the class's own strictness, and applying it here through Pydantic is the same judgement,
    made as soon as the premise is there."""
    info = kind.model_fields[name]
    bounds = tuple(m for m in info.metadata if native(m))
    judged: object = info.annotation
    if bounds:
        judged = Annotated[(info.annotation, *bounds)]  # pyright: ignore[reportInvalidTypeArguments, reportInvalidTypeForm]
    try:
        TypeAdapter(judged).validate_python(value, strict=kind.model_config.get("strict"))
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


def undetermined(withheld: dict[EffectIdentity, Withheld]) -> tuple[Reason, ...]:
    """The deferred effects, when nothing else can advance the invocation, as the one reason
    it is blocked: the judgements they wait behind cannot be made before them."""
    stalled = [(identity, w) for identity, w in withheld.items() if isinstance(w, Deferred)]
    if not stalled:
        return ()
    judgements = once(tuple(j for _, w in stalled for j in (*w.behind, *w.unread)))
    judgements = tuple(sorted(judgements, key=lambda j: (j.premise, type(j).__name__)))
    operations = tuple(sorted({identity.operation for identity, _ in stalled}))
    return (Undetermined(judgements=judgements, operations=operations),)


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
        case Open(dispatch, withheld, awaited):
            if dispatch or awaited:
                return Frontier(
                    dispatch=tuple(dispatch.values()),
                    awaiting=tuple(awaited.values()),
                    withheld=tuple(withheld.values()),
                )
            reasons = (*undecidable(withheld), *undetermined(withheld))
            if not reasons:
                msg = "an open goal with nothing to dispatch, await or choose"
                raise RuntimeError(msg)
            return Blocked(reasons=reasons)
        case Refuted(reasons) | Stuck(reasons):
            return Blocked(reasons=reasons)
