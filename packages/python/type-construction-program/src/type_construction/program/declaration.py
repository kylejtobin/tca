"""What a business program declares beyond its types, and the construction graph compiled from it.

Pydantic already states a program's composition, constraints, aliases, unions and collections.
A ``Fact``'s required fields are its premises; a union field is a choice; a tuple field is a
collection. What Pydantic cannot state is which external party supplies a ``Record``, how that
party's evidence is tied to one invocation, when a source that delivers items over time has
delivered them all, and, where one class is held at more than one place, which place a premise
is obtained from. Those are declared here, once each, and nothing else is.

An ``Interaction`` is one declared relationship with one ``Source``. It names what the source
can say (``receives``), optionally what this program sends to make it say so (``sends``),
optionally the receipt the source may answer the send with before the result (``acknowledges``),
how a delivery is tied to the invocation (``correlated``), where a premise of the request is
obtained when its class alone does not say (``bound``), and, for a source whose items
accumulate, the evidence that closes it (``closed_by``). Whether a result comes back inside the
sending attempt or in a later delivery is not declared: it is observed, and the premise it
satisfies is the same either way.

A ``Program`` is a goal, the input it accepts, its interactions, and the bindings of the goal's
premises that the classes alone do not determine. Constructing one compiles the goal into a
graph of construction relationships, ``Node``: where a value is found, which source says it,
what it is made from, which alternatives it has, and which collection it is one construction
per element of. A request is compiled where its receive is demanded, so one operation demanded
under two collections is two request nodes. A class is not an occurrence: two places that obtain
a class the same way are one node, and two places that obtain it differently are two. A premise
the declarations obtain no way, or more than one way, is refused when the program is
constructed, naming the places and the declaration that would tell them apart.
"""

import types
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from enum import IntEnum
from functools import cached_property
from typing import Any, Union, get_args, get_origin

from annotated_types import BaseMetadata, Predicate
from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator
from pydantic.fields import FieldInfo

from type_construction.world import Record, Refutable, Scalar

DECLARATION = ConfigDict(
    frozen=True,
    strict=True,
    extra="forbid",
    validate_default=True,
    use_attribute_docstrings=True,
)
"""Configuration for a declaration: strict, frozen, no undeclared fields."""

EACH = "*"
"""The step in a field path that enters each element of a collection."""


class Source(Scalar[str]):
    """An external party the program trusts for what it says: a payment provider, a reviewer
    inbox, the clock. Its name is the admission boundary's label for the party; authenticating
    that a delivery is from the party is the host's work, not declared here."""

    root: str = Field(min_length=1)


class Correlation(BaseModel):
    """One declared equality that ties a received record to the invocation: the value at
    ``received`` on the record equals the value at ``subject`` on the accepted input. A subject
    path that enters a collection with ``*`` ties the record to the one element whose value is
    equal, so the receive varies per element. Equal values elsewhere establish nothing; only a
    declared pair does."""

    model_config = DECLARATION

    received: str
    """Dotted field path on the received record."""
    subject: str
    """Dotted field path on the accepted input; ``*`` enters each element of a collection."""


class Binding(BaseModel):
    """One declared construction relationship the classes alone do not determine: the premise
    at ``premise`` is obtained at ``subject`` on the accepted input.

    It is needed only where a class is held at more than one place, which is a business
    distinction the type does not carry: the two accounts of a transfer are both an ``Account``,
    and which one a debit concerns is declared here, not inferred from a field name or a
    traversal. A premise that is a tuple of a constructed class is bound to the collection it is
    one construction per element of.
    """

    model_config = DECLARATION

    premise: str
    """Dotted path from the request an interaction sends, or from the program's goal: field
    names, ``*`` for the element of a tuple, and a class name for the member of a union."""
    subject: str
    """Dotted field path on the accepted input; ``*`` enters each element of a collection."""


def qualified(kind: type[BaseModel]) -> str:
    """The durable name of a declared class: its module and qualified name."""
    return f"{kind.__module__}.{kind.__qualname__}"


def names(kinds: tuple[type[BaseModel], ...]) -> str:
    """The class names, joined for a message."""
    return " | ".join(kind.__name__ for kind in kinds)


def steps(path: str) -> tuple[str, ...]:
    """A dotted path as its steps."""
    return tuple(path.split("."))


def annotated(info: FieldInfo) -> object:
    """A field's annotation, as the unknown object it is until examined."""
    return info.annotation


def element(annotation: object) -> type[BaseModel] | None:
    """The element class of a tuple annotation over one declared class, or ``None``."""
    shape = collection(annotation)
    return None if shape is None else shape[0]


def collection(annotation: object) -> tuple[type[BaseModel], int | None] | None:
    """The element and fixed count of a tuple annotation over one declared class, or ``None``
    for anything else."""
    if get_origin(annotation) is not tuple:
        return None
    args = get_args(annotation)
    if args[-1:] == (Ellipsis,):
        return (args[0], None)
    if args and all(arg is args[0] for arg in args):
        return (args[0], len(args))
    msg = f"{annotation!r}: a collection premise holds one declared class"
    raise ValueError(msg)


def alternatives(annotation: object) -> tuple[type[BaseModel], ...] | None:
    """The members of a union annotation over declared classes, or ``None``."""
    if get_origin(annotation) in (Union, types.UnionType):
        return get_args(annotation)
    return None


def declared(annotation: object) -> type[BaseModel] | None:
    """The annotation as a declared class, or ``None`` when it is not one."""
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return annotation
    return None


def premises(kind: type[BaseModel]) -> Iterator[tuple[str, Any]]:
    """The required fields of a class and their annotations: its premises. A computed field or
    a field with a default is not a premise."""
    for name, info in kind.model_fields.items():
        if info.is_required() and info.annotation is not None:
            yield name, info.annotation


def constant(kind: type[BaseModel]) -> bool:
    """Whether the class constructs from nothing: no required field."""
    return not any(True for _ in premises(kind))


class Control(IntEnum):
    """What controls whether a premise still open will be refused, which orders effects around
    it. Stronger controls are resolved before effects under weaker ones are dispatched.

    ``NONE``: no decision the evaluator knows of; a value found in admitted evidence, a receive
    with one declared answer, a class the evaluator reads nothing from beyond its field types.
    This is not a claim that the construction will succeed; it is the absence of a controlling
    decision, and a construction that fails is reported when it fails. ``OPAQUE``: a validator,
    computation or revalidation Pydantic will run at construction, which the compiler locates
    but cannot interpret, so its outcome is unproven until the construction runs; it withholds
    effects beside it and grants nothing to effects under it. ``CONSTRAINT``: a native constraint
    Pydantic itself interprets, located on a field, which the evaluator checks as soon as the
    field's value is there. ``DECLARED``: a decision the business stated, a source that may
    answer with another record or a declared refutable condition.
    """

    NONE = 0
    OPAQUE = 1
    CONSTRAINT = 2
    DECLARED = 3


def constraint(metadata: object) -> bool:
    """Whether one piece of field metadata is a constraint Pydantic interprets natively, such as
    a bound or a length, as opposed to a callback it runs."""
    return isinstance(metadata, BaseMetadata) and not isinstance(metadata, Predicate)


def constrained(kind: type[BaseModel]) -> frozenset[str]:
    """The premise fields a native constraint of the class judges: constraint metadata on the
    field, or a fixed-length tuple. The evaluator can apply these to a field's value by itself,
    through Pydantic, as soon as the value is there."""
    fields: set[str] = set()
    for name, info in kind.model_fields.items():
        if any(constraint(m) for m in info.metadata):
            fields.add(name)
        shape = collection(info.annotation)
        if shape is not None and shape[1] is not None:
            fields.add(name)
    return frozenset(fields)


def opaque(kind: type[BaseModel]) -> frozenset[str] | None:
    """The premise fields an opaque part of the class judges at construction, which the compiler
    locates but cannot interpret: a callback in a field's metadata, a ``field_validator`` naming
    the field, a discriminator. ``None`` when the whole model is judged, by a ``model_validator``,
    revalidation of instances, a custom core schema, a post-init hook or a validated default,
    since then no field can be left out. Empty when the class has none of these; that is the
    absence of anything recognized, not a proof that construction succeeds."""
    decorators = kind.__pydantic_decorators__
    if decorators.model_validators or decorators.validators or decorators.root_validators:
        return None
    if kind.model_config.get("revalidate_instances", "never") != "never":
        return None
    for base in kind.__mro__:
        if base is BaseModel or base is RootModel:
            break
        if "__get_pydantic_core_schema__" in vars(base) or "model_post_init" in vars(base):
            return None
    if any(not info.is_required() for info in kind.model_fields.values()):
        return None
    fields: set[str] = set()
    for validator in decorators.field_validators.values():
        if "*" in validator.info.fields:
            return None
        fields.update(validator.info.fields)
    for name, info in kind.model_fields.items():
        if info.discriminator is not None or any(not constraint(m) for m in info.metadata):
            fields.add(name)
    return frozenset(fields)


def contradictory(bindings: tuple[Binding, ...], root: type[BaseModel]) -> None:
    """Refuse two bindings of one premise to different places: the declarations would then say
    two things, and the order they were written in must not decide which."""
    subjects: dict[str, str] = {}
    for binding in bindings:
        earlier = subjects.setdefault(binding.premise, binding.subject)
        if earlier != binding.subject:
            msg = (
                f"{root.__name__}.{binding.premise} is bound to both {earlier} and"
                f" {binding.subject}; one place per premise"
            )
            raise ValueError(msg)


def resolve(kind: type[BaseModel], path: str) -> object:
    """The annotation at a path on a class, entering collections at ``*`` and unions at the
    member's class name, or ``ValueError`` naming what is missing, which a declaration's
    validator reports as its refusal."""
    current: object = kind
    for name in steps(path):
        if name == EACH:
            inner = element(current)
            if inner is None:
                msg = f"{kind.__name__}.{path}: {current!r} is not a collection to enter"
                raise ValueError(msg)
            current = inner
            continue
        members = alternatives(current)
        if members is not None:
            named = [m for m in members if m.__name__ == name]
            if len(named) != 1:
                msg = f"{kind.__name__}.{path}: {current!r} has no member {name}"
                raise ValueError(msg)
            current = named[0]
            continue
        holder = declared(current)
        if holder is None:
            msg = f"{kind.__name__}.{path}: {current!r} has no field {name}"
            raise ValueError(msg)
        info = holder.model_fields.get(name)
        if info is None or info.annotation is None:
            msg = f"{kind.__name__} has no field path {path}"
            raise ValueError(msg)
        current = annotated(info)
    return current


class Interaction(BaseModel):
    """One declared relationship with one external source.

    ``receives`` is what the source can say; one admitted answer satisfies the receive. With
    ``sends``, the program constructs that request from its premises and the host dispatches
    it; without, the receive is unsolicited and waits for a correlated delivery. With
    ``acknowledges``, the source may answer the send with that receipt first and deliver the
    result later; a receipt is recorded against the attempt and satisfies no premise. A
    solicited receive is tied to the invocation by the request it answers; ``correlated``
    equalities are checked as well, and tie a delivery that does not name its request. With
    ``closed_by``, the source says many records and the program holds every one until that
    evidence arrives.
    """

    model_config = DECLARATION

    source: Source
    """The party."""
    receives: tuple[type[BaseModel], ...] = Field(min_length=1)
    """What the party can say: records, one of which satisfies the receive."""
    sends: type[BaseModel] | None = None
    """The request this program constructs and dispatches; ``None`` for an unsolicited
    receive."""
    acknowledges: type[BaseModel] | None = None
    """The receipt the party may answer the send with before the result."""
    correlated: tuple[Correlation, ...] = ()
    """Declared equalities between the received record and the accepted input."""
    bound: tuple[Binding, ...] = ()
    """Where a premise of the request is obtained, when its class alone does not say."""
    closed_by: type[BaseModel] | None = None
    """The evidence after which the source says nothing more; declared, the source says many."""

    @model_validator(mode="after")
    def _coherent(self) -> Interaction:
        for kind in (*self.receives, self.acknowledges, self.closed_by):
            if kind is not None and not issubclass(kind, Record):
                msg = (
                    f"{kind.__name__} is what {self.source.root} says, so it must be a Record,"
                    " what an external party says under that party's names"
                )
                raise ValueError(msg)
        if self.acknowledges is not None and self.sends is None:
            msg = (
                f"{self.acknowledges.__name__} acknowledges a send, and this interaction"
                " sends nothing"
            )
            raise ValueError(msg)
        if self.sends is None and not self.correlated:
            msg = (
                f"an unsolicited {names(self.receives)} from {self.source.root} needs a correlation"
                " to the invocation; without one, an arriving record could belong to any"
                " invocation"
            )
            raise ValueError(msg)
        if self.bound and self.sends is None:
            msg = f"{names(self.receives)} binds a premise of a request, and nothing is sent"
            raise ValueError(msg)
        for correlation in self.correlated:
            for kind in self.receives:
                resolve(kind, correlation.received)
        if self.sends is not None:
            for binding in self.bound:
                resolve(self.sends, binding.premise)
            contradictory(self.bound, self.sends)
        return self

    def says(self, kind: type[BaseModel]) -> bool:
        """Whether the source answers with this kind."""
        return kind in self.receives

    @property
    def many(self) -> bool:
        """Whether the source says many records: a collection source."""
        return self.closed_by is not None


@dataclass(frozen=True)
class Collection:
    """One collection a premise can vary over: a tuple field reached by a path inside a
    container, the accepted input or a received record, or the records a collection source
    says, with an empty path."""

    container: type[BaseModel]
    path: tuple[str, ...]

    def __str__(self) -> str:
        return ".".join((self.container.__name__, *self.path)) + f".{EACH}"


@dataclass(frozen=True)
class Location:
    """Where a premise's value is found: a field path inside a container that is the accepted
    input or a received record. A step ``*`` enters each element of a collection; the location
    then varies over that collection."""

    container: type[BaseModel]
    path: tuple[str, ...]

    def __str__(self) -> str:
        return ".".join((self.container.__name__, *self.path))

    def entered(self) -> frozenset[Collection]:
        """The collections the path enters."""
        return frozenset(
            Collection(self.container, self.path[:k])
            for k, step in enumerate(self.path)
            if step == EACH
        )

    def under(self, over: Collection) -> bool:
        """Whether the location is inside an element of the collection."""
        prefix = (*over.path, EACH)
        return self.container is over.container and self.path[: len(prefix)] == prefix


def found(
    container: type[BaseModel],
    matches: Callable[[object], bool],
    skipped: frozenset[str],
) -> list[tuple[str, ...]]:
    """The field paths inside a container whose annotation matches, searching into nested
    classes and into the elements of collections, not into a value's root, and skipping
    declared paths. A path ending in ``*`` matches the element of a collection."""
    paths: list[tuple[str, ...]] = []

    def search(kind: type[BaseModel], prefix: tuple[str, ...]) -> None:
        for name, info in kind.model_fields.items():
            path = (*prefix, name)
            annotation = annotated(info)
            if ".".join(path) in skipped:
                continue
            if matches(annotation):
                paths.append(path)
                continue
            inner = element(annotation)
            if inner is not None:
                each = (*path, EACH)
                if matches(inner):
                    paths.append(each)
                elif not issubclass(inner, RootModel):
                    search(inner, each)
            elif (holder := declared(annotation)) is not None and not issubclass(holder, RootModel):
                search(holder, path)

    if not issubclass(container, RootModel):
        search(container, ())
    return paths


# --- the construction graph ---------------------------------------------------------------------


@dataclass(frozen=True)
class Found:
    """A value found at a location in the accepted input or in a received record. ``held`` is
    the node that supplies the record when the container is one."""

    location: Location
    held: Node | None = None


@dataclass(frozen=True)
class Heard:
    """One record a source says, through its interaction: the answer to ``request`` when the
    interaction sends one, a correlated delivery when it does not, and one element of what the
    source says when the interaction is a collection source."""

    interaction: Interaction
    kind: type[BaseModel]
    request: Node | None = None


@dataclass(frozen=True)
class Made:
    """A class constructed from its premises, each obtained by its own node."""

    kind: type[BaseModel]
    premises: tuple[tuple[str, Node], ...] = ()


@dataclass(frozen=True)
class Choice:
    """A union: the premise is whichever member holds."""

    members: tuple[tuple[type[BaseModel], Node], ...]


@dataclass(frozen=True)
class All:
    """Every record a collection source says, sealed by the closing evidence ``closer``."""

    interaction: Interaction
    kind: type[BaseModel]
    closer: Node


@dataclass(frozen=True)
class Each:
    """One construction of ``element`` per element of ``over``. When ``over`` is a collection
    source, ``closure`` is the accumulation its tuple is sealed by."""

    element: Node
    over: Collection
    closure: All | None = None
    holder: Node | None = None
    """The node supplying the collection's container, when it is a received record."""


type Node = Found | Heard | Made | Choice | All | Each
"""One construction relationship: how a premise is obtained."""


@dataclass
class Graph:
    """What compiling a program established: the root node, the interactions by the request
    they send, and, per node, the collections it varies over and whether its construction can
    be refuted by evidence still to come."""

    root: Node
    sent: dict[str, Interaction]
    varies: dict[Node, frozenset[Collection]]
    control: dict[Node, Control]
    """Per node, the strongest control over it while open; see ``Control``."""


@dataclass(frozen=True)
class Walk:
    """One pass of the compiler over one root: the bindings declared for premises under it,
    keyed by their path, the classes being constructed above the current premise, and the
    collections bound by the tuples enclosing it."""

    bindings: tuple[tuple[tuple[str, ...], str], ...] = ()
    stack: tuple[object, ...] = ()
    bound: frozenset[Collection] = frozenset()

    def into(self, annotation: object) -> Walk:
        """The walk one premise deeper."""
        return Walk(self.bindings, (*self.stack, annotation), self.bound)

    def binding(self, over: Collection) -> Walk:
        """The walk with one more collection bound."""
        return Walk(self.bindings, self.stack, self.bound | {over})

    def rooted(self, bindings: tuple[Binding, ...]) -> Walk:
        """The walk over a new root, a request, with that root's bindings."""
        return Walk(tuple((steps(b.premise), b.subject) for b in bindings), self.stack, self.bound)

    def subject(self, at: tuple[str, ...]) -> str | None:
        """The subject a premise at this path is bound to, if any."""
        for premise, subject in self.bindings:
            if premise == at:
                return subject
        return None


class Program(BaseModel):
    """A goal, the input it accepts, the interactions that supply what the input does not, and
    the bindings that say where a premise is obtained when its class alone does not.

    Construction compiles the whole into a ``Graph`` and validates it: each received kind is
    declared by one interaction, each sent kind by one; every premise the goal transitively
    needs is obtained one way; a tuple of a constructed class varies over exactly one
    collection; a collection source has a declared closure; correlation and binding paths
    exist; the goal itself does not vary. A program that fails is refused with a message naming
    the premise and the missing business distinction.
    """

    model_config = DECLARATION

    goal: type[BaseModel]
    """The declared outcome."""
    accepts: type[BaseModel]
    """The input an invocation is accepted with."""
    interactions: tuple[Interaction, ...] = ()
    """The declared relationships with external sources."""
    bound: tuple[Binding, ...] = ()
    """Where a premise of the goal is obtained, when its class alone does not say."""

    @model_validator(mode="after")
    def _sound(self) -> Program:
        seen: dict[type[BaseModel], Interaction] = {}
        for interaction in self.interactions:
            for kind in interaction.receives:
                if kind in seen:
                    msg = (
                        f"{kind.__name__} is received from both {seen[kind].source.root} and"
                        f" {interaction.source.root}; one declared source per record"
                    )
                    raise ValueError(msg)
                seen[kind] = interaction
            for correlation in interaction.correlated:
                resolve(self.accepts, correlation.subject)
            for binding in interaction.bound:
                resolve(self.accepts, binding.subject)
        sent = [i.sends for i in self.interactions if i.sends is not None]
        if len(set(sent)) != len(sent):
            msg = (
                "two interactions send the same request class; a sent class identifies its"
                " interaction"
            )
            raise ValueError(msg)
        for interaction in self.interactions:
            if interaction.closed_by is not None and interaction.closed_by not in seen:
                msg = (
                    f"{interaction.closed_by.__name__} closes {names(interaction.receives)} but"
                    " no interaction receives it"
                )
                raise ValueError(msg)
        for binding in self.bound:
            resolve(self.goal, binding.premise)
            resolve(self.accepts, binding.subject)
        contradictory(self.bound, self.goal)
        for interaction in self.interactions:
            self.element_collection(interaction)
        varies = self.graph.varies[self.graph.root]
        if varies:
            over = " and ".join(sorted(str(c) for c in varies))
            msg = (
                f"{self.goal.__name__} varies per element of {over}; the goal is one"
                " conclusion, so hold what varies as a tuple"
            )
            raise ValueError(msg)
        return self

    def receiving(self, kind: type[BaseModel]) -> Interaction | None:
        """The interaction whose source says this kind, if any."""
        for interaction in self.interactions:
            if interaction.says(kind):
                return interaction
        return None

    def sending(self, operation: str) -> Interaction | None:
        """The interaction that sends the request class with this durable name."""
        return self.graph.sent.get(operation)

    def subject_collections(self, correlation: Correlation) -> frozenset[Collection]:
        """The collections a correlation's subject path enters."""
        return Location(self.accepts, steps(correlation.subject)).entered()

    def element_collection(self, interaction: Interaction) -> Collection | None:
        """The one collection a receive varies over through its correlation, if any."""
        entered: set[Collection] = set()
        for correlation in interaction.correlated:
            entered |= self.subject_collections(correlation)
        if len(entered) > 1:
            over = " and ".join(sorted(str(c) for c in entered))
            msg = f"{names(interaction.receives)} correlates into {over}; one collection at most"
            raise ValueError(msg)
        return next(iter(entered), None)

    @cached_property
    def graph(self) -> Graph:
        """The compiled construction graph; raises ``ValueError`` for a premise the program
        does not obtain one way."""
        return Compiler(self).compiled()

    def _correlated(self, container: type[BaseModel]) -> frozenset[str]:
        """The field paths on a received container that correlation declares equal to the
        input, so that they are not a second location of the value."""
        interaction = self.receiving(container)
        if interaction is None:
            return frozenset()
        return frozenset(c.received for c in interaction.correlated)

    def locations(self, matches: Callable[[object], bool]) -> list[Location]:
        """Where an annotation is found: in the input, or in a received record."""
        locations = [
            Location(self.accepts, path) for path in found(self.accepts, matches, frozenset())
        ]
        for interaction in self.interactions:
            for container in interaction.receives:
                paths = found(container, matches, self._correlated(container))
                locations.extend(Location(container, path) for path in paths)
        return locations


class Compiler:
    """One compilation of one program's goal into its construction graph."""

    def __init__(self, program: Program) -> None:
        self.program = program
        self.varies: dict[Node, frozenset[Collection]] = {}
        self.control: dict[Node, Control] = {}

    def compiled(self) -> Graph:
        program = self.program
        sent = {qualified(i.sends): i for i in program.interactions if i.sends is not None}
        walk = Walk(tuple((steps(b.premise), b.subject) for b in program.bound))
        root = self.compile(program.goal, (), program.goal.__name__, walk)
        return Graph(root, sent, self.varies, self.control)

    def record(self, node: Node, varies: frozenset[Collection], control: Control) -> Node:
        self.varies[node] = varies
        self.control[node] = control
        return node

    def compile(self, annotation: object, at: tuple[str, ...], path: str, walk: Walk) -> Node:
        """Compile one premise annotation at its path under the current root."""
        if annotation in walk.stack:
            msg = f"{path}: {annotation!r} is constructed from itself with no evidence between"
            raise ValueError(msg)
        subject = walk.subject(at)
        if subject is not None:
            return self.bound(annotation, subject, at, path, walk)
        deeper = walk.into(annotation)
        members = alternatives(annotation)
        if members is not None:
            compiled = tuple(
                (m, self.compile(m, (*at, m.__name__), f"{path}.{m.__name__}", deeper))
                for m in members
            )
            node = Choice(compiled)
            varies = frozenset[Collection]().union(*(self.varies[n] for _, n in compiled))
            control = min(self.control[n] for _, n in compiled)
            return self.record(node, varies, control)
        shape = collection(annotation)
        if shape is not None:
            return self.many(shape[0], at, path, deeper)
        kind = declared(annotation)
        if kind is None:
            msg = (
                f"{path}: a premise is a declared class, a union of them, or a tuple of one;"
                f" {annotation!r} is none"
            )
            raise ValueError(msg)
        return self.one(kind, at, path, deeper)

    def bound(
        self, annotation: object, subject: str, at: tuple[str, ...], path: str, walk: Walk
    ) -> Node:
        """A premise bound by declaration to a place in the accepted input: the value there, or
        the collection a tuple of a constructed class is one construction per element of."""
        accepts = self.program.accepts
        there = resolve(accepts, subject)
        shape = collection(annotation)
        if there == annotation:
            location = Location(accepts, steps(subject))
            return self.record(Found(location), location.entered(), Control.NONE)
        if shape is not None and (held := collection(there)) is not None:
            over = Collection(accepts, steps(subject))
            if over in walk.bound:
                msg = f"{path}: {over} is already bound by a tuple enclosing this one"
                raise ValueError(msg)
            kind = shape[0]
            inner = self.compile(kind, (*at, EACH), f"{path}.{EACH}", walk.binding(over))
            if over not in self.varies[inner]:
                msg = (
                    f"{path}: bound to {over}, but nothing a {kind.__name__} is made from is"
                    f" found in an element of it; {held[0].__name__} is not a premise of"
                    f" {kind.__name__}"
                )
                raise ValueError(msg)
            node = Each(inner, over)
            return self.record(node, self.varies[inner] - {over}, self.control[inner])
        msg = (
            f"{path}: bound to {accepts.__name__}.{subject}, which holds {there!r}, not"
            f" {annotation!r}"
        )
        raise ValueError(msg)

    def heard(self, interaction: Interaction, kind: type[BaseModel], path: str, walk: Walk) -> Node:
        """The node for one record a source says."""
        request: Node | None = None
        varies: frozenset[Collection] = frozenset()
        control = Control.DECLARED if len(interaction.receives) > 1 else Control.NONE
        over = self.program.element_collection(interaction)
        if over is not None:
            varies = frozenset({over})
        if interaction.sends is not None:
            sends = interaction.sends
            rooted = walk.rooted(interaction.bound)
            request = self.compile(sends, (), f"{path}.{sends.__name__}", rooted)
            varies = varies | self.varies[request]
            control = max(control, self.control[request])
        if interaction.many:
            varies = varies | {Collection(kind, ())}
        return self.record(Heard(interaction, kind, request), varies, control)

    def located(self, location: Location, path: str, walk: Walk) -> Node:
        """The node for a value found at a location, with the node that supplies its container
        when the container is a received record."""
        container = location.container
        held: Node | None = None
        varies = location.entered()
        interaction = self.program.receiving(container)
        if interaction is not None:
            held = self.compile(container, (), f"{path}.{container.__name__}", walk)
            varies = varies | self.varies[held]
        return self.record(Found(location, held), varies, Control.NONE)

    def chosen(
        self, kind: type[BaseModel], locations: list[Location], path: str, walk: Walk
    ) -> Location | None:
        """The one location a class is found at, or ``None`` for none. Inside one construction
        per element of a collection, a class found in that element is the element's; a class
        found at two places the declarations do not tell apart is refused, naming the binding
        that would."""
        if len(locations) > 1:
            inner = [loc for loc in locations if any(loc.under(c) for c in walk.bound)]
            if len(inner) == 1:
                return inner[0]
            where = " and ".join(str(location) for location in locations)
            msg = (
                f"{path}: {kind.__name__} is held at {where}; the declaration does not say"
                f" which, so declare it: Binding(premise=<path to this premise>,"
                f" subject=<one of those places>)"
            )
            raise ValueError(msg)
        return locations[0] if locations else None

    def many(self, kind: type[BaseModel], at: tuple[str, ...], path: str, walk: Walk) -> Node:
        """A tuple premise: every record a collection source says, a tuple found in the input or
        in a record, or one construction per element of the one collection the class varies
        over."""
        interaction = self.program.receiving(kind)
        whole = self.program.locations(lambda a: element(a) is kind)
        if interaction is not None and whole:
            msg = (
                f"{path}: every {kind.__name__} is both said by {interaction.source.root} and"
                f" held at {whole[0]}; the declaration does not say which"
            )
            raise ValueError(msg)
        if interaction is not None:
            return self.all(interaction, kind, at, path, walk)
        location = self.chosen(kind, whole, path, walk)
        if location is not None:
            return self.located(location, path, walk)
        inner = self.compile(kind, (*at, EACH), f"{path}.{EACH}", walk)
        unbound = self.varies[inner] - walk.bound
        if not unbound:
            msg = (
                f"{path}: a tuple of {kind.__name__}, but nothing {kind.__name__} is made from"
                " varies, so there is one, not many; a source says many records only when its"
                " interaction declares what closes it"
            )
            raise ValueError(msg)
        if len(unbound) > 1:
            over = " and ".join(sorted(str(c) for c in unbound))
            msg = (
                f"{path}: each {kind.__name__} varies over both {over}; the declaration does"
                " not say which collection the tuple follows, so declare it: Binding(premise="
                f"<path to this premise>, subject=<the collection>)"
            )
            raise ValueError(msg)
        (over,) = unbound
        inner = self.compile(kind, (*at, EACH), f"{path}.{EACH}", walk.binding(over))
        closure: All | None = None
        holder: Node | None = None
        source = self.program.receiving(over.container)
        if source is not None and not over.path:
            closure = self.all(source, over.container, at, path, walk)
        elif source is not None:
            holder = self.compile(over.container, (), f"{path}.{over.container.__name__}", walk)
        node = Each(inner, over, closure, holder)
        varies = self.varies[inner] - {over}
        control = self.control[inner]
        for extra in (closure, holder):
            if extra is not None:
                varies = varies | self.varies[extra]
                control = max(control, self.control[extra])
        return self.record(node, varies, control)

    def all(
        self,
        interaction: Interaction,
        kind: type[BaseModel],
        at: tuple[str, ...],
        path: str,
        walk: Walk,
    ) -> All:
        """Every record a collection source says, sealed by its declared closure."""
        closer = interaction.closed_by
        if closer is None:
            msg = (
                f"{path} holds every {kind.__name__} that {interaction.source.root} will say,"
                " and the interaction declares no closure; which evidence closes the source"
                " is a business rule the program must state"
            )
            raise ValueError(msg)
        closing = self.compile(closer, (*at, closer.__name__), f"{path}.closed_by", walk)
        node = All(interaction, kind, closing)
        varies = self.varies[closing]
        over = self.program.element_collection(interaction)
        if over is not None:
            varies = varies | {over}
        self.record(node, varies, self.control[closing])
        return node

    def one(self, kind: type[BaseModel], at: tuple[str, ...], path: str, walk: Walk) -> Node:
        """A single premise: a record a source says, a value found at one place, or a class
        made from its premises."""
        interaction = self.program.receiving(kind)
        locations = self.program.locations(lambda a: a is kind)
        if kind is self.program.accepts:
            locations.insert(0, Location(kind, ()))
        if interaction is not None and locations:
            msg = (
                f"{path}: {kind.__name__} is both received from {interaction.source.root} and"
                f" held at {locations[0]}; the declaration does not say which"
            )
            raise ValueError(msg)
        if interaction is not None:
            return self.heard(interaction, kind, path, walk)
        location = self.chosen(kind, locations, path, walk)
        if location is not None:
            return self.located(location, path, walk)
        if issubclass(kind, Record):
            msg = (
                f"{path}: {kind.__name__} is what an external party says, and no interaction"
                " declares a source for it; without a declared source it cannot be waited for"
            )
            raise ValueError(msg)  # noqa: TRY004  a validator's refusal is a ValueError
        empty = constant(kind)
        plain = Made(kind)
        if issubclass(kind, RootModel):
            if empty:
                return self.record(plain, frozenset(), Control.NONE)
            msg = (
                f"{path}: no input or received record holds a {kind.__name__}, and it is a"
                " value, not constructed from premises"
            )
            raise ValueError(msg)
        compiled = tuple(
            (name, self.compile(annotation, (*at, name), f"{path}.{name}", walk))
            for name, annotation in premises(kind)
        )
        node = Made(kind, compiled)
        varies = frozenset[Collection]().union(*(self.varies[n] for _, n in compiled))
        control = max((self.control[n] for _, n in compiled), default=Control.NONE)
        if issubclass(kind, Refutable):
            control = Control.DECLARED
        else:
            if constrained(kind):
                control = max(control, Control.CONSTRAINT)
            if opaque(kind) != frozenset():
                control = max(control, Control.OPAQUE)
        return self.record(node, varies, control)
