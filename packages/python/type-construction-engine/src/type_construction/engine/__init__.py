"""The engine: reads a program's classes, proves them at startup, and answers a route by
construction.

A program is one module. The engine reads each class's fields once, and that read is the only
thing it knows: ``holds`` is the classes each single field names, ``collects`` the classes each
tuple field names, ``premises`` the required single fields, ``declares`` the elements a request
or a record holds as a tuple, ``heard`` the records an action declares as ``Action[P, T]``,
``carried`` the scalars and values a request, a record or a value brings with it. A class is a
proposition and its fields are its premises; an instance is a proof; ``model_dump`` of the
reply is the derivation of the answer.

The proof places every class. A placement is a path of element classes: ``()`` is once per run,
``(E,)`` once per element ``E`` of the request or record that declares it, ``(E, I)`` once per
inner element ``I`` of each ``E``. The request, its scalars and values, the deployment's
connections and the constants are placed at ``()``. An element is placed one level under what
declares it; a record where its hearer is; a scalar or value where its carrier is; every other
class at the finest placement its premises name, and one level above a class it collects. The
passes stop when no class can be placed, and ``Proof`` is constructed from what was placed and
what was left waiting. Its validator refuses the program with one ``ValidationError`` naming
every fault: ``missing``, a field no class fills; ``cycle``, classes that wait on each other;
``twice``, a class with two sources; ``unplaceable``, a class whose fields name sibling
elements; ``collects``, a tuple over a class not one level below; ``route``, a route that would
exist once per element; ``unreached``, a class the reply of no route leads to; ``unmodeled``, a
field that names no kind; ``boundary``, a request that holds what does not arrive; ``config``,
no one deployment; ``ambiguous``, two union members not proven exclusive; ``never``, a
relation its operands' intervals make certain or impossible; ``undiscriminated``, two records
one action hears that no field tells apart; ``undecided``, an action performed on one branch of
a choice and not the other that holds nothing deciding the choice.

A run is the same construction over instances. A scope is the instances at one placement,
seeing its ancestors' instances; the request's scope is ``()``, and each element of a request
or a record gets a child scope under the scope the holder arrived in, holding the element and
what it carries. A pass asks Pydantic for every class of the route not yet in its scope whose
premises are present, ``cls.model_validate(supplied)``: a single field is the present member, a
fresh scalar is constructed for the holder, and a tuple field is every child scope's instance in
element order once every child holds one, the empty tuple for no element. A relation or a
selection that refuses is refuted in that scope and asked again next pass; any other refusal
propagates. The pass's actions are performed together in one task group and each record enters
the scope its action was built in. The run ends when the route constructs. A pass that builds
nothing raises one ``ValidationError`` naming each relation that did not hold, with the
ordering observed, or each field no class fills.

``opened`` opens each connection once and closes each once around whatever a server kind runs
inside it. Every answer is one OpenTelemetry span named for the route, with one child per
performed action; the engine depends on ``opentelemetry-api`` only. The engine keeps nothing
about a program between runs: the proof is a value the server computes once and passes in.
"""

from asyncio import TaskGroup
from collections import ChainMap
from collections.abc import AsyncGenerator, Iterable, Iterator, Mapping
from contextlib import asynccontextmanager
from decimal import Decimal
from enum import Enum
from itertools import combinations, product
from types import ModuleType, NoneType, UnionType
from typing import Literal, LiteralString, NamedTuple, Self, TypeIs, Union, get_args, get_origin

from annotated_types import Ge, Gt, Le, Lt, MaxLen, MinLen
from opentelemetry import trace
from pydantic import BaseModel, ConfigDict, RootModel, TypeAdapter, ValidationError, model_validator
from pydantic_core import InitErrorDetails, PydanticCustomError, PydanticUndefined

from type_construction.world import (
    Action,
    Comparison,
    Config,
    Connection,
    Derived,
    Fact,
    Interval,
    Measure,
    Record,
    Relation,
    Reply,
    Request,
    Route,
    Selection,
    Setting,
    Value,
)

__all__ = [
    "Fault",
    "Placement",
    "Proof",
    "Waiting",
    "answer",
    "asked",
    "carried",
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
    "routes",
]

type Path = tuple[type[BaseModel], ...]
"""Where a class lives: ``()`` once per run, ``(E,)`` once per element ``E``, ``(E, I)`` once per
inner element ``I`` of each ``E``."""

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

SIGN = {-1: "<", 0: "=", 1: ">"}
"""How an observed ordering is rendered in a stall."""

tracer = trace.get_tracer("type_construction.engine")
"""Spans named by the program's classes: one per answer, named for the route, with one child per
performed action, named for the action. Attributes are class names and counts, never contents.
With no SDK configured these are no-ops; the deployment supplies the SDK and the exporter."""


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


def is_measure(cls: object) -> TypeIs[type[Measure]]:
    """Whether a class is a derivation: a strict subclass of ``Measure``."""
    return isinstance(cls, type) and issubclass(cls, Measure) and cls is not Measure


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


def is_performed(instance: BaseModel) -> TypeIs[Action[Connection, Record]]:
    """Whether a constructed instance is an action the engine performs."""
    return isinstance(instance, Action)


def carries(cls: type[BaseModel]) -> bool:
    """Whether a class brings the scalars and values it holds into the run: what arrives, what a
    party says, and a composite part."""
    return issubclass(cls, (Request, Record, Value))


def refutable(cls: type[BaseModel]) -> bool:
    """Whether a class's refusal says only that it does not hold for these operands: a relation
    or a selection, the kinds that exist to refuse."""
    return is_relation(cls) or is_selection(cls)


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


def routes(program: ModuleType) -> tuple[type[Route[Request, Reply[Fact]]], ...]:
    """Every ``Route`` subclass the program module declares, in definition order."""
    return tuple(c for c in classes(program) if is_route(c))


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
    """Each required single field that names classes the run must hold before the class is
    asked for: a fresh class is constructed for the holder instead."""
    return {
        name: classes_
        for name, classes_ in holds(cls).items()
        if classes_ and cls.model_fields[name].is_required() and not all(fresh(c) for c in classes_)
    }


def brought(cls: type[BaseModel]) -> frozenset[type[BaseModel]]:
    """The scalars and values a carrying class's single fields hold directly; nothing for a
    class that does not carry."""
    if not carries(cls):
        return frozenset()
    return frozenset(
        c for classes_ in holds(cls).values() for c in classes_ if is_scalar(c) or is_value(c)
    )


def carried(cls: type[BaseModel]) -> frozenset[type[BaseModel]]:
    """The scalars and values a carrying class brings into the run: what it holds directly, and
    what the values among those carry in turn."""
    direct = brought(cls)
    return direct.union(*(carried(c) for c in direct if is_value(c)))


def carried_by(instance: BaseModel) -> dict[type[BaseModel], BaseModel]:
    """The scalar and value instances a carrying instance holds, keyed by class, and what those
    values carry in turn."""
    if not carries(type(instance)):
        return {}
    direct: dict[type[BaseModel], BaseModel] = {
        type(value): value
        for name, classes_ in holds(type(instance)).items()
        if any(is_scalar(c) or is_value(c) for c in classes_)
        and isinstance(value := getattr(instance, name), BaseModel)
    }
    return direct | {k: v for value in direct.values() for k, v in carried_by(value).items()}


def declares(cls: type[BaseModel]) -> Options:
    """The element classes a request or a record holds as tuples, each the root of a child
    scope; nothing for any other class."""
    if not issubclass(cls, (Request, Record)):
        return ()
    return tuple(c for classes_ in collects(cls).values() for c in classes_)


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


def hearers(classes_: Iterable[type[BaseModel]]) -> dict[type[BaseModel], type[BaseModel]]:
    """Each record class and the first action that hears it."""
    found: dict[type[BaseModel], type[BaseModel]] = {}
    for action in classes_:
        if is_action(action):
            for record in heard(action):
                found.setdefault(record, action)
    return found


def carriers_of(cls: type[BaseModel], classes_: Iterable[type[BaseModel]]) -> Options:
    """The carrying classes that hold a scalar or value directly."""
    return tuple(c for c in classes_ if cls in brought(c))


def declarers_of(cls: type[BaseModel], classes_: Iterable[type[BaseModel]]) -> Options:
    """The requests and records that hold a class as elements."""
    return tuple(c for c in classes_ if cls in declares(c))


def holders_of(cls: type[BaseModel], classes_: Iterable[type[BaseModel]]) -> list[tuple[str, str]]:
    """Each class and field that names a class, singly or as an element."""
    return [
        (c.__name__, name)
        for c in classes_
        for name, classes__ in (*holds(c).items(), *collects(c).items())
        if cls in classes__
    ]


def producers_of(
    cls: type[BaseModel], classes_: Iterable[type[BaseModel]]
) -> list[tuple[type[BaseModel], str]]:
    """Each class and computed field that constructs a class as a word."""
    return [
        (c, name) for c in classes_ for name, classes__ in produces(c).items() if cls in classes__
    ]


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


def sources(cls: type[BaseModel], classes_: tuple[type[BaseModel], ...]) -> tuple[str, ...]:
    """Where a class's instances come from without being built from premises: a route's
    request, a carrier, a declarer, a hearer, a config field, a default root. A class with two
    is refused; one with none is built, is a word a computed field says, or is a fault its
    holder reports."""
    found = ["a request"] if cls in requests(classes_) else []
    found += [f"carried by {c.__name__}" for c in carriers_of(cls, classes_)]
    found += [f"an element of {c.__name__}" for c in declarers_of(cls, classes_)]
    found += [f"heard by {a.__name__}" for a in classes_ if is_action(a) and cls in heard(a)]
    found += [by for c, by in deployed(classes_) if c is cls]
    found += ["a constant"] if constant(cls) else []
    found += ["fresh"] if fresh(cls) else []
    return tuple(found)


def fault(
    code: LiteralString, message: LiteralString, loc: tuple[str, ...], **context: str | int
) -> InitErrorDetails:
    """One error of a ``ValidationError`` the engine raises: its type, its message template,
    the context the template reads, and the location, whose first element is the class."""
    return InitErrorDetails(type=PydanticCustomError(code, message, context), loc=loc, input=loc[0])


class Placement(BaseModel):
    """One class and where it lives."""

    model_config = ConfigDict(frozen=True, strict=True)
    cls: type[BaseModel]
    path: Path


class Waiting(BaseModel):
    """The absent case, as a value: what a class waited on when the proof's passes stopped. An
    empty ``on`` is a class with no source at all."""

    model_config = ConfigDict(frozen=True, strict=True)
    cls: type[BaseModel]
    field: str
    on: Options


class Fault(BaseModel):
    """A fault the passes found while placing a class, kept until the proof reports it with the
    rest."""

    model_config = ConfigDict(frozen=True, strict=True)
    code: Literal["unplaceable", "collects", "route"]
    cls: type[BaseModel]
    message: str


PLACED = frozenset[type[BaseModel]]()
"""The empty set of classes."""


def seeds(classes_: tuple[type[BaseModel], ...]) -> dict[type[BaseModel], Path]:
    """What is placed at ``()`` before any pass: every route's request and what it carries, the
    deployment's connections, and every constant and fresh scalar."""
    placed: dict[type[BaseModel], Path] = {}
    for request in requests(classes_):
        placed[request] = ()
        placed.update(dict.fromkeys(carried(request), ()))
    placed.update(dict.fromkeys((c for c, _ in deployed(classes_)), ()))
    placed.update(dict.fromkeys((c for c in classes_ if constant(c) or fresh(c)), ()))
    return placed


def under(
    holder: type[BaseModel],
    cls: type[BaseModel],
    placed: Mapping[type[BaseModel], Path],
    *,
    deeper: bool,
) -> Path | Waiting:
    """Where a class another class places lives: one level under the holder when it is an
    element, else where the holder is; ``Waiting`` on the holder while it is unplaced."""
    if holder not in placed:
        return Waiting(cls=cls, field="", on=(holder,))
    return (*placed[holder], cls) if deeper else placed[holder]


def sourced(
    cls: type[BaseModel],
    placed: Mapping[type[BaseModel], Path],
    classes_: tuple[type[BaseModel], ...],
) -> Path | Waiting | None:
    """The placement of a class another class places: an element one level under its declarer,
    a record where its hearer is, a scalar or value where its carrier is, a word where the
    computed field that says it is; ``Waiting`` while that class is unplaced, waiting on nothing
    for a record no action hears or a scalar nothing carries; ``None`` for a class that is built
    from its premises."""
    if declarers := declarers_of(cls, classes_):
        return under(declarers[0], cls, placed, deeper=True)
    if is_record(cls):
        hearer = hearers(classes_).get(cls)
        if hearer is None:
            return Waiting(cls=cls, field="", on=())
        return under(hearer, cls, placed, deeper=False)
    holders = [*carriers_of(cls, classes_), *(c for c, _ in producers_of(cls, classes_))]
    if holders:
        return under(holders[0], cls, placed, deeper=False)
    return Waiting(cls=cls, field="", on=()) if is_scalar(cls) or is_request(cls) else None


def candidates(
    cls: type[BaseModel], placed: Mapping[type[BaseModel], Path]
) -> tuple[list[Path], list[Path]] | Waiting | Fault:
    """The placements a built class's fields name: those of its premises, and one level above
    each class it collects; ``Waiting`` on the first field with nothing placed; a ``collects``
    fault for a tuple over a class placed once per run."""
    paths: list[Path] = []
    for name, classes_ in premises(cls).items():
        present = [placed[c] for c in classes_ if c in placed]
        if not present:
            return Waiting(cls=cls, field=name, on=classes_)
        paths.extend(present)
    below: list[Path] = []
    for name, classes_ in collects(cls).items():
        present = [placed[c] for c in classes_ if c in placed]
        if not present:
            return Waiting(cls=cls, field=name, on=classes_)
        if any(not p for p in present):
            once = ", ".join(c.__name__ for c in classes_ if c in placed and not placed[c])
            return Fault(
                code="collects",
                cls=cls,
                message=f"{cls.__name__}.{name} collects {once}, which exists once per run;"
                " hold it directly",
            )
        below.extend(p[:-1] for p in present)
    return paths, below


def place(
    cls: type[BaseModel],
    placed: Mapping[type[BaseModel], Path],
    classes_: tuple[type[BaseModel], ...],
) -> Path | Waiting | Fault:
    """The proof's step: where a class lives, read from its fields. A class another class places
    lives where ``sourced`` says. Any other lives at the finest placement its premises name,
    which every other must be a prefix of, and one level above each class it collects, which
    must be exactly that level."""
    if (found := sourced(cls, placed, classes_)) is not None:
        return found
    named = candidates(cls, placed)
    if not isinstance(named, tuple):
        return named
    paths, below = named
    finest = max((*paths, *below), key=len, default=())
    if any(finest[: len(p)] != p for p in paths) or any(p != finest for p in below):
        each = " and ".join(sorted({p[-1].__name__ for p in (*paths, *below) if p}))
        return Fault(
            code="unplaceable",
            cls=cls,
            message=f"{cls.__name__} would exist once per element of {each}; a class exists"
            " per element of one",
        )
    if is_route(cls) and finest:
        return Fault(
            code="route",
            cls=cls,
            message=f"{cls.__name__} would exist once per {finest[-1].__name__}; a route exists"
            " once per run, so its reply's fact collects elements as tuple[X, ...] instead of"
            " holding one",
        )
    return finest


def placements(
    classes_: tuple[type[BaseModel], ...],
) -> tuple[dict[type[BaseModel], Path], dict[type[BaseModel], Waiting], list[Fault]]:
    """The proof's passes: ask ``place`` for every class not yet placed, keep what is placed,
    and stop when a pass places nothing. Deployment values are the environment's and are not
    placed."""
    placed = seeds(classes_)
    pending = [c for c in classes_ if c not in placed and not is_setting(c) and not is_config(c)]
    waiting: dict[type[BaseModel], Waiting] = {}
    faults: list[Fault] = []
    moved = True
    while moved:
        moved = False
        for cls in list(pending):
            match place(cls, placed, classes_):
                case Waiting() as found:
                    waiting[cls] = found
                case Fault() as found:
                    faults.append(found)
                    pending.remove(cls)
                    waiting.pop(cls, None)
                case found:
                    placed[cls] = found
                    pending.remove(cls)
                    waiting.pop(cls, None)
                    moved = True
    return placed, waiting, faults


class Proof(BaseModel):
    """Every class placed, constructed at startup; its validator refuses the program with every
    fault at once."""

    model_config = ConfigDict(frozen=True, strict=True)
    program: str
    classes: tuple[type[BaseModel], ...]
    placed: tuple[Placement, ...]
    waiting: tuple[Waiting, ...]
    faulted: tuple[Fault, ...]

    @property
    def paths(self) -> dict[type[BaseModel], Path]:
        """Each placed class and where it lives."""
        return {p.cls: p.path for p in self.placed}

    def path(self, cls: type[BaseModel]) -> Path:
        """Where a placed class lives."""
        return self.paths[cls]

    @property
    def routes(self) -> tuple[type[Route[Request, Reply[Fact]]], ...]:
        """The program's routes."""
        return tuple(c for c in self.classes if is_route(c))

    def reached(self, start: type[BaseModel]) -> frozenset[type[BaseModel]]:
        """Every class a class leads to: through its fields, the words of its computed fields,
        the carriers of what it holds, the hearer of a record, the declarer of an element, and
        so on from each."""
        found: set[type[BaseModel]] = set()
        todo = [start]
        hearers_ = hearers(self.classes)
        while todo:
            cls = todo.pop()
            if cls in found:
                continue
            found.add(cls)
            named = (*holds(cls).values(), *collects(cls).values(), *produces(cls).values())
            todo.extend(c for classes_ in named for c in classes_)
            todo.extend(carriers_of(cls, self.classes))
            todo.extend(declarers_of(cls, self.classes))
            if cls in hearers_:
                todo.append(hearers_[cls])
        return frozenset(found)

    def built[Q: Request, A: Reply[Fact]](
        self, route: type[Route[Q, A]]
    ) -> tuple[type[BaseModel], ...]:
        """The classes a route's run constructs from premises: those its reply leads to that
        are not scalars and have no source of their own, in definition order."""
        reach = self.reached(route)
        return tuple(
            c
            for c in self.classes
            if c in reach and c in self.paths and not is_scalar(c) and not sources(c, self.classes)
        )

    @property
    def constants(self) -> tuple[type[BaseModel], ...]:
        """The scalars that exist in every run by being declared."""
        return tuple(c for c in self.classes if constant(c))

    @model_validator(mode="after")
    def sound(self) -> Self:
        """Refuse the program with one ``ValidationError`` naming every fault."""
        details = [
            *unfilled(self),
            *(fault(f.code, "{why}", (f.cls.__name__,), why=f.message) for f in self.faulted),
            *twice(self),
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


def unfilled(proof: Proof) -> list[InitErrorDetails]:
    """One ``missing`` error per field that holds a class with no source, at ``(class, field)``,
    and one ``cycle`` error per waiting class that no such root explains: one whose every
    unfilled field names a class that only another unexplained waiting class would bring."""
    waiting = {w.cls: w for w in proof.waiting}
    sourceless = [w.cls for w in proof.waiting if not w.on]
    explained = set(sourceless) | {f.cls for f in proof.faulted}
    moved = True
    while moved:
        moved = False
        for w in waiting.values():
            if w.cls not in explained and any(c in explained for c in w.on):
                explained.add(w.cls)
                moved = True
    return [
        *(
            fault(
                "missing",
                "no class fills {cls}.{name}, which holds {holds}",
                (holder, name),
                cls=holder,
                name=name,
                holds=absent.__name__,
            )
            for absent in sourceless
            for holder, name in holders_of(absent, proof.classes)
        ),
        *(
            fault("cycle", "{cls} holds a class that holds it", (c.__name__,), cls=c.__name__)
            for c in waiting
            if c not in explained
        ),
    ]


def twice(proof: Proof) -> list[InitErrorDetails]:
    """One ``twice`` error per class with more than one source."""
    return [
        fault(
            "twice",
            "{cls} has {n} sources: {by}; exactly one",
            (c.__name__,),
            cls=c.__name__,
            n=len(found),
            by=", ".join(found),
        )
        for c in proof.classes
        if len(found := sources(c, proof.classes)) > 1
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


def owned(cls: type[BaseModel], name: str) -> bool:
    """Whether a field is the kind's own computed one: a relation's ordering or a derivation's
    root."""
    factory = cls.model_fields[name].default_factory
    return isinstance(factory, (Comparison, Derived))


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
        for name, field in c.model_fields.items()
        if not owned(c, name)
        for member in (
            elements(field.annotation)
            if get_origin(field.annotation) is tuple
            else (field.annotation,)
        )
        for member in members(member)
        if not modeled(c, member)
    ]


def arrives(cls: type[BaseModel]) -> bool:
    """Whether a class is data that arrives: a scalar, a value, or an enumeration."""
    return is_scalar(cls) or is_value(cls)


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
    field = cls.model_fields.get("root")
    if field is None:
        return Interval()
    whole = field.annotation is int
    found = Interval()
    for meta in field.metadata:
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
    if isinstance(root.default_factory, Derived):
        operands = tuple(
            hull(interval(c, seen | {cls}) for c in classes_)
            for name in root.default_factory.operands
            for classes_ in ({**holds(cls), **collects(cls)}[name],)
        )
        return root.default_factory.interval(operands)
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
    admits, read from the ordering fields' factories and annotations."""
    return [
        (
            holds(cls)[factory.left],
            holds(cls)[factory.right],
            frozenset(get_args(field.annotation)),
        )
        for field in cls.model_fields.values()
        if isinstance(factory := field.default_factory, Comparison)
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
    field = cls.model_fields["of"]
    if Ellipsis not in get_args(field.annotation):
        return len(get_args(field.annotation)), len(get_args(field.annotation))
    low, high = 0, None
    for meta in field.metadata:
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
    one class."""
    return {
        name: classes_
        for name, classes_ in (*holds(cls).items(), *collects(cls).items())
        if len(classes_) > 1
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
        str(field.validation_alias or field.alias or name)
        for name, field in cls.model_fields.items()
        if field.is_required() or not required
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
                for chosen, other in ((a, b), (b, a)):
                    reach, reach_ = proof.reached(chosen), proof.reached(other)
                    settles = deciders(
                        PLACED.union(*choices(chosen, PLACED)),
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
                            chosen=chosen.__name__,
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
    """The proof of a program: every class placed by the passes, constructed as a ``Proof``,
    whose validator refuses the program with every fault at once."""
    classes_ = models(program)
    placed, waiting, faults = placements(classes_)
    return Proof(
        program=program.__name__,
        classes=classes_,
        placed=tuple(Placement(cls=c, path=p) for c, p in placed.items()),
        waiting=tuple(waiting.values()),
        faulted=tuple(faults),
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


class Scope(NamedTuple):
    """The instances at one placement in a run: its own, over its ancestors', and the child
    scopes under it, one list per element class, in element order."""

    path: Path
    have: ChainMap[type[BaseModel], BaseModel]
    children: dict[type[BaseModel], list[Scope]]


def fanned(scope: Scope, holder: BaseModel) -> None:
    """One child scope per element of each tuple a request or a record holds, holding the
    element and what it carries over the parent's instances; an element class with no element
    gets an empty list, so a collection over it is the empty tuple."""
    for name, classes_ in collects(type(holder)).items():
        for cls in classes_:
            scope.children.setdefault(cls, [])
        for item in getattr(holder, name):
            if isinstance(item, BaseModel):
                have = ChainMap({type(item): item, **carried_by(item)}, scope.have)
                child = Scope((*scope.path, type(item)), have, {})
                scope.children.setdefault(type(item), []).append(child)


def scopes(scope: Scope) -> Iterator[Scope]:
    """A scope and every scope under it, parents first."""
    yield scope
    for children in scope.children.values():
        for child in children:
            yield from scopes(child)


def present(classes_: Options, have: Mapping[type[BaseModel], BaseModel]) -> BaseModel | None:
    """The instance of the first class among those a field may hold that the run has, or a
    fresh one when a fresh class is among them; ``None`` when there is none yet."""
    for cls in classes_:
        if cls in have:
            return have[cls]
    for cls in classes_:
        if fresh(cls):
            return cls()
    return None


def gathered(classes_: Options, scope: Scope, proof: Proof) -> tuple[BaseModel, ...] | None:
    """Every instance of a collected class from the child scopes made for the element it lives
    under, in element order, once the element's holder has arrived and every child holds one;
    the empty tuple for no element; ``None`` while any is absent."""
    found: list[BaseModel] = []
    for element in {proof.path(c)[len(scope.path)] for c in classes_}:
        if element not in scope.children:
            return None
        for child in scope.children[element]:
            instance = present(classes_, child.have.maps[0])
            if instance is None:
                return None
            found.append(instance)
    return tuple(found)


def supplied(
    cls: type[BaseModel], scope: Scope, proof: Proof
) -> dict[str, BaseModel | tuple[BaseModel, ...]] | None:
    """What the scope has for a class's fields: the present member of each single field, and
    every child's instance for each tuple field; ``None`` while a required field has nothing,
    so the class is asked again next pass."""
    given: dict[str, BaseModel | tuple[BaseModel, ...]] = {}
    for name, classes_ in holds(cls).items():
        instance = present(classes_, scope.have)
        if instance is not None:
            given[name] = instance
        elif classes_ and cls.model_fields[name].is_required():
            return None
    for name, classes_ in collects(cls).items():
        instances = gathered(classes_, scope, proof)
        if instances is None:
            return None
        given[name] = instances
    return given


def rendered(cls: type[BaseModel], refusal: ValidationError) -> str:
    """Why a relation or a selection did not hold: the ordering observed between the two
    operands, as ``value Amount > bound Limit``, or Pydantic's message for a selection."""
    for error in refusal.errors():
        loc = error["loc"]
        field = cls.model_fields.get(str(loc[0])) if loc else None
        factory = field.default_factory if field is not None else None
        if isinstance(factory, Comparison) and isinstance(error["input"], int):
            left, right = holds(cls)[factory.left][0], holds(cls)[factory.right][0]
            sign = SIGN[error["input"]]
            return f"{factory.left} {left.__name__} {sign} {factory.right} {right.__name__}"
    return "; ".join(error["msg"] for error in refusal.errors())


def stalled(
    root: Scope,
    asked_for: tuple[type[BaseModel], ...],
    refuted: dict[type[BaseModel], tuple[Scope, ValidationError]],
    proof: Proof,
) -> list[InitErrorDetails]:
    """Why a pass constructed nothing: one ``relation`` error per class whose refusal said it did
    not hold, with what was observed, leaving out one whose complement holds in the same scope,
    since that choice was decided; else one ``missing`` error per required field no class fills
    in the scope the class is asked from; else ``cycle``."""
    causes = {
        cls: refusal
        for cls, (scope, refusal) in refuted.items()
        if not deciders(frozenset({cls}), frozenset(scope.have), proof.classes)
    } or {cls: refusal for cls, (_, refusal) in refuted.items()}
    details = [
        fault(
            "relation",
            "{cls} did not hold: {why}",
            (cls.__name__,),
            cls=cls.__name__,
            why=rendered(cls, refusal),
        )
        for cls, refusal in causes.items()
    ]
    if details:
        return details
    pending = [
        (scope, cls)
        for scope in scopes(root)
        for cls in asked_for
        if proof.path(cls) == scope.path and cls not in scope.have.maps[0]
    ]
    unbuilt = {cls for _, cls in pending}
    heard_ = hearers(proof.classes)
    for scope, cls in pending:
        for name, classes_ in premises(cls).items():
            if present(classes_, scope.have) is None and not any(
                c in unbuilt or c in heard_ for c in classes_
            ):
                details.append(
                    fault(
                        "missing",
                        "no class fills {cls}.{name}, which holds {holds}",
                        (cls.__name__, name),
                        cls=cls.__name__,
                        name=name,
                        holds=" | ".join(c.__name__ for c in classes_),
                    )
                )
    return details or [
        fault("cycle", "{cls} holds a class that holds it", (cls.__name__,), cls=cls.__name__)
        for cls in unbuilt
    ]


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
    route: type[Route[Q, A]], request: Q, deployment: Config, proof: Proof
) -> Route[Q, A]:
    """Construct the route from the request: the route's classes, pass by pass, in the scope
    each lives in, until the route itself constructs, holding the request and the reply.

    Each pass asks Pydantic for every class of the route not yet in its scope whose premises are
    present; a relation or a selection that refuses does not hold in that scope yet; any other
    refusal propagates. The pass's actions are performed together in one task group, across
    every scope, and each record enters the scope its action was built in; a library kind's
    exception cancels the group's other actions and propagates in an ``ExceptionGroup``. A pass
    that constructs nothing raises a ``ValidationError`` naming each relation that did not hold
    or each field no class fills."""
    with tracer.start_as_current_span(
        route.__name__, attributes={"tca.request": type(request).__name__}
    ) as span:
        return await constructed(route, request, deployment, proof, span)


async def constructed[Q: Request, A: Reply[Fact]](
    route: type[Route[Q, A]],
    request: Q,
    deployment: Config,
    proof: Proof,
    span: trace.Span,
) -> Route[Q, A]:
    """The body of ``answer``, inside its span."""
    asked_for = proof.built(route)
    root = Scope(
        (),
        ChainMap(
            {
                type(request): request,
                **carried_by(request),
                **{type(c): c for c in connections(deployment)},
                **{c: c() for c in proof.constants},
            }
        ),
        {},
    )
    fanned(root, request)
    passes = 0
    while route not in root.have:
        passes += 1
        performed: list[tuple[Action[Connection, Record], Scope]] = []
        refuted: dict[type[BaseModel], tuple[Scope, ValidationError]] = {}
        built = False
        for scope in scopes(root):
            for cls in asked_for:
                if proof.path(cls) != scope.path or cls in scope.have.maps[0]:
                    continue
                given = supplied(cls, scope, proof)
                if given is None:
                    continue
                try:
                    instance = cls.model_validate(given)
                except ValidationError as refusal:
                    if refutable(cls):
                        refuted[cls] = (scope, refusal)
                        continue
                    raise
                built = True
                scope.have[cls] = instance
                scope.have.update(carried_by(instance))
                if is_performed(instance):
                    performed.append((instance, scope))
        async with TaskGroup() as group:
            tasks = [group.create_task(performed_in_span(action)) for action, _ in performed]
        for (_, scope), task in zip(performed, tasks, strict=True):
            record = task.result()
            scope.have[type(record)] = record
            scope.have.update(carried_by(record))
            fanned(scope, record)
        if not built:
            why = stalled(root, asked_for, refuted, proof)
            raise ValidationError.from_exception_data(route.__name__, why)
    span.set_attribute("tca.passes", passes)
    return route.model_validate(root.have[route])
