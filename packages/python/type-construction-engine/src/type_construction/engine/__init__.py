"""The engine: reads a program's classes, proves each route at startup by constructing it
symbolically, and answers a route by constructing it from instances at the same sites.

A program is one module. The engine reads each class's fields once, and that read is the only
thing it knows: ``holds`` is the classes each single field names, ``collects`` the classes each
tuple field names, ``premises`` the required single fields, ``heard`` the records an action
declares as ``Action[P, T]``. A class is a proposition and its fields are its premises; an
instance is a proof; ``model_dump`` of the reply is the derivation of the answer.

The unit of construction is the occurrence: one thing at one declared site in one invocation.
A site is the path of field names and positions from a root: ``("request", "cart", "lines",
"[]")`` is an element of the cart's lines, ``("request", "pair", "[1]")`` the second of a fixed
pair, ``("deployment", "payments")`` a connection, ``("Limit",)`` a constant. A class
constructed in a scope has the site of that scope and its own name; a record an action hears
has the action's site and ``heard``. Two instances of one class at two sites are two
occurrences, whatever their values; one occurrence bound into several holders stays one. A
scope opens at a root and at every element of a tuple, owns the occurrences declared or built
there, and sees its ancestors'; a product field opens no scope.

Binding is read from the declarations and nothing else. A single field binds to every
occurrence of its classes visible in the scope, alternatives among them. A tuple field binds to
every collection whose every element's scope holds one of the field's classes, among the
collections reached through the class's bound premises, by their product fields, or, for a
class whose premises reach none, the collections the scope itself holds, alternatives among
them. Whether two alternatives at one field can both be available is the proof's question,
answered from what each needs; a run that finds both refuses to choose. A class is constructed
in each scope that owns one of its candidates or holds a collection it may gather; a class with
neither is constructed once, at the root. Nothing chooses by field name, by declaration order,
by trial validation, or by what arrived first.

The proof constructs each route symbolically from its own request, the deployment and the
constants: the declared tree of the request and the deployment is the tree of symbols, the
passes construct every class the route's reply leads to wherever it binds, an action's records
enter as alternatives, and at the fixed point every construction is bound again against the
whole tree, so a candidate that appeared late is still seen. ``Proof`` is constructed from the
constructions, what was left waiting and the faults; its validator refuses the program with one
``ValidationError`` naming every fault: ``missing``, a field no occurrence fills; ``collects``,
a tuple over a class no collection's elements hold; ``unplaceable``, a class whose fields are
never visible from one scope; ``cycle``, classes that wait on each other; ``route``, a route
whose reply exists per element; ``ambiguous``, two alternatives at one field not proven never
both available; ``unreached``, a class the reply of no route leads to; ``unmodeled``, a field
that names no kind; ``boundary``, a request that holds what does not arrive; ``config``, no one
deployment; ``never``, a relation its operands' intervals make certain or impossible, or a
construction whose premises are never all available together; ``undiscriminated``, two records
one action hears that no field tells apart; ``undecided``, an action whose premises do not
establish, wherever they are all available, every condition some use of it needs before the
effect. Every fault is a structural invariant of the declarations or a contradiction the analysis
establishes; that an admitted request may find no reply is no fault, since a reply is
conditional on evidence, and a run without it ends blocked.

What the proof concludes of the constructions it reads from their references and nothing else.
A world is one way several sources are all available in one scope: what arrives is there, what
is heard brings its action, what is constructed brings one alternative of each premise and one
collection of each tuple field, and a collection brings its holder and, for a fixed collection,
each position's element, or one element standing for any when the field admits no fewer than
one; a variable collection may otherwise be empty and brings no element. A world clashes when
one key of what arrives or is heard would hold two classes, one action occurrence would have
heard two records, two relations over the same operand
references admit no ordering in common, a selection admits no count its collection can have,
or the intervals of what supplies each number and the orderings of the relations over them
have no solution together, where an unknown interval constrains nothing. The worlds are
searched depth first, one alternative at a time: a world that clashes is not extended, since
every extension clashes too, and the first world completed without a clash ends the search,
since one is all an open obligation reports. Two alternatives at one field are never both
available when every way both are clashes, which a run that found both would refuse to choose
between; a construction never constructs when every way its premises are all available
clashes. A way nothing refutes is open and establishes nothing: evidence of the same class at
another site is another occurrence, a default is a default, and bounds that overlap do not say
a run exists. A reference to a member of what arrives or is heard carries the sites it is
conditional on, each field on the way that admits another than it, ``None`` or another class,
which is where a run that lacks it is blocked. ``Proof`` keeps each exclusion and each
existence with its ways and clashes.

An effect is justified by its construction, at startup and in the run. The uses of an action
are the route's constructions that hold it or what it hears; what each needs before the effect
is every field of it no alternative of which draws on the action, since a field some
alternative of which does is filled by the effect. Of each action the proof asks whether its
premises, wherever they are all available, establish every condition of some use: a source is
established when the world holds it, when it arrives conditional on nothing in a scope the
premises populate, when it is a record an action in the world heard or the one record an
established action hears, or when it is constructed from established premises and is not
refutable, since a refutable kind's condition is established by nothing but the kind itself. An
alternative the premises leave open is decided where what decides it is exhaustive and comes
after them, each record an established action hears and each relation of the route over the
same operands where together they admit every ordering, and each case is covered on its own,
so nested choices stay nested and a shared source decides alike wherever it is held. A choice
among what arrives is there from the start, so an action performed under one of its
alternatives holds it, and its premises are the cases.
Nothing assumes the route concludes: a run whose evidence justifies the effect and then blocks
performed it rightly, and one whose premises hold while no use of them applies is the fault
``undecided``, which names the use and the evidence it needs that the action does not hold.
In the run every construction is kept with the witness of what supplied it: the reference bound
at each premise and the occurrence it dereferenced to, the scope that owns the occurrence, what
that scope holds it as and the admitted instance, each collection and each element's in order,
and the instance is of the construction's own class and holds those very instances or the
construction has failed. Before any action of a pass is performed each is authorized from that
witness alone: its construction is the proof's for this route and justified, its scope is one
this invocation opened at its site, the instance is of the class the construction makes, each
witness is a reference the construction binds that still dereferences to the same occurrence,
the action and its party are the instances the witness holds, and the occurrence has not been
performed in this invocation. The same instance held by two scopes, or by two invocations, is
two occurrences, and a witness of one authorizes nothing in the other. The ``Execution`` so
produced is what the effect boundary takes, and nothing else reaches ``perform``. An
authorization that fails is a failure of the engine's own integrity, raised before any task of
the pass is created, so no action of the pass is performed.

A construction binds each premise to references the proof retains from the declarations, one per
candidate: an ``InputRef`` to what arrives, a ``ConstructedRef`` to an occurrence the run
constructs, a ``HeardRef`` to a record an action hears or a member of it; a tuple field to the
collection's holder and one reference per element class in the element's scope. A run is the
same construction over instances at the same sites. The request and the deployment arrive and
are walked into scopes; each pass dereferences every construction of the route not yet constructed
or refuted in a scope at its site, and where every reference resolves asks
``cls.model_validate`` over the instances found, a fresh scalar constructed for the holder, and
a tuple field every element scope's instance in element order, the empty tuple for no element.
A refusal whose every error the kind raised as ``REFUTED``, its declared condition not holding
over validated operands, is the occurrence refuted in that scope, once, kept with the operands'
paths; any other refusal is a failure of the construction and propagates. The pass's actions
are performed together in one task group, what each party said is heard at the one boundary as
the action's record, and each record enters the scope its action was built in once the pass
completes, its elements fanning out under it. The run ends when the route constructs.

A pass that builds nothing ends the run as a value: the same references of each occurrence not
constructed, dereferenced in the observed state, are the pending occurrence that could still
fill the premise or the cause why nothing will, that occurrence refuted, the action having
heard another record or one without the member, or the input absent. An occurrence a premise
of which no candidate can fill is blocked by those causes, and so is every occurrence waiting
on it; the route blocked is ``Blocked``, the business's no, which ``answer`` raises as one
``ValidationError`` naming each cause at its own occurrence. The route waiting on occurrences
that wait on one another is a deadlock no evidence explains, a failure raised as such.

``opened`` enters each connection's ``open`` once and exits each once around whatever a server
kind runs inside it, whatever the body raised and whatever an exit raises. Every answer is one
OpenTelemetry span named for the route, carrying the outcome the run had, answered, refused,
failed or cancelled, and one ``admitted`` event per record that entered a scope after its pass;
one child span per performed action carries the outcome its task had, heard, failed or
cancelled. Each outcome is read from the exit path that made it; the engine depends on
``opentelemetry-api`` only. The engine keeps nothing about a program between runs:
the proof is a value the server computes once and passes in.
"""

from asyncio import CancelledError, Task, TaskGroup
from collections.abc import AsyncGenerator, Iterable, Iterator, Mapping
from contextlib import AsyncExitStack, asynccontextmanager
from dataclasses import dataclass, field, replace
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from enum import Enum
from itertools import combinations
from math import isnan
from types import MappingProxyType, ModuleType, NoneType, UnionType
from typing import (
    Literal,
    LiteralString,
    NamedTuple,
    Self,
    TypeIs,
    Union,
    cast,
    get_args,
    get_origin,
)

from opentelemetry import trace
from opentelemetry.trace import Span, Status, StatusCode
from pydantic import (
    AliasChoices,
    AliasPath,
    BaseModel,
    ConfigDict,
    RootModel,
    TypeAdapter,
    ValidationError,
    model_validator,
)
from pydantic.fields import FieldInfo
from pydantic_core import InitErrorDetails, PydanticCustomError, PydanticUndefined

from type_construction.world import (
    Action,
    Comparison,
    Computation,
    Condition,
    Config,
    Connection,
    Derived,
    Fact,
    Interval,
    Json,
    Python,
    Record,
    Refusals,
    Refutable,
    Relation,
    Reply,
    Request,
    Route,
    Selection,
    Setting,
    Value,
)

__all__ = [
    "Blocked",
    "Clash",
    "Collected",
    "ConstructedRef",
    "Construction",
    "Coverage",
    "Exclusion",
    "Execution",
    "Existence",
    "Fault",
    "HeardRef",
    "InputRef",
    "Joint",
    "Justification",
    "Known",
    "Lack",
    "Proof",
    "Ref",
    "Run",
    "Scope",
    "Site",
    "Source",
    "Unknown",
    "Use",
    "Waiting",
    "World",
    "answer",
    "asked",
    "clash",
    "classes",
    "collects",
    "config",
    "configs",
    "exclusions",
    "existences",
    "hear",
    "heard",
    "holds",
    "interval",
    "joint",
    "justifications",
    "models",
    "never",
    "opened",
    "outcomes",
    "produces",
    "proven",
    "ran",
]

type Site = tuple[str, ...]
"""Where an occurrence is declared: the field names and positions from a root, ``"[]"`` for an
element of ``tuple[E, ...]`` and ``"[0]"`` for the first of a fixed tuple; a class name for a
class constructed in a scope, or a constant; ``"heard"`` for what an action heard."""

type Options = tuple[type[BaseModel], ...]
"""The classes a field may hold: a union's members, else the one class."""

type Weight = tuple[Decimal, int]
"""The weight of a difference constraint ``x - y <= c``: ``c`` and ``-1`` when strict, else
``0``, so that a cycle whose weights sum below ``(0, 0)`` is a contradiction."""

type Edge = tuple[object, object, Weight]
"""One difference constraint ``x - y <= c`` as the edge ``(y, x, weight)``; a variable is a
reference to what supplies a number, so two relations over one reference constrain one value,
and ``ZERO`` stands for the constant zero."""

ZERO = object()
"""The variable whose value is zero, which what a reference supplies is constrained against."""

REQUEST: Site = ("request",)
"""The site of what arrived: the route's own field for it."""

DEPLOYMENT: Site = ("deployment",)
"""The site of the deployment."""

HEARD = "heard"
"""The last step of a record's site: what its action heard."""

tracer = trace.get_tracer("type_construction.engine")
"""Spans named by the program's classes: one per answer, named for the route, with one child per
performed action, named for the action. Attributes are class names and counts, never contents.
With no SDK configured these are no-ops; the deployment supplies the SDK and the exporter."""


@dataclass(eq=False)
class Construction:
    """One class a route constructs, in the scope at a site template: the one record of how it
    constructs, which the proof, the run and the explanation of a run all read. Each premise
    field binds to the references of its candidate sources, alternatives among them; each
    tuple field to the collections it may gather, alternatives among them. Everything else
    about the class, its fresh fields, its computed fields, its shape, is read from the class
    itself. The analysis assembles the graph with these objects, binds each once more against
    the whole tree at its fixed point, and seals them before the proof publishes them: a sealed
    construction refuses every assignment, and a reference to one is a reference to this
    object, never to a name or a path."""

    route: type[BaseModel]
    cls: type[BaseModel]
    scope: Site
    premises: Mapping[str, tuple[Ref, ...]] = field(default_factory=dict[str, tuple["Ref", ...]])
    collections: Mapping[str, tuple[Collected, ...]] = field(
        default_factory=dict[str, tuple["Collected", ...]]
    )
    sealed: bool = field(default=False, init=False)

    def __repr__(self) -> str:
        return f"Construction({self.route.__name__}: {'.'.join(self.site)})"

    def __setattr__(self, name: str, value: object) -> None:
        if self.__dict__.get("sealed"):
            immutable = f"{self!r} is sealed"
            raise AttributeError(immutable)
        super().__setattr__(name, value)

    @property
    def site(self) -> Site:
        """The declared site: the scope's and the class's name, for a concrete path."""
        return (*self.scope, self.cls.__name__)

    def rebound(self, found: Construction) -> None:
        """The binding against the whole tree, in place of the first."""
        self.premises, self.collections = found.premises, found.collections

    def seal(self) -> None:
        """Published: the binding becomes read-only mappings and nothing assigns here again."""
        self.premises = MappingProxyType(dict(self.premises))
        self.collections = MappingProxyType(dict(self.collections))
        self.sealed = True


@dataclass(frozen=True)
class InputRef:
    """A reference to what arrives: the request, the deployment, a constant, or a member of
    one, in the scope at a site, of a class. It dereferences to what the scope chain holds for
    it, present from the start or never. ``because`` is the sites of the fields on the way to
    it that admit another than this, ``None`` or another class: this may not arrive though its
    holder did, and nothing that needs it is present in every invocation."""

    scope: Site
    member: Site
    cls: type[BaseModel]
    because: tuple[Site, ...] = ()

    @property
    def site(self) -> Site:
        """The declared site: the scope's and the member path."""
        return (*self.scope, *self.member)

    @property
    def key(self) -> Key:
        """What a scope holds it under: no origin, and its site."""
        return (None, self.site)

    def held(self, cls: type[BaseModel], name: str, *, conditional: bool) -> InputRef:
        """The reference to what a single field of this holds."""
        return InputRef(self.scope, (*self.member, name), cls, conditioned(self, name, conditional))

    def element(self, cls: type[BaseModel], name: str, step: str, *, conditional: bool) -> InputRef:
        """The reference to an element of a tuple field of this, in the element's own scope."""
        return InputRef((*self.site, name, step), (), cls, conditioned(self, name, conditional))


@dataclass(frozen=True)
class ConstructedRef:
    """A reference to what the run constructs: the construction itself. It dereferences to that
    occurrence in the scope chain, constructed, refuted or pending."""

    construction: Construction

    @property
    def cls(self) -> type[BaseModel]:
        """The class constructed."""
        return self.construction.cls

    @property
    def scope(self) -> Site:
        """The scope template the construction is placed at."""
        return self.construction.scope

    @property
    def site(self) -> Site:
        """The declared site."""
        return self.construction.site


@dataclass(frozen=True)
class HeardRef:
    """A reference to what an action heard: the action's construction, the record among those
    it declares, and the member path under the record, of a class. It dereferences to what the
    action heard in the scope chain: pending while the action is, the record named, another
    record, or the record named without the member. ``because`` as an ``InputRef`` carries
    it."""

    action: Construction
    record: type[BaseModel]
    member: Site
    cls: type[BaseModel]
    because: tuple[Site, ...] = ()

    @property
    def scope(self) -> Site:
        """The scope template the reference is placed at: the action's, where its record
        enters; for an element of a tuple the record declares, or a member of one, that
        element's scope, the site through the innermost position, which the run opens under
        the record as the analysis does."""
        steps = [index for index, part in enumerate(self.member) if part.startswith("[")]
        if not steps:
            return self.action.scope
        return (*self.action.site, HEARD, *self.member[: steps[-1] + 1])

    @property
    def site(self) -> Site:
        """The declared site: the action's, ``heard``, and the member path."""
        return (*self.action.site, HEARD, *self.member)

    @property
    def key(self) -> Key:
        """What a scope holds it under: the action, and the member path."""
        return (self.action, self.member)

    def held(self, cls: type[BaseModel], name: str, *, conditional: bool) -> HeardRef:
        """The reference to what a single field of this holds."""
        return HeardRef(
            self.action,
            self.record,
            (*self.member, name),
            cls,
            conditioned(self, name, conditional),
        )

    def element(self, cls: type[BaseModel], name: str, step: str, *, conditional: bool) -> HeardRef:
        """The reference to an element of a tuple field of this, in the element's own scope."""
        return HeardRef(
            self.action,
            self.record,
            (*self.member, name, step),
            cls,
            conditioned(self, name, conditional),
        )


def conditioned(holder: InputRef | HeardRef, name: str, conditional: bool) -> tuple[Site, ...]:  # noqa: FBT001
    """What a member of a holder is conditional on: the holder's sites, and the field's own
    when what it declares admits another than this member, ``None`` or another class."""
    return (*holder.because, (*holder.site, name)) if conditional else holder.because


type Ref = InputRef | ConstructedRef | HeardRef
"""Where a bound premise comes from, retained from the declarations: the one thing a run
dereferences to construct, and to explain what it could not."""

type Group = tuple[Ref | Collected, ...]
"""The alternatives for one thing a source needs: any one of them available suffices."""

type Key = tuple[Construction | None, Site]
"""What a scope holds an arrived instance or a collection under: its origin, the action that
heard it or none for what arrives, and the member path, the whole declared site for what
arrives."""


@dataclass(frozen=True)
class Collected:
    """One collection a construction's tuple field may gather: the reference to the occurrence
    that holds it, the tuple field's name, the references to the elements it takes, one per
    element class, each in the element's scope, ``"[]"`` for every element of a variable tuple
    and a position for each of a fixed one, the positions the holder declares, ``None`` for
    ``tuple[E, ...]``, and the fewest elements the gathering field admits, from its compiled
    schema: a selection admits no fewer than one, and so needs an element."""

    holder: InputRef | HeardRef
    name: str
    elements: tuple[Ref, ...]
    positions: int | None
    least: int = 0

    @property
    def site(self) -> Site:
        """The collection's declared site."""
        return (*self.holder.site, self.name)

    @property
    def key(self) -> Key:
        """What a scope holds the collection under: the holder's origin, and the field."""
        origin, member = self.holder.key
        return (origin, (*member, self.name))

    @property
    def every(self) -> tuple[str, ...]:
        """The element scopes, as steps under the site: each position of a fixed collection,
        the one element standing for any of a variable one."""
        if self.positions is None:
            return ("[]",)
        return tuple(f"[{index}]" for index in range(self.positions))

    @property
    def steps(self) -> tuple[str, ...]:
        """The element scopes a construction over this needs available: each position of a
        fixed collection; the one element, for a variable collection the field admits no fewer
        than one of; none for a variable collection that may be empty."""
        return self.every if self.positions is not None or self.least else ()

    def placed(self, step: str) -> Group:
        """The element references in one element scope, alternatives among them."""
        return tuple(r for r in self.elements if r.scope == (*self.site, step))


def is_model(cls: object) -> TypeIs[type[BaseModel]]:
    """Whether an annotation is a Pydantic class."""
    return isinstance(cls, type) and issubclass(cls, BaseModel)


def is_route(cls: type[object]) -> TypeIs[type[Route[Request, Reply[Fact]]]]:
    """Whether a class is a program's route: a strict subclass of ``Route``."""
    return issubclass(cls, Route) and cls is not Route


def is_action(cls: type[object]) -> TypeIs[type[Action[Connection, Record]]]:
    """Whether a class is a program's action: a strict subclass of ``Action``."""
    return issubclass(cls, Action) and cls is not Action


def is_request(cls: object) -> TypeIs[type[Request]]:
    """Whether an annotation is a program's request class."""
    return isinstance(cls, type) and issubclass(cls, Request) and cls is not Request


def is_record(cls: object) -> TypeIs[type[Record]]:
    """Whether an annotation is a program's record class."""
    return isinstance(cls, type) and issubclass(cls, Record) and cls is not Record


def is_scalar(cls: object) -> TypeIs[type[RootModel[object]]]:
    """Whether an annotation is a class over one root value."""
    return isinstance(cls, type) and issubclass(cls, RootModel)


def is_setting(cls: object) -> TypeIs[type[Setting[object]]]:
    """Whether an annotation is a deployment value."""
    return isinstance(cls, type) and issubclass(cls, Setting)


def is_value(cls: object) -> TypeIs[type[Value]]:
    """Whether an annotation is a program's composite part."""
    return isinstance(cls, type) and issubclass(cls, Value) and cls is not Value


def is_relation(cls: object) -> TypeIs[type[Relation]]:
    """Whether a class is a relation: a strict subclass of ``Relation``."""
    return isinstance(cls, type) and issubclass(cls, Relation) and cls is not Relation


def is_selection(cls: object) -> TypeIs[type[Selection[BaseModel]]]:
    """Whether a class is a selection: a strict subclass of ``Selection``."""
    return isinstance(cls, type) and issubclass(cls, Selection) and cls is not Selection


def is_connection(cls: object) -> TypeIs[type[Connection]]:
    """Whether an annotation is a party."""
    return isinstance(cls, type) and issubclass(cls, Connection)


def is_config(cls: object) -> TypeIs[type[Config]]:
    """Whether a class is a program's deployment."""
    return isinstance(cls, type) and issubclass(cls, Config) and cls is not Config


def is_enum(cls: object) -> TypeIs[type[Enum]]:
    """Whether an annotation is an enumeration."""
    return isinstance(cls, type) and issubclass(cls, Enum)


def is_literal(annotation: object) -> bool:
    """Whether an annotation is a ``Literal``."""
    return get_origin(annotation) is Literal


def is_elements(value: object) -> TypeIs[tuple[object, ...]]:
    """Whether a field's value is a tuple of elements."""
    return isinstance(value, tuple)


def is_performed(instance: BaseModel) -> TypeIs[Action[Connection, Record]]:
    """Whether a constructed instance is an action the engine performs."""
    return isinstance(instance, Action)


def carries(cls: type[BaseModel]) -> bool:
    """Whether a class brings the scalars and values it holds into the run: what arrives, what a
    party says, and a composite part."""
    return issubclass(cls, (Request, Record, Value))


def refutable(cls: type[BaseModel]) -> bool:
    """Whether a class is a refutable kind, one whose refusal can say only that it does not
    hold for these operands."""
    return issubclass(cls, Refutable)


def written(cls: type[object]) -> bool:
    """Whether a class is one the program wrote: not a parametrization Pydantic registered in
    the module, as ``Tell[Party, Heard]`` beside ``Asked``, and not a library kind whose
    parameters are still open, as ``Tell`` itself."""
    return (
        not issubclass(cls, BaseModel)
        or cls is BaseModel
        or (
            cls.__pydantic_generic_metadata__["origin"] is None
            and not cls.__pydantic_generic_metadata__["parameters"]
        )
    )


def classes(program: ModuleType) -> list[type[object]]:
    """Every class the program module declares: defined there, not imported into it. A class
    whose forward references Pydantic has not resolved is rebuilt first, so its fields read as
    classes."""
    found = [
        c
        for c in vars(program).values()
        if isinstance(c, type) and c.__module__ == program.__name__ and written(c)
    ]
    for c in found:
        if is_model(c) and not c.__pydantic_complete__:
            c.model_rebuild()
    return found


def models(program: ModuleType) -> tuple[type[BaseModel], ...]:
    """Every Pydantic class the program module declares, in definition order."""
    return tuple(c for c in classes(program) if is_model(c))


def configs(program: ModuleType) -> tuple[type[Config], ...]:
    """Every ``Config`` subclass the program module declares; the proof refuses any number but
    one."""
    return tuple(c for c in classes(program) if is_config(c))


def config(program: ModuleType) -> type[Config]:
    """The one ``Config`` subclass a proven program declares."""
    (found,) = configs(program)
    return found


def union_members(annotation: object) -> tuple[object, ...]:
    """A union's members, or the one annotation: the one read of a union the engine makes."""
    return get_args(annotation) if get_origin(annotation) in (UnionType, Union) else (annotation,)


def model_classes(annotation: object) -> Options:
    """The Pydantic classes among an annotation's members."""
    return tuple(m for m in union_members(annotation) if is_model(m))


@dataclass(frozen=True)
class Declared:
    """One field as Pydantic declares it: the engine's one view of a declaration, read from
    ``model_fields`` when asked and kept nowhere. Each structural property the engine needs of
    a field is derived here once, from the resolved annotation, the ``FieldInfo`` and its
    metadata; nothing else in the engine reads them. The meaning stays in the declaration."""

    cls: type[BaseModel]
    name: str
    info: FieldInfo

    @property
    def annotation(self) -> object:
        """The resolved annotation."""
        return self.info.annotation

    @property
    def is_tuple(self) -> bool:
        """Whether the field collects elements: a ``tuple`` annotation."""
        return get_origin(self.annotation) is tuple

    @property
    def items(self) -> tuple[object, ...]:
        """The annotations a value is made of: each position of a fixed tuple, the one element
        of ``tuple[X, ...]``, the annotation itself otherwise."""
        if self.is_tuple:
            return tuple(a for a in get_args(self.annotation) if a is not Ellipsis)
        return (self.annotation,)

    @property
    def fixed(self) -> bool:
        """Whether a tuple fixes its positions: ``tuple[X, X]`` and ``tuple[X]`` do."""
        return self.is_tuple and Ellipsis not in get_args(self.annotation)

    @property
    def positions(self) -> int | None:
        """The positions a tuple declares: their number for a fixed tuple, ``None`` otherwise."""
        return len(self.items) if self.fixed else None

    def step(self, index: int) -> str:
        """The site step of one element: its index for a fixed tuple, ``"[]"`` for every
        element of a variable one."""
        return f"[{index}]" if self.fixed else "[]"

    @property
    def members(self) -> tuple[object, ...]:
        """Every member of every item's union, flattened."""
        return tuple(m for item in self.items for m in union_members(item))

    @property
    def item_classes(self) -> tuple[Options, ...]:
        """The classes each item may hold."""
        return tuple(model_classes(item) for item in self.items)

    @property
    def classes(self) -> Options:
        """The classes the field may hold, every item's in order."""
        return tuple(c for classes_ in self.item_classes for c in classes_)

    @property
    def admits(self) -> frozenset[object]:
        """The values a ``Literal`` annotation admits; empty for any other annotation."""
        return frozenset(get_args(self.annotation)) if is_literal(self.annotation) else frozenset()

    @property
    def admits_none(self) -> bool:
        """Whether the field admits ``None``: what it holds may not arrive."""
        return NoneType in self.members

    @property
    def required(self) -> bool:
        """Whether a value must be given."""
        return self.info.is_required()

    @property
    def aliases(self) -> frozenset[str]:
        """Every top-level key the field validates by, as Pydantic resolves it: the validation
        alias, each choice of an ``AliasChoices``, the first step of an ``AliasPath``, and the
        field's name when the class validates by name or declares no alias."""
        declared_ = self.info.validation_alias or self.info.alias
        choices = declared_.choices if isinstance(declared_, AliasChoices) else [declared_]
        found = {
            str(choice.path[0]) if isinstance(choice, AliasPath) else choice
            for choice in choices
            if isinstance(choice, (str, AliasPath))
        }
        by_name = self.cls.model_config.get("validate_by_name") or self.cls.model_config.get(
            "populate_by_name"
        )
        if declared_ is None or by_name:
            found.add(self.name)
        return frozenset(found)

    @property
    def required_key(self) -> str | None:
        """The one key a payload must carry for this field, when it is required and validates
        by exactly one key; ``None`` when any of several keys would do, which no static
        conclusion rests on."""
        keys_ = self.aliases
        return next(iter(keys_)) if self.required and len(keys_) == 1 else None

    @property
    def output(self) -> Output:
        """What the field's declared type can output when it validates any input it admits:
        ``Known``, every successful output described conservatively, or ``Unknown``, naming
        the node of the compiled schema the description cannot pass. The type's own claim,
        true of every occurrence: a default among the outputs narrows nothing, since another
        admitted value may be given instead."""
        return self.outputs(PLACED)

    def outputs(self, seen: frozenset[type[BaseModel]], inputs: Inputs | None = None) -> Output:
        """``output`` under an input contract a construction site establishes, with the classes
        already being analyzed, so a derivation reached again through its own operands refines
        nothing. The field's complete schema is located in the class's as Pydantic compiled
        it, definitions resolved and the model's own before validators passed, since every
        output still passes the fields' schemas, though a before validator may supply a field,
        so beneath one no input is omitted; any other validator around the model or its fields
        leaves every field's output unknown. The one source of the constraints Pydantic
        applies, since a repeated constraint keeps the last declared and distinct constraints
        all apply."""
        top: Mapping[str, object] = self.cls.__pydantic_core_schema__
        definitions: dict[object, Mapping[str, object]] = {}
        at: tuple[str, ...] = ()
        inputs = ADMITTED if inputs is None else inputs
        if top.get("type") == "definitions":
            definitions = {d.get("ref"): d for d in listed(top.get("definitions"))}
            top, at = mapped(top.get("schema")), ("definitions",)
        model = beneath(top, "model", definitions, at)
        if isinstance(model, Unknown):
            return model
        node, at = model
        config_ = mapped(node.get("config"))
        if not node.get("root_model"):
            fields_ = beneath(mapped(node.get("schema")), "model-fields", definitions, at)
            if isinstance(fields_, Unknown):
                return fields_
            node, at = fields_
            node = mapped(mapped(node.get("fields")).get(self.name))
            at = (*at, "model-field")
        compiled = Compiled(
            self.cls,
            seen | {self.cls},
            definitions,
            bool(config_.get("validate_default")),
            tuple(self.info.metadata),
            inputs.fed() if "function-before" in at else inputs,
        )
        return compiled.outputs(mapped(node.get("schema")), at)

    @property
    def computation(self) -> Computation | None:
        """The computation the field declares in its metadata, if it is computed."""
        return next((m for m in self.info.metadata if isinstance(m, Computation)), None)

    @property
    def condition(self) -> Condition | None:
        """The condition the field declares in its metadata, if it is one a kind refuses by."""
        return next((m for m in self.info.metadata if isinstance(m, Condition)), None)

    @property
    def fresh(self) -> bool:
        """Whether the field is constructed anew for its holder: required, single, and every
        class it may hold a fresh scalar."""
        classes_ = self.classes
        return not self.is_tuple and self.required and bool(classes_) and all(map(fresh, classes_))

    @property
    def premise(self) -> bool:
        """Whether the field is a premise the scope must hold before the class is asked for: a
        required single field naming classes, not fresh."""
        return not self.is_tuple and self.required and bool(self.classes) and not self.fresh

    @property
    def shape(self) -> str:
        """A tuple annotation in the developer's names: ``tuple[X, ...]`` or ``tuple[X, X]``."""
        inner = ", ".join(names(classes_) for classes_ in self.item_classes)
        return f"tuple[{inner}]" if self.fixed else f"tuple[{inner}, ...]"

    @property
    def length(self) -> tuple[int, int | None] | Unknown:
        """How many elements a tuple the field outputs can have: a fixed tuple's positions
        twice, else the ``min_length`` and ``max_length`` of its compiled schema; unbounded
        for a schema that outputs no tuple; unknown as the output is."""
        found = self.output
        return found.lengths if isinstance(found, Known) else found

    @property
    def bounds(self) -> Interval | Unknown:
        """The interval every number the field outputs lies in; unbounded for a schema that
        outputs no number; unknown as the output is."""
        found = self.output
        return found.numbers if isinstance(found, Known) else found


def mapped(schema: object) -> Mapping[str, object]:
    """A core schema node as a mapping; an absent node is empty."""
    return cast("Mapping[str, object]", schema) if isinstance(schema, Mapping) else {}


def items(values: object) -> list[object]:
    """A core schema's list of values; an absent list is empty."""
    return cast("list[object]", values) if isinstance(values, list) else []


def listed(schemas: object) -> list[Mapping[str, object]]:
    """A core schema's list of nodes; an absent list is empty."""
    return [mapped(s) for s in items(schemas)]


@dataclass(frozen=True)
class Unknown:
    """A property of a field's successful outputs that its compiled schema does not justify:
    the node that stands in the way, by type, and where it is, as the node types from the top
    of the class's schema down to it. What is unknown establishes nothing: no exclusivity, no
    impossibility, no certainty, and no permission; a diagnostic that needs it is omitted and
    an obligation that needs it stays unproven."""

    operation: str
    """The node type, or the operation within one, the analysis does not pass."""
    at: tuple[str, ...]
    """The node types from the class's compiled schema down to it."""


UNBOUNDED = Interval()
"""The interval that claims nothing of a number."""


@dataclass(frozen=True)
class Known:
    """Every successful output of a compiled schema, conservatively: an interval that contains
    every number among the outputs, the lengths a tuple among them can have, and whether
    ``None`` is one. A facet the schema says nothing about is unbounded, which claims nothing;
    an empty interval with no ``None`` is a schema no value satisfies. The description can be
    wider than what validates, never narrower: ``multiple_of`` and the decimal digit limits
    are left to remove values from within the interval, and nothing says every value within
    it is attainable."""

    numbers: Interval = UNBOUNDED
    """The interval every number among the outputs lies in."""
    lengths: tuple[int, int | None] = (0, None)
    """The fewest and the most elements a tuple among the outputs has; ``None`` for no most."""
    none: bool = False
    """Whether ``None`` is among the outputs."""


type Output = Known | Unknown
"""What the analysis says of a compiled schema's successful outputs."""


EXECUTED = frozenset({"function-after", "function-plain", "function-wrap"})
"""Validator nodes whose output is their function's: passed only when a kind's own."""

WRAPPED = EXECUTED | {"function-before", "nullable", "custom-error", "json", "default"}
"""Nodes around one inner schema every successful output passes through, or is extended from:
a before validator feeds the inner schema, which bounds the output and says nothing of what
inputs it admits; ``nullable`` adds ``None``; ``default`` adds the default when it is not
validated."""

BRANCHES: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        "union": ("choices",),
        "tagged-union": ("choices",),
        "json-or-python": ("json_schema", "python_schema"),
        "lax-or-strict": ("lax_schema", "strict_schema"),
    }
)
"""Nodes whose output is one alternative's, with the keys the alternatives are under: every
branch of a mode or a strictness is kept, since the analysis is not told which validates."""

NUMBERS = frozenset({"int", "float", "decimal"})
"""The numeric nodes, whose compiled bounds the interval is read from."""

DATA = frozenset(
    {
        "str",
        "bytes",
        "bool",
        "date",
        "time",
        "datetime",
        "timedelta",
        "uuid",
        "url",
        "multi-host-url",
        "complex",
        "enum",
        "is-instance",
        "is-subclass",
        "callable",
        "list",
        "set",
        "frozenset",
        "dict",
        "generator",
        "typed-dict",
        "dataclass",
        "dataclass-args",
        "model",
        "model-fields",
        "arguments",
        "arguments-v3",
    }
)
"""Nodes that output what they validate, none of it bounded as a number, a tuple or ``None``
beyond what the unbounded description already claims."""


def beneath(
    node: Mapping[str, object],
    kind: str,
    definitions: Mapping[object, Mapping[str, object]],
    at: tuple[str, ...],
) -> tuple[Mapping[str, object], tuple[str, ...]] | Unknown:
    """The node of a kind beneath the wrappers every output passes unchanged: a definition
    reference resolved and a before validator passed; any other wrapper, a validator that
    returns what it will, is unknown."""
    while node.get("type") != kind:
        found = str(node.get("type"))
        at = (*at, found)
        if found == "definition-ref":
            node = definitions.get(node.get("schema_ref"), {})
        elif found == "function-before":
            node = mapped(node.get("schema"))
        else:
            return Unknown(found, at)
    return node, (*at, kind)


UNSUPPLIED: Mapping[str, Interval | Unknown] = MappingProxyType({})
"""No operand supplied by a site: each is anything its declared classes admit."""


@dataclass(frozen=True)
class Inputs:
    """What a construction site establishes about a field's inputs, carried into the output
    analysis: whether the field's own input is provably omitted, so only the default's path
    runs, and what the site supplies for each operand field a computation reads, so the
    operation runs over that and not over everything the operand's classes admit. The empty
    contract is the type's own: any admitted input may arrive, and an operand is anything its
    classes admit. A site establishes a contract from its bindings and nowhere else: the
    engine constructs a constant with no input, and binds a derivation's operands to
    references."""

    omitted: bool = False
    """Whether the field's input is provably absent."""
    operands: Mapping[str, Interval | Unknown] = UNSUPPLIED
    """What the site supplies for each operand field it binds."""

    def fed(self) -> Inputs:
        """The contract beneath a before validator, which may supply what was omitted."""
        return replace(self, omitted=False)


ADMITTED = Inputs()
"""The type's own contract: any input the type admits may arrive."""


@dataclass(frozen=True)
class Compiled:
    """One field's place in its class's compiled schema, for the analysis of its outputs: the
    class and those already being analyzed above it, the definitions the schema may
    reference, whether the class validates defaults, the objects the field's metadata
    declares, which own the only validators whose output the analysis follows, and the input
    contract the analysis runs under."""

    cls: type[BaseModel]
    seen: frozenset[type[BaseModel]]
    definitions: Mapping[object, Mapping[str, object]]
    validate_default: bool
    owners: tuple[object, ...]
    inputs: Inputs = ADMITTED

    def outputs(
        self, node: Mapping[str, object], at: tuple[str, ...], seen: frozenset[object] = frozenset()
    ) -> Output:
        """What a node outputs when it validates, from the compiled schema alone: an
        alternative's, a referenced definition's, a chain's last stage's, a wrapper's inner
        schema's extended by what the wrapper adds, or a native node's own."""
        kind = str(node.get("type"))
        here = (*at, kind)
        if kind in BRANCHES:
            return combined(self.outputs(a, here, seen) for a in alternatives(node))
        if kind == "definition-ref":
            return self.referenced(node, here, seen)
        if kind == "chain":
            steps = listed(node.get("steps"))
            return self.outputs(steps[-1], here, seen) if steps else Unknown(kind, here)
        if kind in WRAPPED:
            return self.wrapped(node, here, seen)
        return native(node, here)

    def referenced(
        self, node: Mapping[str, object], here: tuple[str, ...], seen: frozenset[object]
    ) -> Output:
        """A referenced definition's output; unknown for a definition the schema does not hold
        or one already being followed, rather than a bound invented for the recursion."""
        ref = node.get("schema_ref")
        target = self.definitions.get(ref)
        if target is None or ref in seen:
            return Unknown(here[-1], here)
        return self.outputs(target, here, seen | {ref})

    def wrapped(
        self, node: Mapping[str, object], here: tuple[str, ...], seen: frozenset[object]
    ) -> Output:
        """A wrapper's output: unknown for a validator that is not a kind's own, since it
        returns what it will; else the inner schema's, with ``None`` for ``nullable``, the
        default's outcomes for a ``default``, and a derivation's own mathematics for a
        ``Derived`` admitting what it computed through the declared type itself. A before
        validator may supply what the site omitted, so beneath one nothing is omitted."""
        kind = here[-1]
        owner = self.owner(node) if kind in EXECUTED else None
        if kind in EXECUTED and owner is None:
            return Unknown(kind, here)
        inner = replace(self, inputs=self.inputs.fed()) if kind == "function-before" else self
        found = inner.outputs(mapped(node.get("schema")), here, seen)
        if isinstance(found, Unknown):
            return found
        if kind == "nullable":
            return replace(found, none=True)
        if kind == "default":
            return self.defaulted(node, here, found)
        if isinstance(owner, Derived) and direct(node):
            return self.derived(owner, found)
        return found

    def derived(self, owner: Derived, found: Known) -> Known:
        """A derivation's output: what its operation makes of what its operands can be, and
        within what the declared type admits, since the type admits the computed value as it
        is and refuses any value given for it, so this is the type's own claim; an operand is
        what the site supplies for it, else anything its classes admit; the type's bound alone
        when an operand's interval is unknown, which the operation can make nothing of."""
        operands: list[Interval] = []
        for name in owner.operands:
            span = self.inputs.operands.get(name) or spanned(
                declared(self.cls, name).classes, self.seen
            )
            if isinstance(span, Unknown):
                return found
            operands.append(span)
        return replace(found, numbers=meet(found.numbers, owner.interval(tuple(operands))))

    def owner(self, node: Mapping[str, object]) -> Computation | Condition | None:
        """The kind's own object a validator node is the bound method of, if it is one: a wrap
        validator of a ``Computation`` or a ``Condition`` the field's metadata declares, whose
        output is what the field's own type admitted of what it computed or was given."""
        function = mapped(node.get("function")).get("function")
        owner = getattr(function, "__self__", None)
        if (
            node.get("type") == "function-wrap"
            and isinstance(owner, (Computation, Condition))
            and any(owner is o for o in self.owners)
        ):
            return owner
        return None

    def defaulted(self, node: Mapping[str, object], here: tuple[str, ...], found: Known) -> Output:
        """A ``default`` node's output. The type's own claim admits any input, so the output
        is the inner schema's, with the default among the outputs when it is not validated,
        and unknown for a factory, whose value nothing bounds. Where the site omits the input,
        only the default's path runs: the default itself when it is not validated or the
        declared type admits it as it is, else the inner schema's bound it validates within."""
        validate = node.get("validate_default")
        validated = self.validate_default if validate is None else bool(validate)
        if "default_factory" in node:
            return Unknown("default_factory", here)
        if not self.inputs.omitted:
            return found if validated else combined([found, only(node.get("default"), here)])
        return found if validated and not direct(node) else only(node.get("default"), here)


def direct(node: Mapping[str, object]) -> bool:
    """Whether a node's inner schema is a native numeric or literal node, which outputs the
    number it admits as it is: what a default or a computed value passes through unchanged."""
    return mapped(node.get("schema")).get("type") in NUMBERS | {"literal"}


def meet(a: Interval, b: Interval) -> Interval:
    """The interval both intervals contain: the greater low and the lesser high, strict where
    the bound that decides is."""
    lows = [(i.low, i.low_strict) for i in (a, b) if i.low is not None]
    highs = [(i.high, i.high_strict) for i in (a, b) if i.high is not None]
    low = max((v for v, _ in lows), default=None)
    high = min((v for v, _ in highs), default=None)
    return Interval(
        low=low,
        low_strict=any(strict for v, strict in lows if v == low),
        high=high,
        high_strict=any(strict for v, strict in highs if v == high),
    )


def alternatives(node: Mapping[str, object]) -> list[Mapping[str, object]]:
    """The schemas a branching node chooses among: a union's choices, each perhaps labelled, a
    tagged union's by tag, or the two modes or strictnesses."""
    kind = str(node.get("type"))
    if kind == "union":
        return [
            mapped(cast("tuple[object, ...]", c)[0] if isinstance(c, tuple) else c)
            for c in items(node.get("choices"))
        ]
    if kind == "tagged-union":
        return [mapped(c) for c in mapped(node.get("choices")).values()]
    return [mapped(node.get(k)) for k in BRANCHES[kind]]


def combined(outputs: Iterable[Output]) -> Output:
    """What alternatives output together: the hull of their intervals, the fewest and the most
    elements among them, ``None`` if any outputs it; unknown when any alternative is, since
    a bound for the whole needs every alternative accounted for."""
    found = list(outputs)
    knowns = [o for o in found if isinstance(o, Known)]
    if len(knowns) < len(found):
        return next(o for o in found if isinstance(o, Unknown))
    if not knowns:
        return Known()
    highs = [k.lengths[1] for k in knowns]
    return Known(
        numbers=hull(k.numbers for k in knowns),
        lengths=(
            min(k.lengths[0] for k in knowns),
            None if any(h is None for h in highs) else max(h for h in highs if h is not None),
        ),
        none=any(k.none for k in knowns),
    )


def native(node: Mapping[str, object], here: tuple[str, ...]) -> Output:
    """A native node's output, from its compiled constraints: a number's bounds, a literal's
    values, a tuple's lengths, ``None``, anything for ``any``, and the unbounded description
    for data that is none of these; unknown for a node the analysis does not know, such as
    ``call``, whose output is its function's."""
    kind = here[-1]
    if kind in NUMBERS:
        return numeric(node, here)
    if kind == "literal":
        return literal(node)
    if kind == "tuple":
        return Known(lengths=lengths(node))
    if kind in ("none", "any"):
        return Known(none=True)
    if kind in DATA:
        return Known()
    return Unknown(kind, here)


def numeric(node: Mapping[str, object], here: tuple[str, ...]) -> Output:
    """A number's bounds: ``gt`` and ``ge`` both apply, so the lower bound is the stronger,
    strict when the strict one is at least the other; ``lt`` and ``le`` likewise above. An
    integer schema has no value between two integers, so a strict bound is the next integer's
    non-strict one. Bounds that cross are an empty interval. A float admits ``nan`` unless
    the schema forbids it or a bound refuses it, and ``nan`` lies in no interval, so that
    output is unknown; an infinity a bound admits lies beyond the unbounded end."""
    kind = here[-1]
    gt, ge, lt, le = (decimal(node.get(k)) for k in ("gt", "ge", "lt", "le"))
    non_finite = node.get("allow_inf_nan", kind == "float")
    if kind != "int" and non_finite and (gt, ge, lt, le) == (None, None, None, None):
        return Unknown("allow_inf_nan", here)
    low = strongest([(gt, True), (ge, False)], above=True)
    high = strongest([(lt, True), (le, False)], above=False)
    if kind == "int":
        low = low and (low[0].to_integral_value(ROUND_FLOOR) + 1 if low[1] else low[0], False)
        high = high and (
            high[0].to_integral_value(ROUND_CEILING) - 1 if high[1] else high[0],
            False,
        )
    return Known(
        numbers=Interval(
            low=low and low[0],
            low_strict=bool(low and low[1]),
            high=high and high[0],
            high_strict=bool(high and high[1]),
        )
    )


def literal(node: Mapping[str, object]) -> Known:
    """A literal's outputs are its values: the numbers among them span the interval, and
    ``None`` among them is an output."""
    expected = items(node.get("expected"))
    numbers = [d for v in expected if (d := decimal(v)) is not None]
    return Known(
        numbers=Interval(low=min(numbers), high=max(numbers)) if numbers else Interval(),
        none=any(v is None for v in expected),
    )


def lengths(node: Mapping[str, object]) -> tuple[int, int | None]:
    """A tuple's lengths: its positions twice when fixed, else its ``min_length`` and
    ``max_length``, the fewest at least the positions before the variadic one."""
    items = listed(node.get("items_schema"))
    if node.get("variadic_item_index") is None:
        return len(items), len(items)
    low, high = node.get("min_length"), node.get("max_length")
    return max(low if isinstance(low, int) else 0, len(items) - 1), (
        high if isinstance(high, int) else None
    )


def only(default: object, here: tuple[str, ...]) -> Output:
    """A default as the one output: ``None``, a number, a tuple of its length, or something
    that is none of these; a ``nan`` lies in no interval and is unknown."""
    if default is None:
        return Known(none=True)
    if isinstance(default, float) and isnan(default):
        return Unknown("nan", here)
    if (number := decimal(default)) is not None:
        return Known(numbers=Interval(low=number, high=number))
    if isinstance(default, tuple):
        count = len(cast("tuple[object, ...]", default))
        return Known(lengths=(count, count))
    return Known()


def decimal(bound: object) -> Decimal | None:
    """A number of a core schema as a ``Decimal``; ``None`` for what is no number, a ``bool``
    among them."""
    if isinstance(bound, bool) or not isinstance(bound, (int, float, Decimal)):
        return None
    return Decimal(str(bound))


type Endpoint = tuple[Decimal, bool]
"""One end of an interval: the bound and whether it is strict."""


def strongest(candidates: list[tuple[Decimal | None, bool]], *, above: bool) -> Endpoint | None:
    """The bound that constrains most among those declared: the greatest lower bound or the
    least upper bound, strict when a strict candidate is at least as constraining as the
    other; ``None`` when none is declared."""
    found = [(v, strict) for v, strict in candidates if v is not None]
    if not found:
        return None
    best = max(v for v, _ in found) if above else min(v for v, _ in found)
    return best, any(strict for v, strict in found if v == best)


def fields(cls: type[BaseModel]) -> tuple[Declared, ...]:
    """Every field of a class, as declared, in declaration order."""
    return tuple(Declared(cls, name, info) for name, info in cls.model_fields.items())


def declared(cls: type[BaseModel], name: str) -> Declared:
    """One field of a class, as declared."""
    return Declared(cls, name, cls.model_fields[name])


def root_of(cls: type[BaseModel]) -> Declared | None:
    """The ``root`` field of a class that declares one, a scalar's value or a derivation's
    result; ``None`` for a class of fields."""
    info = cls.model_fields.get("root")
    return Declared(cls, "root", info) if info is not None else None


def holds(cls: type[BaseModel]) -> dict[str, Options]:
    """Each single field and the classes it may hold; empty for a field that names no class."""
    return {f.name: f.classes for f in fields(cls) if not f.is_tuple}


def collects(cls: type[BaseModel]) -> dict[str, Options]:
    """Each tuple field and the classes an element may be."""
    return {f.name: f.classes for f in fields(cls) if f.is_tuple}


def produces(cls: type[BaseModel]) -> dict[str, Options]:
    """Each computed field whose return type names classes, and those classes: the words a
    reply says."""
    found = {
        name: model_classes(computed.return_type)
        for name, computed in cls.model_computed_fields.items()
    }
    return {name: classes_ for name, classes_ in found.items() if classes_}


def constant(cls: type[BaseModel]) -> bool:
    """Whether a class is a constant: a scalar whose root has a default, which exists in every
    run by being declared."""
    root = root_of(cls)
    return is_scalar(cls) and root is not None and root.info.default is not PydanticUndefined


def fresh(cls: type[BaseModel]) -> bool:
    """Whether a class is fresh: a scalar whose root has a default factory, constructed anew for
    each holder."""
    root = root_of(cls)
    return is_scalar(cls) and root is not None and root.info.default_factory is not None


def premises(cls: type[BaseModel]) -> dict[str, Options]:
    """Each premise field and the classes it may hold: what the scope must hold before the
    class is asked for."""
    return {f.name: f.classes for f in fields(cls) if f.premise}


def brought(cls: type[BaseModel]) -> frozenset[type[BaseModel]]:
    """The scalars and values a carrying class's single fields hold directly; nothing for a
    class that does not carry."""
    if not carries(cls):
        return frozenset()
    return frozenset(
        c for classes_ in holds(cls).values() for c in classes_ if is_scalar(c) or is_value(c)
    )


def declares(cls: type[BaseModel]) -> Options:
    """The element classes a carrying class holds as tuples: what arrives, what a party says,
    and a composite part each declare elements; nothing for any other class."""
    if not carries(cls):
        return ()
    return tuple(c for classes_ in collects(cls).values() for c in classes_)


def arrives(cls: type[BaseModel]) -> bool:
    """Whether a class is data that arrives: a scalar, a value, or an enumeration."""
    return is_scalar(cls) or is_value(cls)


def built(cls: type[BaseModel]) -> bool:
    """Whether a class is one the engine constructs from premises: a fact, an action, a reply
    or a route. What arrives, what a party says, and what the deployment holds are never
    built."""
    return not (
        arrives(cls)
        or is_request(cls)
        or is_record(cls)
        or is_connection(cls)
        or is_config(cls)
        or is_setting(cls)
    )


def asked[Q: Request, A: Reply[Fact]](route: type[Route[Q, A]]) -> type[Request]:
    """The request class a route declares as ``Route[Q, A]``: the class of its ``request``."""
    (request,) = (c for c in declared(route, "request").classes if is_request(c))
    return request


def replied[Q: Request, A: Reply[Fact]](route: type[Route[Q, A]]) -> Options:
    """The reply classes a route declares as ``Route[Q, A]``: the classes of its ``reply``."""
    return declared(route, "reply").classes


def parametrized(cls: type[BaseModel]) -> Iterator[tuple[type[BaseModel], tuple[object, ...]]]:
    """Each parametrized base in a class's MRO with its arguments made concrete.

    ``Charge(Post[Payments, Payment, Charged])`` yields ``Post`` with those three, then
    ``Action`` with ``(Payments, Charged)``: each base's arguments are bound through the
    parameters of the base before it."""
    binding: dict[object, object] = {}
    for base in cls.__mro__:
        if (
            is_model(base)
            and base is not BaseModel
            and (origin := base.__pydantic_generic_metadata__["origin"]) is not None
        ):
            args = tuple(binding.get(a, a) for a in base.__pydantic_generic_metadata__["args"])
            binding.update(
                zip(origin.__pydantic_generic_metadata__["parameters"], args, strict=True)
            )
            yield origin, args


def said[P: Connection, T: Record](action: type[Action[P, T]]) -> object:
    """The ``T`` an action declares as ``Action[P, T]``: one record class, or a union of them."""
    (record,) = (args[1] for origin, args in parametrized(action) if origin is Action)
    return record


def heard[P: Connection, T: Record](action: type[Action[P, T]]) -> tuple[type[Record], ...]:
    """The record classes an action may hear: the one it declares, or a union's members."""
    return tuple(m for m in union_members(said(action)) if is_record(m))


def hears[P: Connection, T: Record](record: Record, action: Action[P, T]) -> TypeIs[T]:
    """Whether a record is one the action hears."""
    return isinstance(record, heard(type(action)))


def hearers_of(cls: type[BaseModel], classes_: Iterable[type[BaseModel]]) -> Options:
    """Every action that hears a record class."""
    return tuple(a for a in classes_ if is_action(a) and cls in heard(a))


def carriers_of(cls: type[BaseModel], classes_: Iterable[type[BaseModel]]) -> Options:
    """The carrying classes that hold a scalar or value directly."""
    return tuple(c for c in classes_ if cls in brought(c))


def declarers_of(cls: type[BaseModel], classes_: Iterable[type[BaseModel]]) -> Options:
    """The requests and records that hold a class as elements."""
    return tuple(c for c in classes_ if cls in declares(c))


def requests(classes_: Iterable[type[BaseModel]]) -> frozenset[type[BaseModel]]:
    """The request classes of the program's routes."""
    return frozenset(asked(c) for c in classes_ if is_route(c))


def deployed(classes_: Iterable[type[BaseModel]]) -> list[tuple[type[BaseModel], str]]:
    """Each connection class a config holds, with the field that holds it."""
    return [
        (c, f"{deployment.__name__}.{name}")
        for deployment in classes_
        if is_config(deployment)
        for name, classes__ in holds(deployment).items()
        for c in classes__
        if is_connection(c)
    ]


def sourced(cls: type[BaseModel], classes_: tuple[type[BaseModel], ...]) -> bool:
    """Whether a class's instances come from somewhere other than its premises: a route's
    request, a carrier, a declarer, a hearer, a config field, a default root. Such a class is
    never asked for; it arrives, is said, or is declared."""
    return (
        cls in requests(classes_)
        or bool(carriers_of(cls, classes_))
        or bool(declarers_of(cls, classes_))
        or any(is_action(a) and cls in heard(a) for a in classes_)
        or any(c is cls for c, _ in deployed(classes_))
        or constant(cls)
        or fresh(cls)
    )


def fault(
    code: LiteralString, message: LiteralString, loc: tuple[str, ...], **context: str | int
) -> InitErrorDetails:
    """One error of a ``ValidationError`` the engine raises: its type, its message template,
    the context the template reads, and the location, whose first element is the class."""
    return InitErrorDetails(type=PydanticCustomError(code, message, context), loc=loc, input=loc[0])


def names(classes_: Iterable[type[BaseModel]]) -> str:
    """The classes' names joined as a union, for a message."""
    return " | ".join(c.__name__ for c in classes_)


@dataclass(eq=False)
class Context:
    """One scope of the symbolic tree, a discovery structure of the analysis: opened at a root
    or an element, owning the symbols declared or constructed there, seeing its parent's.
    ``many`` when it stands for every element of ``tuple[E, ...]``. Every context of one tree
    shares ``symbols``, each symbol by its reference."""

    site: Site
    parent: Context | None
    many: bool = field(kw_only=True)
    owned: list[Symbol] = field(default_factory=list["Symbol"])
    children: list[Context] = field(default_factory=list["Context"])
    symbols: dict[Ref, Symbol] = field(default_factory=dict[Ref, "Symbol"])

    @property
    def chain(self) -> Iterator[Context]:
        """This context and its ancestors, nearest first."""
        found: Context | None = self
        while found is not None:
            yield found
            found = found.parent

    def visible(self, cls: type[BaseModel]) -> list[Symbol]:
        """Every symbol of a class this context sees: its own and its ancestors'."""
        return [s for c in self.chain for s in c.owned if s.cls is cls]

    def opened(self, site: Site, *, many: bool) -> Context:
        """A child context under this one."""
        child = Context(site, self, many=many, symbols=self.symbols)
        self.children.append(child)
        return child

    def own(self, symbol: Symbol) -> Symbol:
        """A symbol owned here and registered by its reference."""
        self.owned.append(symbol)
        self.symbols[symbol.ref] = symbol
        return symbol


@dataclass(frozen=True)
class Gathered:
    """One collection as the analysis sees it: the symbol that holds it, the tuple field, the
    element symbols, alternatives among them, and the positions the field declares."""

    holder: Symbol
    name: str
    elements: tuple[Symbol, ...]
    positions: int | None

    @property
    def site(self) -> Site:
        """The collection's declared site."""
        return (*self.holder.site, self.name)

    @property
    def contexts(self) -> tuple[Context, ...]:
        """The element contexts, in order, each once."""
        return tuple(dict.fromkeys(e.context for e in self.elements))

    def collected(self, elements: Iterable[Symbol], least: int) -> Collected:
        """The collection as a construction gathers it: by references."""
        holder = self.holder.ref
        if isinstance(holder, ConstructedRef):
            held_by_construction = f"{'.'.join(self.site)} is held by a construction"
            raise TypeError(held_by_construction)
        return Collected(
            holder, self.name, tuple(dict.fromkeys(e.ref for e in elements)), self.positions, least
        )


@dataclass(eq=False)
class Symbol:
    """One occurrence as the analysis sees it: a class at its reference in a context. What
    arrived or was heard holds the symbols of its contents; what was constructed holds its
    construction in its reference and nothing more here."""

    cls: type[BaseModel]
    ref: Ref
    context: Context
    held: dict[str, tuple[Symbol, ...]] = field(default_factory=dict[str, tuple["Symbol", ...]])
    collected: dict[str, Gathered] = field(default_factory=dict[str, Gathered])

    @property
    def site(self) -> Site:
        """The declared site the reference names."""
        return self.ref.site


def declared_symbol(
    ref: InputRef | HeardRef, context: Context, lineage: frozenset[type[BaseModel]]
) -> Symbol:
    """The symbol of a class that arrives or is heard, at the reference's site, with the
    symbols of everything it declares: each single field's classes at the field's site, as
    alternatives, and each tuple field's element classes in element contexts under this one,
    one for ``tuple[E, ...]``, one per position for a fixed tuple, each a reference to a member
    of this one, conditional on the field when what it declares admits ``None``. A class
    already on the lineage is not descended into."""
    cls, site = ref.cls, ref.site
    symbol = context.own(Symbol(cls, ref, context))
    if cls in lineage:
        return symbol
    lineage = lineage | {cls}
    for f in fields(cls):
        if f.is_tuple:
            found: list[Symbol] = []
            for index, classes_ in enumerate(f.item_classes):
                step = f.step(index)
                child = context.opened((*site, f.name, step), many=not f.fixed)
                found.extend(
                    declared_symbol(
                        ref.element(
                            c, f.name, step, conditional=f.admits_none or len(classes_) > 1
                        ),
                        child,
                        lineage,
                    )
                    for c in classes_
                )
            symbol.collected[f.name] = Gathered(symbol, f.name, tuple(found), f.positions)
        else:
            symbol.held[f.name] = tuple(
                declared_symbol(
                    ref.held(c, f.name, conditional=f.admits_none or len(f.classes) > 1),
                    context,
                    lineage,
                )
                for c in f.classes
            )
    return symbol


def single(classes_: Options, context: Context) -> tuple[Symbol, ...]:
    """Every visible symbol of a single field's classes: the candidates, which compete at that
    field and nowhere else; empty while none is visible."""
    return tuple(s for c in classes_ for s in context.visible(c))


def reached_from(symbols: Iterable[Symbol], context: Context) -> list[Gathered]:
    """Every collection reached from symbols through product fields, each once: what a bound
    premise holds, and what that holds in turn; through a constructed premise, what its
    construction may gather and what its premises hold."""
    found: dict[Gathered, None] = {}
    seen: set[Ref] = set()
    todo = [s.ref for s in symbols]
    while todo:
        ref = todo.pop()
        if ref in seen:
            continue
        seen.add(ref)
        if isinstance(ref, ConstructedRef):
            for candidates in ref.construction.collections.values():
                for collected in candidates:
                    holder = context.symbols[collected.holder]
                    found[holder.collected[collected.name]] = None
            todo.extend(r for refs in ref.construction.premises.values() for r in refs)
        else:
            symbol = context.symbols[ref]
            found.update(dict.fromkeys(symbol.collected.values()))
            todo.extend(s.ref for alternatives in symbol.held.values() for s in alternatives)
    return list(found)


def held_by(context: Context) -> list[Gathered]:
    """Every collection the context's own symbols hold."""
    return [g for s in context.owned for g in s.collected.values()]


def chosen(classes_: Options, context: Context) -> list[Symbol]:
    """The symbols of the given classes an element context owns."""
    return [s for s in context.owned if s.cls in classes_]


def compatible(cls: type[BaseModel], name: str, source: Gathered) -> bool:
    """Whether a tuple field may gather a collection of the source's declared shape:
    ``tuple[E, ...]`` gathers any; a fixed tuple gathers a fixed tuple of the same positions;
    a refutable kind gathers any, since refusing the count is what it declares."""
    wanted = declared(cls, name).positions
    return wanted is None or refutable(cls) or wanted == source.positions


def gather(
    cls: type[BaseModel], name: str, classes_: Options, pool: Iterable[Gathered]
) -> tuple[Collected, ...]:
    """Every collection among a pool of a shape the field may gather whose every element
    context owns one of the field's classes, with those elements gathered in order,
    alternatives among them, and the fewest elements the field admits; empty while there is
    none."""
    length = declared(cls, name).length
    least = 0 if isinstance(length, Unknown) else length[0]
    return tuple(
        g.collected([s for element in g.contexts for s in chosen(classes_, element)], least)
        for g in pool
        if compatible(cls, name, g) and all(chosen(classes_, c) for c in g.contexts)
    )


def bound_in(route: type[BaseModel], cls: type[BaseModel], context: Context) -> Construction | None:
    """How a class constructs in a context, read from its fields: each required single field
    bound to the visible symbols of its classes, each tuple field to the collections reached
    through the bound premises or, when they reach none, held by the context; ``None`` while
    a field has nothing."""
    singles: dict[str, tuple[Symbol, ...]] = {}
    for name, classes_ in premises(cls).items():
        found = single(classes_, context)
        if not found:
            return None
        singles[name] = found
    pool = reached_from((s for found in singles.values() for s in found), context) or held_by(
        context
    )
    collections: dict[str, tuple[Collected, ...]] = {}
    for name, classes_ in collects(cls).items():
        gathered = gather(cls, name, classes_, pool)
        if not gathered:
            return None
        collections[name] = gathered
    return Construction(
        route,
        cls,
        context.site,
        {n: tuple(dict.fromkeys(s.ref for s in found)) for n, found in singles.items()},
        collections,
    )


def anchored(construction: Construction, context: Context) -> bool:
    """Whether the context owns one of the construction's candidates or holds a collection it
    may gather, so the class is constructed here; a class with neither is constructed at the
    root."""
    anchors = [
        *(r for refs in construction.premises.values() for r in refs),
        *(c.holder for candidates in construction.collections.values() for c in candidates),
    ]
    if not anchors:
        return context.parent is None
    return any(
        r.construction.scope == context.site
        if isinstance(r, ConstructedRef)
        else context.symbols[r].context is context
        for r in anchors
    )


def contexts(root: Context) -> Iterator[Context]:
    """A context and every context under it, parents first."""
    yield root
    for child in root.children:
        yield from contexts(child)


def symbolized(construction: Construction, context: Context) -> Symbol:
    """The symbol of a construction in its context, under the construction's own reference. An
    action's records enter the context as alternatives at the action's ``heard`` site, with
    everything they declare."""
    symbol = context.own(Symbol(construction.cls, ConstructedRef(construction), context))
    if is_action(construction.cls):
        for record in heard(construction.cls):
            declared_symbol(HeardRef(construction, record, (), record), context, frozenset())
    return symbol


class Waiting(BaseModel):
    """The absent case, as a value: a class a route's passes never constructed, the first field
    that had nothing, and the classes among that field's that the passes could have built."""

    model_config = ConfigDict(frozen=True, strict=True)
    route: type[BaseModel]
    cls: type[BaseModel]
    field: str
    on: Options


class Fault(BaseModel):
    """A fault the passes found, kept until the proof reports it with the rest."""

    model_config = ConfigDict(frozen=True, strict=True)
    code: Literal["missing", "collects", "unplaceable", "route"]
    loc: tuple[str, ...]
    message: str


PLACED = frozenset[type[BaseModel]]()
"""The empty set of classes."""


def reached(
    start: type[BaseModel], classes_: Iterable[type[BaseModel]]
) -> frozenset[type[BaseModel]]:
    """Every class a class leads to: through its fields, the words of its computed fields, the
    carriers of what it holds, the hearer of a record, the declarer of an element, and so on
    from each."""
    classes_ = tuple(classes_)
    found: set[type[BaseModel]] = set()
    todo = [start]
    while todo:
        cls = todo.pop()
        if cls in found:
            continue
        found.add(cls)
        named = (*holds(cls).values(), *collects(cls).values(), *produces(cls).values())
        todo.extend(c for classes__ in named for c in classes__)
        todo.extend(carriers_of(cls, classes_))
        todo.extend(declarers_of(cls, classes_))
        todo.extend(hearers_of(cls, classes_))
    return frozenset(found)


def built_by(
    route: type[BaseModel], classes_: tuple[type[BaseModel], ...]
) -> tuple[type[BaseModel], ...]:
    """The classes a route's run constructs from premises: those its reply leads to that are
    built and come from nowhere else, in definition order. A record is only ever heard, and
    a value only ever arrives; one with no hearer or carrier is what its holder reports as
    missing."""
    reach = reached(route, classes_)
    return tuple(c for c in classes_ if c in reach and built(c) and not sourced(c, classes_))


def rooted[Q: Request, A: Reply[Fact]](
    route: type[Route[Q, A]], classes_: tuple[type[BaseModel], ...]
) -> Context:
    """The root context of a route's symbolic tree: its request, the deployment and every
    constant, with everything the first two declare."""
    root = Context((), None, many=False)
    declared_symbol(InputRef((), REQUEST, asked(route)), root, PLACED)
    for deployment in classes_:
        if is_config(deployment):
            declared_symbol(InputRef((), DEPLOYMENT, deployment), root, PLACED)
    for c in classes_:
        if constant(c):
            root.own(Symbol(c, InputRef((), (c.__name__,), c), root))
    return root


class Symbolic(NamedTuple):
    """What constructing a route symbolically produced."""

    constructions: list[Construction]
    waiting: list[Waiting]
    faulted: list[Fault]


def symbolic[Q: Request, A: Reply[Fact]](
    route: type[Route[Q, A]], classes_: tuple[type[BaseModel], ...]
) -> Symbolic:
    """The proof's construction of one route: passes over the symbolic tree constructing every
    class the route builds wherever it binds, until a pass constructs nothing; then every
    construction bound again against the whole tree, so a candidate that appeared late is
    still seen, and every class never constructed explained."""
    root = rooted(route, classes_)
    asked_for = built_by(route, classes_)
    constructed: list[tuple[Construction, Context]] = []
    done: dict[Context, set[type[BaseModel]]] = {}
    moved = True
    while moved:
        moved = False
        for context in list(contexts(root)):
            for cls in asked_for:
                if cls in done.setdefault(context, set()):
                    continue
                found = bound_in(route, cls, context)
                if found is not None and anchored(found, context):
                    symbolized(found, context)
                    constructed.append((found, context))
                    done[context].add(cls)
                    moved = True
    faulted: list[Fault] = []
    for construction, context in constructed:
        found = bound_in(route, construction.cls, context)
        if found is not None:
            construction.rebound(found)
        if is_route(construction.cls) and context.parent is not None:
            faulted.append(misrouted(construction.cls, context))
    never_built = [c for c in asked_for if not any(c is b.cls for b, _ in constructed)]
    waiting, faults = unexplained(route, never_built, classes_, root)
    for construction, _ in constructed:
        construction.seal()
    return Symbolic([c for c, _ in constructed], waiting, [*faulted, *faults])


def misrouted(cls: type[BaseModel], context: Context) -> Fault:
    """The fault of a route constructed anywhere but the root."""
    return Fault(
        code="route",
        loc=(cls.__name__,),
        message=f"{cls.__name__} would exist once per {'.'.join(context.site)}; a route exists"
        " once per run, so its reply's fact collects elements as tuple[X, ...] instead of"
        " holding one",
    )


def anywhere(root: Context, classes_: Options) -> bool:
    """Whether a symbol of any of the classes exists in the tree."""
    return any(s.cls in classes_ for c in contexts(root) for s in c.owned)


def collected_anywhere(root: Context, cls: type[BaseModel], name: str) -> bool:
    """Whether a collection of a shape the field may gather, whose every element context owns
    one of the field's classes, exists in the tree."""
    classes_ = collects(cls)[name]
    return any(
        compatible(cls, name, g) and all(chosen(classes_, e) for e in g.contexts)
        for c in contexts(root)
        for s in c.owned
        for g in s.collected.values()
    )


def bringers(
    cls: type[BaseModel], classes_: tuple[type[BaseModel], ...]
) -> frozenset[type[BaseModel]]:
    """The built classes that would bring a class that is not built: the actions that hear a
    record, and the bringers of what carries or declares a scalar, a value or an element."""
    found: set[type[BaseModel]] = set()
    todo = [cls]
    seen: set[type[BaseModel]] = set()
    while todo:
        c = todo.pop()
        if c in seen:
            continue
        seen.add(c)
        found.update(hearers_of(c, classes_))
        todo.extend((*carriers_of(c, classes_), *declarers_of(c, classes_)))
    return frozenset(found)


def blockers(
    classes_: Options, never_built: list[type[BaseModel]], every: tuple[type[BaseModel], ...]
) -> Options:
    """The never-built classes a field waits on: those among its own classes, and those that
    would bring one of them."""
    wanted = set(classes_) | {b for c in classes_ for b in bringers(c, every)}
    return tuple(c for c in never_built if c in wanted)


def unexplained(
    route: type[BaseModel],
    never_built: list[type[BaseModel]],
    every: tuple[type[BaseModel], ...],
    root: Context,
) -> tuple[list[Waiting], list[Fault]]:
    """Why each class the passes never constructed was not: a field whose classes occur
    nowhere waits on the never-built classes that would bring them, and with none is
    ``missing``; a tuple field no collection's elements fill waits the same way, and with none
    is ``collects``; a class whose every field has a candidate somewhere but never all from one
    scope is ``unplaceable``, or ``route`` for a route whose reply is under an element.
    ``cycle`` is left to the proof."""
    waiting: list[Waiting] = []
    faults: list[Fault] = []
    for cls in never_built:
        blocked = False
        for name, classes_ in premises(cls).items():
            if anywhere(root, classes_):
                continue
            blocked = True
            if on := blockers(classes_, never_built, every):
                waiting.append(Waiting(route=route, cls=cls, field=name, on=on))
            else:
                faults.append(unfilled_field(cls, name, classes_))
        for name, classes_ in collects(cls).items():
            if collected_anywhere(root, cls, name):
                continue
            blocked = True
            if on := blockers(classes_, never_built, every):
                waiting.append(Waiting(route=route, cls=cls, field=name, on=on))
            else:
                faults.append(uncollected(cls, name, classes_))
        if not blocked:
            faults.append(apart(cls, root))
    return waiting, faults


def unfilled_field(cls: type[BaseModel], name: str, classes_: Options) -> Fault:
    """The fault of a field whose classes occur nowhere in a route and come from nothing."""
    return Fault(
        code="missing",
        loc=(cls.__name__, name),
        message=f"no class fills {cls.__name__}.{name}, which holds {names(classes_)}",
    )


def uncollected(cls: type[BaseModel], name: str, classes_: Options) -> Fault:
    """The fault of a tuple field no collection of its shape fills."""
    declared_as = declared(cls, name).shape
    held = names(dict.fromkeys(classes_))
    return Fault(
        code="collects",
        loc=(cls.__name__, name),
        message=f"{cls.__name__}.{name} collects {held} as {declared_as}, and the"
        " elements of no collection of that shape hold it; a collection is one level down,"
        " under a tuple the request or a record declares",
    )


def apart(cls: type[BaseModel], root: Context) -> Fault:
    """The fault of a class whose fields each have a candidate somewhere, never all from one
    scope: a route whose reply is under an element, else a class over sibling elements."""
    if is_route(cls):
        under = [
            ".".join(s.context.site)
            for c in contexts(root)
            for s in c.owned
            if s.cls in replied(cls) and c.parent is not None
        ]
        return Fault(
            code="route",
            loc=(cls.__name__,),
            message=f"{cls.__name__} would exist once per {', '.join(under)}; a route exists"
            " once per run, so its reply's fact collects elements as tuple[X, ...] instead of"
            " holding one",
        )
    fields = ", ".join(f"{cls.__name__}.{n}" for n in (*premises(cls), *collects(cls)))
    return Fault(
        code="unplaceable",
        loc=(cls.__name__,),
        message=f"{fields} are never visible from one scope; a class over two sibling elements"
        " is an element of its own",
    )


class Proof(BaseModel):
    """Every route constructed symbolically, at startup, with what the proof concluded of the
    constructions: for each two alternatives at one field, whether they are never both
    available; for each construction, whether it can be available at all; each with the ways
    it could be otherwise and the clash that refutes each way; for each action, whether its
    premises establish a use of it wherever they are available, case by case. Its validator
    refuses the program with every fault at once."""

    model_config = ConfigDict(frozen=True, strict=True, arbitrary_types_allowed=True)
    program: str
    classes: tuple[type[BaseModel], ...]
    constructions: tuple[Construction, ...]
    waiting: tuple[Waiting, ...]
    faulted: tuple[Fault, ...]
    exclusions: tuple[Exclusion, ...]
    existences: tuple[Existence, ...]
    justifications: tuple[Justification, ...]

    @property
    def routes(self) -> tuple[type[Route[Request, Reply[Fact]]], ...]:
        """The program's routes."""
        return tuple(c for c in self.classes if is_route(c))

    def constructs(self, route: type[BaseModel]) -> tuple[Construction, ...]:
        """Every construction of a route, in construction order."""
        return tuple(c for c in self.constructions if c.route is route)

    def built[Q: Request, A: Reply[Fact]](
        self, route: type[Route[Q, A]]
    ) -> tuple[type[BaseModel], ...]:
        """The classes a route's run constructs, in definition order."""
        placed = {c.cls for c in self.constructs(route)}
        return tuple(c for c in self.classes if c in placed)

    def sites[Q: Request, A: Reply[Fact]](
        self, route: type[Route[Q, A]], cls: type[BaseModel]
    ) -> tuple[Site, ...]:
        """The sites at which a route constructs a class."""
        return tuple(c.site for c in self.constructs(route) if c.cls is cls)

    @property
    def constants(self) -> tuple[type[BaseModel], ...]:
        """The scalars that exist in every run by being declared."""
        return tuple(c for c in self.classes if constant(c))

    def reached(self, start: type[BaseModel]) -> frozenset[type[BaseModel]]:
        """Every class a class leads to; see ``reached``."""
        return reached(start, self.classes)

    @model_validator(mode="after")
    def sound(self) -> Self:
        """Refuse the program with one ``ValidationError`` naming every fault."""
        details = [
            *(fault(f.code, "{why}", f.loc, why=f.message) for f in unique(self.faulted)),
            *cycles(self),
            *unreached(self),
            *unmodeled(self),
            *boundary(self),
            *deployment(self),
            *certain(self),
            *impossible(self),
            *ambiguous(self),
            *undiscriminated(self),
            *undecided(self),
        ]
        if details:
            raise ValidationError.from_exception_data(self.program, distinct(details))
        return self


def unique(faults: Iterable[Fault]) -> list[Fault]:
    """The faults with each code and location once: a class two routes build is reported
    once."""
    found: dict[tuple[str, tuple[str, ...]], Fault] = {}
    for f in faults:
        found.setdefault((f.code, f.loc), f)
    return list(found.values())


def distinct(details: Iterable[InitErrorDetails]) -> list[InitErrorDetails]:
    """The errors with each type and location once, the first kept: a relation's own
    impossibility and the construction's are one error."""
    found: dict[tuple[str, tuple[object, ...]], InitErrorDetails] = {}
    for d in details:
        code = d["type"]
        name = code.type if isinstance(code, PydanticCustomError) else str(code)
        found.setdefault((name, tuple(d.get("loc", ()))), d)
    return list(found.values())


def cycles(proof: Proof) -> list[InitErrorDetails]:
    """One ``cycle`` error per waiting class that no fault explains: one whose every unfilled
    field names a class that only another unexplained waiting class would bring."""
    explained = {f.loc[0] for f in proof.faulted}
    waiting = list(proof.waiting)
    moved = True
    while moved:
        moved = False
        for w in waiting:
            if w.cls.__name__ not in explained and any(c.__name__ in explained for c in w.on):
                explained.add(w.cls.__name__)
                moved = True
    return [
        fault("cycle", "{cls} holds a class that holds it", (name,), cls=name)
        for name in dict.fromkeys(w.cls.__name__ for w in waiting)
        if name not in explained
    ]


def unreached(proof: Proof) -> list[InitErrorDetails]:
    """One ``unreached`` error per class that no route's reply leads to."""
    reach = PLACED.union(*(proof.reached(r) for r in proof.routes))
    return [
        fault(
            "unreached",
            "{cls} is reached by no route; hold it or delete it",
            (c.__name__,),
            cls=c.__name__,
        )
        for c in proof.classes
        if c not in reach and not is_config(c) and not is_setting(c)
    ]


def kind(annotation: object) -> str:
    """The name of an annotation, for a message."""
    return getattr(annotation, "__name__", str(annotation))


def modeled(cls: type[BaseModel], annotation: object) -> bool:
    """Whether one member of a field's annotation names a kind the class may hold: a model for
    any class; an enumeration on a carrier or a connection; a ``Literal`` or ``None`` on a
    record; a setting on a connection or a config."""
    if is_model(annotation):
        return True
    if is_literal(annotation) or annotation is NoneType:
        return issubclass(cls, Record)
    return is_enum(annotation) and (carries(cls) or issubclass(cls, (Connection, Config)))


def unmodeled(proof: Proof) -> list[InitErrorDetails]:
    """One ``unmodeled`` error per field whose annotation has a member that names no kind: a bare
    primitive anywhere, an enumeration on a fact, ``None`` or a ``Literal`` outside a record."""
    return [
        fault(
            "unmodeled",
            "{cls}.{name} is a bare {primitive}; write a Scalar over it, or a class for the"
            " absent case",
            (c.__name__, name),
            cls=c.__name__,
            name=name,
            primitive=kind(member),
        )
        for c in proof.classes
        if not is_scalar(c)
        for f in fields(c)
        if f.computation is None and f.condition is None
        for name in (f.name,)
        for member in f.members
        if not modeled(c, member)
    ]


def boundary(proof: Proof) -> list[InitErrorDetails]:
    """One ``boundary`` error per field of a request or a value that holds a class that does not
    arrive, and per field of a config or a connection that holds a business value."""
    return [
        *(
            fault(
                "boundary",
                "{cls}.{name} holds {held}; what arrives is scalars, values and tuples of them",
                (c.__name__, name),
                cls=c.__name__,
                name=name,
                held=held.__name__,
            )
            for c in proof.classes
            if issubclass(c, (Request, Value))
            for name, classes_ in (*holds(c).items(), *collects(c).items())
            for held in classes_
            if not arrives(held)
        ),
        *(
            fault(
                "boundary",
                "{cls}.{name} holds {held}; a deployment holds connections and settings",
                (c.__name__, name),
                cls=c.__name__,
                name=name,
                held=held.__name__,
            )
            for c in proof.classes
            if issubclass(c, (Connection, Config))
            for name, classes_ in (*holds(c).items(), *collects(c).items())
            for held in classes_
            if not (is_setting(held) or (is_config(c) and is_connection(held)))
        ),
    ]


def deployment(proof: Proof) -> list[InitErrorDetails]:
    """One ``config`` error when the program declares no deployment or more than one."""
    found = [c.__name__ for c in proof.classes if is_config(c)]
    if len(found) == 1:
        return []
    return [
        fault(
            "config",
            "{program} declares {n} Config classes: {found}; a program declares one",
            (proof.program,),
            program=proof.program,
            n=len(found),
            found=", ".join(found) or "none",
        )
    ]


def hull(intervals: Iterable[Interval]) -> Interval:
    """The interval that covers every interval given: the least low and the greatest high,
    unbounded where any is."""
    found = list(intervals)
    if found and all(i.empty for i in found):
        return found[0]
    found = [i for i in found if not i.empty]
    if not found:
        return Interval()
    lows = [i.low for i in found]
    highs = [i.high for i in found]
    low = None if any(x is None for x in lows) else min(x for x in lows if x is not None)
    high = None if any(x is None for x in highs) else max(x for x in highs if x is not None)
    low_strict = low is not None and all(i.low_strict for i in found if i.low == low)
    high_strict = high is not None and all(i.high_strict for i in found if i.high == high)
    return Interval(low=low, low_strict=low_strict, high=high, high_strict=high_strict)


def interval(cls: type[BaseModel], seen: frozenset[type[BaseModel]] = PLACED) -> Interval | Unknown:
    """What a class's value can be, whatever is given for it: every number its ``root`` field's
    declared type can output, as ``Declared.output`` reads it, a derivation's computation and
    a scalar's bounds among the nodes it passes; unbounded for a class without a root. The
    type's own claim, which a default narrows nowhere, since an occurrence may be given another
    admitted value. A derivation reached again through its own operands is unknown, not a
    bound invented for the recursion."""
    root = root_of(cls)
    if root is None:
        return Interval()
    if cls in seen:
        return Unknown("recursion", (cls.__name__,))
    found = root.outputs(seen)
    return found.numbers if isinstance(found, Known) else found


def interval_at(
    construction: Construction, seen: frozenset[type[BaseModel]] = PLACED
) -> Interval | Unknown:
    """What an occurrence of a construction can be: its class's root under the contract its
    bindings establish, each operand what the references bound to it supply, a collection
    what its element references supply. Narrower than the class's own interval only where
    the bindings say so."""
    cls = construction.cls
    root = root_of(cls)
    if root is None:
        return Interval()
    if cls in seen:
        return Unknown("recursion", (cls.__name__,))
    operands = {
        **{n: gathered(refs, seen | {cls}) for n, refs in construction.premises.items()},
        **{
            n: gathered((r for c in candidates for r in c.elements), seen | {cls})
            for n, candidates in construction.collections.items()
        },
    }
    found = root.outputs(seen, Inputs(operands=operands))
    return found.numbers if isinstance(found, Known) else found


def supplied_by(ref: Ref, seen: frozenset[type[BaseModel]] = PLACED) -> Interval | Unknown:
    """What the occurrence a reference dereferences to can be: a constant at its own site is
    constructed by the engine with its root omitted, so its default's path alone; an
    occurrence the run constructs is what its own bindings make of it; what arrives or is
    heard is anything its class admits."""
    if isinstance(ref, ConstructedRef):
        return interval_at(ref.construction, seen)
    root = root_of(ref.cls)
    if (
        isinstance(ref, InputRef)
        and ref.site == (ref.cls.__name__,)
        and constant(ref.cls)
        and root is not None
    ):
        found = root.outputs(seen, Inputs(omitted=True))
        return found.numbers if isinstance(found, Known) else found
    return interval(ref.cls, seen)


def gathered(refs: Iterable[Ref], seen: frozenset[type[BaseModel]] = PLACED) -> Interval | Unknown:
    """What any of several references can supply: the hull; unknown when any is, and when
    none is bound."""
    found: list[Interval] = []
    for ref in refs:
        own = supplied_by(ref, seen)
        if isinstance(own, Unknown):
            return own
        found.append(own)
    return hull(found) if found else Unknown("unbound", ())


def spanned(
    classes_: Iterable[type[BaseModel]], seen: frozenset[type[BaseModel]] = PLACED
) -> Interval | Unknown:
    """What any of several classes can be: the hull of their intervals; unknown when any is."""
    found: list[Interval] = []
    for c in classes_:
        own = interval(c, seen)
        if isinstance(own, Unknown):
            return own
        found.append(own)
    return hull(found)


def outcomes(left: Interval, right: Interval) -> frozenset[int]:
    """Which orderings two values can have, from what each can be: -1 when the first can be
    under the second, 0 when they can be equal, 1 when the first can be beyond the second."""
    found: set[int] = set()
    if left.empty or right.empty:
        return frozenset()
    if left.low is None or right.high is None or left.low < right.high:
        found.add(-1)
    if right.low is None or left.high is None or right.low < left.high:
        found.add(1)
    lows = [(i.low, i.low_strict) for i in (left, right) if i.low is not None]
    highs = [(i.high, i.high_strict) for i in (left, right) if i.high is not None]
    low = max(lows, default=None)
    high = min(highs, default=None)
    meets = low is None or high is None or low[0] < high[0]
    if meets or (
        low is not None and high is not None and low[0] == high[0] and not (low[1] or high[1])
    ):
        found.add(0)
    return frozenset(found)


def comparisons(cls: type[BaseModel]) -> list[tuple[Comparison, frozenset[int] | Unknown]]:
    """Each comparison a relation makes, naming its two operand fields, and the orderings its
    field admits: the field's ``Literal``, where the compiled schema's every output lies in it;
    unknown where another validator around the field could output otherwise."""
    found: list[tuple[Comparison, frozenset[int] | Unknown]] = []
    for f in fields(cls):
        compared = f.computation
        if not isinstance(compared, Comparison):
            continue
        output = f.output
        if isinstance(output, Unknown):
            found.append((compared, output))
        else:
            found.append((compared, frozenset(int(o) for o in f.admits if isinstance(o, int))))
    return found


def operand(cls: type[BaseModel], name: str, at: Construction | None = None) -> Interval | Unknown:
    """What a relation's operand can be: what the references a construction binds to it
    supply, when a construction is given; else anything the classes the field names admit."""
    if at is None:
        return spanned(declared(cls, name).classes)
    return gathered(at.premises.get(name, ()))


def never(
    cls: type[BaseModel], at: Construction | None = None
) -> Literal["holds", "refuses"] | None:
    """``"holds"`` when some comparison a relation makes admits no ordering its operands'
    intervals allow, ``"refuses"`` when every comparison admits every ordering they allow, and
    ``None`` otherwise, for a comparison over an operand whose interval is unknown, and for
    any class that is not a relation. The class's claim holds of every occurrence, from what
    the operands' types admit; a construction's claim holds of its occurrences, from what its
    bindings supply, a constant's default among them."""
    if not is_relation(cls):
        return None
    decided = True
    for compared, admitted in comparisons(cls):
        lefts, rights = operand(cls, compared.left, at), operand(cls, compared.right, at)
        if (
            isinstance(admitted, Unknown)
            or isinstance(lefts, Unknown)
            or isinstance(rights, Unknown)
        ):
            decided = False
            continue
        possible = outcomes(lefts, rights)
        if not possible & admitted:
            return "holds"
        decided = decided and possible <= admitted
    return "refuses" if decided else None


def certain(proof: Proof) -> list[InitErrorDetails]:
    """One ``never`` error per relation its operands' types make certain or impossible, at the
    class, which holds of every occurrence; else per construction whose bound operands make it
    so, at its site."""
    found: dict[Site, Literal["holds", "refuses"]] = {
        (c.__name__,): what for c in proof.classes if (what := never(c)) is not None
    }
    for c in proof.constructions:
        if (c.cls.__name__,) not in found and (what := never(c.cls, c)) is not None:
            found.setdefault(c.site, what)
    return [
        fault(
            "never",
            "{cls} never {what}, by the intervals of its operands",
            loc,
            cls=loc[-1],
            what=what,
        )
        for loc, what in found.items()
    ]


type Source = Ref | Collected
"""What a construction draws on: a reference, or a collection it may gather."""

type World = frozenset[Source]
"""One way several sources are all available in one scope: every source available with them,
one alternative chosen for each premise and each tuple field of each construction among them,
so no world holds two alternatives of one field."""


@dataclass(frozen=True)
class Clash:
    """Why one world is impossible: the kind of incompatibility, and the sources responsible.
    ``arrived``, two classes under one key of what arrives or is heard, which holds one;
    ``heard``, two records of one action occurrence, which hears one; ``ordering``, two
    relations over the same operand references admitting no ordering in common; ``count``, a
    selection over a collection of a number of positions it admits no count of, or two over one
    collection admitting none in common; ``bounds``, intervals of the references that supply
    numbers and orderings of the relations over them with no solution together."""

    why: Literal["arrived", "heard", "ordering", "count", "bounds"]
    among: tuple[Source, ...]


@dataclass(frozen=True)
class Joint:
    """Whether several sources can be available together in one scope: the ways searched, each
    with the clash that refutes it, or ``None`` for the one way nothing refutes. Impossible
    when every way clashes, which the clashes establish; a way nothing refutes is open, and
    establishes nothing, since bounds that overlap do not say a run exists."""

    refs: tuple[Source, ...]
    ways: tuple[tuple[World, Clash | None], ...]

    @property
    def impossible(self) -> bool:
        """Whether every way clashes: the sources are never all available together."""
        return all(c is not None for _, c in self.ways)

    @property
    def open(self) -> tuple[World, ...]:
        """The way nothing refutes, if the search found one."""
        return tuple(w for w, c in self.ways if c is None)

    @property
    def clashes(self) -> tuple[Clash, ...]:
        """The clashes, one per way refuted."""
        return tuple(c for _, c in self.ways if c is not None)


@dataclass(frozen=True)
class Exclusion:
    """What the proof must establish of two alternatives bound at one field of one construction:
    that they are never both available in the scope the field resolves them from, since a run
    that finds both refuses to choose. Established when their joint is impossible; open
    otherwise, with a way both could be available."""

    construction: Construction
    field: str
    left: Source
    right: Source
    joint: Joint

    @property
    def established(self) -> bool:
        """Whether the two are never both available."""
        return self.joint.impossible


@dataclass(frozen=True)
class Existence:
    """Whether a construction can be available at all: contradicted when every way its
    premises are all available clashes; open otherwise, which does not say a run constructs
    it."""

    construction: Construction
    joint: Joint

    @property
    def contradicted(self) -> bool:
        """Whether the construction's premises are never all available together."""
        return self.joint.impossible


@dataclass(frozen=True)
class Use:
    """One construction that holds an action or what it hears, with what it needs before the
    effect: at each field no alternative of which draws on the action, the alternatives bound
    there. A field some alternative of which draws on the action is filled by the effect, and
    conditions nothing before it."""

    construction: Construction
    field: str
    conditions: tuple[tuple[str, Group], ...]


@dataclass(frozen=True)
class Lack:
    """A condition of a use that a world establishes no alternative of: the use, the field, its
    alternatives, and whether the world excludes every one, so the use does not apply in it, or
    leaves them open, so the action holds nothing that establishes them."""

    use: Use
    field: str
    alternatives: Group
    excluded: bool


@dataclass(frozen=True)
class Coverage:
    """One case of an action's premises all available: the world, each alternative the premises
    leave open decided where what decides it is exhaustive, and the use whose every condition
    the world establishes, or what each use lacks in it."""

    world: World
    use: Use | None
    lacking: tuple[Lack, ...]


@dataclass(frozen=True)
class Justification:
    """What the proof must establish of an action: that wherever its premises are all available
    they establish, before the effect, every condition of some use of it, so the effect is
    performed because the evidence that justifies it is there, whether or not the route
    concludes. The uses are the route's constructions that hold the action or what it hears;
    the coverages are the cases of the premises available, each with the use it establishes or
    with what every use lacks. Established when every case has its use."""

    action: Construction
    uses: tuple[Use, ...]
    coverages: tuple[Coverage, ...]

    @property
    def established(self) -> bool:
        """Whether every case of the premises available establishes a use."""
        return all(c.use is not None for c in self.coverages)


def needs(source: Source) -> list[Group]:
    """What a source needs available with it, one group of alternatives each: nothing, for what
    arrives; its action, for what is heard; for a collection, its holder and the element
    references of each scope it needs, by position for a fixed collection, one element
    standing for any when the field admits no fewer than one, none for a collection that may
    be empty; for a construction, each premise field's references and each tuple field's
    collections."""
    match source:
        case InputRef():
            return []
        case HeardRef():
            return [(ConstructedRef(source.action),)]
        case Collected():
            return [(source.holder,), *(g for step in source.steps if (g := source.placed(step)))]
        case ConstructedRef(construction):
            return [*construction.premises.values(), *construction.collections.values()]


type Ways = tuple[tuple[World, Clash | None], ...]
"""The worlds a search visited, each with the clash that refutes it, or ``None`` for the one way
nothing refutes."""


def searched(todo: list[Group], world: World = frozenset(), *, every: bool = False) -> Ways:
    """The worlds in which every group of alternatives has one available, from a world already
    held: a depth-first search over the groups, one alternative per group, the group with the
    fewest alternatives first, so what every way shares is placed before any way branches and
    a clash among it ends the search at once; a world that clashes is not extended, since every
    extension clashes too, and the first world completed without a clash ends the search, since
    one open way is all an open obligation reports, unless ``every`` way is asked for, as the
    cases of an action's premises are. A world is complete only when each collection that may
    be empty gathers the element whose scope the world populates: an occurrence in an element's
    scope is that element present, and a collection over it is not available without it. Each
    way searched is kept with its clash."""
    ways: list[tuple[World, Clash | None]] = []

    def search(todo: list[Group], world: World) -> bool:
        found = clash(world)
        if found is not None:
            ways.append((world, found))
            return False
        if not todo:
            missing = [
                c.placed("[]")
                for c in ordered(world)
                if isinstance(c, Collected) and populated(c, world) and not gathered_in(c, world)
            ]
            if missing:
                return search(missing, world)
            ways.append((world, None))
            return True
        index = min(range(len(todo)), key=lambda i: len(todo[i]))
        group, rest = todo[index], [*todo[:index], *todo[index + 1 :]]
        completed = False
        for source in group:
            if source in world:
                completed = search(rest, world) or completed
            else:
                completed = search([*needs(source), *rest], world | {source}) or completed
            if completed and not every:
                return True
        return completed

    search(todo, world)
    return tuple(ways)


def joint(sources: Iterable[Source]) -> Joint:
    """Whether several sources can be available together: ``searched`` from the empty world,
    each source its own group."""
    sources = tuple(sources)
    return Joint(sources, searched([(source,) for source in sources]))


def scope_of(source: Source) -> Site:
    """The scope template a source is available in: a reference's, or a collection's holder's."""
    return source.holder.scope if isinstance(source, Collected) else source.scope


def populated(collected: Collected, world: World) -> bool:
    """Whether a world holds an occurrence in the element scope of a variable collection, which
    is that element present."""
    element = (*collected.site, "[]")
    return collected.positions is None and any(
        scope_of(s)[: len(element)] == element for s in world
    )


def gathered_in(collected: Collected, world: World) -> bool:
    """Whether a world holds an element of a variable collection."""
    return any(r in world for r in collected.placed("[]"))


def label(source: Source) -> tuple[Site, str, str]:
    """A source's place in one order: its site, its kind and its class or field."""
    name = source.name if isinstance(source, Collected) else source.cls.__name__
    return (source.site, type(source).__name__, name)


def ordered(world: World) -> list[Source]:
    """A world's sources in one order: by site, kind and name."""
    return sorted(world, key=label)


def clash(world: World) -> Clash | None:
    """The first incompatibility within a world, or ``None``: two classes under one key of what
    arrives or is heard, a union's alternatives, of which the key holds one; two records of one
    action occurrence; two relations contradicting over the same operands; a selection the number of
    positions of its collection refutes, or two selections over one collection with no count in
    common; or the bounds of what supplies each number and the orderings of the relations over
    them with no solution together. An unknown interval bounds nothing, and so refutes
    nothing."""
    sources = ordered(world)
    found = held_twice(sources)
    if found is not None:
        return found
    made = [r for r in sources if isinstance(r, ConstructedRef)]
    relations = [r for r in made if is_relation(r.cls)]
    for x, y in combinations(relations, 2):
        if contradicts(x.construction, y.construction, world):
            return Clash("ordering", (x, y))
    gathering = [r for r in made if r.construction.collections]
    for s in gathering:
        if miscounted(s.construction, world):
            return Clash("count", (s,))
    for x, y in combinations(gathering, 2):
        if exclusive(x.construction, y.construction, world):
            return Clash("count", (x, y))
    bounds = {r: found for r in sources if not isinstance(r, Collected) and (found := edges(r))}
    constraints = [
        *(e for found in bounds.values() for e in found),
        *(e for r in relations for e in constrained(r.construction, world)),
    ]
    if not feasible(constraints):
        return Clash("bounds", (*relations, *bounds))
    return None


def held_twice(sources: Iterable[Source]) -> Clash | None:
    """The first two sources of a world that one holder cannot hold together, or ``None``: two
    records of one action occurrence, or two classes under one key of what arrives or is
    heard, which a scope holds one instance under."""
    arrived_ = [r for r in sources if isinstance(r, InputRef | HeardRef)]
    for x, y in combinations(arrived_, 2):
        if (
            isinstance(x, HeardRef)
            and isinstance(y, HeardRef)
            and x.action is y.action
            and x.record is not y.record
        ):
            return Clash("heard", (x, y))
        if x.key == y.key and x.cls is not y.cls:
            return Clash("arrived", (x, y))
    return None


def edges(ref: Ref) -> list[Edge]:
    """What a reference supplies as difference constraints against zero: ``x >= low`` is
    ``0 - x <= -low``, ``x <= high`` is ``x - 0 <= high``; none for an unknown interval, which
    constrains nothing and so proves nothing, and none for what supplies no number."""
    found = supplied_by(ref)
    constraints: list[Edge] = []
    if isinstance(found, Unknown):
        return constraints
    if found.low is not None:
        constraints.append((ref, ZERO, (-found.low, -1 if found.low_strict else 0)))
    if found.high is not None:
        constraints.append((ZERO, ref, (found.high, -1 if found.high_strict else 0)))
    return constraints


def picked[S: Source](sources: Iterable[S], world: World) -> S | None:
    """The one alternative among a group a world holds; ``None`` for none or for two, which
    the exclusion at that field reports."""
    found = [s for s in sources if s in world]
    return found[0] if len(found) == 1 else None


def operands_in(
    construction: Construction, compared: Comparison, world: World
) -> tuple[Ref, Ref] | None:
    """The two references a comparison is over in a world, or ``None`` while either is not
    one."""
    left = picked(construction.premises.get(compared.left, ()), world)
    right = picked(construction.premises.get(compared.right, ()), world)
    return None if left is None or right is None else (left, right)


UNDER = frozenset({-1})
"""The one ordering ``Under`` admits: a strict constraint."""

BEYOND = frozenset({1})
"""The one ordering ``Beyond`` admits: a strict constraint."""


def constrained(construction: Construction, world: World) -> list[Edge]:
    """A relation's comparisons as difference constraints between the references of its
    operands in a world, for the admitted sets that are one: under is ``value - bound < 0``,
    at most ``<= 0``, equal both ways, at least ``bound - value <= 0``, beyond ``< 0``; differs
    is none, and so is a comparison whose admitted orderings are unknown."""
    found: list[Edge] = []
    for compared, admitted in comparisons(construction.cls):
        operands = operands_in(construction, compared, world)
        if isinstance(admitted, Unknown) or operands is None:
            continue
        left, right = operands
        if admitted <= {-1, 0}:
            found.append((right, left, (Decimal(0), -1 if admitted == UNDER else 0)))
        if admitted <= {0, 1}:
            found.append((left, right, (Decimal(0), -1 if admitted == BEYOND else 0)))
    return found


def contradicts(a: Construction, b: Construction, world: World) -> bool:
    """Whether two relations make a comparison over the same two operand references in a world
    whose admitted orderings are disjoint, the second's negated when its operands are the
    first's reversed: the same references supply the same values, so one ordering holds of
    both."""
    for compared, admitted in comparisons(a.cls):
        operands = operands_in(a, compared, world)
        if isinstance(admitted, Unknown) or operands is None:
            continue
        for compared_, admitted_ in comparisons(b.cls):
            operands_ = operands_in(b, compared_, world)
            if isinstance(admitted_, Unknown) or operands_ is None:
                continue
            if operands == operands_ and not admitted & admitted_:
                return True
            if operands == operands_[::-1] and not admitted & {-o for o in admitted_}:
                return True
    return False


def exclusive(a: Construction, b: Construction, world: World) -> bool:
    """Whether two constructions gather one collection in a world, the same holder and
    elements, as tuple fields admitting no count in common; not when either count is
    unknown."""
    for name, candidates in a.collections.items():
        collected = picked(candidates, world)
        for name_, candidates_ in b.collections.items():
            first, second = declared(a.cls, name).length, declared(b.cls, name_).length
            if (
                collected is None
                or collected != picked(candidates_, world)
                or isinstance(first, Unknown)
                or isinstance(second, Unknown)
            ):
                continue
            (low, high), (low_, high_) = first, second
            if (high is not None and low_ > high) or (high_ is not None and low > high_):
                return True
    return False


def miscounted(construction: Construction, world: World) -> bool:
    """Whether a construction gathers, in a world, a fixed collection whose number of positions
    its tuple field admits no count of: a selection of one over a pair."""
    for name, candidates in construction.collections.items():
        collected = picked(candidates, world)
        length = declared(construction.cls, name).length
        if collected is None or collected.positions is None or isinstance(length, Unknown):
            continue
        low, high = length
        if collected.positions < low or (high is not None and collected.positions > high):
            return True
    return False


def feasible(constraints: Iterable[Edge]) -> bool:
    """Whether a system of difference constraints has a solution: Bellman-Ford over its
    variables from a common origin finds no cycle whose weights sum below zero, where a strict
    constraint on a zero-weight cycle counts below zero."""
    constraints = list(constraints)
    nodes = {n for y, x, _ in constraints for n in (y, x)}
    distance: dict[object, Weight] = dict.fromkeys(nodes, (Decimal(0), 0))
    for _ in range(len(nodes) + 1):
        changed = False
        for y, x, (c, s) in constraints:
            candidate = (distance[y][0] + c, distance[y][1] + s)
            if candidate < distance[x]:
                distance[x] = candidate
                changed = True
        if not changed:
            return True
    return False


def exclusions(constructions: Iterable[Construction]) -> tuple[Exclusion, ...]:
    """The alternatives bound at each field of each construction, pairwise, each with whether
    they are ever both available where the field resolves them: a premise's references, from
    the construction's scope; a tuple field's collections, from the construction's scope; a
    collection's element references, those placed in one element's scope from that scope."""
    found: list[Exclusion] = []
    for c in constructions:
        groups: list[tuple[str, Group]] = [*c.premises.items(), *c.collections.items()]
        for name, candidates in c.collections.items():
            for collected in candidates:
                by_scope: dict[Site, list[Source]] = {}
                for r in collected.elements:
                    by_scope.setdefault(r.scope, []).append(r)
                groups.extend((name, tuple(refs)) for refs in by_scope.values())
        found.extend(
            Exclusion(c, name, left, right, joint((left, right)))
            for name, sources in groups
            for left, right in combinations(sources, 2)
        )
    return tuple(found)


def existences(constructions: Iterable[Construction]) -> tuple[Existence, ...]:
    """Whether each construction can be available at all."""
    return tuple(Existence(c, joint((ConstructedRef(c),))) for c in constructions)


def inherited(construction: Construction) -> bool:
    """Whether a construction's impossibility is one of its premises' own: some group of
    alternatives it needs has none possible alone, and that premise is where it is reported."""
    return any(
        all(joint((s,)).impossible for s in group) for group in needs(ConstructedRef(construction))
    )


def closure(source: Source) -> list[Source]:
    """Every source some way a source is available draws on: all reached through what it needs,
    by any alternative, in one order."""
    seen: set[Source] = set()
    todo: list[Source] = [source]
    while todo:
        s = todo.pop()
        if s in seen:
            continue
        seen.add(s)
        todo.extend(alternative for group in needs(s) for alternative in group)
    return ordered(frozenset(seen))


def produced(source: Source, action: Construction) -> bool:
    """Whether a source is what an action's effect produces: the action, a record it hears, or
    a collection held by or of what it hears."""
    match source:
        case InputRef():
            return False
        case ConstructedRef(construction):
            return construction is action
        case HeardRef():
            return source.action is action
        case Collected():
            return produced(source.holder, action) or any(
                produced(e, action) for e in source.elements
            )


def draws_on(source: Source, action: Construction) -> bool:
    """Whether some way a source is available draws on what an action produces: a collection's
    elements among them, which it holds whether or not it needs one."""
    found = closure(source)
    if isinstance(source, Collected):
        found.extend(s for e in source.elements for s in closure(e))
    return any(produced(s, action) for s in found)


def uses_of(action: Construction, constructions: Iterable[Construction]) -> tuple[Use, ...]:
    """The uses of an action among its route's constructions: each that binds at some field
    what the action produces, with that field, and with its conditions, the fields no
    alternative of which draws on the action."""
    found: list[Use] = []
    for c in constructions:
        groups: list[tuple[str, Group]] = [*c.premises.items(), *c.collections.items()]
        binding = [name for name, group in groups if any(produced(s, action) for s in group)]
        if c is action or not binding:
            continue
        conditions = tuple(
            (name, group) for name, group in groups if not any(draws_on(s, action) for s in group)
        )
        found.append(Use(c, binding[0], conditions))
    return tuple(found)


def populated_at(scope: Site, world: World, action: Construction) -> bool:
    """Whether a scope template is populated wherever an action's premises are all available:
    every element scope on the way to it is the action's own or an ancestor of it, or holds an
    occurrence the world has; a fixed position is populated with its holder."""
    for index, part in enumerate(scope):
        if part != "[]":
            continue
        prefix = scope[: index + 1]
        if action.scope[: len(prefix)] != prefix and not any(
            scope_of(s)[: len(prefix)] == prefix for s in world
        ):
            return False
    return True


def hears_in(world: World, action: Construction, record: type[BaseModel]) -> bool:
    """Whether a world has an action hearing a record: the record or a member of it."""
    return any(isinstance(s, HeardRef) and s.action is action and s.record is record for s in world)


def records_of(construction: Construction) -> tuple[type[Record], ...]:
    """The records an action construction's class hears; none for another class."""
    return heard(construction.cls) if is_action(construction.cls) else ()


def establishes(
    world: World,
    source: Source,
    action: Construction,
    seen: frozenset[Construction] = frozenset(),
) -> bool:
    """Whether a world with an action's premises available has a source available with them:
    it is in the world; it arrives conditional on nothing, in a scope the world populates; it
    is a record an action in the world heard, or the one record an action established here
    hears, or a member of either conditional on nothing; it is constructed from premises each
    established here and is not refutable, since a refutable kind's condition is established by
    nothing but the kind itself; or it is a collection whose holder and needed elements are.
    ``seen`` is the constructions on the way, so a cycle establishes nothing."""
    if source in world:
        return True
    match source:
        case InputRef():
            return not source.because and populated_at(source.scope, world, action)
        case HeardRef():
            heard_ = hears_in(world, source.action, source.record) or (
                source.action is not action
                and records_of(source.action) == (source.record,)
                and establishes(world, ConstructedRef(source.action), action, seen)
            )
            return heard_ and not source.because and populated_at(source.scope, world, action)
        case ConstructedRef(construction):
            return (
                construction is not action
                and not refutable(construction.cls)
                and construction not in seen
                and populated_at(construction.scope, world, action)
                and all(
                    any(establishes(world, a, action, seen | {construction}) for a in group)
                    for group in needs(source)
                )
            )
        case Collected():
            return all(
                any(establishes(world, a, action, seen) for a in group) for group in needs(source)
            )


def extended(world: World, sources: Iterable[Source]) -> tuple[World, ...]:
    """The worlds that extend one with each of several sources and what it needs, by every way
    nothing refutes."""
    return tuple(w for s in sources for w, c in searched([(s,)], world, every=True) if c is None)


def exhaustive(family: Iterable[Construction]) -> bool:
    """Whether several relations over the same operands together admit every ordering, each
    making one comparison of known orderings."""
    admitted: set[int] = set()
    for c in family:
        found = comparisons(c.cls)
        if len(found) != 1 or isinstance(found[0][1], Unknown):
            return False
        admitted |= found[0][1]
    return admitted == {-1, 0, 1}


def decided(
    world: World, source: Source, action: Construction, constructions: tuple[Construction, ...]
) -> tuple[World, ...] | None:
    """The worlds that decide an alternative a world leaves open, where what decides it comes
    after the action's premises and is exhaustive, or ``None``: for a record, each record its
    action hears, when that action is established here and the world holds none of its
    records; for a relation, each relation of the route over the same operand references, when
    together they admit every ordering, the operands are established here and the world holds
    none. Each world is the one given with the alternative and what it needs, by every way
    nothing refutes; a way that clashes is no case."""
    match source:
        case HeardRef(action=hearer):
            records = records_of(hearer)
            if (
                hearer is action
                or any(hears_in(world, hearer, r) for r in records)
                or not establishes(world, ConstructedRef(hearer), action)
            ):
                return None
            return extended(world, [HeardRef(hearer, r, (), r) for r in records])
        case ConstructedRef(relation) if is_relation(relation.cls):
            family = [
                c
                for c in constructions
                if is_relation(c.cls) and dict(c.premises) == dict(relation.premises)
            ]
            if (
                not exhaustive(family)
                or any(ConstructedRef(c) in world for c in family)
                or not all(
                    any(establishes(world, a, action) for a in group)
                    for group in relation.premises.values()
                )
            ):
                return None
            return extended(world, [ConstructedRef(c) for c in family])
        case _:
            return None


def covered(
    world: World,
    uses: tuple[Use, ...],
    action: Construction,
    constructions: tuple[Construction, ...],
) -> list[Coverage]:
    """The coverage of one world with an action's premises available: the first use whose every
    condition the world establishes; else, at the first condition some use lacks that the world
    can decide, the coverage of each world deciding it; else what each use lacks, excluded
    where the world refutes every alternative."""
    for use in uses:
        if all(any(establishes(world, a, action) for a in g) for _, g in use.conditions):
            return [Coverage(world, use, ())]
    lacking: list[Lack] = []
    for use in uses:
        for name, group in use.conditions:
            if any(establishes(world, a, action) for a in group):
                continue
            for a in group:
                split = decided(world, a, action, constructions)
                if split is not None:
                    return [c for w in split for c in covered(w, uses, action, constructions)]
            excluded = all(c is not None for a in group for _, c in searched([(a,)], world))
            lacking.append(Lack(use, name, group, excluded))
            break
    return [Coverage(world, None, tuple(lacking))]


def justification(action: Construction, constructions: tuple[Construction, ...]) -> Justification:
    """The justification of an action among its route's constructions: its uses, and the
    coverage of each world with the action's premises available, by every way nothing
    refutes."""
    uses = uses_of(action, constructions)
    worlds = [w for w, c in searched([(ConstructedRef(action),)], every=True) if c is None]
    return Justification(
        action, uses, tuple(c for w in worlds for c in covered(w, uses, action, constructions))
    )


def justifications(constructions: Iterable[Construction]) -> tuple[Justification, ...]:
    """The justification of each action construction, route by route, among the route's own
    constructions."""
    constructions = tuple(constructions)
    found: list[Justification] = []
    for route in dict.fromkeys(c.route for c in constructions):
        own = tuple(c for c in constructions if c.route is route)
        found.extend(justification(c, own) for c in own if is_action(c.cls))
    return tuple(found)


def where(scope: Site) -> str:
    """A scope template for a message: its path, or the root."""
    return ".".join(scope) or "the root"


def at(source: Source) -> str:
    """A source for a message: a reference's class at its site; a collection's element
    classes, the holder's field, and its site."""
    if isinstance(source, Collected):
        held = names(dict.fromkeys(r.cls for r in source.elements))
        holder = f"{source.holder.cls.__name__}.{source.name}"
        return f"{held} in {holder} at {'.'.join(source.site)}"
    return f"{source.cls.__name__} at {'.'.join(source.site)}"


def holding(world: World) -> list[str]:
    """The conditions a world takes as holding, for a message: each refutable construction and
    each record heard in it, in one order."""
    return [
        at(r)
        for r in ordered(world)
        if (isinstance(r, ConstructedRef) and refutable(r.cls))
        or (isinstance(r, HeardRef) and not r.member)
    ]


def assumed(world: World) -> str:
    """Why an open way excludes neither alternative, for a message: the conditions it takes
    as holding, or that nothing available with them does."""
    found = holding(world)
    if not found:
        return "nothing available with them excludes either"
    return f"with {', '.join(found)} holding, nothing excludes either"


def either(group: Group) -> str:
    """The alternatives of a group, for a message."""
    return " or ".join(map(at, group))


def because_of(clash: Clash) -> str:
    """A clash for a message, in the developer's names."""
    match clash:
        case Clash("arrived", (x, y)):
            return f"{at(x)} and {at(y)} are held under one key, which holds one of them"
        case Clash("heard", (HeardRef() as x, HeardRef() as y)):
            heard_by = f"{x.action.cls.__name__} at {'.'.join(x.action.site)}"
            return f"{heard_by} hears one record, {x.record.__name__} or {y.record.__name__}"
        case Clash("ordering", (x, y)):
            return f"{at(x)} and {at(y)} admit no ordering in common over the same operands"
        case Clash("count", (ConstructedRef(construction) as x,)):
            positions = ", ".join(
                str(c.positions)
                for candidates in construction.collections.values()
                for c in candidates
                if c.positions
            )
            return f"{at(x)} admits no count of {positions} elements"
        case Clash("count", (x, y)):
            return f"{at(x)} and {at(y)} admit no count in common over one collection"
        case _:
            return f"the bounds and orderings of {', '.join(map(at, clash.among))} have no solution"


def impossible(proof: Proof) -> list[InitErrorDetails]:
    """One ``never`` error per construction whose premises are each possible alone and never
    all available together, at its site, where its class's own claim is open."""
    return [
        fault(
            "never",
            "{cls} at {path} never constructs: {why}",
            e.construction.site,
            cls=e.construction.cls.__name__,
            path=".".join(e.construction.site),
            why=because_of(e.joint.clashes[0]),
        )
        for e in proof.existences
        if e.contradicted and never(e.construction.cls) is None and not inherited(e.construction)
    ]


def ambiguous(proof: Proof) -> list[InitErrorDetails]:
    """One ``ambiguous`` error per two alternatives at one field the proof cannot show are never
    both available: at the construction's scope, with what the open way holds, which a run may
    hold too."""
    return [
        fault(
            "ambiguous",
            "{cls}.{name} at {scope} may hold both {left} and {right}; {why}",
            (e.construction.cls.__name__, e.field),
            cls=e.construction.cls.__name__,
            name=e.field,
            scope=where(e.construction.scope),
            left=at(e.left),
            right=at(e.right),
            why=assumed(e.joint.open[0]),
        )
        for e in proof.exclusions
        if not e.established
    ]


def undecided(proof: Proof) -> list[InitErrorDetails]:
    """One ``undecided`` error per action whose justification is open, at the action: nothing
    of the route holds it or what it hears; or, in the first case of its premises available
    that establishes no use, what the first use the case leaves open needs, which the action
    holds nothing that establishes; or, where the case excludes every use, what the case holds
    and the use it excludes."""
    found: list[InitErrorDetails] = []
    for j in proof.justifications:
        if j.established:
            continue
        action, scope = j.action.cls.__name__, where(j.action.scope)
        if not j.uses:
            found.append(
                fault(
                    "undecided",
                    "{action} at {scope} is performed, and nothing of {route} holds it or what"
                    " it hears",
                    (action,),
                    action=action,
                    scope=scope,
                    route=j.action.route.__name__,
                )
            )
            continue
        coverage = next(c for c in j.coverages if c.use is None)
        left_open = [lack for lack in coverage.lacking if not lack.excluded]
        if left_open:
            lack = left_open[0]
            found.append(
                fault(
                    "undecided",
                    "{action} at {scope} is performed before {needed}, which {use} needs, is"
                    " established; {action} holds nothing that establishes it",
                    (action,),
                    action=action,
                    scope=scope,
                    needed=either(lack.alternatives),
                    use=at(ConstructedRef(lack.use.construction)),
                )
            )
            continue
        lack = coverage.lacking[0]
        held = holding(coverage.world)
        found.append(
            fault(
                "undecided",
                "{action} at {scope} is performed where {held} {hold}, excluding {needed}, which"
                " {use} needs; {action} holds nothing that decides it",
                (action,),
                action=action,
                scope=scope,
                held=", ".join(held),
                hold="holds" if len(held) == 1 else "hold",
                needed=either(lack.alternatives),
                use=at(ConstructedRef(lack.use.construction)),
            )
        )
    return found


def keys(cls: type[BaseModel], *, required: bool) -> frozenset[str]:
    """The keys a record validates by: with ``required``, the one key each required field
    must carry, leaving out a field that accepts several; else every key any field accepts."""
    if required:
        return frozenset(k for f in fields(cls) if (k := f.required_key) is not None)
    return frozenset(k for f in fields(cls) for k in f.aliases)


def told_apart(a: type[BaseModel], b: type[BaseModel]) -> bool:
    """Whether two records cannot both construct from one payload: a field both declare as a
    ``Literal`` with no value in common, or a key one requires that the other does not
    declare."""
    shared = {f.name for f in fields(a)} & {f.name for f in fields(b)}
    for name in shared:
        first, second = declared(a, name), declared(b, name)
        if first.admits and second.admits and not (first.admits & second.admits):
            return True
    return bool(keys(a, required=True) - keys(b, required=False)) or bool(
        keys(b, required=True) - keys(a, required=False)
    )


def undiscriminated(proof: Proof) -> list[InitErrorDetails]:
    """One ``undiscriminated`` error per action hearing two records no field tells apart."""
    return [
        fault(
            "undiscriminated",
            "{cls} hears {a} | {b}, and no field tells them apart; declare a Literal on each",
            (c.__name__,),
            cls=c.__name__,
            a=a.__name__,
            b=b.__name__,
        )
        for c in proof.classes
        if is_action(c)
        for a, b in combinations(heard(c), 2)
        if not told_apart(a, b)
    ]


def proven(program: ModuleType) -> Proof:
    """The proof of a program: every route constructed symbolically from its own request, the
    deployment and the constants, as a ``Proof``, whose validator refuses the program with
    every fault at once."""
    classes_ = models(program)
    found = [symbolic(r, classes_) for r in classes_ if is_route(r)]
    constructions = tuple(c for s in found for c in s.constructions)
    return Proof(
        program=program.__name__,
        classes=classes_,
        constructions=constructions,
        waiting=tuple(w for s in found for w in s.waiting),
        faulted=tuple(f for s in found for f in s.faulted),
        exclusions=exclusions(constructions),
        existences=existences(constructions),
        justifications=justifications(constructions),
    )


def connections(deployment: Config) -> tuple[Connection, ...]:
    """Every connection a config holds, in field order."""
    return tuple(
        value
        for value in (getattr(deployment, f.name) for f in fields(type(deployment)))
        if isinstance(value, Connection)
    )


@asynccontextmanager
async def opened(deployment: Config) -> AsyncGenerator[None]:
    """Enter every connection's ``open`` once before the body and exit every one once after it,
    last entered first, whatever the body raised, including its cancellation. Each is an
    asynchronous context on one ``AsyncExitStack``, which exits every context it entered: an
    open that raises or is cancelled, partway through its own acquisitions or not, releases what
    it acquired itself, and the stack exits what was entered before it; an exit that raises does
    not keep the others open, and its exception propagates with the body's as its context."""
    async with AsyncExitStack() as entered:
        for connection in connections(deployment):
            await entered.enter_async_context(connection.open())
        yield


type Provenance = dict[str, tuple[Site, ...]]
"""Which occurrences supplied each field of a construction: the concrete path of each."""

type Given = dict[str, BaseModel | tuple[BaseModel, ...]]
"""What a scope supplies for a construction's fields, as Pydantic takes it."""


class Constructed(NamedTuple):
    """A construction's instance in a scope, with the witness of what supplied it: the instance
    holds the very instances the witness does, which the construction established."""

    instance: BaseModel
    supplied: Bound

    @property
    def provenance(self) -> Provenance:
        """The concrete paths of what supplied each field."""
        return self.supplied.provenance


class Refuted(NamedTuple):
    """A refutable kind whose declared condition the evidence rejected in a scope: Pydantic's
    refusal, every error of which is ``REFUTED``, and the witness of the operands it was
    constructed from."""

    refusal: ValidationError
    supplied: Bound

    @property
    def provenance(self) -> Provenance:
        """The concrete paths of the operands."""
        return self.supplied.provenance


type Made = Constructed | Refuted
"""What a scope holds for a construction once a pass asked for it."""


@dataclass(eq=False)
class Scope:
    """One scope of a run: opened at a root or an element, holding what arrived or was heard
    there by its key, the collections those hold, and what each construction placed here made,
    seeing its parent's. The same shape as the analysis's ``Context``, over instances. ``site``
    is the declared site template, ``"[]"`` for an element of a variable tuple; ``path`` is
    this invocation's concrete path, ``"[1]"`` for the second element, and every occurrence's
    concrete path is the path of the scope that owns it with its site under that scope's."""

    site: Site
    path: Site
    parent: Scope | None
    arrived: dict[Key, BaseModel] = field(default_factory=dict[Key, BaseModel])
    collections: dict[Key, tuple[Scope, ...]] = field(
        default_factory=dict[Key, tuple["Scope", ...]]
    )
    children: list[Scope] = field(default_factory=list["Scope"])
    made: dict[Construction, Made] = field(default_factory=dict[Construction, Made])

    @property
    def chain(self) -> Iterator[Scope]:
        """This scope and its ancestors, nearest first."""
        found: Scope | None = self
        while found is not None:
            yield found
            found = found.parent

    def at(self, site: Site) -> Site:
        """The concrete path of a declared site under this scope's."""
        return (*self.path, *site[len(self.site) :])

    def within(self, site: Site) -> Scope:
        """The scope of this chain at a declared scope template: where a reference's occurrence
        is owned. A template this chain does not pass through is a reference that does not
        apply here, which the proof excludes."""
        found = [s for s in self.chain if s.site == site]
        if not found:
            unseen = f"{'.'.join(self.path)} sees no scope at {'.'.join(site)}"
            raise LookupError(unseen)
        return found[0]

    def holding(self, key: Key) -> Scope | None:
        """The scope of this chain that holds an arrived instance under a key, or ``None``."""
        return next((s for s in self.chain if key in s.arrived), None)

    def collection(self, key: Key) -> tuple[Scope, ...] | None:
        """The element scopes of a collection this scope sees, or ``None``."""
        return next((s.collections[key] for s in self.chain if key in s.collections), None)


def arrived(instance: BaseModel, origin: Construction | None, member: Site, scope: Scope) -> None:
    """Enter what arrived or was heard into a scope under its key, with everything it holds:
    each model a single field holds under the member's key, and each tuple of models as a
    collection, one child scope per element at the element's declared site, holding the
    element and what it holds in turn."""
    declared_ = member if origin is None else (*origin.site, HEARD, *member)
    scope.arrived[origin, member] = instance
    for f in fields(type(instance)):
        value: object = getattr(instance, f.name)
        if isinstance(value, BaseModel):
            arrived(value, origin, (*member, f.name), scope)
        elif is_elements(value):
            opened_: list[Scope] = []
            for index, element in enumerate(value):
                if isinstance(element, BaseModel):
                    step = f.step(index)
                    child = Scope(
                        (*declared_, f.name, step),
                        (*scope.at(declared_), f.name, f"[{index}]"),
                        scope,
                    )
                    scope.children.append(child)
                    arrived(element, origin, (*member, f.name, step), child)
                    opened_.append(child)
            scope.collections[origin, (*member, f.name)] = tuple(opened_)


def scopes(root: Scope) -> Iterator[Scope]:
    """A scope and every scope under it, parents first."""
    yield root
    for child in root.children:
        yield from scopes(child)


class Occurrence(NamedTuple):
    """A construction in a concrete scope: one occurrence of a class the run constructs, with
    what the scope made of it."""

    scope: Scope
    construction: Construction

    @property
    def path(self) -> Site:
        """The concrete path."""
        return self.scope.at(self.construction.site)

    @property
    def made(self) -> Made | None:
        """What the scope made of it, once a pass asked for it."""
        return self.scope.made.get(self.construction)


type Held = Key | Construction
"""What a scope holds an occurrence as: the key of what arrived or was heard, or the
construction of what it made."""


class Available(NamedTuple):
    """A reference dereferenced to evidence: the scope that owns the occurrence, what that scope
    holds it as, and the admitted instance. The occurrence is the owner and what it holds: the
    same instance held by two scopes, or by two invocations, is two occurrences, and the
    concrete path is derived from them."""

    owner: Scope
    held: Held
    instance: BaseModel

    @property
    def site(self) -> Site:
        """The declared site of the occurrence: its construction's, or the member path of what
        arrived or was heard under its origin."""
        if isinstance(self.held, Construction):
            return self.held.site
        origin, member = self.held
        return member if origin is None else (*origin.site, HEARD, *member)

    @property
    def path(self) -> Site:
        """The concrete path: the owner's, and the site under the owner's own."""
        return self.owner.at(self.site)


class Pending(NamedTuple):
    """A reference dereferenced to an occurrence no pass has made yet: a constructed premise, or
    the action whose record a premise is bound to."""

    occurrence: Occurrence


class Absent(NamedTuple):
    """A reference to what arrives dereferenced to nothing of the referenced class: the concrete
    path, and what is there instead, if anything."""

    path: Site
    found: BaseModel | None


class Heard(NamedTuple):
    """A reference to a record dereferenced to what its action heard instead: another record
    than the one named, or the one named without the member."""

    action: Occurrence
    record: BaseModel | None


class Rejected(NamedTuple):
    """A reference to a construction dereferenced to its refutation."""

    occurrence: Occurrence
    refuted: Refuted


type State = Available | Pending | Absent | Heard | Rejected
"""What a reference dereferences to in the observed state of a run."""


def resolve(ref: Ref, scope: Scope) -> State:
    """One reference dereferenced from a scope, the same way in a pass and in the explanation of
    a run that ended: what arrives is held by the chain or absent; what is constructed is made,
    refuted or pending in the scope at its template; what is heard is pending while its action
    is, else held by the chain under the action once the action heard the record named, or the
    action heard otherwise: a member of another record, keyed alike, is not this one."""
    match ref:
        case InputRef():
            return arrival(ref, scope)
        case ConstructedRef():
            occurrence = Occurrence(scope.within(ref.scope), ref.construction)
            made = occurrence.made
            if isinstance(made, Constructed):
                return Available(occurrence.scope, ref.construction, made.instance)
            if isinstance(made, Refuted):
                return Rejected(occurrence, made)
            return Pending(occurrence)
        case HeardRef():
            occurrence = Occurrence(scope.within(ref.action.scope), ref.action)
            if occurrence.made is None:
                return Pending(occurrence)
            record = occurrence.scope.arrived.get((ref.action, ()))
            holder = scope.holding(ref.key) if type(record) is ref.record else None
            found = None if holder is None else holder.arrived[ref.key]
            return (
                Available(holder, ref.key, found)
                if holder is not None and is_exactly(found, ref.cls)
                else Heard(occurrence, record)
            )


def arrival(ref: InputRef, scope: Scope) -> Available | Absent:
    """What arrives, dereferenced from a scope: held by the scope of the chain that holds its
    key, as an instance of the referenced class itself, or absent, at the concrete path."""
    holder = scope.holding(ref.key)
    found = None if holder is None else holder.arrived[ref.key]
    if holder is not None and is_exactly(found, ref.cls):
        return Available(holder, ref.key, found)
    return Absent((holder or scope.within(ref.scope)).at(ref.site), found)


def is_exactly(found: BaseModel | None, cls: type[BaseModel]) -> TypeIs[BaseModel]:
    """Whether what a scope holds is an instance of the referenced class itself: two
    alternatives share a site, and the one that arrived is the one whose class the reference
    names."""
    return type(found) is cls


type Premise = tuple[str, int | None]
"""One premise of a construction: a single field, or one element of a tuple field by its
index."""


class Witness(NamedTuple):
    """One premise as a run supplied it: the reference bound at the field that dereferenced to
    evidence, and the evidence, as the occurrence that supplied it."""

    ref: Ref
    found: Available


class Gathering(NamedTuple):
    """One tuple field as a run supplied it: the collection gathered among the field's
    candidates, and each element's witness, in element order."""

    collected: Collected
    elements: tuple[Witness, ...]


class Bound(NamedTuple):
    """A construction's references dereferenced in a scope: the witness at each premise field
    that is filled and at each tuple field, the fresh instance constructed for each field the
    class declares fresh, held by the construction that made it, and for each premise not
    filled each of its references with the state it dereferenced to; read-only once made. What
    a run constructs from, keeps with what it constructed, and authorizes an effect from."""

    premises: Mapping[str, Witness]
    collections: Mapping[str, Gathering]
    fresh: Mapping[str, Available]
    unfilled: Mapping[Premise, tuple[tuple[Ref, State], ...]]

    @property
    def given(self) -> Given:
        """What is supplied for each field, as Pydantic takes it."""
        return {
            **{name: w.found.instance for name, w in self.premises.items()},
            **{
                name: tuple(w.found.instance for w in g.elements)
                for name, g in self.collections.items()
            },
            **{name: a.instance for name, a in self.fresh.items()},
        }

    @property
    def provenance(self) -> Provenance:
        """The concrete paths of what supplied each field."""
        return {
            **{name: (w.found.path,) for name, w in self.premises.items()},
            **{
                name: tuple(w.found.path for w in g.elements)
                for name, g in self.collections.items()
            },
            **{name: ((*a.path, name),) for name, a in self.fresh.items()},
        }


def one[T](found: list[T], cls: type[BaseModel], name: str, what: LiteralString) -> T | None:
    """The one thing found for a field; ``None`` for none; a failure for more than one, which
    the proof excludes and the run refuses to choose among."""
    if len(found) > 1:
        raise ValidationError.from_exception_data(
            cls.__name__,
            [
                fault(
                    "ambiguous",
                    "{cls}.{name} found {n} {what} where the proof bound one",
                    (cls.__name__, name),
                    cls=cls.__name__,
                    name=name,
                    n=len(found),
                    what=what,
                )
            ],
        )
    return found[0] if found else None


def observed(refs: Iterable[Ref], scope: Scope) -> tuple[tuple[Ref, State], ...]:
    """Each reference with what it dereferences to from a scope."""
    return tuple((r, resolve(r, scope)) for r in refs)


def available(states: Iterable[tuple[Ref, State]]) -> list[Witness]:
    """The evidence among what references dereferenced to, each with its reference."""
    return [Witness(ref, state) for ref, state in states if isinstance(state, Available)]


def bound(construction: Construction, scope: Scope) -> Bound:
    """A construction's references dereferenced in a scope: the witness at each premise
    field's reference; for each tuple field the one collection among its candidates whose
    holder is available with it, and every element scope's witness at the element references
    placed in that element's scope, its position's for a fixed tuple, in element order; for
    each premise nothing fills, what its references dereferenced to."""
    premises_: dict[str, Witness] = {}
    collections_: dict[str, Gathering] = {}
    unfilled: dict[Premise, tuple[tuple[Ref, State], ...]] = {}
    cls = construction.cls
    for name, refs in construction.premises.items():
        states = observed(refs, scope)
        found = one(available(states), cls, name, "instances")
        if found is None:
            unfilled[name, None] = states
        else:
            premises_[name] = found
    for name, candidates in construction.collections.items():
        states = observed((c.holder for c in candidates), scope)
        held = [
            (c, elements)
            for c, (_, state) in zip(candidates, states, strict=True)
            if isinstance(state, Available) and (elements := scope.collection(c.key)) is not None
        ]
        collected = one(held, cls, name, "collections")
        if collected is None:
            unfilled[name, None] = states
            continue
        picked_: list[Witness] = []
        for index, element in enumerate(collected[1]):
            at_element = observed(
                (r for r in collected[0].elements if r.scope == element.site), element
            )
            found = one(available(at_element), cls, name, "instances")
            if found is None:
                unfilled[name, index] = at_element
            else:
                picked_.append(found)
        if len(picked_) == len(collected[1]):
            collections_[name] = Gathering(collected[0], tuple(picked_))
    fresh_: dict[str, Available] = {}
    return Bound(
        MappingProxyType(premises_),
        MappingProxyType(collections_),
        MappingProxyType(fresh_),
        MappingProxyType(unfilled),
    )


def supplied(occurrence: Occurrence) -> Bound | None:
    """What a scope supplies for a construction when every premise is filled, with a fresh
    instance for each field the class declares fresh; ``None`` while any is not, so the class
    is asked again next pass."""
    found = bound(occurrence.construction, occurrence.scope)
    if found.unfilled:
        return None
    fresh_ = {
        f.name: Available(occurrence.scope, occurrence.construction, f.classes[0]())
        for f in fields(occurrence.construction.cls)
        if f.fresh
    }
    return found._replace(fresh=MappingProxyType(fresh_))


def substituted(instance: BaseModel, supplied_: Bound) -> list[str]:
    """The fields of an instance that do not hold the very instance supplied for them, in
    field order: a premise another instance stands at, a tuple field with other elements or
    another count, a fresh field another instance stands at. Pydantic keeps an instance it is
    given; a validator that put another there has broken the witness."""
    found: list[str] = []
    for name, w in supplied_.premises.items():
        if getattr(instance, name) is not w.found.instance:
            found.append(name)
    for name, g in supplied_.collections.items():
        value: object = getattr(instance, name)
        if not (
            is_elements(value)
            and len(value) == len(g.elements)
            and all(v is w.found.instance for v, w in zip(value, g.elements, strict=True))
        ):
            found.append(name)
    found.extend(
        name for name, a in supplied_.fresh.items() if getattr(instance, name) is not a.instance
    )
    return found


def witnessed(occurrence: Occurrence, instance: BaseModel, supplied_: Bound) -> Constructed:
    """A construction's instance with the witness of what supplied it, once the instance is
    established to be of the construction's own class and to hold those very instances; one of
    another class, which a validator returned in place of what Pydantic constructed, or one that
    holds another instance has failed, since what its scope would keep of it is not what the
    run asked for, and the failure propagates as a refusal, at the class or at the fields
    substituted."""
    cls = occurrence.construction.cls
    if type(instance) is not cls:
        raise ValidationError.from_exception_data(
            cls.__name__,
            [
                fault(
                    "substituted",
                    "{cls} at {path} constructed {other}, not itself",
                    (cls.__name__,),
                    cls=cls.__name__,
                    path=".".join(occurrence.path),
                    other=type(instance).__name__,
                )
            ],
        )
    swapped = substituted(instance, supplied_)
    if swapped:
        raise ValidationError.from_exception_data(
            cls.__name__,
            [
                fault(
                    "substituted",
                    "{cls}.{name} at {path} holds another instance than the one supplied for it",
                    (cls.__name__, name),
                    cls=cls.__name__,
                    name=name,
                    path=".".join(occurrence.path),
                )
                for name in swapped
            ],
        )
    return Constructed(instance, supplied_)


def construct(occurrence: Occurrence, given: Given) -> BaseModel | ValidationError:
    """Ask Pydantic for an occurrence with what its scope supplied: the instance, or the refusal
    a refutable kind owns as its declared condition not holding, which says only that it does
    not hold here; any other refusal is a failure and propagates as Pydantic raised it, noted
    with the occurrence's concrete path, as a party's exception is."""
    cls = occurrence.construction.cls
    refusals = Refusals()
    try:
        return cls.model_validate(given, context=refusals)
    except ValidationError as refusal:
        if issubclass(cls, Refutable) and cls.refuted(refusal, refusals):
            return refusal
        refusal.add_note(f"at {'.'.join(occurrence.path)}")
        raise


class Unfilled(NamedTuple):
    """A premise of an occurrence that one of its references can never fill, with what the
    reference dereferenced to."""

    occurrence: Occurrence
    premise: Premise
    ref: Ref
    state: Heard | Absent


class Refutation(NamedTuple):
    """An occurrence whose declared condition the evidence rejected."""

    occurrence: Occurrence
    refuted: Refuted


type Cause = Unfilled | Refutation
"""Why an occurrence can never construct: a premise nothing fills, or its own condition
rejected."""


type Unresolved = Mapping[Premise, tuple[tuple[Ref, State], ...]]
"""What an occurrence's unfilled premises dereferenced to when the run ended."""


def causes(
    occurrence: Occurrence, unresolved: Unresolved, blocked: Mapping[Occurrence, tuple[Cause, ...]]
) -> tuple[Cause, ...]:
    """Why an occurrence can never construct, from what its own references dereferenced to:
    for each premise nothing fills, every reference is a cause, a rejected condition or an
    absent source, or a pending occurrence already blocked, whose causes it inherits; a
    premise with a pending occurrence not blocked may still fill, and is no cause. Empty while
    no premise is blocked."""
    found: list[Cause] = []
    for premise, states in unresolved.items():
        here: list[Cause] = []
        for ref, state in states:
            match state:
                case Pending(pending):
                    if pending not in blocked:
                        break
                    here.extend(blocked[pending])
                case Rejected(rejected, refuted):
                    here.append(Refutation(rejected, refuted))
                case Absent() | Heard():
                    here.append(Unfilled(occurrence, premise, ref, state))
                case Available():
                    break
        else:
            found.extend(here)
    return tuple(found)


def waits_on(
    unresolved: Unresolved, blocked: Mapping[Occurrence, tuple[Cause, ...]]
) -> list[Occurrence]:
    """The pending occurrences, not blocked, that an occurrence's unfilled premises dereferenced
    to: what it still waits for."""
    return [
        state.occurrence
        for states in unresolved.values()
        for _, state in states
        if isinstance(state, Pending) and state.occurrence not in blocked
    ]


class Run[Q: Request, A: Reply[Fact]](NamedTuple):
    """One answered request with everything its construction knew: the route, the root scope,
    whose tree holds every occurrence at its concrete path and what made it, and how many
    passes it took."""

    route: Route[Q, A]
    root: Scope
    passes: int


class Blocked(NamedTuple):
    """One request the route conclusively did not construct for: the route's occurrence, whose
    root scope holds everything the passes constructed, refuted and heard, how many passes they
    took, and each cause the route is blocked by, at its own occurrence."""

    occurrence: Occurrence
    passes: int
    causes: tuple[Cause, ...]


def ended(goal: Occurrence, constructions: tuple[Construction, ...], passes: int) -> Blocked:
    """Why the route did not construct, read from every occurrence the passes left unmade, its
    own references dereferenced once in the observed state: an occurrence a premise of which no
    reference can fill is blocked, and so is every occurrence waiting on it, until nothing
    moves. The route blocked is the structured refusal, as a value. The route not blocked waits
    on occurrences that wait on one another, which no evidence explains: a failure, raised,
    naming each in order of reach and what it waits for."""
    unresolved: dict[Occurrence, Unresolved] = {
        occurrence: bound(c, scope).unfilled
        for scope in scopes(goal.scope)
        for c in constructions
        if c.scope == scope.site and (occurrence := Occurrence(scope, c)).made is None
    }
    blocked: dict[Occurrence, tuple[Cause, ...]] = {}
    moved = True
    while moved:
        moved = False
        for occurrence, states in unresolved.items():
            if occurrence not in blocked and (found := causes(occurrence, states, blocked)):
                blocked[occurrence] = found
                moved = True
    if goal in blocked:
        return Blocked(goal, passes, blocked[goal])
    reach = [goal]
    for occurrence in reach:
        reach.extend(o for o in waits_on(unresolved[occurrence], blocked) if o not in reach)
    details = [
        fault(
            "deadlock",
            "{cls} at {path} waits for {on}, and nothing constructs",
            (occurrence.construction.cls.__name__,),
            cls=occurrence.construction.cls.__name__,
            path=".".join(occurrence.path),
            on=", ".join(
                f"{o.construction.cls.__name__} at {'.'.join(o.path)}"
                for o in waits_on(unresolved[occurrence], blocked)
            ),
        )
        for occurrence in reach
    ]
    raise ValidationError.from_exception_data(goal.construction.cls.__name__, details)


def rendered(refuted: Refuted) -> str:
    """What was observed when a condition did not hold, in the developer's names: a
    comparison's operands at their paths with the ordering, as ``value Amount at
    request.each.[0].Asked.heard.amount > bound Limit at Limit``; the kind's own words
    otherwise."""
    found: list[str] = []
    for error in refuted.refusal.errors():
        ctx = error.get("ctx") or {}
        if "ordering" in ctx:
            left, right = str(ctx["left"]), str(ctx["right"])
            found.append(
                f"{left} {ctx['left_class']} at {'.'.join(refuted.provenance[left][0])}"
                f" {ctx['sign']} {right} {ctx['right_class']} at"
                f" {'.'.join(refuted.provenance[right][0])}"
            )
        else:
            found.append(error["msg"])
    return "; ".join(found)


def explained(cause: Cause) -> InitErrorDetails:
    """One cause as one error: ``relation`` at the refuted class, with what was observed;
    ``missing`` at the consumer's field, with what the reference dereferenced to."""
    cls = cause.occurrence.construction.cls
    path = ".".join(cause.occurrence.path)
    if isinstance(cause, Refutation):
        return fault(
            "relation",
            "{cls} at {path} did not hold: {why}",
            (cls.__name__,),
            cls=cls.__name__,
            path=path,
            why=rendered(cause.refuted),
        )
    name = cause.premise[0]
    match cause.state:
        case Absent(at, None):
            why = f"{'.'.join(at)} is absent"
        case Absent(at, found):
            why = f"{'.'.join(at)} holds {type(found).__name__}"
        case Heard(action, record):
            said = "nothing" if record is None else type(record).__name__
            without = ""
            if isinstance(cause.ref, HeardRef) and type(record) is cause.ref.record:
                without = f" without {'.'.join(cause.ref.member)}"
            heard_by = f"{action.construction.cls.__name__} at {'.'.join(action.path)}"
            why = f"{heard_by} heard {said}{without}"
    return fault(
        "missing",
        "no instance fills {cls}.{name} at {path}, which holds {held}; {why}",
        (cls.__name__, name),
        cls=cls.__name__,
        name=name,
        path=path,
        held=names({**holds(cls), **collects(cls)}[name]),
        why=why,
    )


def refused(blocked: Blocked) -> ValidationError:
    """A blocked route as the ``ValidationError`` the caller receives: one error per cause,
    each once, at its own occurrence."""
    keyed: dict[object, Cause] = {}
    for cause in blocked.causes:
        key = (
            (cause.occurrence, cause.premise, cause.ref)
            if isinstance(cause, Unfilled)
            else (cause.occurrence,)
        )
        keyed.setdefault(key, cause)
    return ValidationError.from_exception_data(
        blocked.occurrence.construction.cls.__name__, [explained(c) for c in keyed.values()]
    )


def hear[P: Connection, T: Record](action: Action[P, T], response: Json | Python) -> T:
    """The record an action hears: what the party said, validated strictly as the ``T`` the
    action declares, in the mode the response declares, so a union chooses its member and a
    record already validated stays the same instance. The one boundary between a library
    kind's ``perform`` and the evidence of a run; what it refuses is a failure of the action."""
    adapter = TypeAdapter[Record](said(type(action)))
    match response:
        case Json(text):
            validated = adapter.validate_json(text, strict=True)
        case Python(data):
            validated = adapter.validate_python(data, strict=True)
    (record,) = (r for r in (validated,) if hears(r, action))
    return record


class Invocation(NamedTuple):
    """One run as authorization sees it: the route requested, the proof it was accepted under,
    the root scope whose tree holds every occurrence of this invocation, and the occurrences
    already handed to the effect boundary."""

    route: type[BaseModel]
    proof: Proof
    root: Scope
    performed: set[Occurrence]


class Execution(NamedTuple):
    """One authorized effect, the only thing the effect boundary takes: the action occurrence,
    the action instance its scope made, and the witness it was constructed from. Produced by
    ``authorized`` and nowhere else; it is a record of this invocation, not a credential."""

    occurrence: Occurrence
    action: Action[Connection, Record]
    supplied: Bound


def unauthorized(invocation: Invocation, occurrence: Occurrence) -> str | None:
    """The first objection to performing an occurrence in an invocation, or ``None``."""
    return next(objections(invocation, occurrence), None)


def objections(invocation: Invocation, occurrence: Occurrence) -> Iterator[str]:
    """Why an occurrence may not be performed in an invocation, in the order established: it
    is misplaced; its scope made nothing of it; what it made is of another class than the
    construction makes, or no action; what supplied it is unbound; the instance or its party is
    not what was supplied; it was performed already. Each reads the witness and the scopes of
    this invocation, and nothing else."""
    construction, made = occurrence.construction, occurrence.made
    why = misplaced(invocation, occurrence)
    if why is not None:
        yield why
    if not isinstance(made, Constructed):
        yield "its scope made no action of it"
        return
    cls, instance = construction.cls, made.instance
    if type(instance) is not cls:
        yield f"it is {type(instance).__name__}, not the {cls.__name__} the construction makes"
    if not is_performed(instance):
        yield "its scope made no action of it"
    why = unbound(construction, occurrence.scope, made.supplied)
    if why is not None:
        yield why
    swapped = substituted(instance, made.supplied)
    if swapped:
        yield f"{', '.join(swapped)} hold other instances than were supplied"
    if occurrence in invocation.performed:
        yield "it was performed in this invocation already"


def misplaced(invocation: Invocation, occurrence: Occurrence) -> str | None:
    """Why an occurrence is not one of this invocation's route, or ``None``: its construction
    is not the proof's for the route; the proof does not justify it; its scope is not one the
    invocation opened at the construction's site."""
    construction, scope = occurrence.construction, occurrence.scope
    route = invocation.route.__name__
    if not any(c is construction for c in invocation.proof.constructs(invocation.route)):
        return f"its construction is not in the proof of {route}"
    if not any(j.action is construction and j.established for j in invocation.proof.justifications):
        return f"the proof of {route} does not justify performing it"
    if not any(s is scope for s in scopes(invocation.root)) or scope.site != construction.scope:
        return "its scope is not one this invocation opened at its site"
    return None


def unbound(construction: Construction, scope: Scope, supplied_: Bound) -> str | None:
    """Why a witness is not the construction's binding dereferenced in a scope, or ``None``:
    other fields than the construction binds; a premise supplied by a reference the
    construction does not bind at that field, or one that dereferences from this scope to
    another occurrence than the one that supplied it; a tuple field supplied by a collection it
    does not bind, or one the scope does not gather from the same occurrences, element by
    element."""
    if set(supplied_.premises) != set(construction.premises) or set(supplied_.collections) != set(
        construction.collections
    ):
        return "what supplied it is not the construction's binding"
    for name, w in supplied_.premises.items():
        if not any(r is w.ref for r in construction.premises[name]):
            return f"{name} was supplied by a reference the construction does not bind"
        if not same(resolve(w.ref, scope), w):
            return f"{name} dereferences to another occurrence than the one that supplied it"
    for name, g in supplied_.collections.items():
        if not any(c is g.collected for c in construction.collections[name]):
            return f"{name} was supplied by a collection the construction does not bind"
        if not gathers(scope, g):
            return f"{name} gathers other occurrences than the ones that supplied it"
    return None


def gathers(scope: Scope, gathering: Gathering) -> bool:
    """Whether a scope gathers the collection a tuple field was supplied with: as many element
    scopes, each dereferencing an element reference of the collection to the very occurrence
    it did, in order."""
    elements = scope.collection(gathering.collected.key)
    return (
        elements is not None
        and len(elements) == len(gathering.elements)
        and all(
            any(r is w.ref for r in gathering.collected.elements) and same(resolve(w.ref, e), w)
            for e, w in zip(elements, gathering.elements, strict=True)
        )
    )


def same(state: State, witness: Witness) -> bool:
    """Whether a reference dereferences now to the very occurrence it did when it supplied a
    construction: the scope that owns it, what that scope holds it as, and the instance, each
    by identity, so the same instance held elsewhere, or held here by another invocation, is
    not it."""
    return (
        isinstance(state, Available)
        and state.owner is witness.found.owner
        and state.held == witness.found.held
        and state.instance is witness.found.instance
    )


def authorized(invocation: Invocation, occurrence: Occurrence) -> Execution:
    """The execution of an action occurrence this invocation authorizes, from the witness of
    what supplied it and nothing else; one it does not authorize is a failure of the engine's
    integrity, raised, which the run propagates before any effect of the pass."""
    why = unauthorized(invocation, occurrence)
    made = occurrence.made
    if why is not None or not isinstance(made, Constructed) or not is_performed(made.instance):
        cls = occurrence.construction.cls
        raise ValidationError.from_exception_data(
            cls.__name__,
            [
                fault(
                    "unauthorized",
                    "{cls} at {path} is not performed: {why}",
                    (cls.__name__,),
                    cls=cls.__name__,
                    path=".".join(occurrence.path),
                    why=why or "its scope made no action of it",
                )
            ],
        )
    return Execution(occurrence, made.instance, made.supplied)


async def performed_in_span(execution: Execution, pass_: int) -> Record:
    """Perform one authorized execution inside a span named for the action's class, carrying
    the party's class name, the occurrence's concrete path, the pass it was built in, and
    ``tca.outcome``, which is the outcome its task has: ``heard``, once what the party said
    validated as the action's record, with the record's class name and path; ``failed``, the
    client's exception or the refusal of what it returned, noted with the path and propagating,
    the span marked as ``failing`` does; ``cancelled``, which is not the action's error and
    leaves the status unset."""
    occurrence, action, _ = execution
    attributes = {
        "tca.party": type(action.party).__name__,
        "tca.site": ".".join(occurrence.path),
        "tca.pass": pass_,
    }
    with tracer.start_as_current_span(
        type(action).__name__,
        attributes=attributes,
        record_exception=False,
        set_status_on_exception=False,
    ) as span:
        try:
            record = hear(action, await action.perform())
        except CancelledError:
            span.set_attribute("tca.outcome", "cancelled")
            raise
        except Exception as failure:
            failing(span, failure)
            failure.add_note(f"at {'.'.join(occurrence.path)}")
            raise
        span.set_attribute("tca.outcome", "heard")
        span.set_attribute("tca.record", type(record).__name__)
        span.set_attribute("tca.heard", ".".join((*occurrence.path, HEARD)))
        return record


def failing(span: Span, failure: BaseException) -> None:
    """A span's failure, read from the exception that left it: ``tca.outcome`` failed, the
    status error named with the exception's class, and one ``exception`` event with the
    class alone. The exception's message and traceback stay out of the span: what a party
    said or a request holds is in a refusal's message, and a span is exported."""
    span.set_attribute("tca.outcome", "failed")
    span.set_status(Status(StatusCode.ERROR, type(failure).__name__))
    span.add_event(
        "exception", {"exception.type": f"{type(failure).__module__}.{type(failure).__qualname__}"}
    )


async def answer[Q: Request, A: Reply[Fact]](
    route: type[Route[Q, A]], request: Q, deployment: Config, proof: Proof
) -> Route[Q, A]:
    """Construct the route from the request: ``ran``, with a blocked route raised as the
    ``ValidationError`` naming each cause at its own occurrence."""
    found = await ran(route, request, deployment, proof)
    if isinstance(found, Blocked):
        raise refused(found)
    return found.route


async def ran[Q: Request, A: Reply[Fact]](
    route: type[Route[Q, A]], request: Q, deployment: Config, proof: Proof
) -> Run[Q, A] | Blocked:
    """Construct the route from the request, pass by pass, in every scope at each construction's
    template, until the route itself constructs or a pass constructs nothing, inside the
    route's span, whose ``tca.outcome`` is the outcome the run had, read from what the
    construction returned or raised: ``answered``, a ``Run``, with ``tca.passes``; ``refused``,
    a ``Blocked``, the business's no, as a value; ``failed``, anything raised, a construction
    that is not a refutation refusing, a party's exception in its pass's group, a deadlock or
    any other, the span marked as ``failing`` does; ``cancelled``, from outside, which
    is no error of the run and leaves the status unset. Each record that entered a scope after
    its pass is one ``admitted`` event on the span, with the record's class and path: an action
    heard in a pass another action failed leaves none."""
    with tracer.start_as_current_span(
        route.__name__,
        attributes={"tca.request": type(request).__name__},
        record_exception=False,
        set_status_on_exception=False,
    ) as span:
        try:
            found = await constructed(route, request, deployment, proof, span)
        except CancelledError:
            span.set_attribute("tca.outcome", "cancelled")
            raise
        except Exception as failure:
            failing(span, failure)
            raise
        if isinstance(found, Blocked):
            span.set_attribute("tca.outcome", "refused")
            return found
        span.set_attribute("tca.outcome", "answered")
        span.set_attribute("tca.passes", found.passes)
        return found


async def constructed[Q: Request, A: Reply[Fact]](
    route: type[Route[Q, A]], request: Q, deployment: Config, proof: Proof, span: Span
) -> Run[Q, A] | Blocked:
    """The passes of ``ran``. Each pass dereferences every construction of the route not yet
    made in a scope at its template and, where every reference resolves, asks Pydantic for it;
    a refutable kind whose declared condition does not hold is refuted in that scope, once; any
    other refusal is a failure and propagates; so is an instance that does not hold what was
    supplied for it. The pass's actions are each authorized from the witness of what supplied
    them, every one before any is performed, so an authorization that fails performs none; then
    performed together in one task group, across every scope, each heard at the one boundary,
    and each record enters the scope its action was built in once every action of the pass was
    heard, as one ``admitted`` event on the route's span; a library kind's exception, or a
    refusal of what it returned,
    cancels the group's other actions and propagates in an ``ExceptionGroup``, noted with the
    paths of the actions cancelled with it. An action's effect may have happened whenever its
    task started: one heard returned a validated record, one failed or cancelled may have had
    its effect and returned none, and no record of the pass is admitted, which the group's note
    says; an action that cancelled itself fails the pass the same way, once every other task
    is done. A pass that constructs nothing ends the run as ``ended`` reads it."""
    constructions = proof.constructs(route)
    root = Scope((), (), None)
    arrived(request, None, REQUEST, root)
    arrived(deployment, None, DEPLOYMENT, root)
    for c in proof.constants:
        root.arrived[None, (c.__name__,)] = c()
    goal = Occurrence(root, goal_of(route, constructions))
    invocation = Invocation(route, proof, root, set())
    passes = 0
    while goal.made is None:
        passes += 1
        ready: list[Occurrence] = []
        built = False
        for scope in list(scopes(root)):
            for construction in constructions:
                occurrence = Occurrence(scope, construction)
                if construction.scope != scope.site or occurrence.made is not None:
                    continue
                found = supplied(occurrence)
                if found is None:
                    continue
                instance = construct(occurrence, found.given)
                if isinstance(instance, ValidationError):
                    scope.made[construction] = Refuted(instance, found)
                    continue
                built = True
                scope.made[construction] = witnessed(occurrence, instance, found)
                if is_action(construction.cls):
                    ready.append(occurrence)
        executions = [authorized(invocation, o) for o in ready]
        invocation.performed.update(ready)
        performed = [e.occurrence for e in executions]
        tasks: list[Task[Record]] = []
        try:
            async with TaskGroup() as group:
                tasks = [group.create_task(performed_in_span(e, passes)) for e in executions]
        except BaseExceptionGroup as failed:
            failed.add_note(outcomes_of(performed, tasks))
            raise
        records = heard_in(performed, tasks, passes)
        for o, record in zip(performed, records, strict=True):
            arrived(record, o.construction, (), o.scope)
            span.add_event(
                "admitted",
                {"tca.record": type(record).__name__, "tca.heard": ".".join((*o.path, HEARD))},
            )
        if not built:
            return ended(goal, constructions, passes)
    made = goal.made
    if not isinstance(made, Constructed):
        msg = f"{route.__name__} refuted"
        raise TypeError(msg)
    return Run(route.model_validate(made.instance), root, passes)


def goal_of(route: type[BaseModel], constructions: tuple[Construction, ...]) -> Construction:
    """The route's own construction among a proof's: what a run ends by constructing. A proof
    without one is no proof of the route, a failure."""
    own = [c for c in constructions if c.cls is route]
    if not own:
        unconstructed = f"{route.__name__} is constructed by none of the proof's constructions"
        raise LookupError(unconstructed)
    return own[0]


def heard_in(performed: list[Occurrence], tasks: list[Task[Record]], pass_: int) -> list[Record]:
    """Every record a pass's actions heard, taken from every task before any is admitted. A
    task that cancelled itself leaves its group's exit silent, by ``TaskGroup``'s contract,
    and is the pass failing, with what the others did: its effect may have happened, the
    others' records are heard, and none is admitted."""
    if any(task.cancelled() for task in tasks):
        quit_ = f"an action of pass {pass_} cancelled itself; {outcomes_of(performed, tasks)}"
        raise RuntimeError(quit_)
    return [task.result() for task in tasks]


def outcomes_of(performed: list[Occurrence], tasks: list[Task[Record]]) -> str:
    """What a failed pass's actions did, for the note on its group: which were heard, whose
    effect happened and whose record was validated; which were cancelled, whose effect may
    have happened; and that none was admitted. The failed ones are the group's exceptions,
    each noted with its path; their effects may have happened too."""
    heard = [
        ".".join(p.path)
        for p, t in zip(performed, tasks, strict=True)
        if not t.cancelled() and t.exception() is None
    ]
    cancelled = [".".join(p.path) for p, t in zip(performed, tasks, strict=True) if t.cancelled()]
    return (
        f"heard {', '.join(heard) or 'none'}; cancelled {', '.join(cancelled) or 'none'};"
        " admitted none"
    )
