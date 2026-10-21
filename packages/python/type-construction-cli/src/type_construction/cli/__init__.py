"""Runs a program's route from the command line.

``shop checkout --sku tea --quantity 3`` runs the route ``Checkout`` of the program
registered as ``shop``. The options are rendered from the request's JSON schema,
``Q.model_json_schema()``, the document FastAPI publishes as OpenAPI. The schema is
parsed once into the node classes below; a discriminator chooses each node's class from
the keys it carries, and each node knows how it renders: a primitive is one option with its
title as metavar, its description and bounds as help, and its ``enum`` as choices; an
object is dotted options, ``--ship-to.city``; an array repeats, ``--tags gift --tags
rush``, taking one JSON object per repeat when its items are objects. The option tree is
validated with ``Q.model_validate(tree, strict=False)``, the lenient mode for a text
edge; the class stays strict in code. Connections come from the environment and
``.env`` through the program's ``Config``. The reply's computed fields are printed as
JSON.

``shop`` or ``shop --help`` lists the routes with their docstrings and the environment
variables the config reads. ``shop checkout --help`` lists the request's options. A
request that does not construct, or a deployment with a variable missing, prints the
``ValidationError`` to standard error and exits 1. A route that does not exist exits 2.

The program is the module the project file names under
``[project.entry-points."type_construction.programs"]``; the entry's name is the command.
"""

import asyncio
import json
import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Iterator
from decimal import Decimal
from importlib.metadata import entry_points
from pathlib import Path
from types import ModuleType
from typing import Annotated, Literal, TypeIs

from pydantic import (
    BaseModel,
    ConfigDict,
    Discriminator,
    Field,
    Tag,
    ValidationError,
    computed_field,
)
from pydantic.alias_generators import to_snake

from type_construction.engine import answer, arguments, config, opened, routes
from type_construction.world import Config, Fact, Record, Reply, Request, Route

__all__ = ["main"]

GROUP = "type_construction.programs"
"""The entry-point group a program registers under; the entry's name is the command."""

type Tree = dict[str, "Tree | str | list[object]"]
"""The parsed options as nested dicts of text, the shape ``Request.model_validate`` takes."""


class Node(Record):
    """A node of a JSON schema, under Pydantic's schema generator's names; keys not read are
    ignored.

    Each kind of node renders itself: ``option`` adds the options for one property,
    ``repeated`` adds the option for one array element, ``variables`` yields the
    environment variables a config property reads."""

    model_config = ConfigDict(extra="ignore")
    title: str = ""
    description: str = ""

    def option(
        self, schema: Schema, built: ArgumentParser, key: str, text: str, required: bool
    ) -> None:
        """Add the options for the property at ``key``; ``text`` is the property's own
        description, if any."""
        raise NotImplementedError

    def repeated(self, schema: Schema, built: ArgumentParser, key: str, text: str) -> None:
        """Add the one repeated option for an array whose elements are this node."""
        raise NotImplementedError

    def variables(self, schema: Schema, key: str, text: str) -> Iterator[tuple[str, str]]:
        """Yield each environment variable under ``key`` that a config property of this node
        reads, with its help."""
        raise NotImplementedError


class Reference(Node):
    """A property that points at a definition: ``{"$ref": "#/$defs/Sku"}``; renders as its
    target."""

    ref: str = Field(alias="$ref")

    @computed_field
    @property
    def name(self) -> str:
        """The definition's key in ``$defs``: the class name of the scalar or value."""
        return self.ref.rsplit("/", 1)[-1]

    def option(
        self, schema: Schema, built: ArgumentParser, key: str, text: str, required: bool
    ) -> None:
        """Render the definition this reference points at, under the property's description."""
        schema.defs[self.name].option(schema, built, key, text or self.description, required)

    def repeated(self, schema: Schema, built: ArgumentParser, key: str, text: str) -> None:
        """Render the definition this reference points at as the element of an array."""
        schema.defs[self.name].repeated(schema, built, key, text or self.description)

    def variables(self, schema: Schema, key: str, text: str) -> Iterator[tuple[str, str]]:
        """The variables of the definition this reference points at."""
        return schema.defs[self.name].variables(schema, key, text or self.description)


class Primitive(Node):
    """A value of one JSON type, with the bounds Pydantic wrote for its constraints and its
    ``enum`` if closed."""

    type: Literal["string", "integer", "number", "boolean"]
    """The JSON type Pydantic wrote for the scalar's root: ``str``, ``int``, ``float``, ``bool``."""
    format: str = ""
    """Pydantic's name for a well-known string form: ``uri`` for ``HttpUrl``, ``password`` for
    ``SecretStr``."""
    enum: tuple[str, ...] = ()
    """The members of a ``StrEnum`` field; empty for any other value."""
    exclusive_minimum: Decimal | None = Field(
        None, alias="exclusiveMinimum", description="From Field(gt=...) on the scalar."
    )
    minimum: Decimal | None = Field(None, description="From Field(ge=...) on the scalar.")
    exclusive_maximum: Decimal | None = Field(
        None, alias="exclusiveMaximum", description="From Field(lt=...) on the scalar."
    )
    maximum: Decimal | None = Field(None, description="From Field(le=...) on the scalar.")
    min_length: int | None = Field(
        None, alias="minLength", description="From Field(min_length=...) on the scalar."
    )
    max_length: int | None = Field(
        None, alias="maxLength", description="From Field(max_length=...) on the scalar."
    )
    pattern: str | None = Field(None, description="From Field(pattern=...) on the scalar.")

    @computed_field
    @property
    def bounds(self) -> tuple[str, ...]:
        """What to show after the description: the format alone when there is one, else each
        bound."""
        if self.format:
            return (self.format,)
        pairs = (
            (">", self.exclusive_minimum),
            (">=", self.minimum),
            ("<", self.exclusive_maximum),
            ("<=", self.maximum),
            ("min length", self.min_length),
            ("max length", self.max_length),
            ("pattern", self.pattern),
        )
        return tuple(f"{word} {value}" for word, value in pairs if value is not None)

    @computed_field
    @property
    def metavar(self) -> str:
        """The value's name in usage lines: the scalar's class name, else its JSON type, in
        upper case."""
        return (self.title or self.type).upper()

    def help(self, text: str) -> str:
        """The help line: the description, then the bounds in parentheses."""
        suffix = f"({', '.join(self.bounds)})" if self.bounds else ""
        return f"{text or self.description} {suffix}".strip()

    def option(
        self, schema: Schema, built: ArgumentParser, key: str, text: str, required: bool
    ) -> None:
        """One option: required as the schema says, choices from ``enum``, metavar from the
        title, help from the description and bounds."""
        built.add_argument(
            f"--{key.replace('_', '-')}",
            dest=key,
            required=required,
            choices=list(self.enum) or None,
            metavar=None if self.enum else self.metavar,
            help=self.help(text),
        )

    def repeated(self, schema: Schema, built: ArgumentParser, key: str, text: str) -> None:
        """One option that may be given more than once, one element per repeat."""
        built.add_argument(
            f"--{key.replace('_', '-')}",
            dest=key,
            action="append",
            choices=list(self.enum) or None,
            metavar=None if self.enum else self.metavar,
            help=self.help(text),
        )

    def variables(self, schema: Schema, key: str, text: str) -> Iterator[tuple[str, str]]:
        """One environment variable: this key, with the description and bounds as help."""
        yield key, self.help(text)


class AnyOf(Node):
    """A value with more than one JSON form, as Pydantic writes ``Decimal``: a number or a
    string; renders as the first."""

    any_of: tuple[Primitive, ...] = Field(alias="anyOf")

    def option(
        self, schema: Schema, built: ArgumentParser, key: str, text: str, required: bool
    ) -> None:
        """Render the first form; for ``Decimal`` that is the number with its bounds."""
        self.any_of[0].option(schema, built, key, text or self.description, required)

    def repeated(self, schema: Schema, built: ArgumentParser, key: str, text: str) -> None:
        """Render the first form as the element of an array."""
        self.any_of[0].repeated(schema, built, key, text or self.description)

    def variables(self, schema: Schema, key: str, text: str) -> Iterator[tuple[str, str]]:
        """The first form's variable."""
        return self.any_of[0].variables(schema, key, text or self.description)


class Array(Node):
    """Several of one thing, ``tuple[T, ...]``: the option repeats, once per element."""

    type: Literal["array"]
    items: Member

    def option(
        self, schema: Schema, built: ArgumentParser, key: str, text: str, required: bool
    ) -> None:
        """The repeated option of the element, since an array is given one element per repeat."""
        self.items.repeated(schema, built, key, text or self.description)


class Object(Node):
    """A thing with fields, a ``Value`` or the request itself: one dotted option per field; as
    an element, one JSON object."""

    type: Literal["object"]
    properties: dict[str, Member]
    required: tuple[str, ...] = ()

    def option(
        self, schema: Schema, built: ArgumentParser, key: str, text: str, required: bool
    ) -> None:
        """One dotted option per field, ``--key.field``, each required as this object says."""
        for name, prop in self.properties.items():
            prop.option(schema, built, f"{key}.{name}", "", name in self.required)

    def repeated(self, schema: Schema, built: ArgumentParser, key: str, text: str) -> None:
        """One repeated option taking a JSON object per element, since argv cannot nest a repeat."""
        built.add_argument(
            f"--{key.replace('_', '-')}",
            dest=key,
            action="append",
            type=json.loads,
            metavar="JSON",
            help=text or self.description,
        )

    def variables(self, schema: Schema, key: str, text: str) -> Iterator[tuple[str, str]]:
        """The variables of each field, nested under this key with ``__``."""
        for name, prop in self.properties.items():
            yield from prop.variables(schema, f"{key}__{name}".upper(), "")


class Schema(Object):
    """A request's or a config's whole schema: its properties and the definitions they refer to."""

    defs: dict[str, Member] = Field(alias="$defs", default_factory=dict)

    def options(self, built: ArgumentParser) -> None:
        """Add every option of a request to a parser."""
        for name, prop in self.properties.items():
            prop.option(self, built, name, "", name in self.required)

    def environment(self) -> Iterator[tuple[str, str]]:
        """Yield every environment variable a config reads, with its help."""
        for name, prop in self.properties.items():
            yield from prop.variables(self, name.upper(), "")


def is_schema(value: object) -> TypeIs[dict[str, object]]:
    """Whether a value is a JSON schema object."""
    return isinstance(value, dict)


SHAPES: dict[type[object], str] = {
    Reference: "ref",
    Object: "object",
    Array: "array",
    AnyOf: "anyOf",
}
"""Each node class's tag, for serialization, where the discriminator sees an instance."""


def shape(node: object) -> str:
    """Which kind of node a schema object is, from the keys it carries; the discriminator for
    ``Member``."""
    if is_schema(node):
        if "$ref" in node:
            return "ref"
        if "anyOf" in node:
            return "anyOf"
        kind = node.get("type")
        return "object" if kind == "object" else "array" if kind == "array" else "primitive"
    return SHAPES.get(type(node), "primitive")


type Member = Annotated[
    Annotated[Reference, Tag("ref")]
    | Annotated[Object, Tag("object")]
    | Annotated[Array, Tag("array")]
    | Annotated[AnyOf, Tag("anyOf")]
    | Annotated[Primitive, Tag("primitive")],
    Discriminator(shape),
]
"""The kinds of node, chosen by ``shape`` from the keys a node carries: ``$ref``, ``anyOf``,
``type`` object or array, else a primitive."""

Array.model_rebuild()
Object.model_rebuild()
Schema.model_rebuild()


def schema(model: type[BaseModel]) -> Schema:
    """A model's JSON schema, parsed into nodes; the document is data, so it is validated
    leniently."""
    return Schema.model_validate(model.model_json_schema(), strict=False)


def program(name: str) -> ModuleType:
    """The program module registered under ``name`` in the entry-point group."""
    module = entry_points(group=GROUP)[name].load()
    assert isinstance(module, ModuleType)
    return module


def command(route: type[Route[Request, Reply[Fact]]]) -> str:
    """The route's name on the command line: ``RequoteSku`` is ``requote-sku``."""
    return to_snake(route.__name__).replace("_", "-")


def parser(prog: str, request: type[Request]) -> ArgumentParser:
    """The command line of one route, rendered from its request's schema."""
    built = ArgumentParser(prog=prog, description=request.__doc__)
    schema(request).options(built)
    return built


def tree(namespace: Namespace) -> Tree:
    """The parsed options as the nested dict the request validates from; absent options are
    omitted."""
    root: Tree = {}
    for key, value in vars(namespace).items():
        if value is None:
            continue
        node = root
        *path, leaf = key.split(".")
        for step in path:
            child = node.setdefault(step, {})
            assert isinstance(child, dict)
            node = child
        node[leaf] = value
    return root


def usage(
    prog: str, table: dict[str, type[Route[Request, Reply[Fact]]]], deployment: type[Config]
) -> str:
    """The program's routes with their docstrings, and the environment variables its config
    reads."""
    env = list(schema(deployment).environment())
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
    module = program(prog)
    table = {command(route): route for route in routes(module)}
    if not args or args[0] in ("-h", "--help"):
        print(usage(prog, table, config(module)))
        return 0
    if args[0] not in table:
        print(usage(prog, table, config(module)), file=sys.stderr)
        return 2
    route = table[args[0]]
    request_cls, _ = arguments(route)
    namespace = parser(f"{prog} {args[0]}", request_cls).parse_args(args[1:])
    try:
        request = request_cls.model_validate(tree(namespace), strict=False)
        deployment = config(module)()
        reply = asyncio.run(run(route, request, deployment, module))
    except ValidationError as error:
        print(error, file=sys.stderr)
        return 1
    print(reply.model_dump_json())
    return 0


async def run(
    route: type[Route[Request, Reply[Fact]]],
    request: Request,
    deployment: Config,
    module: ModuleType,
) -> Reply[Fact]:
    """One answer with every connection opened before it and closed after it."""
    async with opened(deployment):
        return await answer(route, request, deployment, module)
