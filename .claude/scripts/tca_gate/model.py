# pyright: reportIncompatibleMethodOverride=false
# Row models intentionally expose a `construct` discriminator because the
# ontology file owns that vocabulary. The name shadows Pydantic v1's deprecated
# BaseModel.construct method in stubs, so the override warning is disabled here
# instead of renaming the catalog field away from the doctrine.
"""Declarative grammar for the ontology catalog and violation ledger.

No AST or source inspection lives here. This module constructs the JSON records
the agents exchange: row types, field specs, cross-row coherence, topology
checks, deterministic build order, and the ledger of condemned tree content.
The CLI imports only this module for ``--order`` so ontology proof stays cheap
and independent from source auditing.
"""

import warnings
from pathlib import Path
from typing import Annotated, Literal

warnings.filterwarnings("ignore", message='Field name "construct"')

from pydantic import BaseModel, Field, RootModel, model_validator


class LineNumber(RootModel[int], frozen=True):
    root: int = Field(ge=1)


class RuleBroken(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class Violation(BaseModel, frozen=True, extra="forbid"):
    rule: RuleBroken
    line: LineNumber


_TYPE_NAME = r"^[A-Z][A-Za-z0-9_]*$"


_MEMBER_NAME = r"^[a-z_][a-z0-9_]*$"


_PRIMITIVE_NAMES = ("str", "int", "float", "Decimal", "bool", "bytes", "date")


class ConstraintText(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class OpennessReason(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class StatelessReason(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class FieldSpec(BaseModel, frozen=True, extra="forbid"):
    """A field value carrying more than its type: a foreign-key alias, a wrapper
    path, or a default. The bare `"name": "Type"` form is the type alone."""

    type: str = Field(pattern=_TYPE_NAME)
    alias: str | None = None
    path: tuple[str, ...] | None = None
    default: str | None = None


def field_type(value: "str | FieldSpec") -> str:
    """Return the declared type name from either compact or expanded field form."""

    return value if isinstance(value, str) else value.type


class _Row(BaseModel, frozen=True, extra="forbid"):
    name: str = Field(pattern=_TYPE_NAME)
    file: str = Field(min_length=1)


class SemanticScalarRow(_Row, frozen=True):
    """Ontology row for one atomic domain value."""

    construct: Literal["semantic scalar"]
    primitive: Literal["str", "int", "float", "Decimal", "bool", "bytes", "date"] | None = None
    value_space: str | None = Field(default=None, pattern=_TYPE_NAME)
    members: tuple[str, ...] | None = None
    constraint: ConstraintText | None = None
    openness: OpennessReason | None = None

    @model_validator(mode="after")
    def _one_value_space(self) -> "SemanticScalarRow":
        if (self.primitive is None) == (self.value_space is None):
            raise ValueError(f"semantic scalar {self.name}: exactly one of primitive | value_space")
        if (self.value_space is None) != (self.members is None):
            raise ValueError(f"semantic scalar {self.name}: value_space and members come together")
        if self.members is not None and len(self.members) < 2:
            raise ValueError(f"semantic scalar {self.name}: a closed value space has at least two members")
        if self.primitive is not None and self.constraint is None and self.openness is None:
            raise ValueError(f"semantic scalar {self.name}: a primitive scalar carries a constraint or a stated openness; an unconstrained scalar without stated openness is a structure with no meaning")
        return self


class ValueObjectRow(_Row, frozen=True):
    """Ontology row for a small identity-less composition of scalars."""

    construct: Literal["value object"]
    fields: dict[str, str | FieldSpec] = Field(min_length=1)


class CollectionRow(_Row, frozen=True):
    """Ontology row for a named domain sequence."""

    construct: Literal["collection"]
    element: str = Field(pattern=_TYPE_NAME)
    constraint: ConstraintText | None = None


class KindPin(BaseModel, frozen=True, extra="forbid"):
    """A variant's pinned union axis member."""

    axis: str = Field(pattern=_TYPE_NAME)
    member: str = Field(min_length=1)


class ConceptModelRow(_Row, frozen=True):
    """Ontology row for a full domain thing, fact, or union variant."""

    construct: Literal["concept model"]
    fields: dict[str, str | FieldSpec] = Field(default_factory=dict)
    kind: KindPin | None = None

    @model_validator(mode="after")
    def _payload_or_identity(self) -> "ConceptModelRow":
        if not self.fields and self.kind is None:
            raise ValueError(f"concept model {self.name}: no fields and no kind pin; a row with neither payload nor identity models nothing")
        return self


class UnionRow(_Row, frozen=True):
    """Ontology row for a closed identity-carrying choice over one axis."""

    construct: Literal["union"]
    axis: str = Field(pattern=_TYPE_NAME)
    members: tuple[str, ...] = Field(min_length=2)
    variants: tuple[str, ...] = Field(min_length=2)

    @model_validator(mode="after")
    def _distinct_members(self) -> "UnionRow":
        if len(set(self.members)) != len(self.members):
            raise ValueError(f"union {self.name}: duplicate axis members")
        return self


class OrderedUnionRow(_Row, frozen=True):
    """The expected-failure crossing: ordered selection of identity-free foreign data."""

    construct: Literal["ordered union"]
    axis: str = Field(pattern=_TYPE_NAME)
    members: tuple[str, ...] = Field(min_length=2)
    variants: tuple[str, ...] = Field(min_length=2)

    @model_validator(mode="after")
    def _distinct_members(self) -> "OrderedUnionRow":
        if len(set(self.members)) != len(self.members):
            raise ValueError(f"ordered union {self.name}: duplicate axis members")
        return self


class DerivationRow(BaseModel, frozen=True, extra="forbid"):
    """Ontology row for a fact implied by one frozen value's fields."""

    construct: Literal["derivation"]
    name: str = Field(pattern=_MEMBER_NAME)
    file: str = Field(min_length=1)
    on: str = Field(pattern=_TYPE_NAME)
    returns: str = Field(pattern=_TYPE_NAME)
    compute: dict[str, object] | None = None
    serialized: bool = False


class Captures(BaseModel, frozen=True, extra="forbid"):
    """A verb's capture of a raising client: the declared exception signals and
    the ordered union the caught value constructs."""

    signals: tuple[str, ...] = Field(min_length=1)
    into: str = Field(pattern=_TYPE_NAME)


class VerbRow(BaseModel, frozen=True, extra="forbid"):
    """The consistency model's surface: a transition the one mutable node carries."""

    construct: Literal["verb"]
    name: str = Field(pattern=_MEMBER_NAME)
    file: str = Field(min_length=1)
    on: str = Field(pattern=_TYPE_NAME)
    accepts: str | None = Field(default=None, pattern=_TYPE_NAME)
    returns: str | None = Field(default=None, pattern=_TYPE_NAME)
    yields: str | None = Field(default=None, pattern=_TYPE_NAME)
    constructs: str | None = Field(default=None, pattern=_TYPE_NAME)
    emits: tuple[str, ...] = ()
    captures: Captures | None = None
    state: str | None = None

    @model_validator(mode="after")
    def _exclusive_returns_yields(self) -> "VerbRow":
        if self.returns is not None and self.yields is not None:
            raise ValueError(f"verb {self.name}: returns and yields are mutually exclusive")
        return self

    @model_validator(mode="after")
    def _chain_declared(self) -> "VerbRow":
        if not self.constructs and not self.emits and self.yields is None and self.captures is None:
            raise ValueError(
                f"verb {self.name}: declares no chain; a verb is a transition, and a row that "
                "constructs nothing, emits nothing, yields nothing, and captures nothing is not a verb"
            )
        if self.returns is not None and not self.constructs:
            raise ValueError(
                f"verb {self.name}: returns {self.returns} but constructs nothing; "
                "a verb's return is read off a fact its body constructs"
            )
        return self


class ForeignModelRow(_Row, frozen=True):
    """Ontology row for another system's data shape entering the program."""

    construct: Literal["foreign model"]
    fields: dict[str, str | FieldSpec] = Field(min_length=1)


class ContractModelRow(_Row, frozen=True):
    """Ontology row for this program's own API request or reply shape."""

    construct: Literal["contract model"]
    fields: dict[str, str | FieldSpec] = Field(min_length=1)


class ConsistencyModelRow(_Row, frozen=True):
    """Ontology row for the single live node of a context."""

    construct: Literal["consistency model"]
    clients: dict[str, str] = Field(min_length=1)
    fields: dict[str, str] = Field(default_factory=dict)
    stateless: StatelessReason | None = None

    @model_validator(mode="after")
    def _state_declared(self) -> "ConsistencyModelRow":
        if not self.fields and self.stateless is None:
            raise ValueError(
                f"consistency model {self.name}: holds no state and declares no reason; "
                "the present is fields a verb evolves, or `stateless` with the reason stated"
            )
        if self.fields and self.stateless is not None:
            raise ValueError(
                f"consistency model {self.name}: declares stateless while holding fields; "
                "one of the two is false"
            )
        return self


class BindingRow(_Row, frozen=True):
    """Ontology row for binding constructed clients to the consistency model."""

    construct: Literal["binding"]
    binds: dict[str, str] = Field(min_length=1)
    to: str = Field(pattern=_TYPE_NAME)


class Dispatch(BaseModel, frozen=True, extra="forbid"):
    """A route dispatch target: verb name plus the value passed to it."""

    verb: str = Field(pattern=_MEMBER_NAME)
    value: str = Field(min_length=1)


class RouteRow(_Row, frozen=True):
    """Ontology row for transport ingress."""

    construct: Literal["route"]
    ingress: str | None = Field(default=None, pattern=_TYPE_NAME)
    dispatch: Dispatch | None = None
    reply: str | None = Field(default=None, pattern=_TYPE_NAME)


class ConfigRow(_Row, frozen=True):
    """Ontology row for environment values constructed once."""

    construct: Literal["config"]
    env_prefix: str | None = None
    fields: dict[str, str | FieldSpec] = Field(min_length=1)


class CompositionRootRow(_Row, frozen=True):
    """Ontology row for program startup wiring."""

    construct: Literal["composition root"]


class ExistingRow(_Row, frozen=True):
    """A type that already exists; a reference target, never a build item."""

    construct: Literal["existing"]


Row = Annotated[
    SemanticScalarRow
    | ValueObjectRow
    | CollectionRow
    | ConceptModelRow
    | UnionRow
    | OrderedUnionRow
    | DerivationRow
    | VerbRow
    | ForeignModelRow
    | ContractModelRow
    | ConsistencyModelRow
    | BindingRow
    | RouteRow
    | ConfigRow
    | CompositionRootRow
    | ExistingRow,
    Field(discriminator="construct"),
]


_REFERENCEABLE = {"semantic scalar", "value object", "collection", "concept model", "union", "ordered union", "foreign model", "contract model", "existing"}


def _row_refs(row: Row) -> tuple[str, ...]:
    """Return the row names this row depends on for coherence and build order."""

    if isinstance(row, CollectionRow):
        return (row.element,)
    if isinstance(row, (ValueObjectRow, ConceptModelRow, ForeignModelRow, ContractModelRow)):
        return tuple(field_type(v) for v in row.fields.values())
    if isinstance(row, ConfigRow):
        return tuple(field_type(v) for v in row.fields.values() if field_type(v) != "SecretStr")
    if isinstance(row, UnionRow):
        return row.variants
    if isinstance(row, OrderedUnionRow):
        return row.variants
    if isinstance(row, DerivationRow):
        return (row.on, row.returns)
    if isinstance(row, VerbRow):
        chain = tuple(ref for ref in (row.accepts, row.returns, row.yields, row.constructs) if ref is not None) + row.emits
        return chain + ((row.captures.into,) if row.captures is not None else ())
    if isinstance(row, ConsistencyModelRow):
        return tuple(row.fields.values())
    if isinstance(row, BindingRow):
        return (row.to,)
    if isinstance(row, RouteRow):
        return tuple(ref for ref in (row.ingress, row.reply) if ref is not None)
    return ()


class OntologyContext(BaseModel, frozen=True, extra="forbid"):
    """A named domain context and the ontology rows that belong to it."""

    name: str = Field(min_length=1)
    features: tuple[str, ...] = ()
    rows: tuple[Row, ...] = Field(min_length=1)


class OntologyCatalog(BaseModel, frozen=True, extra="forbid"):
    """The constructed ontology catalog consumed by the gate and builder."""

    contexts: tuple[OntologyContext, ...] = Field(min_length=1)

    @property
    def rows(self) -> tuple[Row, ...]:
        """Flatten context rows in catalog order."""

        return tuple(row for context in self.contexts for row in context.rows)

    @model_validator(mode="after")
    def _coherent(self) -> "OntologyCatalog":
        """Prove cross-row coherence that single row construction cannot see."""

        named = [r for r in self.rows if not isinstance(r, (DerivationRow, VerbRow))]
        by_name: dict[str, Row] = {}
        for r in named:
            if r.name in by_name:
                raise ValueError(f"duplicate row name {r.name}")
            by_name[r.name] = r
        deriv_keys = [(r.on, r.name) for r in self.rows if isinstance(r, DerivationRow)]
        if len(set(deriv_keys)) != len(deriv_keys):
            raise ValueError("duplicate derivation (on, name)")
        verb_keys = [(r.on, r.name) for r in self.rows if isinstance(r, VerbRow)]
        if len(set(verb_keys)) != len(verb_keys):
            raise ValueError("duplicate verb (on, name)")
        consistency_models = [r for r in self.rows if isinstance(r, ConsistencyModelRow)]
        if len(consistency_models) > 1:
            raise ValueError("two consistency models in one context; one unfrozen node per context")
        for row in self.rows:
            for ref in _row_refs(row):
                target = by_name.get(ref)
                if target is None:
                    raise ValueError(f"{row.name}: reference {ref} resolves to no row")
                if not isinstance(row, BindingRow) and target.construct not in _REFERENCEABLE:
                    raise ValueError(f"{row.name}: reference {ref} is a {target.construct}, not a value type")
            if isinstance(row, BindingRow):
                target = by_name[row.to]
                if not isinstance(target, (ConsistencyModelRow, ExistingRow)):
                    raise ValueError(f"binding {row.name}: binds to {row.to}, which is neither the consistency model nor an existing row naming one")
                if isinstance(target, ConsistencyModelRow) and row.binds != target.clients:
                    raise ValueError(f"binding {row.name}: binds must exactly match client fields on {row.to}")
            if isinstance(row, UnionRow):
                pinned: set[str] = set()
                for variant_name in row.variants:
                    variant = by_name[variant_name]
                    if isinstance(variant, ConceptModelRow):
                        if variant.kind is None:
                            raise ValueError(f"union {row.name}: variant {variant_name} pins no kind")
                        if variant.kind.axis != row.axis:
                            raise ValueError(f"union {row.name}: variant {variant_name} pins axis {variant.kind.axis}, union axis is {row.axis}")
                        if variant.kind.member not in row.members:
                            raise ValueError(f"union {row.name}: variant {variant_name} pins {variant.kind.member}, not an axis member")
                        if variant.kind.member in pinned:
                            raise ValueError(f"union {row.name}: member {variant.kind.member} pinned twice")
                        pinned.add(variant.kind.member)
                    elif not isinstance(variant, ExistingRow):
                        raise ValueError(f"union {row.name}: variant {variant_name} is a {variant.construct}, not a concept model")
            if isinstance(row, OrderedUnionRow):
                ordered_pinned: set[str] = set()
                for variant_name in row.variants:
                    variant = by_name[variant_name]
                    if isinstance(variant, ConceptModelRow):
                        if variant.kind is None:
                            raise ValueError(f"ordered union {row.name}: variant {variant_name} pins no kind")
                        if variant.kind.axis != row.axis:
                            raise ValueError(f"ordered union {row.name}: variant {variant_name} pins axis {variant.kind.axis}, ordered union axis is {row.axis}")
                        if variant.kind.member not in row.members:
                            raise ValueError(f"ordered union {row.name}: variant {variant.kind.member}, not an axis member")
                        if variant.kind.member in ordered_pinned:
                            raise ValueError(f"ordered union {row.name}: member {variant.kind.member} pinned twice")
                        ordered_pinned.add(variant.kind.member)
                    elif not isinstance(variant, ExistingRow):
                        raise ValueError(f"ordered union {row.name}: variant {variant_name} is a {variant.construct}, not a concept model")
            if isinstance(row, DerivationRow):
                on_row = by_name.get(row.on)
                if on_row is None:
                    raise ValueError(f"derivation {row.name}: on {row.on} resolves to no row")
                if not isinstance(on_row, ExistingRow) and on_row.file != row.file:
                    raise ValueError(f"derivation {row.name}: lives in {row.file}, its model lives in {on_row.file}")
            if isinstance(row, VerbRow):
                on_row = by_name.get(row.on)
                if not isinstance(on_row, ConsistencyModelRow):
                    raise ValueError(f"verb {row.name}: on {row.on}, which is not the consistency model; a verb is a transition on the consistency model")
                if on_row.file != row.file:
                    raise ValueError(f"verb {row.name}: lives in {row.file}, its consistency model lives in {on_row.file}")
                taken = set(on_row.fields) | set(on_row.clients)
                if row.name in taken:
                    raise ValueError(f"verb {row.name}: shares its name with a field or client on {row.on}; one name, one office")
        self._topology_rules()
        return self

    def _topology_rules(self) -> None:
        """Enforce file-placement rules derived from the topology doctrine."""

        for row in self.rows:
            base = Path(row.file).name
            if isinstance(row, SemanticScalarRow) and base != "type.py":
                raise ValueError(f"semantic scalar {row.name}: belongs in type.py, not {row.file}")
            if base == "type.py" and row.construct not in {"semantic scalar", "existing"}:
                raise ValueError(f"{row.name}: type.py holds the atomic vocabulary only, not a {row.construct}")
            if isinstance(row, CompositionRootRow) and base != "main.py":
                raise ValueError(f"composition root row {row.name}: file must be main.py")
            if isinstance(row, ConfigRow) and base != "config.py":
                raise ValueError(f"config {row.name}: file must be config.py")
            if isinstance(row, BindingRow) and "service/" not in row.file:
                raise ValueError(f"binding {row.name}: belongs under service/")
            if isinstance(row, RouteRow) and "api/" not in row.file:
                raise ValueError(f"route {row.name}: belongs under api/")
            if isinstance(row, ContractModelRow) and base != "api.py":
                raise ValueError(f"contract model {row.name}: belongs in the context's api.py")
            if isinstance(row, (ForeignModelRow, OrderedUnionRow)) and (base in {"api.py", "config.py", "main.py"} or "service/" in row.file or "api/" in row.file):
                raise ValueError(f"{row.construct} {row.name}: belongs in the concept-named file of the foreign thing it models, not {row.file}")

    def build_order(self) -> tuple[Row, ...]:
        """Return buildable rows in dependency order.

        Existing rows, derivations, and verbs do not produce standalone files in
        the ordered build. The rank only breaks ties between dependency-ready
        rows so the printed order is stable and follows the construct stack.
        """

        named = {r.name: r for r in self.rows if not isinstance(r, (DerivationRow, VerbRow))}
        construct_rank = {
            "semantic scalar": 0, "value object": 1, "collection": 2, "concept model": 3,
            "union": 4, "foreign model": 5, "contract model": 6, "ordered union": 7,
            "consistency model": 8, "verb": 9, "binding": 10, "route": 11,
            "config": 12, "composition root": 13,
        }
        buildable = [r for r in self.rows if not isinstance(r, (DerivationRow, VerbRow, ExistingRow))]
        deps = {
            r.name: {ref for ref in _row_refs(r) if ref in named and not isinstance(named[ref], ExistingRow)}
            for r in buildable
        }
        ordered: list[Row] = []
        placed: set[str] = set()
        remaining = {r.name: r for r in buildable}
        while remaining:
            ready = sorted(
                (name for name in remaining if deps[name] <= placed),
                key=lambda n: (construct_rank[remaining[n].construct], n),
            )
            if not ready:
                raise ValueError("dependency cycle among rows: " + ", ".join(sorted(remaining)))
            for name in ready:
                ordered.append(remaining.pop(name))
                placed.add(name)
        return tuple(ordered)


class ViolationFound(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class ViolationNote(RootModel[str], frozen=True):
    root: str = Field(min_length=20, max_length=400)


class ViolationEntry(BaseModel, frozen=True, extra="forbid"):
    """A violation observed in the tree: sentenced and noted, never solved here."""

    file: str = Field(min_length=1)
    found: ViolationFound
    breaks: Literal["escaped", "duplicated", "vacuous", "fused"]
    note: ViolationNote


class ViolationLog(BaseModel, frozen=True, extra="forbid"):
    """The target violation ledger: observed violations the ontology has sentenced."""

    violations: tuple[ViolationEntry, ...] = ()

    @model_validator(mode="after")
    def _entries_unique(self) -> "ViolationLog":
        keys = [(v.file, v.found) for v in self.violations]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate violation entry (file, found); one entry per violation")
        return self
