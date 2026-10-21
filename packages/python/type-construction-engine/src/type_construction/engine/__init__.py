"""The engine: reads a program's classes, proves a route, and answers it.

A program is one module, named by the entry-point group ``type_construction.programs``.
``routes`` and ``config`` read its ``Route`` and ``Config`` subclasses; ``arguments``
reads a route's ``Q`` and ``A`` from its generic parameters; ``hears`` and ``party``
read an action's ``T`` and ``P``.

``prove`` reads a route top-down, from ``A`` through its ``F`` and every field's class,
and returns the classes in the order they can exist; it is cached, so it runs once per
route. Every leaf is the request, a record exactly one action hears, a class exactly one
computed field produces, or an ``Instant`` or ``Identity`` that constructs itself;
anything else is a fault, and every fault is raised at once as a ``ValidationError``
named for the route. A class whose field names an element, a class that a request or a
record holds as ``tuple[E, ...]``, is per element; a class whose field is ``tuple[X, ...]``
of a per-element class collects every element's ``X``.

``connections`` reads a config's connections; ``opened`` opens each once and closes each
once around whatever a server kind runs inside it.

``answer`` runs that order bottom-up: the request is given; a fact, value or action is
``model_validate``d from the instances its fields name once they exist; a per-element
class is constructed once per element, in a child run that sees the parent's instances
and its own element; a computed field that produces a class puts its value into the run,
so a union of constrained scalars chooses which fact can construct; a member of a union
that refuses is skipped; the actions of one level are performed together, across all
elements; a collecting field receives the children's results in element order, validated
by Pydantic as ``tuple[X, ...]``; the reply is ``A(of=F)``. The engine holds no class and
no state beyond the instances of one run.

Every answer is one OpenTelemetry span named for the route, with one child span per performed
action named for the action and carrying the party's and the record's class names; a skipped union
member is an event; a refusal sets the span's status. The engine depends on ``opentelemetry-api``
only; the deployment configures the SDK and the exporter.
"""

from asyncio import gather
from collections import ChainMap
from collections.abc import AsyncGenerator, MutableMapping
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
    Identity,
    Instant,
    Record,
    Reply,
    Request,
    Route,
    Value,
)

__all__ = [
    "answer",
    "config",
    "opened",
    "routes",
]

SELF_CONSTRUCTING = (Instant, Identity)
"""Classes a product's field may name that construct from nothing; the engine never
supplies them."""

type Run = MutableMapping[type[BaseModel], BaseModel]
"""The instances of one run, keyed by class; a child run chains its element over its parent."""

tracer = trace.get_tracer("type_construction.engine")
"""Spans named by the program's classes: one per answer, named for the route, with one child per
performed action, named for the action. Attributes are class names and counts, never contents. With
no SDK configured these are no-ops; the deployment supplies the SDK and the exporter."""


def is_route(cls: type[object]) -> TypeIs[type[Route[Request, Reply[Fact]]]]:
    """Whether a class is a program's route: a strict subclass of ``Route``."""
    return issubclass(cls, Route) and cls is not Route


def is_reply(cls: type[object]) -> TypeIs[type[Reply[Fact]]]:
    """Whether a class is a program's reply: a strict subclass of ``Reply``."""
    return issubclass(cls, Reply) and cls is not Reply


def is_action(cls: type[object]) -> TypeIs[type[Action[Connection, Record]]]:
    """Whether a class is a program's action: a strict subclass of ``Action`` toward a named
    party."""
    return bool(generic(cls)) and issubclass(cls, Action) and cls is not Action


def is_model(cls: object) -> TypeIs[type[BaseModel]]:
    """Whether an annotation is a Pydantic class."""
    return isinstance(cls, type) and issubclass(cls, BaseModel)


def is_built(
    cls: type[BaseModel],
) -> TypeIs[type[Fact] | type[Value] | type[Action[Connection, Record]]]:
    """Whether the run constructs a class from its fields: a fact, a value or an action."""
    return issubclass(cls, (Fact, Value, Action))


def is_performed(instance: BaseModel) -> TypeIs[Action[Connection, Record]]:
    """Whether a constructed instance is an action the engine performs."""
    return isinstance(instance, Action)


def declared(cls: type[object]) -> bool:
    """Whether a class was written in the module, not a parametrization Pydantic registered there.

    ``Says[Catalog, Price]`` appears in the module beside ``Quote``; Pydantic marks it with an
    ``origin``. A class the developer wrote has none."""
    return (
        not issubclass(cls, BaseModel)
        or cls is BaseModel
        or cls.__pydantic_generic_metadata__["origin"] is None
    )


def classes(program: ModuleType) -> list[type[object]]:
    """Every class the program module declares."""
    return [c for c in vars(program).values() if isinstance(c, type) and declared(c)]


def routes(program: ModuleType) -> tuple[type[Route[Request, Reply[Fact]]], ...]:
    """Every ``Route`` subclass the program module declares, in definition order."""
    return tuple(c for c in classes(program) if is_route(c))


def config(program: ModuleType) -> type[Config]:
    """The one ``Config`` subclass the program module declares."""
    return next(c for c in classes(program) if issubclass(c, Config) and c is not Config)


def made_from(reply: type[Reply[Fact]]) -> type[Fact]:
    """The fact a reply declares as ``Reply[F]``."""
    (fact,) = resolved(reply, Reply)
    assert isinstance(fact, type) and issubclass(fact, Fact)
    return fact


def members(annotation: object) -> tuple[object, ...]:
    """A union's members, or the one annotation."""
    return get_args(annotation) if get_origin(annotation) in (UnionType, Union) else (annotation,)


@asynccontextmanager
async def opened(deployment: Config) -> AsyncGenerator[None]:
    """Open every connection once before the body and close every one once after it, last
    opened first."""
    held = connections(deployment)
    for connection in held:
        await connection.open()
    try:
        yield
    finally:
        for connection in reversed(held):
            await connection.close()


async def performed_in_span(action: Action[Connection, Record]) -> Record:
    """Perform one action inside a span named for it, carrying the party's and the record's
    class names."""
    with tracer.start_as_current_span(
        type(action).__name__,
        attributes={
            "tca.record": hears(type(action)).__name__,
        },
    ):
        return await action.perform()


async def answer(
    route: type[Route[Request, Reply[Fact]]], request: Request, config: Config, program: ModuleType
) -> Reply[Fact]:
    """Construct the route's reply from the request, bottom-up over the proven order.

    Each class is ``model_validate``d from the instances its fields name; a union field takes
    whichever member exists; a member of a union that refuses is skipped, because the holder's
    union is the choice. A per-element class is constructed in one child run per element, which
    sees the parent's instances and its element. A collecting field receives every child's
    instance in element order. A computed field that produces a class puts what it produced into
    its run. An action is performed through its library kind against the config's connection for
    its party; the actions of one level are performed together, across all elements, and each
    record is what came back. The reply is ``A(of=F)``. Any other ``ValidationError``, and a
    library kind's exception, propagates to the caller."""
    with tracer.start_as_current_span(
        route.__name__,
        attributes={
            "tca.request": type(request).__name__,
            "tca.levels": len(levels(route, program)),
        },
    ) as span:
        return await constructed(route, request, config, program, span)


async def constructed(
    route: type[Route[Request, Reply[Fact]]],
    request: Request,
    config: Config,
    program: ModuleType,
    span: trace.Span,
) -> Reply[Fact]:
    """The body of ``answer``, inside its span."""
    _, reply = arguments(route)
    skippable = alternatives(program)
    scope = scopes(route, program)
    given = elements(program)
    parties = {type(connection): connection for connection in connections(config)}
    run: Run = {type(request): request}
    children: dict[type[BaseModel], list[Run]] = {}

    def runs_for(element: type[BaseModel] | None) -> list[Run]:
        """The runs a class is constructed in: the one run, or one child per element, each
        chaining its element over the parent."""
        if element is None:
            return [run]
        if element not in children:
            holder, field = given[element]
            children[element] = [
                ChainMap({type(item): item}, run)
                for item in getattr(run[holder], field)
                if isinstance(item, BaseModel)
            ]
        return children[element]

    def gathered(options: tuple[type[BaseModel], ...]) -> tuple[BaseModel, ...]:
        """Every child's instance of a collected class, in element order, for a
        ``tuple[X, ...]`` field."""
        element = next(scope[o] for o in options if scope.get(o) is not None)
        assert element is not None
        return tuple(child[o] for child in runs_for(element) for o in options if o in child)

    for level in levels(route, program):
        performed: list[tuple[Action[Connection, Record], Run]] = []
        for cls in level:
            for scope_run in runs_for(scope.get(cls)):
                held: dict[str, BaseModel | tuple[BaseModel, ...]] = {
                    name: scope_run[next(o for o in options if o in scope_run)]
                    for name, options in needs(cls).items()
                    if any(o in scope_run for o in options)
                }
                held.update({name: gathered(options) for name, options in collects(cls).items()})
                try:
                    instance = cls.model_validate(held)
                except ValidationError:
                    if cls in skippable:
                        span.add_event("skipped", {"tca.class": cls.__name__})
                        continue
                    raise
                scope_run[cls] = instance
                for name, options in produces(cls).items():
                    value = getattr(instance, name)
                    if type(value) in options:
                        scope_run[type(value)] = value
                if is_performed(instance):
                    performed.append((instance, scope_run))
        heard = await gather(
            *(performed_in_span(action, parties[party(type(action))]) for action, _ in performed)
        )
        for (action, scope_run), record in zip(performed, heard, strict=True):
            scope_run[hears(type(action))] = record
    return reply.model_validate({"of": run[made_from(reply)]})
