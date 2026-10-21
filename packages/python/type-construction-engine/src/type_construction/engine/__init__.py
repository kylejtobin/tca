"""The engine: reads a program's classes, proves them, and answers a route by construction.

A program is one module, named by the entry-point group ``type_construction.programs``.
``routes`` and ``config`` read its ``Route`` and ``Config`` subclasses; ``asked`` reads a
route's request class from its ``request`` field; ``heard`` reads the ``T`` an action
declares as ``Action[P, T]``.

A run is the instances of one answer, keyed by class, seeded with the request and the
deployment's connections. A pass visits every class of the route not yet in the run and
asks Pydantic for it from the instances its fields name: ``cls.model_validate(held)``.
Pydantic answers one of three ways. The class constructs: the instance enters the run,
each computed field's value enters under its own class, and an action is performed with
the pass's other actions, its record entering under the record's class. The class refuses
with ``missing`` only: it is not ready, and the next pass visits it again. The class
refuses otherwise: the refusal propagates. The run ends when the route constructs, which
needs the reply, which needs its fact. A union field takes whichever member exists, so a
member that never exists is never built and the holder's union is the choice. A request
or a record that holds ``tuple[E, ...]`` fans out: each ``E`` gets a child run that sees
the parent's instances and its own element, a class whose fields name ``E`` exists once
per element, and a ``tuple[X, ...]`` field of a parent-run class collects every child's
``X`` in element order.

``prove`` is the same passes over classes, at startup: a class joins when every required
field names a class that has joined; an action's record, a computed field's return
classes and a request's or record's elements join with their class. The classes that join
from a route's request are the route's. ``proven`` checks every class joins some route and
otherwise raises one ``ValidationError`` naming, for each class left, each field no class
fills.

``opened`` opens each connection once and closes each once around whatever a server kind
runs inside it. Every answer is one OpenTelemetry span named for the route, with one child
per performed action named for the action and carrying the party's and the record's class
names; the engine depends on ``opentelemetry-api`` only.
"""

from asyncio import gather
from collections import ChainMap, Counter
from collections.abc import AsyncGenerator, Container, Iterable, Iterator, MutableMapping
from contextlib import asynccontextmanager
from functools import cache
from types import ModuleType, UnionType
from typing import LiteralString, TypeIs, Union, get_args, get_origin

from opentelemetry import trace
from pydantic import BaseModel, ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError

from type_construction.world import (
    Action,
    Config,
    Connection,
    Fact,
    Record,
    Reply,
    Request,
    Route,
    Value,
)

__all__ = ["answer", "asked", "config", "hear", "opened", "prove", "proven", "routes"]

type Run = MutableMapping[type[BaseModel], BaseModel]
"""The instances of one run, keyed by class; a child run chains its element over its parent."""

type Options = tuple[type[BaseModel], ...]
"""The classes a field may hold: a union's members, else the one class."""

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


def declared(cls: type[object]) -> bool:
    """Whether a class is one the page wrote: not a parametrization Pydantic registered in the
    module, as ``Says[Catalog, Price]`` beside ``Quote``, and not a library kind whose parameters
    are still open, as ``Says`` itself."""
    return (
        not issubclass(cls, BaseModel)
        or cls is BaseModel
        or (
            cls.__pydantic_generic_metadata__["origin"] is None
            and not cls.__pydantic_generic_metadata__["parameters"]
        )
    )


def classes(program: ModuleType) -> list[type[object]]:
    """Every class the program module declares: defined there, not imported into it."""
    return [
        c
        for c in vars(program).values()
        if isinstance(c, type) and c.__module__ == program.__name__ and declared(c)
    ]


def routes(program: ModuleType) -> tuple[type[Route[Request, Reply[Fact]]], ...]:
    """Every ``Route`` subclass the program module declares, in definition order."""
    return tuple(c for c in classes(program) if is_route(c))


def config(program: ModuleType) -> type[Config]:
    """The one ``Config`` subclass the program module declares."""
    return next(c for c in classes(program) if issubclass(c, Config) and c is not Config)


def built(program: ModuleType) -> list[type[BaseModel]]:
    """Every class the run constructs, in definition order."""
    return [c for c in classes(program) if is_model(c) and is_built(c)]


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


def unmet(
    cls: type[BaseModel], have: Container[type[BaseModel]], gathered: Container[type[BaseModel]]
) -> dict[str, Options]:
    """Each required field of a class that no present class fills: a single field from what the
    run has, a ``tuple[X, ...]`` field from what the run and its children have."""
    singles = {
        name: classes_
        for name, classes_ in held(cls).items()
        if cls.model_fields[name].is_required() and not any(c in have for c in classes_)
    }
    tuples = {
        name: classes_
        for name, classes_ in collected(cls).items()
        if cls.model_fields[name].is_required() and not any(c in gathered for c in classes_)
    }
    return singles | tuples


def asked(route: type[Route[Request, Reply[Fact]]]) -> type[Request]:
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


def heard[P: Connection, T: Record](action: type[Action[P, T]]) -> type[Record]:
    """The record an action declares as ``Action[P, T]``."""
    (record,) = (
        a
        for origin, args in parametrized(action)
        if origin is Action
        for a in args[1:]
        if is_record(a)
    )
    return record


def hears[P: Connection, T: Record](record: Record, action: Action[P, T]) -> TypeIs[T]:
    """Whether a record is the one an action hears."""
    return isinstance(record, heard(type(action)))


def hear[P: Connection, T: Record](action: Action[P, T], text: str) -> T:
    """The record an action hears, validated strictly from the party's JSON text; what a library
    kind's ``perform`` returns."""
    (record,) = (r for r in (heard(type(action)).model_validate_json(text),) if hears(r, action))
    return record


def brought(cls: type[BaseModel]) -> frozenset[type[BaseModel]]:
    """The classes that exist in the same run once a class does: itself, what its computed
    fields produce, and the record its action hears."""
    none = frozenset[type[BaseModel]]()
    produced_ = frozenset(c for classes_ in produced(cls).values() for c in classes_)
    return frozenset((cls,)) | produced_ | (brought(heard(cls)) if is_action(cls) else none)


def elements(cls: type[BaseModel]) -> frozenset[type[BaseModel]]:
    """The classes that exist once per element when a class does: those a request or a record
    holds as ``tuple[E, ...]``, each in a child run of its own."""
    none = frozenset[type[BaseModel]]()
    held_ = frozenset(c for classes_ in collected(cls).values() for c in classes_)
    return held_ if issubclass(cls, (Request, Record)) else none


def faults(
    pending: Iterable[type[BaseModel]], have: Container[type[BaseModel]]
) -> list[InitErrorDetails]:
    """One ``missing`` error per required field of a pending class that no present class fills
    and no pending class would bring, at ``(class, field)``: the root faults, not what follows
    from them. When every pending class waits on another, one ``cycle`` error per class."""
    blocked = frozenset[type[BaseModel]]().union(*(brought(c) | elements(c) for c in pending))
    details = [
        InitErrorDetails(
            type=PydanticCustomError(
                "missing",
                "no class fills {cls}.{name}, which holds {holds}",
                {
                    "cls": cls.__name__,
                    "name": name,
                    "holds": " | ".join(c.__name__ for c in classes_),
                },
            ),
            loc=(cls.__name__, name),
            input=cls.__name__,
        )
        for cls in pending
        for name, classes_ in unmet(cls, have, have).items()
        if not any(c in blocked for c in classes_)
    ]
    cycle = [
        InitErrorDetails(
            type=PydanticCustomError(
                "cycle", "{cls} holds a class that holds it", {"cls": cls.__name__}
            ),
            loc=(cls.__name__,),
            input=cls.__name__,
        )
        for cls in pending
    ]
    return details or cycle


type Proof = tuple[frozenset[type[BaseModel]], frozenset[type[BaseModel]]]
"""The classes a route constructs once per run, and those it constructs once per element."""


@cache
def prove(route: type[Route[Request, Reply[Fact]]], program: ModuleType) -> Proof:
    """The classes a route constructs: those that join, pass by pass, from its request and the
    deployment's connections, once per run or once per element; read once per route.

    A class joins the run when every required single field names a class in the run and every
    ``tuple[X, ...]`` field names a class in the run or its children; it joins the children when
    its fields are filled there. An action's record and a computed field's return classes join
    with their class; a request's or record's elements join the children. The passes stop when
    none of the classes left can join."""
    once = brought(asked(route))
    for field in config(program).model_fields.values():
        for connection in options(field.annotation):
            once |= brought(connection)
    per = elements(asked(route))
    pending = built(program)
    while pending:
        ready = [c for c in pending if not unmet(c, once, once | per)]
        ready_per = [c for c in pending if c not in ready and not unmet(c, once | per, once | per)]
        once = once.union(*(brought(c) for c in ready))
        per = per.union(
            *(elements(c) for c in ready), *(brought(c) | elements(c) for c in ready_per)
        )
        pending = [c for c in pending if c not in ready and c not in ready_per]
        if not ready and not ready_per:
            break
    return once, per


def ambiguous(
    code: LiteralString, message: LiteralString, pairs: Iterable[tuple[type[BaseModel], str]]
) -> list[InitErrorDetails]:
    """One error per class that appears more than once in the pairs: a record two actions hear,
    a class two computed fields produce, a party two config fields hold."""
    counted = Counter(cls for cls, _ in pairs)
    return [
        InitErrorDetails(
            type=PydanticCustomError(
                code,
                message,
                {
                    "n": n,
                    "cls": cls.__name__,
                    "by": ", ".join(sorted(by for c, by in pairs if c is cls)),
                },
            ),
            loc=(cls.__name__,),
            input=cls.__name__,
        )
        for cls, n in counted.items()
        if n > 1
    ]


@cache
def proven(program: ModuleType) -> None:
    """Every class the program declares joins some route, each record has one hearer, each
    produced class one producer and each party one config field, or one ``ValidationError``
    names every fault; read once per program, at startup."""
    classes_ = built(program)
    proofs = {r: prove(r, program) for r in routes(program)}
    have = frozenset[type[BaseModel]]().union(*(once | per for once, per in proofs.values()))
    pending = [c for c in classes_ if c not in have]
    scope = [
        *(
            InitErrorDetails(
                type=PydanticCustomError(
                    "scope",
                    "{cls} exists once per element; a route exists once per run, so its reply's"
                    " fact collects elements as tuple[X, ...] instead of holding one",
                    {"cls": route.__name__},
                ),
                loc=(route.__name__,),
                input=route.__name__,
            )
            for route, (_, per) in proofs.items()
            if route in per
        ),
        *(
            InitErrorDetails(
                type=PydanticCustomError(
                    "scope",
                    "{cls}.{name} collects {held}, which exists once per run; hold it directly",
                    {"cls": cls.__name__, "name": name, "held": held_.__name__},
                ),
                loc=(cls.__name__, name),
                input=cls.__name__,
            )
            for once, _ in proofs.values()
            for cls in classes_
            if cls in once
            for name, classes__ in collected(cls).items()
            for held_ in classes__
            if held_ in once
        ),
    ]
    twice = [
        *ambiguous(
            "hearer",
            "{n} actions hear {cls}: {by}; exactly one must",
            [(heard(c), c.__name__) for c in classes_ if is_action(c)],
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
            "party",
            "{n} config fields hold {cls}: {by}; exactly one must",
            [
                (connection, name)
                for name, field in config(program).model_fields.items()
                for connection in options(field.annotation)
            ],
        ),
    ]
    if pending or scope or twice:
        raise ValidationError.from_exception_data(
            program.__name__, [*faults(pending, have), *scope, *twice]
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
    opened first."""
    held_ = connections(deployment)
    for connection in held_:
        await connection.open()
    try:
        yield
    finally:
        for connection in reversed(held_):
            await connection.close()


def fanned(scope: Run, given: Request | Record) -> list[Run]:
    """One child run per element of each ``tuple[E, ...]`` field a request or a record holds,
    chaining the element over the parent run."""
    return [
        ChainMap({type(item): item}, scope)
        for name in collected(type(given))
        for item in getattr(given, name)
        if isinstance(item, BaseModel)
    ]


def supplied(
    cls: type[BaseModel], scope: Run, children: list[Run]
) -> dict[str, BaseModel | tuple[BaseModel, ...]]:
    """What the run has for a class's fields: the present member of each single field, and
    every child's member of each collecting field once every child has one. A field with
    nothing present is left out, and Pydantic reports it ``missing``."""
    singles = {
        name: scope[c] for name, classes_ in held(cls).items() for c in classes_ if c in scope
    }
    tuples = {
        name: tuple(child[c] for child in children for c in classes_ if c in child)
        for name, classes_ in collected(cls).items()
        if children and all(any(c in child for c in classes_) for child in children)
    }
    return singles | tuples


async def performed_in_span(action: Action[Connection, Record]) -> Record:
    """Perform one action inside a span named for it, carrying the party's and the record's
    class names."""
    with tracer.start_as_current_span(
        type(action).__name__, attributes={"tca.party": type(action.party).__name__}
    ) as span:
        record = await action.perform()
        span.set_attribute("tca.record", type(record).__name__)
        return record


async def answer(
    route: type[Route[Request, Reply[Fact]]], request: Request, config: Config, program: ModuleType
) -> Route[Request, Reply[Fact]]:
    """Construct the route from the request: the route's classes, pass by pass, until the route
    itself constructs, holding the request and the reply.

    Each pass asks Pydantic for every class not yet in the run, from the instances its fields
    name; a class whose refusal is ``missing`` only is not ready; any other refusal, and a
    library kind's exception, propagates. The pass's actions are performed together, across
    the parent run and its children, and each record enters the run it was asked from. A pass
    that constructs nothing raises a ``ValidationError`` naming the fields no class fills."""
    with tracer.start_as_current_span(
        route.__name__, attributes={"tca.request": type(request).__name__}
    ) as span:
        return await constructed(route, request, config, program, span)


async def constructed(
    route: type[Route[Request, Reply[Fact]]],
    request: Request,
    config: Config,
    program: ModuleType,
    span: trace.Span,
) -> Route[Request, Reply[Fact]]:
    """The body of ``answer``, inside its span."""
    once, per = prove(route, program)
    todo = [c for c in built(program) if c in once or c in per]
    run: Run = {}
    run[type(request)] = request
    run.update((type(c), c) for c in connections(config))
    children = fanned(run, request)
    passes = 0
    while route not in run:
        passes += 1
        performed: list[tuple[Action[Connection, Record], Run]] = []
        progress = False
        for scope in [run, *children]:
            for cls in todo:
                if cls in scope:
                    continue
                try:
                    instance = cls.model_validate(
                        supplied(cls, scope, children if scope is run else [])
                    )
                except ValidationError as refusal:
                    if all(error["type"] == "missing" for error in refusal.errors()):
                        continue
                    raise
                progress = True
                scope[cls] = instance
                for name, classes_ in produced(cls).items():
                    value = getattr(instance, name)
                    if type(value) in classes_:
                        scope[type(value)] = value
                if is_performed(instance):
                    performed.append((instance, scope))
        records = await gather(*(performed_in_span(action) for action, _ in performed))
        for (_, scope), record in zip(performed, records, strict=True):
            scope[type(record)] = record
            if scope is run:
                children.extend(fanned(run, record))
        if not progress:
            pending = [
                c for c in todo if c not in run and not any(c in child for child in children)
            ]
            raise ValidationError.from_exception_data(route.__name__, faults(pending, run))
    span.set_attribute("tca.passes", passes)
    return route.model_validate(run[route])
