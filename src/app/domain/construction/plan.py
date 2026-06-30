"""The construction worksheet: the plan an agent fills out for any build activity, before any code.

Each entry names one domain meaning, selects the one construct from the closed whitelist that carries
it, and declares the constructs it is built from, by name. The collection of entries is the construction
graph; construction order is the graph, there is no runner. An entry that cannot legally exist as its
construct (a scalar that composes a domain type, a union with one variant) is not constructible as that
variant: the discriminated union admits each kind only in the shape its card allows.

References between entries are by name, so a construct used by many appears once: one meaning, one entry.
"""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel

# ── Scalars: the worksheet's atomic values ───────────────────────────────────────


class Meaning(RootModel[str], frozen=True):
    """The single domain meaning a construct carries, stated in one sentence."""

    root: str = Field(min_length=1)


class ConstructName(RootModel[str], frozen=True):
    """The name a construct is given, and the way one entry references another."""

    root: str = Field(min_length=1)


class FieldName(RootModel[str], frozen=True):
    """The name of one field within a composite construct."""

    root: str = Field(min_length=1)


class FilePath(RootModel[str], frozen=True):
    """The file an existing, already-built type lives in."""

    root: str = Field(min_length=1)


class Constraint(RootModel[str], frozen=True):
    """A scalar's bound, the `Field(...)` constraint that proves its value space."""

    root: str = Field(min_length=1)


class VocabularyMember(RootModel[str], frozen=True):
    """One member of a closed vocabulary a scalar wraps."""

    root: str = Field(min_length=1)


class Primitive(StrEnum):
    """The closed set of primitives a semantic scalar may wrap."""

    STR = "str"
    INT = "int"
    FLOAT = "float"
    DECIMAL = "Decimal"
    BOOL = "bool"
    BYTES = "bytes"
    DATE = "date"


class ConstructKind(StrEnum):
    """The closed whitelist a build activity selects from, plus the existing-reference row for a type
    built elsewhere."""

    SEMANTIC_SCALAR = "semantic_scalar"
    VALUE_OBJECT = "value_object"
    CONCEPT_MODEL = "concept_model"
    COLLECTION = "collection"
    UNION = "union"
    ORDERED_UNION = "ordered_union"
    DERIVATION = "derivation"
    FOREIGN_MODEL = "foreign_model"
    CONTRACT_MODEL = "contract_model"
    CONSISTENCY_MODEL = "consistency_model"
    VERB = "verb"
    BINDING = "binding"
    ROUTE = "route"
    CONFIG = "config"
    COMPOSITION_ROOT = "composition_root"
    EXISTING = "existing"


# ── Value objects: one edge of the graph ─────────────────────────────────────────


class Member(BaseModel):
    """One named field of a composite, and the construct that field is typed as: an edge from the
    composite to the construct it holds."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    name: FieldName
    holds: ConstructName


class Variants(RootModel[tuple[ConstructName, ...]], frozen=True):
    """The two or more variants of a union, by name. For an ordered union the order is attempt order and
    the failure variant is last."""

    root: tuple[ConstructName, ...] = Field(min_length=2)


# ── A scalar's value space (semantic scalar) ─────────────────────────────────────


class BoundKind(StrEnum):
    CONSTRAINED = "constrained"
    OPEN = "open"


class Constrained(BaseModel):
    """A primitive scalar whose value space is fixed by a constraint."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    bound: Literal[BoundKind.CONSTRAINED] = BoundKind.CONSTRAINED
    constraint: Constraint


class Open(BaseModel):
    """A primitive scalar left unconstrained on purpose, the open range stated as the domain fact."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    bound: Literal[BoundKind.OPEN] = BoundKind.OPEN
    why: Meaning


ScalarBound = Annotated[Constrained | Open, Field(discriminator="bound")]


class BaseKind(StrEnum):
    PRIMITIVE = "primitive"
    VOCABULARY = "vocabulary"


class PrimitiveBase(BaseModel):
    """A scalar over one primitive, with its bound."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    base: Literal[BaseKind.PRIMITIVE] = BaseKind.PRIMITIVE
    primitive: Primitive
    bound: ScalarBound


class VocabularyBase(BaseModel):
    """A scalar over one closed vocabulary, the member set being its value space."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    base: Literal[BaseKind.VOCABULARY] = BaseKind.VOCABULARY
    members: tuple[VocabularyMember, ...] = Field(min_length=1)


ScalarBase = Annotated[PrimitiveBase | VocabularyBase, Field(discriminator="base")]


# ── A collection's shape (collection) ────────────────────────────────────────────


class ShapeKind(StrEnum):
    ORDERED = "ordered"
    KEYED = "keyed"


class OrderedItems(BaseModel):
    """A sequence collection: a tuple of one element type."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    shape: Literal[ShapeKind.ORDERED] = ShapeKind.ORDERED
    element: ConstructName


class KeyedItems(BaseModel):
    """A keyed collection: a namespace whose key-uniqueness is the domain fact."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    shape: Literal[ShapeKind.KEYED] = ShapeKind.KEYED
    key: ConstructName
    value: ConstructName


CollectionShape = Annotated[OrderedItems | KeyedItems, Field(discriminator="shape")]


# ── The construct plans, one variant per whitelist row ───────────────────────────


class SemanticScalarPlan(BaseModel):
    """A single domain value. A leaf: it references no other construct."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.SEMANTIC_SCALAR] = ConstructKind.SEMANTIC_SCALAR
    name: ConstructName
    meaning: Meaning
    space: ScalarBase


class ValueObjectPlan(BaseModel):
    """A small identity-less value composed of scalars."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.VALUE_OBJECT] = ConstructKind.VALUE_OBJECT
    name: ConstructName
    meaning: Meaning
    fields: tuple[Member, ...]


class ConceptModelPlan(BaseModel):
    """A full domain thing or fact, or a union variant, composed of declared types."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.CONCEPT_MODEL] = ConstructKind.CONCEPT_MODEL
    name: ConstructName
    meaning: Meaning
    fields: tuple[Member, ...]


class CollectionPlan(BaseModel):
    """A domain sequence with its own name, bound, or whole-sequence fact."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.COLLECTION] = ConstructKind.COLLECTION
    name: ConstructName
    meaning: Meaning
    items: CollectionShape


class UnionPlan(BaseModel):
    """A choice among variants over one axis, the axis a closed-vocabulary scalar, identity by discriminator."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.UNION] = ConstructKind.UNION
    name: ConstructName
    meaning: Meaning
    axis: ConstructName
    variants: Variants


class OrderedUnionPlan(BaseModel):
    """Identity-free foreign data with expected construction failure, variants in attempt order."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.ORDERED_UNION] = ConstructKind.ORDERED_UNION
    name: ConstructName
    meaning: Meaning
    attempts: Variants


class DerivationPlan(BaseModel):
    """A fact implied by a frozen value's fields, written on the model that owns them."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.DERIVATION] = ConstructKind.DERIVATION
    name: ConstructName
    meaning: Meaning
    owner: ConstructName
    returns: ConstructName


class ForeignModelPlan(BaseModel):
    """Another system's data shape entering the program, its fields lifting the foreign keys."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.FOREIGN_MODEL] = ConstructKind.FOREIGN_MODEL
    name: ConstructName
    meaning: Meaning
    fields: tuple[Member, ...]


class ContractModelPlan(BaseModel):
    """This program's own API request or reply shape, in this program's vocabulary."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.CONTRACT_MODEL] = ConstructKind.CONTRACT_MODEL
    name: ConstructName
    meaning: Meaning
    fields: tuple[Member, ...]


class ConsistencyModelPlan(BaseModel):
    """The single live node of a context: client fields and mutable proven state fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.CONSISTENCY_MODEL] = ConstructKind.CONSISTENCY_MODEL
    name: ConstructName
    meaning: Meaning
    clients: tuple[Member, ...]
    state: tuple[Member, ...]


class VerbPlan(BaseModel):
    """A state transition on the consistency model: it consumes a value and constructs a fact."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.VERB] = ConstructKind.VERB
    name: ConstructName
    meaning: Meaning
    owner: ConstructName
    consumes: ConstructName
    constructs: ConstructName


class BindingPlan(BaseModel):
    """Constructed transport clients bound to the consistency model it builds."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.BINDING] = ConstructKind.BINDING
    name: ConstructName
    meaning: Meaning
    clients: tuple[Member, ...]
    builds: ConstructName


class RoutePlan(BaseModel):
    """Transport ingress: construct an ingress shape, dispatch a verb, serialize a reply."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.ROUTE] = ConstructKind.ROUTE
    name: ConstructName
    meaning: Meaning
    ingress: ConstructName
    dispatches: ConstructName
    reply: ConstructName


class ConfigPlan(BaseModel):
    """Environment values constructed once into declared scalar and secret fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.CONFIG] = ConstructKind.CONFIG
    name: ConstructName
    meaning: Meaning
    fields: tuple[Member, ...]


class CompositionRootPlan(BaseModel):
    """The program entrypoint, wiring config, clients, bindings, the consistency model, and routes."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.COMPOSITION_ROOT] = ConstructKind.COMPOSITION_ROOT
    name: ConstructName
    meaning: Meaning
    wires: tuple[ConstructName, ...]


class ExistingRef(BaseModel):
    """A type built elsewhere. It builds nothing; it carries its name and the file it lives in."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    kind: Literal[ConstructKind.EXISTING] = ConstructKind.EXISTING
    name: ConstructName
    file: FilePath


ConstructPlan = Annotated[
    SemanticScalarPlan
    | ValueObjectPlan
    | ConceptModelPlan
    | CollectionPlan
    | UnionPlan
    | OrderedUnionPlan
    | DerivationPlan
    | ForeignModelPlan
    | ContractModelPlan
    | ConsistencyModelPlan
    | VerbPlan
    | BindingPlan
    | RoutePlan
    | ConfigPlan
    | CompositionRootPlan
    | ExistingRef,
    Field(discriminator="kind"),
]


class Plan(RootModel[tuple[ConstructPlan, ...]], frozen=True):
    """The construction worksheet: every construct a build activity will produce, as a graph of entries
    that reference one another by name. Construction order is the graph; there is no runner."""

    root: tuple[ConstructPlan, ...] = Field(min_length=1)
