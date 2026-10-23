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

Binding is read from the declarations and nothing else. A single field binds to the occurrences
of its classes visible in the scope; a class with two visible sites is ambiguous, and the
consuming field is refused, not the reuse of the class. A tuple field gathers one collection:
the collections reached through the class's bound premises, by their product fields, or, for a
class whose premises reach none, the collections the scope itself holds; a collection is a
candidate when every element's scope holds one of the field's classes, and two candidates are
ambiguous at that field. A class is constructed in each scope that owns one of its bound
premises or holds the collection it gathers; a class with neither is constructed once, at the
root. Nothing chooses by field name, by declaration order, by trial validation, or by what
arrived first.

The proof constructs each route symbolically from its own request, the deployment and the
constants: the declared tree of the request and the deployment is the tree of symbols, the
passes construct every class the route's reply leads to wherever it binds, an action's records
enter as alternatives, and at the fixed point every construction is bound again against the
whole tree, so a candidate that appeared late is still seen. ``Proof`` is constructed from the
constructions, what was left waiting and the faults; its validator refuses the program with one
``ValidationError`` naming every fault: ``missing``, a field no occurrence fills; ``collects``,
a tuple over a class no collection's elements hold; ``unplaceable``, a class whose fields are
never visible from one scope; ``cycle``, classes that wait on each other; ``route``, a route
whose reply exists per element; ``ambiguous``, a field with two candidates, or two union
members not proven exclusive; ``unreached``, a class the reply of no route leads to;
``unmodeled``, a field that names no kind; ``boundary``, a request that holds what does not
arrive; ``config``, no one deployment; ``never``, a relation its operands' intervals make
certain or impossible; ``undiscriminated``, two records one action hears that no field tells
apart; ``undecided``, an action performed on one branch of a choice that holds nothing deciding
it.

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
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from itertools import combinations, product
from types import ModuleType, NoneType, UnionType
from typing import Literal, LiteralString, NamedTuple, Self, TypeIs, Union, get_args, get_origin

from annotated_types import Ge, Gt, Le, Lt, MaxLen, MinLen
from opentelemetry import trace
from opentelemetry.trace import Span
from pydantic import BaseModel, ConfigDict, RootModel, TypeAdapter, ValidationError, model_validator
from pydantic_core import InitErrorDetails, PydanticCustomError, PydanticUndefined

from type_construction.world import (
    Action,
    Comparison,
    Computation,
    Config,
    Connection,
    Derived,
    Fact,
    Interval,
    Json,
    Python,
    Record,
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
    "Collected",
    "ConstructedRef",
    "Construction",
    "Fault",
    "HeardRef",
    "InputRef",
    "Proof",
    "Ref",
    "Run",
    "Scope",
    "Site",
    "Waiting",
    "answer",
    "asked",
    "classes",
    "coexist",
    "collects",
    "config",
    "configs",
    "hear",
    "heard",
    "holds",
    "interval",
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
numeric class, and ``ZERO`` stands for the constant zero."""

ZERO = object()
"""The variable whose value is zero, which a class's interval is constraints against."""

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
    constructs, which the proof, the run and the explanation of a run all read. Each required
    single field binds to the references of its candidate sources, alternatives among them;
    each tuple field to the collection it gathers; each fresh field to the class constructed
    for the holder; ``because`` is the optional sites it exists only when they arrive. The
    declaration analysis writes the binding when the class first binds and once more against
    the whole tree at the fixed point; after the analysis nothing writes it. A construction is
    its object: a reference to one is a reference to this, never to a name or a path."""

    route: type[BaseModel]
    cls: type[BaseModel]
    scope: Site
    premises: dict[str, tuple[Ref, ...]] = field(default_factory=dict[str, tuple["Ref", ...]])
    collections: dict[str, Collected] = field(default_factory=dict[str, "Collected"])
    freshly: dict[str, type[BaseModel]] = field(default_factory=dict[str, type[BaseModel]])
    because: tuple[Site, ...] = ()

    def __repr__(self) -> str:
        return f"Construction({self.route.__name__}: {'.'.join(self.site)})"

    @property
    def site(self) -> Site:
        """The declared site: the scope's and the class's name, for a concrete path."""
        return (*self.scope, self.cls.__name__)

    def rebound(self, found: Construction) -> None:
        """The binding against the whole tree, in place of the first."""
        self.premises, self.collections = found.premises, found.collections
        self.freshly, self.because = found.freshly, found.because


@dataclass(frozen=True)
class InputRef:
    """A reference to what arrives: the request, the deployment, a constant, or a member of
    one, in the scope at a site, of a class. It dereferences to what the scope chain holds for
    it, present from the start or never."""

    scope: Site
    member: Site
    cls: type[BaseModel]

    @property
    def site(self) -> Site:
        """The declared site: the scope's and the member path."""
        return (*self.scope, *self.member)

    @property
    def key(self) -> Key:
        """What a scope holds it under: no origin, and its site."""
        return (None, self.site)

    def held(self, cls: type[BaseModel], name: str) -> InputRef:
        """The reference to what a single field of this holds."""
        return InputRef(scope=self.scope, member=(*self.member, name), cls=cls)

    def element(self, cls: type[BaseModel], name: str, step: str) -> InputRef:
        """The reference to an element of a tuple field of this, in the element's own scope."""
        return InputRef(scope=(*self.site, name, step), member=(), cls=cls)


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
    record, or the record named without the member."""

    action: Construction
    record: type[BaseModel]
    member: Site
    cls: type[BaseModel]

    @property
    def scope(self) -> Site:
        """The scope template the action is placed at, where its record enters."""
        return self.action.scope

    @property
    def site(self) -> Site:
        """The declared site: the action's, ``heard``, and the member path."""
        return (*self.action.site, HEARD, *self.member)

    @property
    def key(self) -> Key:
        """What a scope holds it under: the action, and the member path."""
        return (self.action, self.member)

    def held(self, cls: type[BaseModel], name: str) -> HeardRef:
        """The reference to what a single field of this holds."""
        return HeardRef(self.action, self.record, (*self.member, name), cls)

    def element(self, cls: type[BaseModel], name: str, step: str) -> HeardRef:
        """The reference to an element of a tuple field of this, in the element's own scope."""
        return HeardRef(self.action, self.record, (*self.member, name, step), cls)


type Ref = InputRef | ConstructedRef | HeardRef
"""Where a bound premise comes from, retained from the declarations: the one thing a run
dereferences to construct, and to explain what it could not."""

type Key = tuple[Construction | None, Site]
"""What a scope holds an arrived instance or a collection under: its origin, the action that
heard it or none for what arrives, and the member path, the whole declared site for what
arrives."""


@dataclass(frozen=True)
class Collected:
    """Where a construction's tuple field gathers: the reference to the occurrence that holds
    the collection, the tuple field's name, the references to the elements it takes, one per
    element class, each in the element's scope, ``"[]"`` for every element of a variable tuple
    and a position for each of a fixed one, and the positions the holder declares, ``None``
    for ``tuple[E, ...]``."""

    holder: InputRef | HeardRef
    name: str
    elements: tuple[Ref, ...]
    positions: int | None

    @property
    def site(self) -> Site:
        """The collection's declared site."""
        return (*self.holder.site, self.name)

    @property
    def key(self) -> Key:
        """What a scope holds the collection under: the holder's origin, and the field."""
        origin, member = self.holder.key
        return (origin, (*member, self.name))


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


def declared(cls: type[object]) -> bool:
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
        if isinstance(c, type) and c.__module__ == program.__name__ and declared(c)
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


def members(annotation: object) -> tuple[object, ...]:
    """A union's members, or the one annotation."""
    return get_args(annotation) if get_origin(annotation) in (UnionType, Union) else (annotation,)


def options(annotation: object) -> Options:
    """The classes an annotation may hold."""
    return tuple(m for m in members(annotation) if is_model(m))


def elements(annotation: object) -> tuple[object, ...]:
    """The element annotations of a tuple annotation: ``tuple[X, ...]`` and ``tuple[X]`` name
    ``X``."""
    return tuple(a for a in get_args(annotation) if a is not Ellipsis)


def fixed(annotation: object) -> bool:
    """Whether a tuple annotation fixes its positions: ``tuple[X, X]`` and ``tuple[X]`` do,
    ``tuple[X, ...]`` does not."""
    return Ellipsis not in get_args(annotation)


def position(annotation: object, index: int) -> str:
    """The site step of one element of a tuple: its index for a fixed tuple, ``"[]"`` for
    every element of a variable one."""
    return f"[{index}]" if fixed(annotation) else "[]"


def holds(cls: type[BaseModel]) -> dict[str, Options]:
    """Each single field and the classes it may hold; empty for a field that names no class."""
    return {
        name: options(field.annotation)
        for name, field in cls.model_fields.items()
        if get_origin(field.annotation) is not tuple
    }


def collects(cls: type[BaseModel]) -> dict[str, Options]:
    """Each tuple field and the classes an element may be."""
    return {
        name: tuple(c for e in elements(field.annotation) for c in options(e))
        for name, field in cls.model_fields.items()
        if get_origin(field.annotation) is tuple
    }


def produces(cls: type[BaseModel]) -> dict[str, Options]:
    """Each computed field whose return type names classes, and those classes: the words a
    reply says."""
    found = {
        name: options(computed.return_type) for name, computed in cls.model_computed_fields.items()
    }
    return {name: classes_ for name, classes_ in found.items() if classes_}


def constant(cls: type[BaseModel]) -> bool:
    """Whether a class is a constant: a scalar whose root has a default, which exists in every
    run by being declared."""
    root = cls.model_fields.get("root")
    return is_scalar(cls) and root is not None and root.default is not PydanticUndefined


def fresh(cls: type[BaseModel]) -> bool:
    """Whether a class is fresh: a scalar whose root has a default factory, constructed anew for
    each holder."""
    root = cls.model_fields.get("root")
    return is_scalar(cls) and root is not None and root.default_factory is not None


def premises(cls: type[BaseModel]) -> dict[str, Options]:
    """Each required single field that names classes the scope must hold before the class is
    asked for: a fresh class is constructed for the holder instead."""
    return {
        name: classes_
        for name, classes_ in holds(cls).items()
        if classes_ and cls.model_fields[name].is_required() and not all(fresh(c) for c in classes_)
    }


def freshly(cls: type[BaseModel]) -> dict[str, type[BaseModel]]:
    """Each required single field whose class is fresh, and that class: constructed for the
    holder when the holder is asked for."""
    return {
        name: classes_[0]
        for name, classes_ in holds(cls).items()
        if classes_ and cls.model_fields[name].is_required() and all(fresh(c) for c in classes_)
    }


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
    (request,) = (m for m in members(route.model_fields["request"].annotation) if is_request(m))
    return request


def replied[Q: Request, A: Reply[Fact]](route: type[Route[Q, A]]) -> Options:
    """The reply classes a route declares as ``Route[Q, A]``: the classes of its ``reply``."""
    return options(route.model_fields["reply"].annotation)


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
    return tuple(m for m in members(said(action)) if is_record(m))


def hears[P: Connection, T: Record](record: Record, action: Action[P, T]) -> TypeIs[T]:
    """Whether a record is one the action hears."""
    return isinstance(record, heard(type(action)))


def hearers(classes_: Iterable[type[BaseModel]]) -> dict[type[BaseModel], type[BaseModel]]:
    """Each record class and the first action that hears it."""
    found: dict[type[BaseModel], type[BaseModel]] = {}
    for action in classes_:
        if is_action(action):
            for record in heard(action):
                found.setdefault(record, action)
    return found


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

    def collected(self, elements: Iterable[Symbol]) -> Collected:
        """The collection as a construction gathers it: by references."""
        holder = self.holder.ref
        if isinstance(holder, ConstructedRef):
            held_by_construction = f"{'.'.join(self.site)} is held by a construction"
            raise TypeError(held_by_construction)
        return Collected(
            holder, self.name, tuple(dict.fromkeys(e.ref for e in elements)), self.positions
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
    because: tuple[Site, ...] = ()
    """The sites of the optional fields this occurrence exists only when they arrive: its own,
    when what declares it admits ``None``, and its holder's or its premises'. An occurrence
    with none is present in every invocation."""

    @property
    def site(self) -> Site:
        """The declared site the reference names."""
        return self.ref.site


def absent(cls: type[BaseModel], name: str) -> bool:
    """Whether a field admits ``None``: what it holds may not arrive."""
    return NoneType in members(cls.model_fields[name].annotation)


def positions(annotation: object) -> int | None:
    """The positions a tuple annotation declares: their number for a fixed tuple, ``None`` for
    ``tuple[E, ...]``."""
    return len(elements(annotation)) if fixed(annotation) else None


def declared_symbol(
    ref: InputRef | HeardRef,
    context: Context,
    lineage: frozenset[type[BaseModel]],
    because: tuple[Site, ...] = (),
) -> Symbol:
    """The symbol of a class that arrives or is heard, at the reference's site, with the
    symbols of everything it declares: each single field's classes at the field's site, as
    alternatives, and each tuple field's element classes in element contexts under this one,
    one for ``tuple[E, ...]``, one per position for a fixed tuple, each a reference to a member
    of this one. What a field admitting ``None`` holds exists only when it arrives, and so does
    everything under it. A class already on the lineage is not descended into."""
    cls, site = ref.cls, ref.site
    symbol = context.own(Symbol(cls, ref, context, because=because))
    if cls in lineage:
        return symbol
    lineage = lineage | {cls}
    for name, classes_ in holds(cls).items():
        held = (*because, (*site, name)) if absent(cls, name) else because
        symbol.held[name] = tuple(
            declared_symbol(ref.held(c, name), context, lineage, held) for c in classes_
        )
    for name, info in cls.model_fields.items():
        if get_origin(info.annotation) is not tuple:
            continue
        found: list[Symbol] = []
        for index, element in enumerate(elements(info.annotation)):
            step = position(info.annotation, index)
            child = context.opened((*site, name, step), many=not fixed(info.annotation))
            found.extend(
                declared_symbol(ref.element(c, name, step), child, lineage, because)
                for c in options(element)
            )
        symbol.collected[name] = Gathered(symbol, name, tuple(found), positions(info.annotation))
    return symbol


class Ambiguity(NamedTuple):
    """A field with more than one candidate: what the proof refuses at the consuming field."""

    field: str
    message: str


def single(name: str, classes_: Options, context: Context) -> tuple[Symbol, ...] | Ambiguity | None:
    """The visible symbols of a single field's classes: one site per class, else ambiguous;
    ``None`` while none is visible."""
    found = [s for c in classes_ for s in context.visible(c)]
    for cls in classes_:
        sites = list(dict.fromkeys(s.site for s in found if s.cls is cls))
        if len(sites) > 1:
            where = ", ".join(".".join(s) for s in sites)
            return Ambiguity(name, f"{cls.__name__} is at {len(sites)} sites here: {where}")
    return tuple(found) or None


def reached_from(symbols: Iterable[Symbol], context: Context) -> dict[Site, Gathered]:
    """Every collection reached from symbols through product fields, by site: what a bound
    premise holds, and what that holds in turn; through a constructed premise, what its
    construction gathers and what its premises hold."""
    found: dict[Site, Gathered] = {}
    seen: set[Ref] = set()
    todo = [s.ref for s in symbols]
    while todo:
        ref = todo.pop()
        if ref in seen:
            continue
        seen.add(ref)
        if isinstance(ref, ConstructedRef):
            for collected in ref.construction.collections.values():
                holder = context.symbols[collected.holder]
                found[collected.site] = holder.collected[collected.name]
            todo.extend(r for refs in ref.construction.premises.values() for r in refs)
        else:
            symbol = context.symbols[ref]
            found.update({g.site: g for g in symbol.collected.values()})
            todo.extend(s.ref for alternatives in symbol.held.values() for s in alternatives)
    return found


def held_by(context: Context) -> dict[Site, Gathered]:
    """Every collection the context's own symbols hold, by site."""
    return {g.site: g for s in context.owned for g in s.collected.values()}


def chosen(classes_: Options, context: Context) -> list[Symbol]:
    """The symbols of the given classes an element context owns."""
    return [s for s in context.owned if s.cls in classes_]


def compatible(cls: type[BaseModel], name: str, source: Gathered) -> bool:
    """Whether a tuple field may gather a collection of the source's declared shape:
    ``tuple[E, ...]`` gathers any; a fixed tuple gathers a fixed tuple of the same positions;
    a refutable kind gathers any, since refusing the count is what it declares."""
    wanted = positions(cls.model_fields[name].annotation)
    return wanted is None or refutable(cls) or wanted == source.positions


def gather(
    cls: type[BaseModel], name: str, classes_: Options, pool: Mapping[Site, Gathered]
) -> Collected | Ambiguity | None:
    """The one collection among a pool, of a shape the field may gather, whose every element
    context owns one of the field's classes, with those elements gathered in order; ambiguous
    with two such collections, or an element context owning a class at two sites; ``None``
    while there is none."""
    complete = [
        g
        for g in pool.values()
        if compatible(cls, name, g) and all(chosen(classes_, c) for c in g.contexts)
    ]
    if len(complete) > 1:
        where = ", ".join(".".join(g.site) for g in complete)
        return Ambiguity(name, f"{names(classes_)} is collected by {len(complete)}: {where}")
    if not complete:
        return None
    (found,) = complete
    picked: list[Symbol] = []
    for element in found.contexts:
        own = chosen(classes_, element)
        for member in classes_:
            sites = list(dict.fromkeys(s.site for s in own if s.cls is member))
            if len(sites) > 1:
                where = ", ".join(".".join(s) for s in sites)
                return Ambiguity(
                    name, f"{member.__name__} is at {len(sites)} sites per element: {where}"
                )
        picked.extend(own)
    return found.collected(picked)


def bound_in(
    route: type[BaseModel], cls: type[BaseModel], context: Context
) -> Construction | Ambiguity | None:
    """How a class constructs in a context, read from its fields: each required single field
    bound to the visible symbols of its classes, each tuple field to one collection reached
    through the bound premises or, when they reach none, held by the context; ``None`` while
    a field has nothing; the ambiguity of the first field with more than one candidate."""
    singles: dict[str, tuple[Symbol, ...]] = {}
    for name, classes_ in premises(cls).items():
        found = single(name, classes_, context)
        if found is None or isinstance(found, Ambiguity):
            return found
        singles[name] = found
    pool = reached_from((s for found in singles.values() for s in found), context) or held_by(
        context
    )
    collections: dict[str, Collected] = {}
    for name, classes_ in collects(cls).items():
        gathered = gather(cls, name, classes_, pool)
        if gathered is None or isinstance(gathered, Ambiguity):
            return gathered
        collections[name] = gathered
    sources = (
        *(s for found in singles.values() for s in found),
        *(context.symbols[e] for g in collections.values() for e in g.elements),
    )
    return Construction(
        route,
        cls,
        context.site,
        {n: tuple(dict.fromkeys(s.ref for s in found)) for n, found in singles.items()},
        collections,
        freshly(cls),
        tuple(dict.fromkeys(site for s in sources for site in s.because)),
    )


def anchored(construction: Construction, context: Context) -> bool:
    """Whether the context owns one of the construction's premises or holds a collection it
    gathers, so the class is constructed here; a class with neither is constructed at the
    root."""
    anchors = [
        *(r for refs in construction.premises.values() for r in refs),
        *(c.holder for c in construction.collections.values()),
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
    symbol = context.own(
        Symbol(
            construction.cls, ConstructedRef(construction), context, because=construction.because
        )
    )
    if is_action(construction.cls):
        for record in heard(construction.cls):
            ref = HeardRef(construction, record, (), record)
            declared_symbol(ref, context, frozenset(), construction.because)
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
    code: Literal["missing", "collects", "unplaceable", "route", "ambiguous", "conditional"]
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
                if isinstance(found, Construction) and anchored(found, context):
                    symbolized(found, context)
                    constructed.append((found, context))
                    done[context].add(cls)
                    moved = True
    faulted: list[Fault] = []
    for construction, context in constructed:
        cls = construction.cls
        found = bound_in(route, cls, context)
        if isinstance(found, Construction):
            construction.rebound(found)
        elif isinstance(found, Ambiguity):
            faulted.append(ambiguity(cls, found))
        if is_route(cls) and context.parent is not None:
            faulted.append(misrouted(cls, context))
        if is_route(cls) and isinstance(found, Construction) and found.because:
            faulted.append(conditional(cls, found.because))
    never_built = [c for c in asked_for if not any(c is b.cls for b, _ in constructed)]
    waiting, faults = unexplained(route, never_built, classes_, root)
    return Symbolic([c for c, _ in constructed], waiting, [*faulted, *faults])


def ambiguity(cls: type[BaseModel], found: Ambiguity) -> Fault:
    """The fault of a field with more than one candidate."""
    return Fault(
        code="ambiguous",
        loc=(cls.__name__, found.field),
        message=f"{cls.__name__}.{found.field} has two sources: {found.message}; hold what"
        " tells them apart",
    )


def conditional(cls: type[BaseModel], because: tuple[Site, ...]) -> Fault:
    """The fault of a route that answers only when an optional field arrives: an absence is
    not evidence, and a request the route admits may carry the absence."""
    sites = ", ".join(".".join(site) for site in because)
    return Fault(
        code="conditional",
        loc=(cls.__name__,),
        message=f"{cls.__name__} answers only when {sites} arrives, and what declares it admits"
        " its absence; an absence the business concludes from is a class",
    )


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
    """Why each class the passes never constructed was not: a context that finds a field
    ambiguous is that fault; a field whose classes occur nowhere waits on the never-built
    classes that would bring them, and with none is ``missing``; a tuple field no collection's
    elements fill waits the same way, and with none is ``collects``; a class whose every field
    has a candidate somewhere but never all from one scope is ``unplaceable``, or ``route`` for
    a route whose reply is under an element. ``cycle`` is left to the proof."""
    waiting: list[Waiting] = []
    faults: list[Fault] = []
    for cls in never_built:
        found = [bound_in(route, cls, c) for c in contexts(root)]
        if any(isinstance(f, Ambiguity) for f in found):
            faults.extend(ambiguity(cls, f) for f in found if isinstance(f, Ambiguity))
            continue
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


def shape(annotation: object) -> str:
    """A tuple annotation in the developer's names: ``tuple[X, ...]`` or ``tuple[X, X]``."""
    inner = ", ".join(names(options(e)) for e in elements(annotation))
    return f"tuple[{inner}]" if fixed(annotation) else f"tuple[{inner}, ...]"


def uncollected(cls: type[BaseModel], name: str, classes_: Options) -> Fault:
    """The fault of a tuple field no collection of its shape fills."""
    declared_as = shape(cls.model_fields[name].annotation)
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
    """Every route constructed symbolically, at startup; its validator refuses the program with
    every fault at once."""

    model_config = ConfigDict(frozen=True, strict=True, arbitrary_types_allowed=True)
    program: str
    classes: tuple[type[BaseModel], ...]
    constructions: tuple[Construction, ...]
    waiting: tuple[Waiting, ...]
    faulted: tuple[Fault, ...]

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
            *ambiguous(self),
            *certain(self),
            *undiscriminated(self),
            *undecided(self),
        ]
        if details:
            raise ValidationError.from_exception_data(self.program, details)
        return self


def unique(faults: Iterable[Fault]) -> list[Fault]:
    """The faults with each code and location once: a class two routes build is reported
    once."""
    found: dict[tuple[str, tuple[str, ...]], Fault] = {}
    for f in faults:
        found.setdefault((f.code, f.loc), f)
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


def computation(cls: type[BaseModel], name: str) -> Computation | None:
    """The computation a field declares in its annotation, if it is a computed one: a
    relation's ordering or a derivation's root."""
    return next(
        (found for found in cls.model_fields[name].metadata if isinstance(found, Computation)),
        None,
    )


def owned(cls: type[BaseModel], name: str) -> bool:
    """Whether a field is the kind's own computed one: a relation's ordering or a derivation's
    root."""
    return computation(cls, name) is not None


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
        for name, info in c.model_fields.items()
        if not owned(c, name)
        for member in (
            elements(info.annotation)
            if get_origin(info.annotation) is tuple
            else (info.annotation,)
        )
        for member in members(member)
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


def bounds(cls: type[BaseModel]) -> Interval:
    """A scalar's interval from the ``gt``, ``ge``, ``lt`` and ``le`` metadata on its root. A
    scalar over ``int`` has no value between two integers, so its strict bounds are the next
    integer's non-strict ones."""
    info = cls.model_fields.get("root")
    if info is None:
        return Interval()
    whole = info.annotation is int
    found = Interval()
    for meta in info.metadata:
        match meta:
            case Gt(gt=int() | float() | Decimal() as v):
                low = Decimal(str(v))
                found = found._replace(low=low + 1 if whole else low, low_strict=not whole)
            case Ge(ge=int() | float() | Decimal() as v):
                found = found._replace(low=Decimal(str(v)), low_strict=False)
            case Lt(lt=int() | float() | Decimal() as v):
                high = Decimal(str(v))
                found = found._replace(high=high - 1 if whole else high, high_strict=not whole)
            case Le(le=int() | float() | Decimal() as v):
                found = found._replace(high=Decimal(str(v)), high_strict=False)
            case _:
                pass
    return found


def hull(intervals: Iterable[Interval]) -> Interval:
    """The interval that covers every interval given: the least low and the greatest high,
    unbounded where any is."""
    found = list(intervals)
    if not found:
        return Interval()
    lows = [i.low for i in found]
    highs = [i.high for i in found]
    low = None if any(x is None for x in lows) else min(x for x in lows if x is not None)
    high = None if any(x is None for x in highs) else max(x for x in highs if x is not None)
    low_strict = low is not None and all(i.low_strict for i in found if i.low == low)
    high_strict = high is not None and all(i.high_strict for i in found if i.high == high)
    return Interval(low=low, low_strict=low_strict, high=high, high_strict=high_strict)


def interval(cls: type[BaseModel], seen: frozenset[type[BaseModel]] = PLACED) -> Interval:
    """What a numeric class can be: a constant is its default; a scalar is its bounds; a
    derivation is what its operation makes of its operands' intervals; anything else is
    unbounded."""
    root = cls.model_fields.get("root")
    if cls in seen or root is None:
        return Interval()
    if constant(cls):
        value = Decimal(str(root.default))
        return Interval(low=value, high=value)
    if is_scalar(cls):
        return bounds(cls)
    if isinstance(derived := computation(cls, "root"), Derived):
        operands = tuple(
            hull(interval(c, seen | {cls}) for c in classes_)
            for name in derived.operands
            for classes_ in ({**holds(cls), **collects(cls)}[name],)
        )
        return derived.interval(operands)
    return Interval()


def outcomes(left: Interval, right: Interval) -> frozenset[int]:
    """Which orderings two values can have, from what each can be: -1 when the first can be
    under the second, 0 when they can be equal, 1 when the first can be beyond the second."""
    found: set[int] = set()
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


def comparisons(cls: type[BaseModel]) -> list[tuple[Options, Options, frozenset[int]]]:
    """Each comparison a relation makes: the classes of its two operands and the orderings it
    admits, read from the ordering fields' metadata and annotations."""
    return [
        (
            holds(cls)[compared.left],
            holds(cls)[compared.right],
            frozenset(get_args(info.annotation)),
        )
        for name, info in cls.model_fields.items()
        if isinstance(compared := computation(cls, name), Comparison)
    ]


def never(cls: type[BaseModel]) -> Literal["holds", "refuses"] | None:
    """``"holds"`` when some comparison a relation makes admits no ordering its operands'
    intervals allow, ``"refuses"`` when every comparison admits every ordering they allow, and
    ``None`` otherwise, and for any class that is not a relation."""
    if not is_relation(cls):
        return None
    decided = True
    for left, right, admitted in comparisons(cls):
        possible = outcomes(hull(map(interval, left)), hull(map(interval, right)))
        if not possible & admitted:
            return "holds"
        decided = decided and possible <= admitted
    return "refuses" if decided else None


def certain(proof: Proof) -> list[InitErrorDetails]:
    """One ``never`` error per relation its operands' intervals make certain or impossible."""
    return [
        fault(
            "never",
            "{cls} never {what}, by the intervals of its operands",
            (c.__name__,),
            cls=c.__name__,
            what=what,
        )
        for c in proof.classes
        if (what := never(c)) is not None
    ]


def edges(cls: type[BaseModel]) -> list[Edge]:
    """A numeric class's interval as difference constraints against zero: ``x >= low`` is
    ``0 - x <= -low``, ``x <= high`` is ``x - 0 <= high``."""
    found = interval(cls)
    constraints: list[Edge] = []
    if found.low is not None:
        constraints.append((cls, ZERO, (-found.low, -1 if found.low_strict else 0)))
    if found.high is not None:
        constraints.append((ZERO, cls, (found.high, -1 if found.high_strict else 0)))
    return constraints


def constrained(cls: type[BaseModel]) -> list[Edge]:
    """A relation's comparisons as difference constraints between its operands, for the
    admitted sets that are one: under is ``value - bound < 0``, at most ``<= 0``, equal both ways,
    at least ``bound - value <= 0``, beyond ``< 0``; differs is none."""
    found: list[Edge] = []
    for lefts, rights, admitted in comparisons(cls):
        for left, right in product(lefts, rights):
            if admitted <= {-1, 0}:
                found.append((right, left, (Decimal(0), -1 if admitted == frozenset({-1}) else 0)))
            if admitted <= {0, 1}:
                found.append((left, right, (Decimal(0), -1 if admitted == frozenset({1}) else 0)))
    return found


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


def choices(
    cls: type[BaseModel], seen: frozenset[type[BaseModel]]
) -> list[frozenset[type[BaseModel]]]:
    """Every way a class can be present in a run, as the set of classes present with it: the
    class, and for each single field one of the classes it may hold, with their own choices in
    turn. A class already seen contributes nothing more."""
    if cls in seen:
        return [frozenset()]
    seen = seen | {cls}
    per_field = [
        [member for c in classes_ for member in choices(c, seen)]
        for classes_ in holds(cls).values()
        if classes_
    ]
    return [frozenset({cls}).union(*combination) for combination in product(*per_field)]


def contradicts(a: type[BaseModel], b: type[BaseModel]) -> bool:
    """Whether two relations make a comparison over the same two operands whose admitted
    orderings are disjoint, the second's negated when its operands are the first's reversed."""
    for lefts, rights, admitted in comparisons(a):
        for lefts_, rights_, admitted_ in comparisons(b):
            if (lefts, rights) == (lefts_, rights_) and not admitted & admitted_:
                return True
            if (lefts, rights) == (rights_, lefts_) and not admitted & {-o for o in admitted_}:
                return True
    return False


def counts(cls: type[BaseModel]) -> tuple[int, int | None]:
    """How many elements a selection admits: a fixed tuple's length twice, else its
    ``min_length`` and ``max_length``."""
    info = cls.model_fields["of"]
    if fixed(info.annotation):
        return len(get_args(info.annotation)), len(get_args(info.annotation))
    low, high = 0, None
    for meta in info.metadata:
        match meta:
            case MinLen(min_length=n):
                low = n
            case MaxLen(max_length=n):
                high = n
            case _:
                pass
    return low, high


def exclusive(a: type[BaseModel], b: type[BaseModel]) -> bool:
    """Whether two selections over the same elements admit disjoint counts."""
    if collects(a)["of"] != collects(b)["of"]:
        return False
    (low, high), (low_, high_) = counts(a), counts(b)
    return (high is not None and low_ > high) or (high_ is not None and low > high_)


def deciders(
    present: frozenset[type[BaseModel]],
    against: frozenset[type[BaseModel]],
    classes_: Iterable[type[BaseModel]],
) -> frozenset[type[BaseModel]]:
    """The classes among those present that cannot be present with those against: a record
    whose hearer hears one of them, a relation that contradicts one of them, a selection
    exclusive with one of them."""
    hearers_ = hearers(classes_)
    return frozenset(
        c
        for c in present
        for d in against
        if (
            (is_record(c) and is_record(d) and c is not d and hearers_.get(c) is hearers_.get(d))
            or (is_relation(c) and is_relation(d) and contradicts(c, d))
            or (is_selection(c) and is_selection(d) and exclusive(c, d))
        )
    )


def conflict(present: frozenset[type[BaseModel]], classes_: Iterable[type[BaseModel]]) -> bool:
    """Whether a set of classes cannot all be present in one run: two of them decide against
    each other, or their intervals and comparisons have no solution together."""
    if deciders(present, present, classes_):
        return True
    constraints = [e for c in present for e in edges(c)] + [
        e for c in present if is_relation(c) for e in constrained(c)
    ]
    return not feasible(constraints)


def coexist(a: type[BaseModel], b: type[BaseModel], classes_: Iterable[type[BaseModel]]) -> bool:
    """Whether two classes a field may hold are not proven exclusive: the same class is not;
    otherwise some choice of what each holds puts in one run no conflict."""
    if a is b:
        return True
    return any(
        not conflict(x | y, classes_) for x in choices(a, PLACED) for y in choices(b, PLACED)
    )


def unions(cls: type[BaseModel]) -> dict[str, Options]:
    """Each field of a class that holds a choice: a single field or a tuple field with more than
    one class; a fixed tuple's positions of one class are no choice."""
    return {
        name: distinct
        for name, classes_ in (*holds(cls).items(), *collects(cls).items())
        if len(distinct := tuple(dict.fromkeys(classes_))) > 1
    }


def ambiguous(proof: Proof) -> list[InitErrorDetails]:
    """One ``ambiguous`` error per union field two of whose members are not proven exclusive."""
    return [
        fault(
            "ambiguous",
            "{cls}.{name} holds {a} | {b}, and the proof cannot show that at most one holds;"
            " write members a record or a relation tells apart",
            (c.__name__, name),
            cls=c.__name__,
            name=name,
            a=a.__name__,
            b=b.__name__,
        )
        for c in proof.classes
        for name, classes_ in unions(c).items()
        for a, b in combinations(classes_, 2)
        if coexist(a, b, proof.classes)
    ]


def keys(cls: type[BaseModel], *, required: bool) -> frozenset[str]:
    """The names a record validates by: each field's alias, or its name."""
    return frozenset(
        str(info.validation_alias or info.alias or name)
        for name, info in cls.model_fields.items()
        if info.is_required() or not required
    )


def told_apart(a: type[BaseModel], b: type[BaseModel]) -> bool:
    """Whether two records cannot both construct from one payload: a field both declare as a
    ``Literal`` with no value in common, or a key one requires that the other does not
    declare."""
    for name in a.model_fields.keys() & b.model_fields.keys():
        first, second = a.model_fields[name].annotation, b.model_fields[name].annotation
        if (
            is_literal(first)
            and is_literal(second)
            and not (set(get_args(first)) & set(get_args(second)))
        ):
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


def closure(start: type[BaseModel]) -> frozenset[type[BaseModel]]:
    """Every class a class holds, singly or as elements, and so on: what must exist for it to."""
    found: set[type[BaseModel]] = set()
    todo = [start]
    while todo:
        cls = todo.pop()
        if cls in found:
            continue
        found.add(cls)
        todo.extend(
            c for classes_ in (*holds(cls).values(), *collects(cls).values()) for c in classes_
        )
    return frozenset(found)


def undecided(proof: Proof) -> list[InitErrorDetails]:
    """One ``undecided`` error per action that one member of a choice leads to and another does
    not, whose premises hold nothing that decides between them: it would be performed whichever
    held."""
    details: list[InitErrorDetails] = []
    for c in proof.classes:
        for name, classes_ in unions(c).items():
            for a, b in combinations(classes_, 2):
                if coexist(a, b, proof.classes):
                    continue
                for chosen_, other in ((a, b), (b, a)):
                    reach, reach_ = proof.reached(chosen_), proof.reached(other)
                    settles = deciders(
                        PLACED.union(*choices(chosen_, PLACED)),
                        PLACED.union(*choices(other, PLACED)),
                        proof.classes,
                    )
                    details += [
                        fault(
                            "undecided",
                            "{action} is performed when {cls}.{name} holds {chosen} and not when it"
                            " holds {other}, yet holds nothing that decides between them",
                            (action.__name__,),
                            action=action.__name__,
                            cls=c.__name__,
                            name=name,
                            chosen=chosen_.__name__,
                            other=other.__name__,
                        )
                        for action in proof.classes
                        if is_action(action)
                        and action in reach
                        and action not in reach_
                        and not closure(action) & settles
                    ]
    return details


def proven(program: ModuleType) -> Proof:
    """The proof of a program: every route constructed symbolically from its own request, the
    deployment and the constants, as a ``Proof``, whose validator refuses the program with
    every fault at once."""
    classes_ = models(program)
    found = [symbolic(r, classes_) for r in classes_ if is_route(r)]
    return Proof(
        program=program.__name__,
        classes=classes_,
        constructions=tuple(c for s in found for c in s.constructions),
        waiting=tuple(w for s in found for w in s.waiting),
        faulted=tuple(f for s in found for f in s.faulted),
    )


def connections(deployment: Config) -> tuple[Connection, ...]:
    """Every connection a config holds, in field order."""
    return tuple(
        value
        for value in (getattr(deployment, name) for name in type(deployment).model_fields)
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
    """A construction's instance in a scope, with the concrete paths of what supplied it."""

    instance: BaseModel
    provenance: Provenance


class Refuted(NamedTuple):
    """A refutable kind whose declared condition the evidence rejected in a scope: Pydantic's
    refusal, every error of which is ``REFUTED``, and the concrete paths of the operands it was
    constructed from."""

    refusal: ValidationError
    provenance: Provenance


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
    declared = member if origin is None else (*origin.site, HEARD, *member)
    scope.arrived[origin, member] = instance
    for name, info in type(instance).model_fields.items():
        value: object = getattr(instance, name)
        if isinstance(value, BaseModel):
            arrived(value, origin, (*member, name), scope)
        elif is_elements(value):
            opened_: list[Scope] = []
            for index, element in enumerate(value):
                if isinstance(element, BaseModel):
                    step = position(info.annotation, index)
                    child = Scope(
                        (*declared, name, step), (*scope.at(declared), name, f"[{index}]"), scope
                    )
                    scope.children.append(child)
                    arrived(element, origin, (*member, name, step), child)
                    opened_.append(child)
            scope.collections[origin, (*member, name)] = tuple(opened_)


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


class Available(NamedTuple):
    """A reference dereferenced to evidence: the instance, at its concrete path."""

    path: Site
    instance: BaseModel


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
    is, else held by the chain under the action, or the action heard otherwise."""
    match ref:
        case InputRef():
            holder = scope.holding(ref.key)
            path = (holder or scope.within(ref.scope)).at(ref.site)
            found = None if holder is None else holder.arrived[ref.key]
            return Available(path, found) if is_exactly(found, ref.cls) else Absent(path, found)
        case ConstructedRef():
            occurrence = Occurrence(scope.within(ref.scope), ref.construction)
            made = occurrence.made
            if isinstance(made, Constructed):
                return Available(occurrence.path, made.instance)
            if isinstance(made, Refuted):
                return Rejected(occurrence, made)
            return Pending(occurrence)
        case HeardRef():
            occurrence = Occurrence(scope.within(ref.scope), ref.action)
            if occurrence.made is None:
                return Pending(occurrence)
            holder = scope.holding(ref.key)
            found = None if holder is None else holder.arrived[ref.key]
            return (
                Available(holder.at(ref.site), found)
                if holder is not None and is_exactly(found, ref.cls)
                else Heard(occurrence, occurrence.scope.arrived.get((ref.action, ())))
            )


def is_exactly(found: BaseModel | None, cls: type[BaseModel]) -> TypeIs[BaseModel]:
    """Whether what a scope holds is an instance of the referenced class itself: two
    alternatives share a site, and the one that arrived is the one whose class the reference
    names."""
    return type(found) is cls


type Premise = tuple[str, int | None]
"""One premise of a construction: a single field, or one element of a tuple field by its
index."""


class Bound(NamedTuple):
    """The transient result of dereferencing a construction's references in a scope: the
    instance at each premise that is filled, with the concrete path of what supplied it, and
    for each premise not filled the scope it is dereferenced from, the element's for an
    element, and its references."""

    given: Given
    provenance: Provenance
    unfilled: dict[Premise, tuple[Scope, tuple[Ref, ...]]]


def present(found: list[Available], cls: type[BaseModel], name: str) -> Available | None:
    """The one instance found for a field; ``None`` for none; a failure for more than one, which
    the proof excludes and the run refuses to choose among."""
    if len(found) > 1:
        raise ValidationError.from_exception_data(
            cls.__name__,
            [
                fault(
                    "ambiguous",
                    "{cls}.{name} found {n} instances where the proof bound one",
                    (cls.__name__, name),
                    cls=cls.__name__,
                    name=name,
                    n=len(found),
                )
            ],
        )
    return found[0] if found else None


def available(refs: Iterable[Ref], scope: Scope) -> list[Available]:
    """The references among several that dereference to evidence from a scope."""
    return [found for r in refs if isinstance(found := resolve(r, scope), Available)]


def bound(construction: Construction, scope: Scope) -> Bound:
    """A construction's references dereferenced in a scope: the instance at each single field's
    reference, and for each tuple field every element scope's instance at the element
    references placed in that element's scope, its position's for a fixed tuple, in element
    order; the references of each premise nothing fills."""
    given: Given = {}
    provenance: Provenance = {}
    unfilled: dict[Premise, tuple[Scope, tuple[Ref, ...]]] = {}
    cls = construction.cls
    for name, refs in construction.premises.items():
        found = present(available(refs, scope), cls, name)
        if found is None:
            unfilled[name, None] = (scope, refs)
        else:
            provenance[name], given[name] = (found.path,), found.instance
    for name, collected in construction.collections.items():
        elements = scope.collection(collected.key)
        if elements is None:
            unfilled[name, None] = (scope, (collected.holder,))
            continue
        picked: list[Available] = []
        for index, element in enumerate(elements):
            refs = tuple(r for r in collected.elements if r.scope == element.site)
            found = present(available(refs, element), cls, name)
            if found is None:
                unfilled[name, index] = (element, refs)
            else:
                picked.append(found)
        if len(picked) == len(elements):
            provenance[name] = tuple(f.path for f in picked)
            given[name] = tuple(f.instance for f in picked)
    return Bound(given, provenance, unfilled)


def supplied(occurrence: Occurrence) -> Bound | None:
    """What a scope supplies for a construction when every premise is filled, with a fresh
    instance for each fresh field; ``None`` while any is not, so the class is asked again next
    pass."""
    found = bound(occurrence.construction, occurrence.scope)
    if found.unfilled:
        return None
    for name, cls in occurrence.construction.freshly.items():
        found.provenance[name], found.given[name] = ((*occurrence.path, name),), cls()
    return found


def construct(occurrence: Occurrence, given: Given) -> BaseModel | ValidationError:
    """Ask Pydantic for an occurrence with what its scope supplied: the instance, or the refusal
    a refutable kind owns as its declared condition not holding, which says only that it does
    not hold here; any other refusal is a failure and propagates as Pydantic raised it, noted
    with the occurrence's concrete path, as a party's exception is."""
    cls = occurrence.construction.cls
    try:
        return cls.model_validate(given)
    except ValidationError as refusal:
        if issubclass(cls, Refutable) and cls.refuted(refusal):
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


def causes(
    occurrence: Occurrence, blocked: Mapping[Occurrence, tuple[Cause, ...]]
) -> tuple[Cause, ...]:
    """Why an occurrence can never construct, from its own references dereferenced in the
    observed state: for each premise nothing fills, every reference is a cause, a rejected
    condition or an absent source, or a pending occurrence already blocked, whose causes it
    inherits; a premise with a pending occurrence not blocked may still fill, and is no
    cause. Empty while no premise is blocked."""
    found: list[Cause] = []
    for premise, (at, refs) in bound(occurrence.construction, occurrence.scope).unfilled.items():
        here: list[Cause] = []
        for ref in refs:
            match resolve(ref, at):
                case Pending(pending):
                    if pending not in blocked:
                        break
                    here.extend(blocked[pending])
                case Rejected(rejected, refuted):
                    here.append(Refutation(rejected, refuted))
                case Absent() | Heard() as state:
                    here.append(Unfilled(occurrence, premise, ref, state))
                case Available():
                    break
        else:
            found.extend(here)
    return tuple(found)


def waits_on(
    occurrence: Occurrence, blocked: Mapping[Occurrence, tuple[Cause, ...]]
) -> list[Occurrence]:
    """The pending occurrences, not blocked, that an occurrence's unfilled premises dereference
    to: what it still waits for."""
    return [
        pending.occurrence
        for at, refs in bound(occurrence.construction, occurrence.scope).unfilled.values()
        for ref in refs
        if isinstance(pending := resolve(ref, at), Pending) and pending.occurrence not in blocked
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
    own references dereferenced in the observed state: an occurrence a premise of which no
    reference can fill is blocked, and so is every occurrence waiting on it, until nothing
    moves. The route blocked is the structured refusal, as a value. The route not blocked waits
    on occurrences that wait on one another, which no evidence explains: a failure, raised,
    naming each in order of reach and what it waits for."""
    root = goal.scope
    pending = [
        occurrence
        for scope in scopes(root)
        for c in constructions
        if c.scope == scope.site and (occurrence := Occurrence(scope, c)).made is None
    ]
    blocked: dict[Occurrence, tuple[Cause, ...]] = {}
    moved = True
    while moved:
        moved = False
        for occurrence in pending:
            if occurrence not in blocked and (found := causes(occurrence, blocked)):
                blocked[occurrence] = found
                moved = True
    if goal in blocked:
        return Blocked(goal, passes, blocked[goal])
    reach = [goal]
    for occurrence in reach:
        reach.extend(o for o in waits_on(occurrence, blocked) if o not in reach)
    details = [
        fault(
            "deadlock",
            "{cls} at {path} waits for {on}, and nothing constructs",
            (occurrence.construction.cls.__name__,),
            cls=occurrence.construction.cls.__name__,
            path=".".join(occurrence.path),
            on=", ".join(
                f"{o.construction.cls.__name__} at {'.'.join(o.path)}"
                for o in waits_on(occurrence, blocked)
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


async def performed_in_span(
    occurrence: Occurrence, action: Action[Connection, Record], pass_: int
) -> Record:
    """Perform one action occurrence inside a span named for its class, carrying the party's
    class name, the occurrence's concrete path, the pass it was built in, and ``tca.outcome``,
    which is the outcome its task has: ``heard``, once what the party said validated as the
    action's record, with the record's class name and path; ``failed``, the client's exception
    or the refusal of what it returned, noted with the path and propagating, the span's status
    set to error by the API; ``cancelled``, which is not the action's error and leaves the
    status unset."""
    attributes = {
        "tca.party": type(action.party).__name__,
        "tca.site": ".".join(occurrence.path),
        "tca.pass": pass_,
    }
    with tracer.start_as_current_span(type(action).__name__, attributes=attributes) as span:
        try:
            record = hear(action, await action.perform())
        except CancelledError:
            span.set_attribute("tca.outcome", "cancelled")
            raise
        except Exception as failure:
            span.set_attribute("tca.outcome", "failed")
            failure.add_note(f"at {'.'.join(occurrence.path)}")
            raise
        span.set_attribute("tca.outcome", "heard")
        span.set_attribute("tca.record", type(record).__name__)
        span.set_attribute("tca.heard", ".".join((*occurrence.path, HEARD)))
        return record


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
    any other, the span's status set to error by the API; ``cancelled``, from outside, which
    is no error of the run and leaves the status unset. Each record that entered a scope after
    its pass is one ``admitted`` event on the span, with the record's class and path: an action
    heard in a pass another action failed leaves none."""
    with tracer.start_as_current_span(
        route.__name__, attributes={"tca.request": type(request).__name__}
    ) as span:
        try:
            found = await constructed(route, request, deployment, proof, span)
        except CancelledError:
            span.set_attribute("tca.outcome", "cancelled")
            raise
        except Exception:
            span.set_attribute("tca.outcome", "failed")
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
    other refusal is a failure and propagates. The pass's actions are performed together in one
    task group, across every scope, each heard at the one boundary, and each record enters the
    scope its action was built in once every action of the pass was heard, as one ``admitted``
    event on the route's span; a library kind's exception, or a refusal of what it returned,
    cancels the group's other actions and propagates in an ``ExceptionGroup``, noted with the
    paths of the actions cancelled with it. An action's effect may have happened whenever its
    task started: one heard returned a validated record, one failed or cancelled may have had
    its effect and returned none, and no record of the pass is admitted, which the group's note
    says. A pass that constructs nothing ends the run as ``ended`` reads it."""
    constructions = proof.constructs(route)
    root = Scope((), (), None)
    arrived(request, None, REQUEST, root)
    arrived(deployment, None, DEPLOYMENT, root)
    for c in proof.constants:
        root.arrived[None, (c.__name__,)] = c()
    goal = Occurrence(root, goal_of(route, constructions))
    passes = 0
    while goal.made is None:
        passes += 1
        performed: list[tuple[Occurrence, Action[Connection, Record]]] = []
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
                    scope.made[construction] = Refuted(instance, found.provenance)
                    continue
                built = True
                scope.made[construction] = Constructed(instance, found.provenance)
                if is_performed(instance):
                    performed.append((occurrence, instance))
        tasks: list[Task[Record]] = []
        try:
            async with TaskGroup() as group:
                tasks = [group.create_task(performed_in_span(o, a, passes)) for o, a in performed]
        except BaseExceptionGroup as failed:
            failed.add_note(outcomes_of([o for o, _ in performed], tasks))
            raise
        for (o, _), task in zip(performed, tasks, strict=True):
            record = task.result()
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
