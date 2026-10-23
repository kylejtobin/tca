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
accumulate, the evidence that closes it (``closed_by``). Whether the result comes back inside
the sending attempt or in a later delivery is not declared: it is observed, and the premise it
satisfies is the same either way.

A ``Program`` is a goal, the input it accepts, and its interactions. Constructing one checks
that every premise the goal transitively needs has exactly one way to be obtained: a declared
interaction, one location in the accepted input or in a received record, or construction from
premises that do. A premise with no way is refused at declaration, so no absent field can become
a wait at evaluation.
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


class Source(Scalar[str]):
    """An external party the program trusts for what it says: a payment provider, a reviewer
    inbox, the clock. Its name is the admission boundary's label for the party; authenticating
    that a delivery is from the party is the host's work, not declared here."""

    root: str = Field(min_length=1)


class Correlation(BaseModel):
    """One declared equality that ties a received record to the invocation: the value at
    ``received`` on the record equals the value at ``subject`` on the accepted input. Equal
    values elsewhere establish nothing; only a declared pair does."""

    model_config = DECLARATION

    received: str
    """Dotted field path on the received record."""
    subject: str
    """Dotted field path on the accepted input."""


def qualified(kind: type[BaseModel]) -> str:
    """The durable name of a declared class: its module and qualified name."""
    return f"{kind.__module__}.{kind.__qualname__}"


def names(kinds: tuple[type[BaseModel], ...]) -> str:
    """The class names, joined for a message."""
    return " | ".join(kind.__name__ for kind in kinds)


def at(value: BaseModel, path: str) -> object:
    """The value at a dotted field path."""
    current: object = value
    for name in path.split("."):
        current = getattr(current, name)
    return current


def resolve(kind: type[BaseModel], path: str) -> object:
    """The annotation at a dotted field path on a class, or ``ValueError`` naming what is
    missing, which a declaration's validator reports as its refusal."""
    current: object = kind
    for name in path.split("."):
        if not (isinstance(current, type) and issubclass(current, BaseModel)):
            msg = f"{kind.__name__}.{path}: {current!r} has no field {name}"
            raise ValueError(msg)  # noqa: TRY004  a validator's refusal is a ValueError
        info = current.model_fields.get(name)
        if info is None or info.annotation is None:
            msg = f"{kind.__name__} has no field path {path}"
            raise ValueError(msg)
        current = annotated(info)
    return current


def annotated(info: FieldInfo) -> object:
    """A field's annotation, as the unknown object it is until examined."""
    return info.annotation


class Interaction(BaseModel):
    """One declared relationship with one external source.

    ``receives`` is what the source can say; one admitted answer satisfies the receive. With
    ``sends``, the program constructs that request from its premises and the host dispatches
    it; without, the receive is unsolicited and waits for a correlated delivery. With
    ``acknowledges``, the source may answer the send with that receipt first and deliver the
    result later; a receipt is recorded against the attempt and satisfies no premise. A
    solicited receive with no ``correlated`` pair is tied to the invocation by the delivery
    naming the intent it answers. ``closed_by`` names the evidence after which the source says
    nothing more; it is required where the program holds every item the source delivers.
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
    """The evidence after which the source delivers nothing more."""

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


@dataclass(frozen=True)
class Location:
    """Where a premise's value is found: a field path inside a container that is the accepted
    input or a received record. A projected location is inside each element of a received
    collection, so it yields one value per element."""

    container: type[BaseModel]
    path: tuple[str, ...]
    projected: bool = False

    def __str__(self) -> str:
        return ".".join((self.container.__name__, *self.path))


type Held = tuple[type[BaseModel], int | None] | None
"""How a premise holds a received kind: ``None`` for one record; otherwise the element and the
fixed count, ``None`` for any number."""


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


def found(
    container: type[BaseModel],
    matches: Callable[[object], bool],
    skipped: frozenset[str],
) -> list[tuple[str, ...]]:
    """The field paths inside a container whose annotation matches, searching into nested
    classes but not into collections or into a value's root, and skipping declared paths."""
    paths: list[tuple[str, ...]] = []

    def search(kind: type[BaseModel], prefix: tuple[str, ...]) -> None:
        for name, info in kind.model_fields.items():
            path = (*prefix, name)
            annotation = info.annotation
            if ".".join(path) in skipped:
                continue
            if matches(annotation):
                paths.append(path)
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
    """What one walk of a program's declarations established: how each received kind is held,
    where each located premise is found, and the request kinds the program sends."""

    held: dict[type[BaseModel], Held] = field(default_factory=dict)
    located: dict[object, Location] = field(default_factory=dict)
    sent: dict[str, Interaction] = field(default_factory=dict)
    walked: set[object] = field(default_factory=set)


class Program(BaseModel):
    """A goal, the input it accepts, and the interactions that supply what the input does not.

    Construction validates the whole: each received kind is declared by one interaction, each
    sent kind by one; every premise the goal transitively needs is obtained one way; a
    collection held from a source has a declared closure; correlation paths exist. A program
    that fails is refused with a message naming the premise and the missing business
    distinction.
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
        _ = self.analysis
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

    @cached_property
    def analysis(self) -> Analysis:
        """The walk of the goal's premises; raises ``ValueError`` for a premise the program
        does not obtain one way."""
        analysis = Analysis()
        for interaction in self.interactions:
            if interaction.sends is not None:
                analysis.sent[qualified(interaction.sends)] = interaction
        self._walk(self.goal, self.goal.__name__, analysis, ())
        return analysis

    def _correlated(self, container: type[BaseModel]) -> frozenset[str]:
        """The field paths on a received container that correlation declares equal to the
        input, so that they are not a second location of the value."""
        interaction = self.receiving(container)
        if interaction is None:
            return frozenset()
        return frozenset(c.received for c in interaction.correlated)

    def _locations(self, matches: Callable[[object], bool], *, projected: bool) -> list[Location]:
        """Where an annotation is found: in the input, or in a received record. Projected
        searches look inside received kinds for a value found once per element."""
        locations: list[Location] = []
        if not projected:
            locations.extend(
                Location(self.accepts, path) for path in found(self.accepts, matches, frozenset())
            )
        for interaction in self.interactions:
            for container in interaction.receives:
                paths = found(container, matches, self._correlated(container))
                locations.extend(Location(container, path, projected) for path in paths)
        return locations

    def _walk(
        self, annotation: object, path: str, analysis: Analysis, stack: tuple[object, ...]
    ) -> None:
        if annotation in stack:
            msg = f"{path}: {annotation!r} is constructed from itself with no evidence between"
            raise ValueError(msg)
        if annotation in analysis.walked:
            return
        analysis.walked.add(annotation)
        members = alternatives(annotation)
        if members is not None:
            for member in members:
                self._walk(member, f"{path}.{member.__name__}", analysis, (*stack, annotation))
            return
        shape = collection(annotation)
        if shape is not None:
            self._walk_many(annotation, shape, path, analysis, (*stack, annotation))
            return
        if not (isinstance(annotation, type) and issubclass(annotation, BaseModel)):
            msg = (
                f"{path}: a premise is a declared class, a union of them, or a tuple of one;"
                f" {annotation!r} is none"
            )
            raise ValueError(msg)  # noqa: TRY004  a validator's refusal is a ValueError
        self._walk_one(annotation, path, analysis, (*stack, annotation))

    def _hold(self, kind: type[BaseModel], shape: Held, path: str, analysis: Analysis) -> None:
        if kind in analysis.held and analysis.held[kind] != shape:
            msg = (
                f"{path}: {kind.__name__} is held both as one record and as a collection; a"
                " source is one or the other"
            )
            raise ValueError(msg)
        analysis.held[kind] = shape

    def _walk_interaction(
        self, interaction: Interaction, path: str, analysis: Analysis, stack: tuple[object, ...]
    ) -> None:
        if interaction.sends is not None:
            self._walk(interaction.sends, f"{path}.{interaction.sends.__name__}", analysis, stack)

    def _walk_many(
        self,
        annotation: object,
        shape: tuple[type[BaseModel], int | None],
        path: str,
        analysis: Analysis,
        stack: tuple[object, ...],
    ) -> None:
        kind, _ = shape
        interaction = self.receiving(kind)
        whole = self._locations(lambda a: element(a) is kind, projected=False)
        projected = self._locations(lambda a: a is kind, projected=True)
        ways = [str(w) for w in (*whole, *projected)]
        if interaction is not None:
            ways.append(interaction.source.root)
        if len(ways) > 1:
            msg = (
                f"{path}: every {kind.__name__} is found more than one way ({', '.join(ways)});"
                " the declaration does not say which"
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
            self._hold(kind, shape, path, analysis)
            self._walk_interaction(interaction, path, analysis, stack)
            self._walk(interaction.closed_by, f"{path}.closed_by", analysis, stack)
            return
        if whole:
            analysis.located[annotation] = whole[0]
            return
        if projected:
            location = projected[0]
            analysis.located[annotation] = location
            self._walk(
                tuple[location.container, ...],
                f"{path}.{location.container.__name__}",
                analysis,
                stack,
            )
            return
        msg = (
            f"{path}: no declared source says {kind.__name__}, and no input or received record"
            " holds them"
        )
        raise ValueError(msg)

    def _walk_one(
        self, kind: type[BaseModel], path: str, analysis: Analysis, stack: tuple[object, ...]
    ) -> None:
        interaction = self.receiving(kind)
        locations = self._locations(lambda a: a is kind, projected=False)
        if interaction is not None and locations:
            msg = (
                f"{path}: {kind.__name__} is both received from {interaction.source.root} and"
                f" held at {locations[0]}; the declaration does not say which"
            )
            raise ValueError(msg)
        if interaction is not None:
            self._hold(kind, None, path, analysis)
            self._walk_interaction(interaction, path, analysis, stack)
            return
        if len(locations) > 1:
            where = " and ".join(str(location) for location in locations)
            msg = f"{path}: {kind.__name__} is held at {where}; the declaration does not say which"
            raise ValueError(msg)
        if locations:
            analysis.located[kind] = locations[0]
            return
        empty = constant(kind)
        if issubclass(kind, Record):
            msg = (
                f"{path}: {kind.__name__} is what an external party says, and no interaction"
                " declares a source for it; without a declared source it cannot be waited for"
            )
            raise ValueError(msg)  # noqa: TRY004  a validator's refusal is a ValueError
        if issubclass(kind, RootModel):
            if empty:
                return
            msg = (
                f"{path}: no input or received record holds a {kind.__name__}, and it is a"
                " value, not constructed from premises"
            )
            raise ValueError(msg)
        for name, annotation in premises(kind):
            self._walk(annotation, f"{path}.{name}", analysis, stack)
