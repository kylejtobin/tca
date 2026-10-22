"""Runs a program's route from the command line.

The command line is the request's type. One subcommand per route, named from the route class,
``RequoteSku`` as ``requote-sku``. The options are read from the request class with the
engine's own reads, ``holds`` and ``collects``: a scalar is one option with its class name as
the metavar, the field's docstring as help and its root's bounds after it, and its members as
choices when the root is an enumeration; a value is one dotted option per field,
``--place.city``; a tuple repeats, ``--tags gift --tags rush``, taking one JSON object per
repeat when its elements are values. The parsed options are read back into the tree the
request validates from, with ``Q.model_validate(tree, strict=False)``, the lenient mode for a
text edge; the class stays strict in code, and a field that was not given is reported by
Pydantic as ``missing``. Connections come from the environment and ``.env`` through the
program's ``Config``, whose variables the program's help lists the same way. The reply's
computed fields are printed as JSON.

The program is proven before anything is listed or run; a program that does not prove, a
request that does not construct, a deployment with a variable missing, a run that stalls, or a
reply whose word refuses prints the ``ValidationError`` to standard error and exits 1. A route
that does not exist exits 2. Two routes that would share a command are refused at startup.

The program is the module the project file names under
``[project.entry-points."type_construction.programs"]``; the entry's name is the command and
its value is the module's import path.
"""

import asyncio
import json
import sys
from argparse import SUPPRESS, ArgumentParser
from collections.abc import Iterator, Mapping
from decimal import Decimal
from enum import Enum
from importlib import import_module
from importlib.metadata import entry_points
from pathlib import Path
from types import ModuleType
from typing import Annotated, get_args, get_origin

from annotated_types import Ge, Gt, Le, Lt, MaxLen, MinLen
from pydantic import BaseModel, RootModel, ValidationError
from pydantic.alias_generators import to_snake
from pydantic_core import InitErrorDetails, PydanticCustomError, PydanticSerializationError

from type_construction.engine import (
    Proof,
    answer,
    asked,
    collects,
    config,
    holds,
    opened,
    proven,
)
from type_construction.world import Config, Fact, Reply, Request, Route

__all__ = ["Given", "commands", "exits", "main", "ran", "tree", "usage"]

GROUP = "type_construction.programs"
"""The entry-point group a program registers under; the entry's name is the command."""

type Tree = dict[str, "Tree | str | list[object]"]
"""The parsed options as nested dicts of text, the shape ``Request.model_validate`` takes."""

type Given = dict[str, str | list[object]]
"""What argparse parsed, by dotted key: text for an option, a list for a repeated one."""


def is_enum(cls: object) -> bool:
    """Whether an annotation is an enumeration."""
    return isinstance(cls, type) and issubclass(cls, Enum)


def is_scalar(cls: type[BaseModel]) -> bool:
    """Whether a class is one over a root value."""
    return issubclass(cls, RootModel)


def named(annotation: object) -> str:
    """The name of a root's type, for help: ``str`` for a string, ``HttpUrl`` for an address;
    an ``Annotated`` type is named by what it annotates."""
    inner = get_args(annotation)[0] if get_origin(annotation) is Annotated else annotation
    return getattr(inner, "__name__", str(inner))


def bounds(cls: type[BaseModel]) -> tuple[str, ...]:
    """What to show after a scalar's description: each bound on its root, from the ``Field``
    metadata, or the root's type when it is not a primitive the shell reads as text."""
    field = cls.model_fields["root"]
    found: list[str] = []
    for meta in field.metadata:
        match meta:
            case Gt(gt=v):
                found.append(f"> {v}")
            case Ge(ge=v):
                found.append(f">= {v}")
            case Lt(lt=v):
                found.append(f"< {v}")
            case Le(le=v):
                found.append(f"<= {v}")
            case MinLen(min_length=n):
                found.append(f"min length {n}")
            case MaxLen(max_length=n):
                found.append(f"max length {n}")
            case _:
                pass
    if field.annotation not in (str, int, bool, Decimal) and not is_enum(field.annotation):
        found.append(named(field.annotation))
    return tuple(found)


def choices(cls: type[BaseModel]) -> list[str] | None:
    """The members of a scalar whose root is an enumeration, else nothing."""
    root = cls.model_fields["root"].annotation
    if isinstance(root, type) and issubclass(root, Enum):
        return [str(member.value) for member in root]
    return None


def helped(text: str, cls: type[BaseModel]) -> str:
    """The help line of one option: the field's description, or the class's docstring, then the
    bounds in parentheses."""
    first = (text or cls.__doc__ or "").strip().splitlines()
    found = bounds(cls) if is_scalar(cls) else ()
    suffix = f"({', '.join(found)})" if found else ""
    return f"{first[0] if first else ''} {suffix}".strip()


def flag(key: str) -> str:
    """The option for a dotted key: ``--ship-to.city`` for ``ship_to.city``."""
    return f"--{key.replace('_', '-')}"


def option(built: ArgumentParser, key: str, cls: type[BaseModel], text: str) -> None:
    """Add the options for one single field: a scalar is one option, a value is one dotted
    option per field."""
    if is_scalar(cls):
        built.add_argument(
            flag(key),
            dest=key,
            default=SUPPRESS,
            choices=choices(cls),
            metavar=None if choices(cls) else cls.__name__.upper(),
            help=helped(text, cls),
        )
        return
    for name, field in cls.model_fields.items():
        for held in (c for c in (field.annotation,) if isinstance(c, type)):
            if issubclass(held, BaseModel):
                option(built, f"{key}.{name}", held, field.description or "")
            elif issubclass(held, Enum):
                enumerated(built, f"{key}.{name}", held, field.description or "")


def enumerated(built: ArgumentParser, key: str, cls: type[Enum], text: str) -> None:
    """One option whose choices are an enumeration's members."""
    built.add_argument(
        flag(key),
        dest=key,
        default=SUPPRESS,
        choices=[str(member.value) for member in cls],
        help=text or (cls.__doc__ or "").strip(),
    )


def repeated(built: ArgumentParser, key: str, cls: type[BaseModel], text: str) -> None:
    """One option that may be given more than once, one element per repeat: a scalar's text, or
    one JSON object for a value, since argv cannot nest a repeat."""
    if is_scalar(cls):
        built.add_argument(
            flag(key),
            dest=key,
            action="append",
            default=SUPPRESS,
            choices=choices(cls),
            metavar=None if choices(cls) else cls.__name__.upper(),
            help=helped(text, cls),
        )
        return
    built.add_argument(
        flag(key),
        dest=key,
        action="append",
        default=SUPPRESS,
        type=json.loads,
        metavar="JSON",
        help=helped(text, cls),
    )


def options(built: ArgumentParser, request: type[BaseModel]) -> None:
    """Add every option of a request to a parser: its single fields, and its tuple fields as
    repeated options."""
    for name, field in request.model_fields.items():
        text = field.description or ""
        annotation = field.annotation
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            option(built, name, annotation, text)
        elif isinstance(annotation, type) and issubclass(annotation, Enum):
            enumerated(built, name, annotation, text)
    for name, classes_ in collects(request).items():
        for cls in classes_:
            repeated(built, name, cls, request.model_fields[name].description or "")


def entries(given: Given, key: str, cls: type[BaseModel]) -> Tree:
    """What was given for one single field, as the entries it contributes to its parent's tree:
    the text for a scalar, the nested dict for a value, nothing when not given."""
    leaf = key.rsplit(".", 1)[-1]
    if is_scalar(cls):
        return {leaf: given[key]} if key in given else {}
    merged: Tree = {}
    for name, classes_ in holds(cls).items():
        for held in classes_:
            merged.update(entries(given, f"{key}.{name}", held))
        if not classes_ and f"{key}.{name}" in given:
            merged[name] = given[f"{key}.{name}"]
    return {leaf: merged} if merged else {}


def tree(given: Given, request: type[BaseModel]) -> Tree:
    """The parsed options as the nested dict the request validates from; a field not given is
    absent."""
    found: Tree = {}
    for name, classes_ in holds(request).items():
        for held in classes_:
            found.update(entries(given, name, held))
        if not classes_ and name in given:
            found[name] = given[name]
    for name in collects(request):
        if name in given:
            found[name] = given[name]
    return found


def variables(cls: type[BaseModel], prefix: str) -> Iterator[tuple[str, str]]:
    """Each environment variable a config or a connection reads, with its help: a setting is
    one variable, a connection nests its settings under its key with ``__``."""
    for name, field in cls.model_fields.items():
        key = f"{prefix}{name}".upper()
        for held in (c for c in (field.annotation,) if isinstance(c, type)):
            if issubclass(held, BaseModel) and is_scalar(held):
                yield key, helped(field.description or "", held)
            elif issubclass(held, BaseModel):
                yield from variables(held, f"{key}__")


def program(name: str) -> ModuleType:
    """The program module registered under ``name`` in the entry-point group, imported by the
    entry's module path."""
    return import_module(entry_points(group=GROUP)[name].module)


def command(route: type[Route[Request, Reply[Fact]]]) -> str:
    """The route's name on the command line: ``RequoteSku`` is ``requote-sku``."""
    return to_snake(route.__name__).replace("_", "-")


def commands(proof: Proof) -> dict[str, type[Route[Request, Reply[Fact]]]]:
    """Each command and its route; two routes that would share a command are refused."""
    table: dict[str, type[Route[Request, Reply[Fact]]]] = {}
    details: list[InitErrorDetails] = []
    for route in proof.routes:
        if (name := command(route)) in table:
            details.append(
                InitErrorDetails(
                    type=PydanticCustomError(
                        "command",
                        "{a} and {b} would both be the command {name}",
                        {"a": table[name].__name__, "b": route.__name__, "name": name},
                    ),
                    loc=(route.__name__,),
                    input=route.__name__,
                )
            )
        table[name] = route
    if details:
        raise ValidationError.from_exception_data(proof.program, details)
    return table


def usage(
    prog: str, table: Mapping[str, type[Route[Request, Reply[Fact]]]], deployment: type[Config]
) -> str:
    """The program's routes with their docstrings, and the environment variables its config
    reads."""
    env = list(variables(deployment, ""))
    width = max(len(name) for name in [*table, *(name for name, _ in env)])
    lines = [f"usage: {prog} <route> [options]", "", "routes:"]
    lines += [f"  {name:<{width}}  {route.__doc__ or ''}".rstrip() for name, route in table.items()]
    lines += ["", "environment:"]
    lines += [f"  {name:<{width}}  {text}".rstrip() for name, text in env]
    return "\n".join(lines)


def main(argv: list[str] | None = None, name: str | None = None) -> int:
    """Run one route of the program named by the command, or list the routes."""
    args = sys.argv[1:] if argv is None else argv
    prog = Path(sys.argv[0]).name if name is None else name
    return exits(prog, args, program(prog))


def exits(prog: str, args: list[str], module: ModuleType) -> int:
    """``ran`` with its refusals printed: a ``ValidationError`` anywhere, from the proof, the
    request, the deployment, a party's answer, a stalled run or a reply's word, is printed to
    standard error with exit code 1. A party's own exception propagates in the
    ``ExceptionGroup`` the engine raised it in."""
    try:
        return ran(prog, args, module)
    except (ValidationError, PydanticSerializationError) as refusal:
        print(refusal, file=sys.stderr)
        return 1
    except ExceptionGroup as group:
        refusals, others = group.split(ValidationError)
        if refusals is None or others is not None:
            raise
        for refusal in refusals.exceptions:
            print(refusal, file=sys.stderr)
        return 1


def ran(prog: str, args: list[str], module: ModuleType) -> int:
    """The body of ``main``: prove the program, then list the routes or run one."""
    proof = proven(module)
    table = commands(proof)
    deployment = config(module)
    if not args or args[0] in ("-h", "--help"):
        print(usage(prog, table, deployment))
        return 0
    if args[0] not in table:
        print(usage(prog, table, deployment), file=sys.stderr)
        return 2
    route = table[args[0]]
    request_cls = asked(route)
    built = ArgumentParser(prog=f"{prog} {args[0]}", description=request_cls.__doc__)
    options(built, request_cls)
    namespace = built.parse_args(args[1:])
    request = request_cls.model_validate(tree(vars(namespace), request_cls), strict=False)
    answered = asyncio.run(run(route, request, deployment(), proof))
    print(answered.reply.model_dump_json())
    return 0


async def run(
    route: type[Route[Request, Reply[Fact]]],
    request: Request,
    deployment: Config,
    proof: Proof,
) -> Route[Request, Reply[Fact]]:
    """One answer with every connection opened before it and closed after it."""
    async with opened(deployment):
        return await answer(route, request, deployment, proof)
