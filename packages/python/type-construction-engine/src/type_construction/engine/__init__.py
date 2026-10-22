"""The engine: reads a program's classes, proves them, and answers a route by construction.

A program is one module, named by the entry-point group ``type_construction.programs``.
``routes`` and ``config`` read its ``Route`` and ``Config`` subclasses; ``asked`` reads a
route's request class from its ``request`` field; ``heard`` reads the record classes an
action declares as ``Action[P, T]``, one or the members of a union.

A class is a proposition and its fields are the hypotheses; an instance is a proof. A run is
the instances of one answer, keyed by class, one per class, seeded with the request, the
scalars and values it carries, and the deployment's connections. A pass visits every class of
the route not yet in the run and asks Pydantic for it from the instances its fields name:
``cls.model_validate(supplied)``. Pydantic answers one of three ways. The class constructs:
the instance enters the run, each computed field's value enters under its own class, and an
action is performed with the pass's other actions in one task group, its record and what the
record carries entering under their classes. The class refuses with ``missing`` only, or a
relation or a selection refuses with ``relation``: it does not exist yet, and the next pass
asks again. The class refuses otherwise: the refusal propagates. The run ends when the route
constructs, which needs the reply, which needs its fact; a pass that constructs nothing ends
it with a ``ValidationError`` naming each relation that did not hold and each field no class
fills, in the run each was asked from. A union field takes the one member that exists.

A request or a record that holds ``tuple[E, ...]`` fans out: each ``E`` gets a child run that
sees the parent's instances and its own element with what it carries. Which run a class
belongs to is read from its fields: a class descends from the element its hypotheses mention,
through the classes its fields name, the action that hears a record, the carrier that holds a
scalar, and the computed field that produces a class. A class that descends from nothing is
asked for in the parent; one that descends from ``E`` is asked for in each child of an ``E``;
a ``tuple[X, ...]`` field collects every such child's ``X`` in element order once the
carrier of ``E`` is in the run, and is the empty tuple when it fanned out to nothing. The
engine keeps nothing about a program; every question is a read of ``model_fields``, the
generic parameters, and the error types Pydantic reports.

``prove`` is the same passes over classes, at startup: a class joins when every required
field names a class that has joined. ``proven`` checks that every declared class joins some
route and is named by some field, that each record has one hearer, each produced or carried
class one source and each party one config field, that a route exists once per run and a
collection collects what exists per element, that no relation is one its operands' bounds make
certain or impossible, and that no union holds two members that could both hold; otherwise it
raises one ``ValidationError`` naming every fault. Whether two facts can both hold, and
whether a relation can ever hold or ever refuse, is decided exactly: every scalar class is one
variable, every scalar's bounds and every relation kind's declared ``constraints`` are
difference constraints over them, and a system is feasible when it has no negative cycle. A
relation kind that declares no constraints cannot be decided, and the program is refused.

``opened`` opens each connection once and closes each once around whatever a server kind runs
inside it, closing what it opened when a later open raises. Every answer is one OpenTelemetry
span named for the route, with one child per performed action named for the action and
carrying the party's and the record's class names; the engine depends on
``opentelemetry-api`` only.
"""

from asyncio import TaskGroup
from collections import ChainMap, Counter
from collections.abc import AsyncGenerator, Container, Iterable, Iterator, MutableMapping
from contextlib import asynccontextmanager
from decimal import Decimal
from functools import cache
from itertools import product
from types import ModuleType, UnionType
from typing import LiteralString, TypeIs, Union, get_args, get_origin

from annotated_types import Ge, Gt, Le, Lt
from opentelemetry import trace
from pydantic import BaseModel, RootModel, TypeAdapter, ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError

from type_construction.world import (
    Action,
    Config,
    Connection,
    Fact,
    Record,
    Relation,
    Reply,
    Request,
    Route,
    Selection,
    Value,
)

__all__ = ["answer", "asked", "config", "hear", "opened", "prove", "proven", "routes"]

type Run = MutableMapping[type[BaseModel], BaseModel]
"""The instances of one run, keyed by class; a child run chains its element over its parent."""

type Options = tuple[type[BaseModel], ...]
"""The classes a field may hold: a union's members, else the one class."""

type Proof = frozenset[type[BaseModel]]
"""The classes a route constructs: those that join, pass by pass, from its request."""

type Weight = tuple[Decimal, int]
"""The weight of a difference constraint ``x - y <= c``: ``c`` and ``-1`` when strict, else
``0``, so that a cycle whose weights sum below ``(0, 0)`` is a contradiction."""

type Edge = tuple[object, object, Weight]
"""One difference constraint ``x - y <= c`` as the edge ``(y, x, weight)``; a variable is a
scalar or derived class, and ``ZERO`` stands for the constant zero."""

ZERO = object()
"""The variable whose value is zero, which a scalar's bounds are constraints against."""

tracer = trace.get_tracer("type_construction.engine")
"""Spans named by the program's classes: one per answer, named for the route, with one child per
performed action, named for the action. Attributes are class names and counts, never contents.
With no SDK configured these are no-ops; the deployment supplies the SDK and the exporter."""


def is_route(cls: type[object]) -> TypeIs[type[Route[Request, Reply[Fact]]]]:
    """Whether a class is a program's route: a strict subclass of ``Route``."""
    return issubclass(cls, Route) and cls is not Route


def is_request(cls: object) -> TypeIs[type[Request]]:
    """Whether an annotation is a program's request class."""
    return isinstance(cls, type) and issubclass(cls, Request) and cls is not Request


def is_record(cls: object) -> TypeIs[type[Record]]:
    """Whether an annotation is a program's record class."""
    return isinstance(cls, type) and issubclass(cls, Record) and cls is not Record


def is_model(cls: object) -> TypeIs[type[BaseModel]]:
    """Whether an annotation is a Pydantic class."""
    return isinstance(cls, type) and issubclass(cls, BaseModel)


def is_scalar(cls: object) -> TypeIs[type[RootModel[object]]]:
    """Whether an annotation is a class over one root value."""
    return isinstance(cls, type) and issubclass(cls, RootModel)


def is_value(cls: object) -> TypeIs[type[Value]]:
    """Whether an annotation is a program's composite part."""
    return isinstance(cls, type) and issubclass(cls, Value) and cls is not Value


def is_relation(cls: object) -> TypeIs[type[Relation]]:
    """Whether a class is a relation: a strict subclass of ``Relation``."""
    return isinstance(cls, type) and issubclass(cls, Relation) and cls is not Relation


def is_selection(cls: object) -> TypeIs[type[Selection[BaseModel]]]:
    """Whether a class is a selection: a strict subclass of ``Selection``."""
    return isinstance(cls, type) and issubclass(cls, Selection) and cls is not Selection


def is_built(
    cls: type[BaseModel],
) -> TypeIs[
    type[Fact]
    | type[Value]
    | type[Action[Connection, Record]]
    | type[Reply[Fact]]
    | type[Route[Request, Reply[Fact]]]
]:
    """Whether the run constructs a class from the instances its fields name."""
    return issubclass(cls, (Fact, Value, Action, Reply, Route))


def is_action(cls: type[BaseModel]) -> TypeIs[type[Action[Connection, Record]]]:
    """Whether a class is a program's action: a strict subclass of ``Action``."""
    return issubclass(cls, Action) and cls is not Action


def is_performed(instance: BaseModel) -> TypeIs[Action[Connection, Record]]:
    """Whether a constructed instance is an action the engine performs."""
    return isinstance(instance, Action)


def carries(cls: type[BaseModel]) -> bool:
    """Whether a class brings what its fields hold into the run: what arrives, what a party
    says, and a composite part."""
    return issubclass(cls, (Request, Record, Value))


def declared(cls: type[object]) -> bool:
    """Whether a class is one the program wrote: not a parametrization Pydantic registered in
    the module, as ``Says[Catalog, Price]`` beside ``Quote``, and not a library kind whose
    parameters are still open, as ``Says`` itself."""
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


def models(program: ModuleType) -> list[type[BaseModel]]:
    """Every Pydantic class the program module declares, in definition order."""
    return [c for c in classes(program) if is_model(c)]


def routes(program: ModuleType) -> tuple[type[Route[Request, Reply[Fact]]], ...]:
    """Every ``Route`` subclass the program module declares, in definition order."""
    return tuple(c for c in classes(program) if is_route(c))


def config(program: ModuleType) -> type[Config]:
    """The one ``Config`` subclass the program module declares."""
    return next(c for c in classes(program) if issubclass(c, Config) and c is not Config)


def built(program: ModuleType) -> list[type[BaseModel]]:
    """Every class the run constructs, in definition order."""
    return [c for c in models(program) if is_built(c)]


def carriers(program: ModuleType) -> list[type[BaseModel]]:
    """Every class the program declares that carries scalars and values into the run."""
    return [c for c in models(program) if carries(c)]


def members(annotation: object) -> tuple[object, ...]:
    """A union's members, or the one annotation."""
    return get_args(annotation) if get_origin(annotation) in (UnionType, Union) else (annotation,)


def options(annotation: object) -> Options:
    """The classes an annotation may hold."""
    return tuple(m for m in members(annotation) if is_model(m))


def held(cls: type[BaseModel]) -> dict[str, Options]:
    """Each single-valued field and the classes that may fill it."""
    return {
        name: options(field.annotation)
        for name, field in cls.model_fields.items()
        if get_origin(field.annotation) is not tuple
    }


def collected(cls: type[BaseModel]) -> dict[str, Options]:
    """Each ``tuple[X, ...]`` field and the classes an element may be."""
    return {
        name: options(get_args(field.annotation)[0])
        for name, field in cls.model_fields.items()
        if get_origin(field.annotation) is tuple
    }


def produced(cls: type[BaseModel]) -> dict[str, Options]:
    """Each computed field whose return type names classes, and those classes."""
    found = {
        name: options(computed.return_type) for name, computed in cls.model_computed_fields.items()
    }
    return {name: classes_ for name, classes_ in found.items() if classes_}


def carried(cls: type[BaseModel]) -> frozenset[type[BaseModel]]:
    """The scalars and values a carrying class's single fields hold, and what those values
    carry in turn; nothing for a class that does not carry."""
    none = frozenset[type[BaseModel]]()
    if not carries(cls):
        return none
    direct = frozenset(
        c for classes_ in held(cls).values() for c in classes_ if is_scalar(c) or is_value(c)
    )
    return direct.union(*(carried(c) for c in direct))


def carried_by(instance: BaseModel) -> dict[type[BaseModel], BaseModel]:
    """The scalar and value instances a carrying instance holds, keyed by class, and what
    those values carry in turn."""
    if not carries(type(instance)):
        return {}
    direct: dict[type[BaseModel], BaseModel] = {
        type(value): value
        for name, classes_ in held(type(instance)).items()
        if any(is_scalar(c) or is_value(c) for c in classes_)
        and isinstance(value := getattr(instance, name), BaseModel)
    }
    return direct | {k: v for value in direct.values() for k, v in carried_by(value).items()}


def unmet(
    cls: type[BaseModel],
    have: Container[type[BaseModel]],
    gathered: Container[type[BaseModel]] | None,
) -> dict[str, Options]:
    """Each required field of a class that no present class fills: a single field from what the
    run has, a ``tuple[X, ...]`` field from what the run and its children have; with ``gathered``
    ``None``, single fields only, since a collecting field waits on its children and a fault is
    theirs."""
    singles = {
        name: classes_
        for name, classes_ in held(cls).items()
        if cls.model_fields[name].is_required() and not any(c in have for c in classes_)
    }
    tuples = {
        name: classes_
        for name, classes_ in collected(cls).items()
        if gathered is not None
        and cls.model_fields[name].is_required()
        and not any(c in gathered for c in classes_)
    }
    return singles | tuples


def asked[Q: Request, A: Reply[Fact]](route: type[Route[Q, A]]) -> type[Request]:
    """The request class a route declares as ``Route[Q, A]``: the class of its ``request``."""
    (request,) = (m for m in members(route.model_fields["request"].annotation) if is_request(m))
    return request


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


def hear[P: Connection, T: Record](action: Action[P, T], text: str) -> T:
    """The record an action hears, validated strictly from the party's JSON text as the ``T``
    the action declares, so a union chooses its member; what a library kind's ``perform``
    returns."""
    validated = TypeAdapter[Record](said(type(action))).validate_json(text, strict=True)
    (record,) = (r for r in (validated,) if hears(r, action))
    return record


def hearers(program: ModuleType) -> dict[type[BaseModel], type[BaseModel]]:
    """Each record class and the action that hears it; the proof refuses a second hearer."""
    return {r: a for a in built(program) if is_action(a) for r in heard(a)}


def brought(cls: type[BaseModel]) -> frozenset[type[BaseModel]]:
    """The classes that exist in the same run once a class does: itself, what its computed
    fields produce, what it carries, and the records its action hears."""
    none = frozenset[type[BaseModel]]()
    produced_ = frozenset(c for classes_ in produced(cls).values() for c in classes_)
    heard_ = none.union(*(brought(r) for r in heard(cls))) if is_action(cls) else none
    return frozenset((cls,)) | produced_ | carried(cls) | heard_


def elements(cls: type[BaseModel]) -> frozenset[type[BaseModel]]:
    """The classes that exist once per element when a class does: those a request or a record
    holds as ``tuple[E, ...]``, each in a child run of its own, with what each carries; for an
    action, those the records it hears hold."""
    none = frozenset[type[BaseModel]]()
    direct = (
        frozenset(c for classes_ in collected(cls).values() for c in classes_)
        if issubclass(cls, (Request, Record))
        else none
    )
    heard_ = none.union(*(elements(r) for r in heard(cls))) if is_action(cls) else none
    return direct.union(*(carried(e) for e in direct)) | heard_


def element_classes(program: ModuleType) -> frozenset[type[BaseModel]]:
    """The classes a request or a record of the program holds as ``tuple[E, ...]``: the
    elements, each the hypothesis a child run introduces."""
    return frozenset(
        c
        for carrier in carriers(program)
        if issubclass(carrier, (Request, Record))
        for classes_ in collected(carrier).values()
        for c in classes_
    )


def descends(cls: type[BaseModel], program: ModuleType) -> frozenset[type[BaseModel]]:
    """The element classes a class descends from: the hypotheses its proposition mentions,
    read through the classes its single fields name, the action that hears a record, the
    carrier that holds a scalar or value, and the computed field that produces a class, until
    an element is reached. Empty for a class that exists once per run. A class that reaches two
    elements would exist per element of two things at once, and the proof refuses it."""
    found = set[type[BaseModel]]()
    seen = set[type[BaseModel]]()
    todo = [cls]
    while todo:
        c = todo.pop()
        if c in seen:
            continue
        seen.add(c)
        if c in element_classes(program):
            found.add(c)
            continue
        todo.extend(s for classes_ in held(c).values() for s in classes_)
        for other in models(program):
            if is_action(other) and c in heard(other):
                todo.append(other)
            if carries(other) and any(c in classes_ for classes_ in held(other).values()):
                todo.append(other)
            if any(c in classes_ for classes_ in produced(other).values()):
                todo.append(other)
    return frozenset(found)


def element_of(cls: type[BaseModel], program: ModuleType) -> type[BaseModel] | None:
    """The one element class a class descends from, or ``None`` for a class that exists once
    per run."""
    return next(iter(descends(cls, program)), None)


def fault(
    code: LiteralString, message: LiteralString, loc: tuple[str, ...], **context: str | int
) -> InitErrorDetails:
    """One error of a ``ValidationError`` the engine raises: its type, its message template,
    the context the template reads, and the location, whose first element is the class."""
    return InitErrorDetails(type=PydanticCustomError(code, message, context), loc=loc, input=loc[0])


def unfilled(
    pending: Iterable[type[BaseModel]],
    have: Container[type[BaseModel]],
    gathered: Container[type[BaseModel]] | None,
) -> list[InitErrorDetails]:
    """One ``missing`` error per required field of a pending class that no present class fills
    and no pending class would bring, at ``(class, field)``: the root faults, not what follows
    from them; ``gathered`` as for ``unmet``."""
    pending = list(pending)
    blocked = frozenset[type[BaseModel]]().union(*(brought(c) | elements(c) for c in pending))
    return [
        fault(
            "missing",
            "no class fills {cls}.{name}, which holds {holds}",
            (cls.__name__, name),
            cls=cls.__name__,
            name=name,
            holds=" | ".join(c.__name__ for c in classes_),
        )
        for cls in pending
        for name, classes_ in unmet(cls, have, gathered).items()
        if not any(c in blocked for c in classes_)
    ]


def faults(
    pending: Iterable[type[BaseModel]], have: Container[type[BaseModel]]
) -> list[InitErrorDetails]:
    """The root faults among pending classes, and one ``cycle`` error per pending class that no
    root fault explains: one whose every unfilled field names a class that only another
    unexplained pending class would bring."""
    pending = list(pending)
    details = unfilled(pending, have, have)
    rooted = {loc[0] for d in details if (loc := d.get("loc"))}
    explained = {c for c in pending if c.__name__ in rooted}
    while True:
        brings = frozenset[type[BaseModel]]().union(*(brought(c) | elements(c) for c in explained))
        more = {
            c
            for c in pending
            if c not in explained
            and any(x in brings for classes_ in unmet(c, have, have).values() for x in classes_)
        }
        if not more:
            break
        explained |= more
    return [
        *details,
        *(
            fault("cycle", "{cls} holds a class that holds it", (c.__name__,), cls=c.__name__)
            for c in pending
            if c not in explained
        ),
    ]


@cache
def prove[Q: Request, A: Reply[Fact]](route: type[Route[Q, A]], program: ModuleType) -> Proof:
    """The classes a route constructs: those that join, pass by pass, from its request, what
    the request carries and holds as elements, and the deployment's connections; read once
    per route.

    A class joins when every required field names a class that has joined, anywhere; an
    action's records, a computed field's return classes, a carrier's scalars and values, and a
    request's or record's elements join with their class. The passes stop when none of the
    classes left can join."""
    request = asked(route)
    joined = brought(request) | elements(request)
    for field in config(program).model_fields.values():
        for connection in options(field.annotation):
            joined |= brought(connection)
    pending = built(program)
    while pending:
        ready = [c for c in pending if not unmet(c, joined, joined)]
        if not ready:
            break
        joined = joined.union(*(brought(c) | elements(c) for c in ready))
        pending = [c for c in pending if c not in ready]
    return joined


def named(program: ModuleType) -> frozenset[type[BaseModel]]:
    """Every class some field of some declared class names, singly, as an element, or as what
    a computed field produces."""
    return frozenset(
        c
        for cls in models(program)
        for classes_ in (*held(cls).values(), *collected(cls).values(), *produced(cls).values())
        for c in classes_
    )


def used(cls: type[BaseModel], program: ModuleType) -> bool:
    """Whether a class is used: some field names it or a subclass of it; for a carrier, some
    field names what it carries; for an action, some field names what a record it hears
    brings. A route is the root of its own proof and the config is the deployment's; both are
    used by being."""
    if is_route(cls) or issubclass(cls, Config):
        return True
    if any(issubclass(n, cls) for n in named(program)):
        return True
    if is_action(cls):
        return any(used(r, program) for r in heard(cls))
    return carries(cls) and any(used(c, program) for c in carried(cls))


def interval(cls: type[BaseModel]) -> list[Edge]:
    """A scalar's ``gt``, ``ge``, ``lt`` and ``le`` constraints as difference constraints
    against zero: ``x > 5`` is ``0 - x < -5``, ``x <= 7`` is ``x - 0 <= 7``. A scalar over
    ``int`` has no value between two integers, so its strict bounds are the next integer's
    non-strict ones. A class with no numeric bound, a derived value among them, is
    unbounded."""
    field = cls.model_fields.get("root")
    whole = field is not None and field.annotation is int
    edges: list[Edge] = []
    for meta in field.metadata if field is not None else []:
        match meta:
            case Gt(gt=int() | float() | Decimal() as v):
                low = Decimal(str(v))
                edges.append((cls, ZERO, (-(low + 1), 0) if whole else (-low, -1)))
            case Ge(ge=int() | float() | Decimal() as v):
                edges.append((cls, ZERO, (-Decimal(str(v)), 0)))
            case Lt(lt=int() | float() | Decimal() as v):
                high = Decimal(str(v))
                edges.append((ZERO, cls, (high - 1, 0) if whole else (high, -1)))
            case Le(le=int() | float() | Decimal() as v):
                edges.append((ZERO, cls, (Decimal(str(v)), 0)))
            case _:
                pass
    return edges


def operand(cls: type[BaseModel], name: str) -> type[BaseModel]:
    """The one class a relation's operand field holds."""
    (found,) = held(cls)[name]
    return found


def constrained(cls: type[Relation]) -> list[Edge]:
    """A relation's declared constraints as difference constraints between its operands'
    variables: ``less - than <= by`` is the edge from ``than`` to ``less``."""
    return [
        (operand(cls, c.than), operand(cls, c.less), (c.by, -1 if c.strict else 0))
        for c in cls.constraints
    ]


def negated(edge: Edge) -> Edge:
    """The negation of one difference constraint: ``x - y <= c`` is false exactly when
    ``y - x < -c``, and ``x - y < c`` exactly when ``y - x <= -c``."""
    y, x, (c, strict) = edge
    return (x, y, (-c, -1 - strict))


def feasible(edges: Iterable[Edge]) -> bool:
    """Whether a system of difference constraints has a solution: Bellman-Ford over its
    variables from a common origin finds no cycle whose weights sum below zero, where a strict
    constraint on a zero-weight cycle counts below zero."""
    edges = list(edges)
    nodes = {n for y, x, _ in edges for n in (y, x)}
    distance: dict[object, Weight] = dict.fromkeys(nodes, (Decimal(0), 0))
    for _ in range(len(nodes) + 1):
        changed = False
        for y, x, (c, s) in edges:
            candidate = (distance[y][0] + c, distance[y][1] + s)
            if candidate < distance[x]:
                distance[x] = candidate
                changed = True
        if not changed:
            return True
    return False


def variables(classes_: Iterable[type[BaseModel]]) -> list[Edge]:
    """The bounds of every scalar among the classes, as edges."""
    return [edge for c in classes_ if is_scalar(c) for edge in interval(c)]


def never(cls: type[BaseModel]) -> str | None:
    """``"holds"`` when a relation's constraints and its operands' bounds have no solution,
    ``"refuses"`` when no solution makes any constraint false, ``None`` otherwise, and for any
    class that is not a relation."""
    if not is_relation(cls) or not cls.constraints:
        return None
    bounds = variables(c for classes_ in held(cls).values() for c in classes_)
    own = constrained(cls)
    if not feasible([*bounds, *own]):
        return "holds"
    if all(not feasible([*bounds, negated(e)]) for e in own):
        return "refuses"
    return None


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
        for classes_ in held(cls).values()
        if classes_
    ]
    return [frozenset({cls}).union(*combination) for combination in product(*per_field)]


def coexist(a: type[BaseModel], b: type[BaseModel], program: ModuleType) -> bool:
    """Whether two classes a field may hold can both be present in one run: the same class
    can; otherwise some choice of what each holds puts in one run no two records one action
    hears, and relations and scalar bounds that have a solution together."""
    if a is b:
        return True
    hearers_ = hearers(program)
    for present in (x | y for x in choices(a, frozenset()) for y in choices(b, frozenset())):
        records = [c for c in present if c in hearers_]
        if len({hearers_[r] for r in records}) < len(records):
            continue
        edges = variables(present) + [e for c in present if is_relation(c) for e in constrained(c)]
        if feasible(edges):
            return True
    return False


def ambiguous(
    code: LiteralString, message: LiteralString, pairs: Iterable[tuple[type[BaseModel], str]]
) -> list[InitErrorDetails]:
    """One error per class that appears more than once in the pairs: a record two actions hear,
    a class two computed fields produce, a scalar two carriers hold, a party two config fields
    hold."""
    pairs = list(pairs)
    counted = Counter(cls for cls, _ in pairs)
    return [
        fault(
            code,
            message,
            (cls.__name__,),
            n=n,
            cls=cls.__name__,
            by=", ".join(sorted(by for c, by in pairs if c is cls)),
        )
        for cls, n in counted.items()
        if n > 1
    ]


def scoped(program: ModuleType, classes_: list[type[BaseModel]]) -> list[InitErrorDetails]:
    """One ``scope`` error per route that descends from an element, per ``tuple[X, ...]`` field
    whose class descends from nothing, per class that descends from two elements, and per
    record heard once per element that holds a collection, since a record fans out from the
    parent run only."""
    return [
        *(
            fault(
                "scope",
                "{cls} exists once per element; a route exists once per run, so its reply's"
                " fact collects elements as tuple[X, ...] instead of holding one",
                (cls.__name__,),
                cls=cls.__name__,
            )
            for cls in classes_
            if is_route(cls) and descends(cls, program)
        ),
        *(
            fault(
                "scope",
                "{cls}.{name} collects {held}, which exists once per run; hold it directly",
                (cls.__name__, name),
                cls=cls.__name__,
                name=name,
                held=held_.__name__,
            )
            for cls in classes_
            for name, classes__ in collected(cls).items()
            for held_ in classes__
            if not descends(held_, program)
        ),
        *(
            fault(
                "scope",
                "{cls} exists once per element of {each}; a class exists per element of one",
                (cls.__name__,),
                cls=cls.__name__,
                each=" and ".join(sorted(e.__name__ for e in descends(cls, program))),
            )
            for cls in classes_
            if len(descends(cls, program)) > 1
        ),
        *(
            fault(
                "scope",
                "{record} is heard once per element and holds a collection; a record fans out"
                " from the parent run only",
                (record.__name__,),
                record=record.__name__,
            )
            for cls in classes_
            if is_action(cls) and descends(cls, program)
            for record in heard(cls)
            if collected(record)
        ),
    ]


def twice(program: ModuleType, classes_: list[type[BaseModel]]) -> list[InitErrorDetails]:
    """One error per record two actions hear, class two computed fields produce, scalar or value
    two carriers hold, and party two config fields hold."""
    return [
        *ambiguous(
            "hearer",
            "{n} actions hear {cls}: {by}; exactly one must",
            [(r, c.__name__) for c in classes_ if is_action(c) for r in heard(c)],
        ),
        *ambiguous(
            "producer",
            "{n} computed fields produce {cls}: {by}; exactly one must",
            [
                (produced_, f"{c.__name__}.{name}")
                for c in classes_
                for name, options_ in produced(c).items()
                for produced_ in options_
            ],
        ),
        *ambiguous(
            "carrier",
            "{n} classes carry {cls}: {by}; exactly one must",
            [
                (carried_, c.__name__)
                for c in carriers(program)
                for classes__ in held(c).values()
                for carried_ in classes__
                if is_scalar(carried_) or is_value(carried_)
            ],
        ),
        *ambiguous(
            "party",
            "{n} config fields hold {cls}: {by}; exactly one must",
            [
                (connection, name)
                for name, field in config(program).model_fields.items()
                for connection in options(field.annotation)
            ],
        ),
    ]


def unsound(program: ModuleType, classes_: list[type[BaseModel]]) -> list[InitErrorDetails]:
    """One ``undecidable`` error per relation that declares no constraints, one ``relation``
    error per relation its operands' bounds make certain or impossible, and one ``overlap``
    error per union field two of whose members can both hold."""
    return [
        *(
            fault(
                "undecidable",
                "{cls} declares no constraints, so the proof cannot tell what it decides",
                (cls.__name__,),
                cls=cls.__name__,
            )
            for cls in classes_
            if is_relation(cls) and not cls.constraints
        ),
        *(
            fault(
                "relation",
                "{cls} never {what}, by the constraints on its operands",
                (cls.__name__,),
                cls=cls.__name__,
                what=what,
            )
            for cls in classes_
            if (what := never(cls)) is not None
        ),
        *(
            fault(
                "overlap",
                "{cls}.{name} holds {a} | {b}, and both could hold; write members so at most"
                " one can",
                (cls.__name__, name),
                cls=cls.__name__,
                name=name,
                a=a.__name__,
                b=b.__name__,
            )
            for cls in classes_
            for name, options_ in held(cls).items()
            for i, a in enumerate(options_)
            for b in options_[i + 1 :]
            if coexist(a, b, program)
        ),
    ]


def unused(program: ModuleType) -> list[InitErrorDetails]:
    """One ``unused`` error per declared class no field names: the mirror of ``missing``."""
    return [
        fault("unused", "no field holds {cls}; hold it or delete it", (c.__name__,), cls=c.__name__)
        for c in models(program)
        if not used(c, program)
    ]


@cache
def proven(program: ModuleType) -> None:
    """Every class the program declares joins some route and is held by some field, each record
    has one hearer, each produced or carried class one source and each party one config field,
    every class has one scope, no relation is undecidable, certain or impossible, and no union
    holds two members that could both hold, or one ``ValidationError`` names every fault; read
    once per program, at startup."""
    classes_ = built(program)
    have = frozenset[type[BaseModel]]().union(*(prove(r, program) for r in routes(program)))
    pending = [c for c in classes_ if c not in have]
    details = [
        *faults(pending, have),
        *unused(program),
        *scoped(program, classes_),
        *twice(program, classes_),
        *unsound(program, classes_),
    ]
    if details:
        raise ValidationError.from_exception_data(program.__name__, details)


def connections(deployment: Config) -> tuple[Connection, ...]:
    """Every connection a config holds, in field order."""
    return tuple(
        value
        for value in (getattr(deployment, name) for name in type(deployment).model_fields)
        if isinstance(value, Connection)
    )


@asynccontextmanager
async def opened(deployment: Config) -> AsyncGenerator[None]:
    """Open every connection once before the body and close every one once after it, last
    opened first; when an open raises, close what was opened and let it propagate."""
    opened_: list[Connection] = []
    try:
        for connection in connections(deployment):
            await connection.open()
            opened_.append(connection)
        yield
    finally:
        for connection in reversed(opened_):
            await connection.close()


def fanned(scope: Run, given: Request | Record) -> list[Run]:
    """One child run per element of each ``tuple[E, ...]`` field a request or a record holds,
    chaining the element and what it carries over the parent run."""
    return [
        ChainMap({type(item): item, **carried_by(item)}, scope)
        for name in collected(type(given))
        for item in getattr(given, name)
        if isinstance(item, BaseModel)
    ]


def element(child: Run) -> type[BaseModel] | None:
    """The element class a child run was made for: the first class in its own layer."""
    return next(iter(child.maps[0]), None) if isinstance(child, ChainMap) else None


def supplied(
    cls: type[BaseModel], scope: Run, children: list[Run], program: ModuleType
) -> dict[str, BaseModel | tuple[BaseModel, ...]]:
    """What the run has for a class's fields: the present member of each single field, and,
    for each ``tuple[X, ...]`` field, every ``X`` from the children made for the element ``X``
    descends from, once that element's carrier is in the run and every such child holds an
    ``X``; the empty tuple when the carrier fanned out to nothing. A field with nothing present
    is left out, and Pydantic reports it ``missing``."""
    given: dict[str, BaseModel | tuple[BaseModel, ...]] = {
        name: scope[c] for name, classes_ in held(cls).items() for c in classes_ if c in scope
    }
    for name, classes_ in collected(cls).items():
        found = {e for c in classes_ for e in descends(c, program)}
        if len(found) != 1:
            continue
        (e,) = found
        carrier = next(
            c
            for c in carriers(program)
            if any(e in classes__ for classes__ in collected(c).values())
        )
        if carrier not in scope:
            continue
        runs = [child for child in children if element(child) is e]
        if all(any(c in child for c in classes_) for child in runs):
            given[name] = tuple(child[c] for child in runs for c in classes_ if c in child)
    return given


def absent(refusal: ValidationError) -> bool:
    """Whether a refusal says only that the class does not exist yet: every error is a field no
    present class fills, or a relation or selection that does not hold."""
    return all(error["type"] in ("missing", "relation") for error in refusal.errors())


def stalled(
    scopes: list[tuple[Run, list[type[BaseModel]]]],
    held_back: list[tuple[type[BaseModel], ValidationError]],
) -> list[InitErrorDetails]:
    """Why a pass constructed nothing, read from the refusals it was given: one ``relation``
    error per class whose refusal was a relation or selection that did not hold, with the
    kind's message, and one ``missing`` error per required single field no class fills, in the
    run the class is asked from, each once; or ``cycle`` when neither explains it."""
    relations = {
        cls: next(e["msg"] for e in refusal.errors() if e["type"] == "relation")
        for cls, refusal in held_back
        if any(e["type"] == "relation" for e in refusal.errors())
    }
    missing = {
        detail.get("loc"): detail
        for scope, todo in scopes
        for detail in unfilled([c for c in todo if c not in scope], scope, None)
    }
    details = [
        *(
            fault(
                "relation", "{cls} did not hold: {why}", (cls.__name__,), cls=cls.__name__, why=why
            )
            for cls, why in relations.items()
        ),
        *missing.values(),
    ]
    run, todo = scopes[0]
    return details or faults([c for c in todo if c not in run], run)


async def performed_in_span(action: Action[Connection, Record]) -> Record:
    """Perform one action inside a span named for it, carrying the party's and the record's
    class names."""
    with tracer.start_as_current_span(
        type(action).__name__, attributes={"tca.party": type(action.party).__name__}
    ) as span:
        record = await action.perform()
        span.set_attribute("tca.record", type(record).__name__)
        return record


async def answer[Q: Request, A: Reply[Fact]](
    route: type[Route[Q, A]], request: Q, config: Config, program: ModuleType
) -> Route[Q, A]:
    """Construct the route from the request: the route's classes, pass by pass, until the route
    itself constructs, holding the request and the reply.

    Each pass asks Pydantic for every class of the route not yet in the run it belongs to, from
    the instances its fields name; a class whose refusal is ``missing`` or ``relation`` only
    does not exist yet; any other refusal propagates. The pass's actions are performed together
    in one task group, across the parent run and its children, and each record enters the run
    it was asked from; a library kind's exception cancels the group's other actions and
    propagates in an ``ExceptionGroup``. A pass that constructs nothing raises a
    ``ValidationError`` naming each relation that did not hold and each field no class fills."""
    with tracer.start_as_current_span(
        route.__name__, attributes={"tca.request": type(request).__name__}
    ) as span:
        return await constructed(route, request, config, program, span)


async def constructed[Q: Request, A: Reply[Fact]](
    route: type[Route[Q, A]],
    request: Q,
    config: Config,
    program: ModuleType,
    span: trace.Span,
) -> Route[Q, A]:
    """The body of ``answer``, inside its span."""
    proof = prove(route, program)
    todo = [c for c in built(program) if c in proof]
    run: Run = {}
    run[type(request)] = request
    run.update(carried_by(request))
    run.update((type(c), c) for c in connections(config))
    children = fanned(run, request)
    passes = 0
    while route not in run:
        passes += 1
        performed: list[tuple[Action[Connection, Record], Run]] = []
        held_back: list[tuple[type[BaseModel], ValidationError]] = []
        scopes = [
            (run, [c for c in todo if element_of(c, program) is None]),
            *(
                (child, [c for c in todo if element_of(c, program) is element(child)])
                for child in children
            ),
        ]
        progress = False
        for scope, asked_for in scopes:
            for cls in asked_for:
                if cls in scope:
                    continue
                try:
                    instance = cls.model_validate(supplied(cls, scope, children, program))
                except ValidationError as refusal:
                    if absent(refusal):
                        held_back.append((cls, refusal))
                        continue
                    raise
                progress = True
                scope[cls] = instance
                scope.update(carried_by(instance))
                for name, classes_ in produced(cls).items():
                    value = getattr(instance, name)
                    if type(value) in classes_:
                        scope[type(value)] = value
                if is_performed(instance):
                    performed.append((instance, scope))
        async with TaskGroup() as group:
            tasks = [group.create_task(performed_in_span(action)) for action, _ in performed]
        for (_, scope), task in zip(performed, tasks, strict=True):
            record = task.result()
            scope[type(record)] = record
            scope.update(carried_by(record))
            if scope is run:
                children.extend(fanned(run, record))
        if not progress:
            raise ValidationError.from_exception_data(route.__name__, stalled(scopes, held_back))
    span.set_attribute("tca.passes", passes)
    return route.model_validate(run[route])
