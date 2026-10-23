"""What a business program declares beyond its types: where external evidence comes from.

Pydantic already states a program's composition, constraints, aliases, unions and collections.
A ``Fact``'s required fields are its premises; a union field is a choice; a tuple field is a
collection. What Pydantic cannot state is which external party supplies a ``Record``, how that
party's evidence is tied to one invocation, and when a source that delivers items over time has
delivered them all. Those three are declared here, once each, and nothing else is.

An ``Interaction`` is one declared relationship with one ``Source``. It names what the source
can say (``receives``), optionally what this program sends to make it say so (``sends``),
optionally the receipt the source may answer the send with before the result (``acknowledges``),
how a delivery is tied to the invocation (``correlated``), and, for a source whose items
accumulate, the evidence that closes it (``closed_by``). An interaction with ``closed_by`` is a
collection source: the source says many records, and the program holds every one of them.
Whether a result comes back inside the sending attempt or in a later delivery is not declared:
it is observed, and the premise it satisfies is the same either way.

A ``Program`` is a goal, the input it accepts, and its interactions. Constructing one walks the
goal's premises and checks that each is obtained exactly one way: a declared interaction, one
location in the accepted input or in a received record, or construction from premises that are.
A class is not an occurrence. A premise found inside a collection varies, one occurrence per
element, and a tuple of a constructed class is one construction per element of the one
collection its premises vary over. A premise that varies where the goal needs one, or that is
found at two places the declaration does not tell apart, is refused when the program is
constructed, naming both places. Distinct roles of one class are distinct classes.
"""

import types
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Union, get_args, get_origin

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator
from pydantic.fields import FieldInfo

from type_construction.world import Record, Scalar

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


def premises(kind: type[BaseModel]) -> Iterator[tuple[str, Any]]:
    """The required fields of a class and their annotations: its premises. A computed field or
    a field with a default is not a premise."""
    for name, info in kind.model_fields.items():
        if info.is_required() and info.annotation is not None:
            yield name, info.annotation


def constant(kind: type[BaseModel]) -> bool:
    """Whether the class constructs from nothing: no required field."""
    return not any(True for _ in premises(kind))


def resolve(kind: type[BaseModel], path: str) -> object:
    """The annotation at a field path on a class, entering collections at ``*``, or
    ``ValueError`` naming what is missing, which a declaration's validator reports as its
    refusal."""
    current: object = kind
    for name in steps(path):
        if name == EACH:
            inner = element(current)
            if inner is None:
                msg = f"{kind.__name__}.{path}: {current!r} is not a collection to enter"
                raise ValueError(msg)
            current = inner
            continue
        if not (isinstance(current, type) and issubclass(current, BaseModel)):
            msg = f"{kind.__name__}.{path}: {current!r} has no field {name}"
            raise ValueError(msg)  # noqa: TRY004  a validator's refusal is a ValueError
        info = current.model_fields.get(name)
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
    solicited receive with no ``correlated`` pair is tied to the invocation by the delivery
    naming the intent it answers. With ``closed_by``, the source says many records and the
    program holds every one until that evidence arrives.
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
        for correlation in self.correlated:
            for kind in self.receives:
                resolve(kind, correlation.received)
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

    def collections(self, *, source_many: bool) -> frozenset[Collection]:
        """The collections the location varies over: the container's own records when it is a
        collection source, and each collection the path enters."""
        entered = {
            Collection(self.container, self.path[:k])
            for k, step in enumerate(self.path)
            if step == EACH
        }
        if source_many:
            entered.add(Collection(self.container, ()))
        return frozenset(entered)


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
            elif (
                isinstance(annotation, type)
                and issubclass(annotation, BaseModel)
                and not issubclass(annotation, RootModel)
            ):
                search(annotation, path)

    if not issubclass(container, RootModel):
        search(container, ())
    return paths


@dataclass
class Analysis:
    """What one walk of a program's declarations established: where each located premise is
    found, which collection each tuple of constructed classes is one construction per element
    of, the collections each premise varies over, and the request kinds the program sends."""

    located: dict[object, Location] = field(default_factory=dict)
    mapped: dict[object, Collection] = field(default_factory=dict)
    varies: dict[tuple[object, frozenset[Collection]], frozenset[Collection]] = field(
        default_factory=dict
    )
    sent: dict[str, Interaction] = field(default_factory=dict)

    def walked(self, annotation: object) -> frozenset[Collection] | None:
        """The collections a premise varies over, if the walk reached it under any bound
        collections; what a premise varies over is intrinsic to it."""
        for (walked, _), varies in self.varies.items():
            if walked == annotation:
                return varies
        return None

    def varying(self, annotation: object, bound: frozenset[Collection]) -> frozenset[Collection]:
        """The collections a premise varies over, as walked under the given bound collections
        or under any. A premise the walk never reached is a defect: evaluation must construct
        only what the declaration validated."""
        exact = self.varies.get((annotation, bound))
        if exact is not None:
            return exact
        varies = self.walked(annotation)
        if varies is None:
            msg = f"{annotation!r} was not walked when the program was validated"
            raise KeyError(msg)
        return varies


@dataclass(frozen=True)
class Walk:
    """One pass of the walk: what it records, the premises being constructed above the current
    one, and the collections bound by the tuples enclosing it."""

    analysis: Analysis
    stack: tuple[object, ...] = ()
    bound: frozenset[Collection] = frozenset()

    def into(self, annotation: object) -> Walk:
        """The walk one premise deeper."""
        return Walk(self.analysis, (*self.stack, annotation), self.bound)

    def binding(self, over: Collection) -> Walk:
        """The walk with one more collection bound."""
        return Walk(self.analysis, self.stack, self.bound | {over})


class Program(BaseModel):
    """A goal, the input it accepts, and the interactions that supply what the input does not.

    Construction validates the whole: each received kind is declared by one interaction, each
    sent kind by one; every premise the goal transitively needs is obtained one way; a tuple of
    a constructed class varies over exactly one collection; a collection source has a declared
    closure; correlation paths exist; the goal itself does not vary. A program that fails is
    refused with a message naming the premise and the missing business distinction.
    """

    model_config = DECLARATION

    goal: type[BaseModel]
    """The declared outcome."""
    accepts: type[BaseModel]
    """The input an invocation is accepted with."""
    interactions: tuple[Interaction, ...] = ()
    """The declared relationships with external sources."""

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
        varies = self.analysis.varying(self.goal, frozenset())
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
        return self.analysis.sent.get(operation)

    def subject_collections(self, correlation: Correlation) -> frozenset[Collection]:
        """The collections a correlation's subject path enters."""
        return Location(self.accepts, steps(correlation.subject)).collections(source_many=False)

    def element_collection(self, interaction: Interaction) -> Collection | None:
        """The one collection an unsolicited receive varies over through its correlation, if
        any."""
        entered: set[Collection] = set()
        for correlation in interaction.correlated:
            entered |= self.subject_collections(correlation)
        if len(entered) > 1:
            over = " and ".join(sorted(str(c) for c in entered))
            msg = f"{names(interaction.receives)} correlates into {over}; one collection at most"
            raise ValueError(msg)
        return next(iter(entered), None)

    @cached_property
    def analysis(self) -> Analysis:
        """The walk of the goal's premises; raises ``ValueError`` for a premise the program
        does not obtain one way."""
        analysis = Analysis()
        for interaction in self.interactions:
            if interaction.sends is not None:
                analysis.sent[qualified(interaction.sends)] = interaction
        self._walk(self.goal, self.goal.__name__, Walk(analysis))
        return analysis

    def _correlated(self, container: type[BaseModel]) -> frozenset[str]:
        """The field paths on a received container that correlation declares equal to the
        input, so that they are not a second location of the value."""
        interaction = self.receiving(container)
        if interaction is None:
            return frozenset()
        return frozenset(c.received for c in interaction.correlated)

    def _locations(self, matches: Callable[[object], bool]) -> list[Location]:
        """Where an annotation is found: in the input, or in a received record."""
        locations = [
            Location(self.accepts, path) for path in found(self.accepts, matches, frozenset())
        ]
        for interaction in self.interactions:
            for container in interaction.receives:
                paths = found(container, matches, self._correlated(container))
                locations.extend(Location(container, path) for path in paths)
        return locations

    def _walk(self, annotation: object, path: str, walk: Walk) -> frozenset[Collection]:
        """Walk one premise annotation, record how it is obtained, and return the collections
        it varies over."""
        if annotation in walk.stack:
            msg = f"{path}: {annotation!r} is constructed from itself with no evidence between"
            raise ValueError(msg)
        key = (annotation, walk.bound)
        if key in walk.analysis.varies:
            return walk.analysis.varies[key]
        deeper = walk.into(annotation)
        members = alternatives(annotation)
        if members is not None:
            varies: frozenset[Collection] = frozenset()
            for member in members:
                varies |= self._walk(member, f"{path}.{member.__name__}", deeper)
        elif (shape := collection(annotation)) is not None:
            varies = self._walk_many(annotation, shape[0], path, deeper)
        elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
            varies = self._walk_one(annotation, path, deeper)
        else:
            msg = (
                f"{path}: a premise is a declared class, a union of them, or a tuple of one;"
                f" {annotation!r} is none"
            )
            raise ValueError(msg)
        walk.analysis.varies[key] = varies
        return varies

    def _walk_interaction(
        self, interaction: Interaction, path: str, walk: Walk
    ) -> frozenset[Collection]:
        """The collections a receive varies over: those of its request, or of the element its
        correlation selects."""
        if interaction.sends is not None:
            sends = interaction.sends
            return self._walk(sends, f"{path}.{sends.__name__}", walk)
        over = self.element_collection(interaction)
        return frozenset() if over is None else frozenset({over})

    def _walk_source(
        self, interaction: Interaction, path: str, walk: Walk
    ) -> frozenset[Collection]:
        """The collections a collection source varies over: those of its request and of its
        closing evidence, both walked so that what supplies them is validated and recorded."""
        varies = self._walk_interaction(interaction, path, walk)
        closer = interaction.closed_by
        if closer is None:
            return varies
        return varies | self._walk(closer, f"{path}.closed_by", walk)

    def _located_varies(self, location: Location, path: str, walk: Walk) -> frozenset[Collection]:
        """The collections a located premise varies over: those its path enters, and those of
        its container, which is walked too when it is a received record, so that what supplies
        the record is validated and recorded."""
        container = location.container
        interaction = self.receiving(container)
        varies = location.collections(source_many=interaction is not None and interaction.many)
        if interaction is not None:
            varies |= self._walk(container, f"{path}.{container.__name__}", walk)
        return varies

    def _walk_many(
        self, annotation: object, kind: type[BaseModel], path: str, walk: Walk
    ) -> frozenset[Collection]:
        interaction = self.receiving(kind)
        whole = self._locations(lambda a: element(a) is kind)
        if interaction is not None and whole:
            msg = (
                f"{path}: every {kind.__name__} is both said by {interaction.source.root} and"
                f" held at {whole[0]}; the declaration does not say which"
            )
            raise ValueError(msg)
        if interaction is not None:
            if interaction.closed_by is None:
                msg = (
                    f"{path} holds every {kind.__name__} that {interaction.source.root} will say,"
                    " and the interaction declares no closure; which evidence closes the source"
                    " is a business rule the program must state"
                )
                raise ValueError(msg)
            return self._walk_source(interaction, path, walk)
        if len(whole) > 1:
            where = " and ".join(str(location) for location in whole)
            msg = (
                f"{path}: every {kind.__name__} is held at {where}; the declaration does not"
                " say which"
            )
            raise ValueError(msg)
        if whole:
            walk.analysis.located[annotation] = whole[0]
            return self._located_varies(whole[0], path, walk)
        each = self._walk(kind, f"{path}.{EACH}", walk)
        unbound = each - walk.bound
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
                " not say which collection the tuple follows"
            )
            raise ValueError(msg)
        (over,) = unbound
        walk.analysis.mapped[annotation] = over
        self._walk(kind, f"{path}.{EACH}", walk.binding(over))
        return each - {over}

    def _walk_one(self, kind: type[BaseModel], path: str, walk: Walk) -> frozenset[Collection]:
        interaction = self.receiving(kind)
        locations = self._locations(lambda a: a is kind)
        if interaction is not None and locations:
            msg = (
                f"{path}: {kind.__name__} is both received from {interaction.source.root} and"
                f" held at {locations[0]}; the declaration does not say which"
            )
            raise ValueError(msg)
        if interaction is not None:
            if interaction.many:
                source = self._walk_source(interaction, path, walk)
                return frozenset({Collection(kind, ())}) | source
            return self._walk_interaction(interaction, path, walk)
        if len(locations) > 1:
            where = " and ".join(str(location) for location in locations)
            msg = (
                f"{path}: {kind.__name__} is held at {where}; the declaration does not say"
                " which, and distinct roles of one class are distinct classes"
            )
            raise ValueError(msg)
        if locations:
            walk.analysis.located[kind] = locations[0]
            return self._located_varies(locations[0], path, walk)
        empty = constant(kind)
        if issubclass(kind, Record):
            msg = (
                f"{path}: {kind.__name__} is what an external party says, and no interaction"
                " declares a source for it; without a declared source it cannot be waited for"
            )
            raise ValueError(msg)  # noqa: TRY004  a validator's refusal is a ValueError
        if issubclass(kind, RootModel):
            if empty:
                return frozenset()
            msg = (
                f"{path}: no input or received record holds a {kind.__name__}, and it is a"
                " value, not constructed from premises"
            )
            raise ValueError(msg)
        varies: frozenset[Collection] = frozenset()
        for name, annotation in premises(kind):
            varies |= self._walk(annotation, f"{path}.{name}", walk)
        return varies
