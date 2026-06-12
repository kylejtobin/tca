"""Building block classifier: a recursive Pydantic type-tree classifier.

Hand it any BaseModel class and it walks the entire construction graph,
classifying every field and every field of every model-typed field, all the
way down, with zero domain knowledge.

Usage:
    uv run python tests/non_conforming/building_block.py module:ClassName
    uv run python tests/non_conforming/building_block.py module:ClassName --json

This file is a deliberately non-conforming adversarial fixture for the build
agents. See README.md in this directory. Do not treat it as an example.
"""

from __future__ import annotations

import importlib
import types
from collections.abc import Callable
from contextvars import ContextVar
from enum import StrEnum
from typing import (
    Annotated,
    ClassVar,
    Literal,
    TypeAliasType,
    get_args,
    get_origin,
    override,
)

from functools import cached_property

from pydantic import BaseModel, Field, RootModel, computed_field, model_validator
from pydantic.fields import FieldInfo


class Block(StrEnum):
    """The eight structural building blocks the classifier sorts types into."""

    ENUM = "enum"  # StrEnum — closed set of string values
    NEWTYPE = "newtype"  # RootModel[scalar] — semantic wrapper (e.g. UserName(str))
    COLLECTION = "collection"  # RootModel[tuple[T, ...]] — immutable sequence
    RECORD = "record"  # BaseModel, frozen=True — product type with named fields
    ALGEBRA = "algebra"  # Record + @computed_field — stored fields in, derived out
    EFFECT = "effect"  # Record + model_post_init — construction triggers action
    SCALAR = "scalar"  # str, int, bool, etc. — Python primitives
    UNION = "union"  # A | B — any union with 2+ non-None members

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


class AnnotationKind(StrEnum):
    """The six structural forms a Python type annotation can take."""

    DIRECT = "direct"  # Plain type: str, int, MyModel
    OPTIONAL = "optional"  # Exactly T | None — one non-None member
    TUPLE = "tuple"  # tuple[X, ...] — variadic tuple
    FIXED_TUPLE = "fixed_tuple"  # tuple[A, B, ...] — fixed-length positional product
    ALIAS = "alias"  # type X = ... — TypeAliasType
    UNION = "union"  # union with 2+ non-None members; may include NoneType

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


class DirectAnnotation(BaseModel, frozen=True, from_attributes=True):
    """A plain type annotation — not wrapped in Optional, tuple, or alias."""

    kind: Literal[AnnotationKind.DIRECT] = AnnotationKind.DIRECT
    resolved_type: object = Field(
        exclude=True, description="The Python type the field holds"
    )
    nullable: Literal[False]
    collection: Literal[False]


class OptionalAnnotation(BaseModel, frozen=True, from_attributes=True):
    """An X | None annotation — the field can be absent."""

    kind: Literal[AnnotationKind.OPTIONAL] = AnnotationKind.OPTIONAL
    resolved_type: object = Field(
        exclude=True, description="The Python type the field holds"
    )
    nullable: Literal[True]
    collection: Literal[False]


class TupleAnnotation(BaseModel, frozen=True, from_attributes=True):
    """A tuple[X, ...] annotation — a homogeneous immutable sequence."""

    kind: Literal[AnnotationKind.TUPLE] = AnnotationKind.TUPLE
    resolved_type: object = Field(
        exclude=True, description="The Python type the field holds"
    )
    nullable: Literal[False]
    collection: Literal[True]


class FixedTupleAnnotation(BaseModel, frozen=True, from_attributes=True):
    """A fixed-length tuple annotation — a positional product of heterogeneous types."""

    kind: Literal[AnnotationKind.FIXED_TUPLE] = AnnotationKind.FIXED_TUPLE
    resolved_type: object = Field(
        exclude=True,
        description="The tuple typing object; positional member types preserved",
    )
    nullable: Literal[False]
    collection: Literal[False]


class AliasAnnotation(BaseModel, frozen=True, from_attributes=True):
    """A TypeAliasType annotation — created by 'type X = ...' syntax."""

    kind: Literal[AnnotationKind.ALIAS] = AnnotationKind.ALIAS
    resolved_type: object = Field(
        exclude=True, description="The Python type the field holds"
    )
    nullable: bool = Field(
        default=False, description="True when the alias target is an Optional type"
    )
    collection: bool = Field(
        default=False, description="True when the alias target is a tuple type"
    )


class UnionAnnotation(BaseModel, frozen=True, from_attributes=True):
    """A multi-member union — 2+ non-None types, optionally including NoneType."""

    kind: Literal[AnnotationKind.UNION] = AnnotationKind.UNION
    resolved_type: object = Field(
        exclude=True,
        description="The union typing object; members preserved (including NoneType if present)",
    )
    nullable: bool = Field(description="True when union includes NoneType")
    collection: Literal[False]


AnnotationShape = Annotated[
    DirectAnnotation | OptionalAnnotation | TupleAnnotation | FixedTupleAnnotation | AliasAnnotation | UnionAnnotation,
    Field(discriminator="kind"),
]


class TypeAnnotation(RootModel[object], frozen=True):
    """Self-classifying wrapper #1: raw annotation → structural form + truth.

    Wraps any annotation and exposes classification (.kind, .resolved_type)
    and structural truth (.nullable, .collection) as properties, which
    downstream models read via from_attributes to route the AnnotationShape
    union.
    """

    @staticmethod
    def peel(t: object) -> object:
        """Strip Annotated wrappers from the surface of a typing object."""
        while get_origin(t) is Annotated:
            # get_args returns tuple[Any, ...]; safe in Annotated branch
            t = get_args(t)[0]  # pyright: ignore[reportAny]
        return t

    @property
    def base(self) -> object:
        """The root annotation with surface Annotated wrappers removed."""
        return self.peel(self.root)

    @property
    def effective(self) -> object:
        """The fully resolved typing object: aliases chased, Annotated peeled at each hop."""
        t = self.base
        while isinstance(t, TypeAliasType):
            # TypeAliasType.__value__ is Any; safe in isinstance branch
            t = self.peel(t.__value__) # pyright: ignore[reportAny]
        return t

    @property
    def kind(self) -> AnnotationKind:
        """Classify the structural form of this annotation."""
        b = self.base
        if isinstance(b, TypeAliasType):
            return AnnotationKind.ALIAS

        e = self.effective
        o = get_origin(e)

        if o is tuple:
            args = get_args(e)
            if len(args) == 2 and args[1] is Ellipsis:
                return AnnotationKind.TUPLE
            return AnnotationKind.FIXED_TUPLE

        if o is types.UnionType:
            args = get_args(e)
            non_none_count = sum(1 for a in args if a is not type(None))  # pyright: ignore[reportAny]
            if type(None) in args and non_none_count == 1:
                return AnnotationKind.OPTIONAL
            if non_none_count >= 2:
                return AnnotationKind.UNION
            raise TypeError(
                f"UnionType with {non_none_count} non-None members is an invariant violation: {e}"
            )

        return AnnotationKind.DIRECT

    @property
    def resolved_type(self) -> object:
        """The inner type after structural unwrapping."""
        e = self.effective
        o = get_origin(e)

        if o is types.UnionType:
            args = get_args(e)
            non_none = tuple(a for a in args if a is not type(None)) # pyright: ignore[reportAny]

            # T | None -> T (peeled)
            if type(None) in args and len(non_none) == 1:
                return self.peel(non_none[0]) # pyright: ignore[reportAny]

            # multi-member union -> preserve union object (top-level peeled only)
            return e

        if o is tuple:
            args = get_args(e)
            if len(args) == 2 and args[1] is Ellipsis:
                return self.peel(args[0]) # pyright: ignore[reportAny]
            # fixed tuple -> return as-is (truthful)
            return e

        return e

    @property
    def nullable(self) -> bool:
        """True if the effective type includes NoneType in a union."""
        e = self.effective
        return get_origin(e) is types.UnionType and type(None) in get_args(e)

    @property
    def collection(self) -> bool:
        """True if the effective type is a variadic tuple: tuple[X, ...]."""
        e = self.effective
        o = get_origin(e)
        if o is tuple:
            args = get_args(e)
            return len(args) == 2 and args[1] is Ellipsis
        return False


class FieldSlot(BaseModel, frozen=True, from_attributes=True, populate_by_name=True):
    """A single entry from model_fields: field name + its type annotation.

    Constructed from dict.items() tuples via the before validator, because
    dict keys are not attributes.
    """

    field_name: str = Field(
        alias="name", description="Name of the field on the model being classified"
    )
    annotation: TypeAnnotation = Field(
        description="The field's type annotation as declared in source"
    )

    @model_validator(mode="before")
    @classmethod
    def _from_tuple(cls, data: tuple[str, FieldInfo]) -> dict[str, object]:
        """Pair a dict key with its value's annotation: position → name."""
        return {"field_name": data[0], "annotation": data[1].annotation}

    @property
    def resolved_type(self) -> ResolvedType:
        """Wrap the unwrapped inner type for BlockShape routing."""
        return ResolvedType(self.annotation.resolved_type)


class FieldEntry(BaseModel, frozen=True, from_attributes=True):
    """A field with its annotation resolved into an AnnotationShape.

    Properties flatten the nested shape so ClassifiedNode can read
    .resolved_type, .nullable, and .collection via from_attributes.
    """

    field_name: str = Field(
        description="Name of the field on the model being classified"
    )
    shape: AnnotationShape = Field(
        alias="annotation",
        description="Structural form of the annotation — direct, optional, tuple, fixed_tuple, alias, or union — with nullable and collection flags",
    )

    @property
    def resolved_type(self) -> object:
        return self.shape.resolved_type

    @property
    def nullable(self) -> bool:
        return self.shape.nullable

    @property
    def collection(self) -> bool:
        return self.shape.collection


class ClassifiedNode(FieldEntry, frozen=True, from_attributes=True):
    """One field fully classified: its building block type, structural flags, and children.

    Inherits field_name, shape, and the flattening properties from FieldEntry;
    adds block classification routed from ResolvedType.block_kind.
    """

    block_shape: BlockShape = Field(
        alias="resolved_type",
        description="Building block classification with recursive children for record-like types",
    )

    @property
    def block(self) -> Block:
        return self.block_shape.block_kind

    @property
    def children(self) -> tuple[ClassifiedNode, ...]:
        return self.block_shape.children


class ResolvedType(RootModel[object], frozen=True):
    """Self-classifying wrapper #2: raw type → building block classification.

    .block_kind drives BlockShape routing via a predicate table walked in
    priority order. .children fires recursive descent; it is only ever read
    when a variant with a children field constructs via from_attributes.
    """

    _BLOCK_MAP: ClassVar[tuple[tuple[Callable[[type], bool], Block], ...]] = (
        (lambda t: issubclass(t, StrEnum), Block.ENUM),
        (
            lambda t: issubclass(t, RootModel)
            and TypeAnnotation(t.model_fields["root"].annotation).collection,
            Block.COLLECTION,
        ),
        (lambda t: issubclass(t, RootModel), Block.NEWTYPE),
        (
            lambda t: issubclass(t, BaseModel) and bool(t.model_computed_fields),
            Block.ALGEBRA,
        ),
        (
            lambda t: issubclass(t, BaseModel) and "model_post_init" in vars(t),
            Block.EFFECT,
        ),
        (lambda t: issubclass(t, BaseModel), Block.RECORD),
    )

    @property
    def block_kind(self) -> Block:
        effective = TypeAnnotation.peel(self.root)
        if get_origin(effective) is types.UnionType:
            return Block.UNION

        return next(
            (
                b
                for pred, b in self._BLOCK_MAP
                if isinstance(effective, type) and pred(effective)
            ),
            Block.SCALAR,
        )

    @property
    def children(self) -> tuple[ClassifiedNode, ...]:
        return ModelTree.model_validate(TypeAnnotation.peel(self.root)).fields


class RecordBlock(BaseModel, frozen=True, from_attributes=True):
    """A plain BaseModel — frozen product type with named fields. Recurses."""

    block_kind: Literal[Block.RECORD] = Block.RECORD
    children: tuple[ClassifiedNode, ...] = Field(
        description="Classified fields of the inner model, one per field"
    )


class AlgebraBlock(BaseModel, frozen=True, from_attributes=True):
    """A BaseModel with @computed_field — stored fields in, derived knowledge out. Recurses."""

    block_kind: Literal[Block.ALGEBRA] = Block.ALGEBRA
    children: tuple[ClassifiedNode, ...] = Field(
        description="Classified fields of the inner model, one per field"
    )


class EffectBlock(BaseModel, frozen=True, from_attributes=True):
    """A BaseModel with model_post_init — construction triggers a side effect. Recurses."""

    block_kind: Literal[Block.EFFECT] = Block.EFFECT
    children: tuple[ClassifiedNode, ...] = Field(
        description="Classified fields of the inner model, one per field"
    )


class LeafBlock(BaseModel, frozen=True, from_attributes=True):
    """A non-record type — enum, newtype, collection, scalar, or union.

    INVARIANT: leaf variants must never define a stored field named
    "children"; recursion fires only when a variant's children field reads
    ResolvedType.children during construction. The .children property returns
    () for uniform delegation only.
    """

    block_kind: Literal[
        Block.ENUM, Block.NEWTYPE, Block.COLLECTION, Block.SCALAR, Block.UNION
    ] = Field(
        description="Which leaf building block — enum, newtype, collection, scalar, or union"
    )

    @property
    def children(self) -> tuple[ClassifiedNode, ...]:
        return ()


BlockShape = Annotated[
    RecordBlock | AlgebraBlock | EffectBlock | LeafBlock,
    Field(discriminator="block_kind"),
]


class FieldReport(BaseModel, frozen=True, from_attributes=True):
    """One classified field projected for display."""

    field_name: str = Field(description="Name of the field on the analyzed model")
    block: Block = Field(
        description="Structural role: record (named fields), enum (closed vocabulary), newtype (typed wrapper), scalar (primitive), algebra (record + derived), effect (record + side effects), collection (sequence wrapper), union (multi-member union)"
    )
    nullable: bool = Field(
        description="True when the field's type includes NoneType — T | None or A | B | None"
    )
    collection: bool = Field(
        description="True when the field's type was tuple[X, ...] — the field holds a sequence"
    )
    children: tuple[FieldReport, ...] = Field(
        default=(),
        description="Classified children of the inner type, present for record/algebra/effect, empty for leaves",
    )

    @computed_field(
        description="Single-line summary: name, block type, nullable, and collection"
    )
    @cached_property
    def line(self) -> str:
        return f"{self.field_name}: {self.block.value} (nullable={self.nullable}, collection={self.collection})"

    @computed_field(
        description="This field's line plus all descendant lines, flattened in tree order"
    )
    @cached_property
    def lines(self) -> tuple[str, ...]:
        return (self.line, *(line for child in self.children for line in child.lines))


class ModelTree(BaseModel, frozen=True, from_attributes=True, populate_by_name=True):
    """Root of the cascade — one model_validate classifies every field on a BaseModel.

    The wrap validator (not a before validator: returning a ModelTree from a
    before validator would re-trigger it) reshapes model_fields.items() and
    guards against cycles via the _seen ContextVar: already-visited types
    short-circuit with cycle=True and empty fields.
    """

    _seen: ClassVar[ContextVar[frozenset[type]]] = ContextVar("_seen")

    cycle: bool = Field(
        default=False,
        description="True when this node was already visited in an ancestor — fields is empty due to cycle, not because the model has no fields",
    )
    fields: tuple[ClassifiedNode, ...] = Field(
        description="Every field on the model, fully classified with block type, flags, and recursive children",
    )

    @model_validator(mode="wrap")
    @classmethod
    def _reshape(
        cls, data: type[BaseModel], handler: Callable[..., ModelTree]
    ) -> ModelTree:
        seen = cls._seen.get(frozenset())
        if data in seen:
            return handler({"fields": (), "cycle": True})

        token = cls._seen.set(seen | {data})
        try:
            return handler(
                {
                    "fields": tuple(
                        FieldSlot.model_validate(item) for item in data.model_fields.items()
                    ),
                    "cycle": False,
                }
            )
        finally:
            cls._seen.reset(token)


class TreeReport(BaseModel, frozen=True, from_attributes=True):
    """Human-readable projection of a ModelTree; owns indentation and depth."""

    reports: tuple[FieldReport, ...] = Field(
        alias="fields",
        description="One report per field, each carrying classification results and recursive children",
    )

    @computed_field(
        description="Complete indented tree — each nesting level indented two spaces"
    )
    @cached_property
    def text(self) -> str:
        def _indent(report: FieldReport, depth: int) -> tuple[str, ...]:
            prefix = "  " * depth
            return (
                f"{prefix}{report.line}",
                *(
                    line
                    for child in report.children
                    for line in _indent(child, depth + 1)
                ),
            )

        return "\n".join(line for r in self.reports for line in _indent(r, 0))

    @override
    def __str__(self) -> str:
        return self.text


class TextOutput(BaseModel, frozen=True):
    """Indented human-readable rendering of a classified tree."""

    kind: Literal["text"] = "text"

    def render(self, report: TreeReport) -> str:
        return report.text


class JsonOutput(BaseModel, frozen=True):
    """Full JSON serialization of the classified tree, two-space indented."""

    kind: Literal["json"] = "json"

    def render(self, report: TreeReport) -> str:
        return report.model_dump_json(indent=2)


OutputFormat = Annotated[
    TextOutput | JsonOutput,
    Field(discriminator="kind"),
]


class ClassifierRun(BaseModel, frozen=True):
    """The entire CLI as a frozen product type.

    Stored fields: target and output_format. Everything else is a derived
    projection chain: target → model_class → tree → report → __str__.
    """

    target: str = Field(
        description="Module and class to classify in module:ClassName format, e.g. myapp.models:Order"
    )
    output_format: OutputFormat = Field(
        default_factory=TextOutput,
        description="Rendering variant — TextOutput for indented human text, JsonOutput for full JSON serialization",
    )

    @cached_property
    def model_class(self) -> type[BaseModel]:
        """Resolve the target string to a BaseModel class."""
        module_path, class_name = self.target.rsplit(":", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)  # pyright: ignore[reportAny]

    @cached_property
    def tree(self) -> ModelTree:
        return ModelTree.model_validate(self.model_class)

    @cached_property
    def report(self) -> TreeReport:
        return TreeReport.model_validate(self.tree)

    @override
    def __str__(self) -> str:
        return self.output_format.render(self.report)


if __name__ == "__main__":
    import sys

    output_format: OutputFormat = JsonOutput() if "--json" in sys.argv else TextOutput()
    run = ClassifierRun(target=sys.argv[1], output_format=output_format)
    print(run)
