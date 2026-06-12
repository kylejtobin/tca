# pyright: reportIncompatibleMethodOverride=false
# Every row's `construct` discriminator field shadows pydantic's deprecated v1
# `BaseModel.construct` classmethod in the stubs; the spec format owns the name.
"""TCA gate: deterministic enforcement of model-first construction (PreToolUse Write|Edit).

The hook fires on `.py` writes in scope, only; the catalog (exactly one,
at the repo root `spec/model.json`) is written freely and proven by
construction wherever it is consumed:

1. `.py` writes are denied unless a valid model table claims the file, and
   every class in the file is checked against its row: name, construct shape,
   frozen-ness, exact field set, exact field types. Code the table did not
   model cannot be written, and a table that fails construction blocks every
   build it would govern.
2. `--order TABLE` validates the table and prints the build order as a
   topological sort. The builder follows the printed order; it never chooses.
3. `--check FILE...` runs the same audits standalone (model.json included).

Legacy audits (bare primitives, mutable containers, Optional fields, raw
Literals, bare enums) still run on every write. `arbitrary_types_allowed` is
legal on exactly the class the table names as the consistency model, nowhere else.
`model_validator(mode="after")` is denied everywhere (the asserting-validator
exception is removed from the doctrine); `mode="before"` is legal only in a
file a boundary or ordered crossing row claims.

Modes: hook (stdin PreToolUse event), --check FILE..., --order TABLE.

This file is procedural code policing a declarative doctrine, and the
inversion is deliberate. A language model generates by continuation over a
corpus that is overwhelmingly procedural, so type-driven invariants stated
as instructions compete with that prior on every token; stated as
write-time constraints, they do not compete at all. The gate holds the
line while constraint migrates to where it belongs, into the grammar of
what the agents can express, and it shrinks as that migration proceeds.
It is scaffolding with a demolition date, kept exactly as long as it is
load-bearing.
"""

import ast
import json
import os
import sys
import warnings
from pathlib import Path
from typing import Annotated, Literal

warnings.filterwarnings("ignore", message='Field name "construct"')

from pydantic import BaseModel, Field, RootModel, ValidationError, model_validator

# --------------------------------------------------------------------------
# Verdict types
# --------------------------------------------------------------------------


class LineNumber(RootModel[int], frozen=True):
    root: int = Field(ge=1)


class RuleBroken(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class Violation(BaseModel, frozen=True, extra="forbid"):
    rule: RuleBroken
    line: LineNumber


# --------------------------------------------------------------------------
# Model table grammar. The agent's modeling judgment is expressed only in
# this form; anything else fails construction and never reaches a .py file.
# --------------------------------------------------------------------------

_TYPE_NAME = r"^[A-Z][A-Za-z0-9_]*$"
_MEMBER_NAME = r"^[a-z_][a-z0-9_]*$"
_PRIMITIVE_NAMES = ("str", "int", "float", "Decimal", "bool", "bytes", "date")


class _Row(BaseModel, frozen=True, extra="forbid"):
    name: str = Field(pattern=_TYPE_NAME)
    file: str = Field(min_length=1)


class ScalarRow(_Row, frozen=True):
    construct: Literal["scalar"]
    primitive: Literal["str", "int", "float", "Decimal", "bool", "bytes", "date"] | None = None
    value_space: str | None = Field(default=None, pattern=_TYPE_NAME)
    members: tuple[str, ...] | None = None
    constraint: str | None = None

    @model_validator(mode="after")
    def _one_value_space(self) -> "ScalarRow":
        if (self.primitive is None) == (self.value_space is None):
            raise ValueError(f"scalar {self.name}: exactly one of primitive | value_space")
        if (self.value_space is None) != (self.members is None):
            raise ValueError(f"scalar {self.name}: value_space and members come together")
        if self.members is not None and len(self.members) < 2:
            raise ValueError(f"scalar {self.name}: a closed value space has at least two members")
        return self


class CollectionRow(_Row, frozen=True):
    construct: Literal["collection"]
    element: str = Field(pattern=_TYPE_NAME)
    constraint: str | None = None


class KindPin(BaseModel, frozen=True, extra="forbid"):
    axis: str = Field(pattern=_TYPE_NAME)
    member: str = Field(min_length=1)


class FrozenModelRow(_Row, frozen=True):
    construct: Literal["frozen_model"]
    fields: dict[str, str] = Field(default_factory=dict)
    kind: KindPin | None = None

    @model_validator(mode="after")
    def _payload_or_identity(self) -> "FrozenModelRow":
        if not self.fields and self.kind is None:
            raise ValueError(f"frozen_model {self.name}: no fields and no kind pin; a row with neither payload nor identity models nothing")
        return self


class UnionRow(_Row, frozen=True):
    construct: Literal["union"]
    axis: str = Field(pattern=_TYPE_NAME)
    members: tuple[str, ...] = Field(min_length=2)
    variants: tuple[str, ...] = Field(min_length=2)


class DiscriminatedUnionRow(_Row, frozen=True):
    construct: Literal["discriminated_union"]
    over: str = Field(pattern=_TYPE_NAME)


class OrderedUnionRow(_Row, frozen=True):
    """The expected-failure crossing: ordered selection, legal only at the boundary."""

    construct: Literal["ordered_union"]
    over: str = Field(pattern=_TYPE_NAME)


class DerivationRow(BaseModel, frozen=True, extra="forbid"):
    construct: Literal["derivation"]
    name: str = Field(pattern=_MEMBER_NAME)
    file: str = Field(min_length=1)
    on: str = Field(pattern=_TYPE_NAME)
    returns: str = Field(pattern=_TYPE_NAME)


class VerbRow(BaseModel, frozen=True, extra="forbid"):
    """The consistency model's surface: a transition the one mutable node carries."""

    construct: Literal["verb"]
    name: str = Field(pattern=_MEMBER_NAME)
    file: str = Field(min_length=1)
    on: str = Field(pattern=_TYPE_NAME)
    accepts: str | None = Field(default=None, pattern=_TYPE_NAME)
    returns: str | None = Field(default=None, pattern=_TYPE_NAME)
    yields: str | None = Field(default=None, pattern=_TYPE_NAME)
    constructs: tuple[str, ...] = ()
    emits: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _exclusive_returns_yields(self) -> "VerbRow":
        if self.returns is not None and self.yields is not None:
            raise ValueError(f"verb {self.name}: returns and yields are mutually exclusive")
        return self

    @model_validator(mode="after")
    def _chain_declared(self) -> "VerbRow":
        if not self.constructs and not self.emits and self.yields is None:
            raise ValueError(
                f"verb {self.name}: declares no chain; a verb is a transition, and a row that "
                "constructs nothing, emits nothing, and yields nothing is not a verb"
            )
        if self.returns is not None and not self.constructs:
            raise ValueError(
                f"verb {self.name}: returns {self.returns} but constructs nothing; "
                "a verb's return is read off a fact its body constructs"
            )
        return self


class BoundaryRow(_Row, frozen=True):
    construct: Literal["boundary"]
    fields: dict[str, str] = Field(min_length=1)


class ConsistencyModelRow(_Row, frozen=True):
    construct: Literal["consistency_model"]
    clients: dict[str, str] = Field(min_length=1)
    fields: dict[str, str] = Field(default_factory=dict)
    stateless: str | None = Field(default=None, min_length=1)

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


class ServiceRow(_Row, frozen=True):
    construct: Literal["service"]
    binds: str = Field(pattern=_TYPE_NAME)
    to: str = Field(pattern=_TYPE_NAME)


class RouteRow(_Row, frozen=True):
    construct: Literal["route"]


class ConfigRow(_Row, frozen=True):
    construct: Literal["config"]
    fields: dict[str, str] = Field(min_length=1)


class MainRow(_Row, frozen=True):
    construct: Literal["main"]


class ExternalRow(_Row, frozen=True):
    """A type that already exists; a reference target, never a build item."""

    construct: Literal["external"]


Row = Annotated[
    ScalarRow
    | CollectionRow
    | FrozenModelRow
    | UnionRow
    | DiscriminatedUnionRow
    | OrderedUnionRow
    | DerivationRow
    | VerbRow
    | BoundaryRow
    | ConsistencyModelRow
    | ServiceRow
    | RouteRow
    | ConfigRow
    | MainRow
    | ExternalRow,
    Field(discriminator="construct"),
]

_REFERENCEABLE = {"scalar", "collection", "frozen_model", "union", "discriminated_union", "ordered_union", "external"}


def _row_refs(row: Row) -> tuple[str, ...]:
    if isinstance(row, CollectionRow):
        return (row.element,)
    if isinstance(row, (FrozenModelRow, BoundaryRow, ConfigRow)):
        return tuple(row.fields.values())
    if isinstance(row, UnionRow):
        return row.variants
    if isinstance(row, (DiscriminatedUnionRow, OrderedUnionRow)):
        return (row.over,)
    if isinstance(row, DerivationRow):
        return (row.on, row.returns)
    if isinstance(row, VerbRow):
        return tuple(ref for ref in (row.accepts, row.returns, row.yields) if ref is not None) + row.constructs + row.emits
    if isinstance(row, ConsistencyModelRow):
        return tuple(row.fields.values())
    if isinstance(row, ServiceRow):
        return (row.to,)
    return ()


class ModelTable(BaseModel, frozen=True, extra="forbid"):
    context: str = Field(min_length=1)
    rows: tuple[Row, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _coherent(self) -> "ModelTable":
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
                if not isinstance(row, ServiceRow) and target.construct not in _REFERENCEABLE:
                    raise ValueError(f"{row.name}: reference {ref} is a {target.construct}, not a value type")
            if isinstance(row, ServiceRow) and not isinstance(by_name[row.to], (ConsistencyModelRow, ExternalRow)):
                raise ValueError(f"service {row.name}: binds to {row.to}, which is neither the consistency model nor an external row naming one")
            if isinstance(row, UnionRow):
                if len(set(row.members)) != len(row.members):
                    raise ValueError(f"union {row.name}: duplicate axis members")
                pinned: set[str] = set()
                for variant_name in row.variants:
                    variant = by_name[variant_name]
                    if isinstance(variant, FrozenModelRow):
                        if variant.kind is None:
                            raise ValueError(f"union {row.name}: variant {variant_name} pins no kind")
                        if variant.kind.axis != row.axis:
                            raise ValueError(f"union {row.name}: variant {variant_name} pins axis {variant.kind.axis}, union axis is {row.axis}")
                        if variant.kind.member not in row.members:
                            raise ValueError(f"union {row.name}: variant {variant_name} pins {variant.kind.member}, not an axis member")
                        if variant.kind.member in pinned:
                            raise ValueError(f"union {row.name}: member {variant.kind.member} pinned twice")
                        pinned.add(variant.kind.member)
                    elif not isinstance(variant, ExternalRow):
                        raise ValueError(f"union {row.name}: variant {variant_name} is a {variant.construct}, not a frozen model")
            if isinstance(row, (DiscriminatedUnionRow, OrderedUnionRow)) and not isinstance(by_name[row.over], (UnionRow, ExternalRow)):
                raise ValueError(f"{'envelope' if isinstance(row, DiscriminatedUnionRow) else 'crossing'} {row.name}: over {row.over}, which is not a union")
            if isinstance(row, DerivationRow):
                on_row = by_name.get(row.on)
                if on_row is None:
                    raise ValueError(f"derivation {row.name}: on {row.on} resolves to no row")
                if not isinstance(on_row, ExternalRow) and on_row.file != row.file:
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
        for row in self.rows:
            base = Path(row.file).name
            if isinstance(row, ScalarRow) and base != "type.py":
                raise ValueError(f"scalar {row.name}: belongs in type.py, not {row.file}")
            if base == "type.py" and row.construct not in {"scalar", "external"}:
                raise ValueError(f"{row.name}: type.py holds the atomic vocabulary only, not a {row.construct}")
            if isinstance(row, MainRow) and base != "main.py":
                raise ValueError(f"main row {row.name}: file must be main.py")
            if isinstance(row, ConfigRow) and base != "config.py":
                raise ValueError(f"config {row.name}: file must be config.py")
            if isinstance(row, ServiceRow) and "service/" not in row.file:
                raise ValueError(f"service {row.name}: belongs under service/")
            if isinstance(row, RouteRow) and "api/" not in row.file:
                raise ValueError(f"route {row.name}: belongs under api/")
            if isinstance(row, BoundaryRow) and base != "api.py":
                raise ValueError(f"boundary {row.name}: belongs in the context's api.py")
            if isinstance(row, OrderedUnionRow) and base != "api.py":
                raise ValueError(f"ordered crossing {row.name}: ordered selection is legal exactly at the identity-free boundary crossing and nowhere else (api.py)")

    def build_order(self) -> tuple[Row, ...]:
        named = {r.name: r for r in self.rows if not isinstance(r, (DerivationRow, VerbRow))}
        construct_rank = {
            "scalar": 0, "collection": 1, "frozen_model": 2, "union": 3,
            "discriminated_union": 4, "ordered_union": 5, "boundary": 6,
            "consistency_model": 7, "service": 8, "route": 9, "config": 10, "main": 11,
        }
        buildable = [r for r in self.rows if not isinstance(r, (DerivationRow, VerbRow, ExternalRow))]
        deps = {
            r.name: {ref for ref in _row_refs(r) if ref in named and not isinstance(named[ref], ExternalRow)}
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


# --------------------------------------------------------------------------
# Hook event shapes
# --------------------------------------------------------------------------


class _Edit(BaseModel, extra="ignore"):
    old_string: str | None = None
    new_string: str | None = None
    old_text: str | None = None
    new_text: str | None = None


class _ToolInput(BaseModel, extra="ignore"):
    file_path: str = ""
    content: str | None = None
    file_content: str | None = None
    file_text: str | None = None
    old_string: str | None = None
    new_string: str | None = None
    edits: list[_Edit] | None = None


class _HookEvent(BaseModel, extra="ignore"):
    tool_name: str = ""
    tool_input: _ToolInput = Field(default_factory=_ToolInput)


_PRIMITIVES = {"str", "int", "float", "bool", "bytes", "Decimal", "date", "complex", "bytearray"}
_ENUM_BASES = {"Enum", "StrEnum", "IntEnum", "IntFlag", "Flag"}
_CONTAINERS = {"list", "tuple", "set", "frozenset", "dict"}
_MUTABLE_CONTAINERS = {"list", "set", "dict"}
_DERIVATION_DECORATORS = {"cached_property", "computed_field", "property"}
_VALIDATOR_DECORATORS = {"model_validator", "field_validator", "classmethod"}


def _resulting_source(tool_input: _ToolInput) -> str | None:
    for whole in (tool_input.content, tool_input.file_content, tool_input.file_text):
        if whole is not None:
            return whole
    path = Path(tool_input.file_path)
    base = path.read_text() if path.exists() else ""
    if tool_input.edits:
        for edit in tool_input.edits:
            old = edit.old_string or edit.old_text or ""
            new = edit.new_string or edit.new_text or ""
            base = base.replace(old, new, 1) if old else base
        return base
    if tool_input.old_string is not None and tool_input.new_string is not None:
        return base.replace(tool_input.old_string, tool_input.new_string, 1)
    return tool_input.new_string


# --------------------------------------------------------------------------
# AST helpers
# --------------------------------------------------------------------------


def _base_names(node: ast.ClassDef) -> list[str]:
    names: list[str] = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)
        elif isinstance(base, ast.Subscript) and isinstance(base.value, ast.Name):
            names.append(base.value.id)
    return names


def _annotation_is_primitive(annotation: ast.expr) -> bool:
    if isinstance(annotation, ast.Name):
        return annotation.id in _PRIMITIVES
    if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name):
        if annotation.value.id not in _CONTAINERS:
            return False
        slice_node = annotation.slice
        elements = slice_node.elts if isinstance(slice_node, ast.Tuple) else [slice_node]
        return any(isinstance(e, ast.Name) and e.id in _PRIMITIVES for e in elements)
    return False


def _annotation_is_mutable_container(annotation: ast.expr) -> bool:
    if isinstance(annotation, ast.Name):
        return annotation.id in _MUTABLE_CONTAINERS
    if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name):
        return annotation.value.id in _MUTABLE_CONTAINERS
    return False


def _is_none_constant(node: ast.expr) -> bool:
    return isinstance(node, ast.Constant) and node.value is None


def _annotation_is_optional(annotation: ast.expr) -> bool:
    if isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
        return (
            _is_none_constant(annotation.left)
            or _is_none_constant(annotation.right)
            or _annotation_is_optional(annotation.left)
            or _annotation_is_optional(annotation.right)
        )
    if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name):
        return annotation.value.id == "Optional"
    return False


def _annotation_is_raw_literal(annotation: ast.expr) -> bool:
    if not (isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name) and annotation.value.id == "Literal"):
        return False
    slice_node = annotation.slice
    elements = slice_node.elts if isinstance(slice_node, ast.Tuple) else [slice_node]
    return any(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in elements)


def _annotation_names_enum(annotation: ast.expr, enum_names: set[str]) -> bool:
    if isinstance(annotation, ast.Name):
        return annotation.id in enum_names
    if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name) and annotation.value.id in _CONTAINERS:
        slice_node = annotation.slice
        elements = slice_node.elts if isinstance(slice_node, ast.Tuple) else [slice_node]
        return any(isinstance(e, ast.Name) and e.id in enum_names for e in elements)
    return False


def _configdict_keyword(value: ast.expr | None, arg: str) -> bool:
    if not isinstance(value, ast.Call):
        return False
    func = value.func
    name = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else ""
    if name != "ConfigDict":
        return False
    return any(
        kw.arg == arg and isinstance(kw.value, ast.Constant) and kw.value.value in (True, "forbid")
        for kw in value.keywords
    )


def _class_has_flag(node: ast.ClassDef, arg: str) -> bool:
    for keyword in node.keywords:
        if keyword.arg == arg and isinstance(keyword.value, ast.Constant) and keyword.value.value in (True, "forbid"):
            return True
    return any(
        isinstance(item, (ast.Assign, ast.AnnAssign)) and _configdict_keyword(item.value, arg)
        for item in node.body
    )


def _class_fields(node: ast.ClassDef) -> dict[str, ast.expr]:
    return {
        item.target.id: item.annotation
        for item in node.body
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name) and item.target.id != "model_config"
    }


def _annotation_names_exactly(annotation: ast.expr, expected: str) -> bool:
    return isinstance(annotation, ast.Name) and annotation.id == expected


def _annotation_is_kind_pin(annotation: ast.expr, pin: KindPin) -> bool:
    if not (isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name) and annotation.value.id == "Literal"):
        return False
    inner = annotation.slice
    return (
        isinstance(inner, ast.Attribute)
        and isinstance(inner.value, ast.Name)
        and inner.value.id == pin.axis
        and inner.attr == pin.member.upper()
    )


def _annotation_is_element_tuple(annotation: ast.expr, element: str) -> bool:
    if not (isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name) and annotation.value.id == "tuple"):
        return False
    inner = annotation.slice
    if not isinstance(inner, ast.Tuple) or len(inner.elts) != 2:
        return False
    head, tail = inner.elts
    return (
        isinstance(head, ast.Name) and head.id == element
        and isinstance(tail, ast.Constant) and tail.value is Ellipsis
    )


def _flatten_union(annotation: ast.expr) -> list[str] | None:
    if isinstance(annotation, ast.Name):
        return [annotation.id]
    if isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
        left = _flatten_union(annotation.left)
        right = _flatten_union(annotation.right)
        if left is None or right is None:
            return None
        return left + right
    return None


def _has_discriminator_kind(item: ast.AnnAssign) -> bool:
    value = item.value
    if not isinstance(value, ast.Call):
        return False
    func = value.func
    name = func.id if isinstance(func, ast.Name) else ""
    if name != "Field":
        return False
    return any(
        kw.arg == "discriminator" and isinstance(kw.value, ast.Constant) and kw.value.value == "kind"
        for kw in value.keywords
    )


def _decorator_names(func: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    names: set[str] = set()
    for decorator in func.decorator_list:
        node = decorator.func if isinstance(decorator, ast.Call) else decorator
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
    return names


def _validator_mode(func: ast.FunctionDef) -> str | None:
    for decorator in func.decorator_list:
        if isinstance(decorator, ast.Call):
            target = decorator.func
            name = target.id if isinstance(target, ast.Name) else target.attr if isinstance(target, ast.Attribute) else ""
            if name == "model_validator":
                for kw in decorator.keywords:
                    if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                        return str(kw.value.value)
    return None


def _enum_member_names(node: ast.ClassDef) -> set[str]:
    return {
        target.id.lower()
        for item in node.body
        if isinstance(item, ast.Assign)
        for target in item.targets
        if isinstance(target, ast.Name)
    }


# --------------------------------------------------------------------------
# Legacy audit (table-unaware breaks)
# --------------------------------------------------------------------------


def _legacy_audit(tree: ast.Module, consistency_model_name: str | None) -> list[Violation]:
    found: list[Violation] = []
    enum_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and any(b in _ENUM_BASES for b in _base_names(node))
    }
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        bases = _base_names(node)
        if _class_has_flag(node, "arbitrary_types_allowed") and node.name != consistency_model_name:
            found.append(
                Violation(rule=RuleBroken(f"arbitrary_types_allowed on {node.name}, which the model table does not name as the consistency model"), line=LineNumber(node.lineno))
            )
        is_root_model = any("RootModel" in b for b in bases)
        is_base_model = any(b in {"BaseModel", "BaseSettings"} for b in bases)
        if not (is_base_model and not is_root_model):
            continue
        for item in node.body:
            if not (isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name) and item.target.id != "model_config"):
                continue
            if _annotation_is_optional(item.annotation):
                found.append(Violation(rule=RuleBroken(f"absence fused into field `{item.target.id}` (`T | None`); factor the states into a union over a named axis"), line=LineNumber(item.lineno)))
            elif _annotation_is_mutable_container(item.annotation):
                found.append(Violation(rule=RuleBroken(f"mutable container field `{item.target.id}`; a sequence is `tuple[T, ...]` or a Collection, a mapping is an association (entry model + collection + query model)"), line=LineNumber(item.lineno)))
            elif _annotation_is_primitive(item.annotation):
                found.append(Violation(rule=RuleBroken(f"bare primitive field `{item.target.id}`; use a semantic scalar"), line=LineNumber(item.lineno)))
            elif _annotation_names_enum(item.annotation, enum_names) and node.name != consistency_model_name:
                found.append(Violation(rule=RuleBroken(f"standalone enum as field `{item.target.id}`; declare its value space as a RootModel scalar"), line=LineNumber(item.lineno)))
            elif _annotation_is_raw_literal(item.annotation):
                found.append(Violation(rule=RuleBroken(f"raw string Literal field `{item.target.id}`; pin a StrEnum member, never a bare string"), line=LineNumber(item.lineno)))
    return found


# --------------------------------------------------------------------------
# Row conformance: the written file against the table that models it
# --------------------------------------------------------------------------


def _check_scalar(node: ast.ClassDef, row: ScalarRow) -> list[Violation]:
    found: list[Violation] = []
    if not any("RootModel" in b for b in _base_names(node)):
        found.append(Violation(rule=RuleBroken(f"{row.name} is modeled scalar; the shape is class {row.name}(RootModel[...], frozen=True)"), line=LineNumber(node.lineno)))
        return found
    if not _class_has_flag(node, "frozen"):
        found.append(Violation(rule=RuleBroken(f"{row.name}: scalar must be frozen=True"), line=LineNumber(node.lineno)))
    expected = row.primitive if row.primitive is not None else row.value_space
    root = _class_fields(node).get("root")
    if root is None or not _annotation_names_exactly(root, str(expected)):
        found.append(Violation(rule=RuleBroken(f"{row.name}: root must be annotated {expected}, as modeled"), line=LineNumber(node.lineno)))
    return found


def _check_collection(node: ast.ClassDef, row: CollectionRow) -> list[Violation]:
    found: list[Violation] = []
    if not any("RootModel" in b for b in _base_names(node)) or not _class_has_flag(node, "frozen"):
        found.append(Violation(rule=RuleBroken(f"{row.name} is modeled collection; the shape is class {row.name}(RootModel[tuple[{row.element}, ...]], frozen=True)"), line=LineNumber(node.lineno)))
    root = _class_fields(node).get("root")
    if root is None or not _annotation_is_element_tuple(root, row.element):
        found.append(Violation(rule=RuleBroken(f"{row.name}: root must be tuple[{row.element}, ...], as modeled"), line=LineNumber(node.lineno)))
    return found


def _check_fields_exact(node: ast.ClassDef, row_name: str, declared: dict[str, str], kind: KindPin | None) -> list[Violation]:
    found: list[Violation] = []
    actual = _class_fields(node)
    expected_names = set(declared) | ({"kind"} if kind else set[str]())
    for fname in sorted(set(actual) - expected_names):
        found.append(Violation(rule=RuleBroken(f"{row_name}: field `{fname}` is not in the model table; model it before building it"), line=LineNumber(node.lineno)))
    for fname in sorted(expected_names - set(actual)):
        found.append(Violation(rule=RuleBroken(f"{row_name}: modeled field `{fname}` is missing"), line=LineNumber(node.lineno)))
    for fname, type_name in declared.items():
        annotation = actual.get(fname)
        if annotation is not None and not _annotation_names_exactly(annotation, type_name):
            found.append(Violation(rule=RuleBroken(f"{row_name}: field `{fname}` must be {type_name}, as modeled"), line=LineNumber(annotation.lineno)))
    if kind is not None:
        annotation = actual.get("kind")
        if annotation is not None and not _annotation_is_kind_pin(annotation, kind):
            found.append(Violation(rule=RuleBroken(f"{row_name}: kind must be Literal[{kind.axis}.{kind.member.upper()}]"), line=LineNumber(annotation.lineno)))
    return found


def _check_frozen_product(node: ast.ClassDef, row_name: str, declared: dict[str, str], kind: KindPin | None) -> list[Violation]:
    found: list[Violation] = []
    if not _class_has_flag(node, "frozen"):
        found.append(Violation(rule=RuleBroken(f"{row_name}: must be frozen=True; the one unfrozen node is the consistency model the table names"), line=LineNumber(node.lineno)))
    if not _class_has_flag(node, "extra"):
        found.append(Violation(rule=RuleBroken(f"{row_name}: must close shape with extra=\"forbid\""), line=LineNumber(node.lineno)))
    found.extend(_check_fields_exact(node, row_name, declared, kind))
    return found


def _check_envelope(node: ast.ClassDef, row: DiscriminatedUnionRow, table: ModelTable) -> list[Violation]:
    found: list[Violation] = []
    union_row = next((r for r in table.rows if not isinstance(r, DerivationRow) and r.name == row.over), None)
    if not isinstance(union_row, UnionRow):
        return found
    if not any("RootModel" in b for b in _base_names(node)) or not _class_has_flag(node, "frozen"):
        found.append(Violation(rule=RuleBroken(f"{row.name}: envelope shape is class {row.name}(RootModel[A | B], frozen=True)"), line=LineNumber(node.lineno)))
    root_item = next(
        (item for item in node.body if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name) and item.target.id == "root"),
        None,
    )
    if root_item is None:
        found.append(Violation(rule=RuleBroken(f"{row.name}: envelope must declare root over the union's variants"), line=LineNumber(node.lineno)))
        return found
    flat = _flatten_union(root_item.annotation)
    if flat is None or set(flat) != set(union_row.variants):
        found.append(Violation(rule=RuleBroken(f"{row.name}: root must be exactly {' | '.join(union_row.variants)}, as modeled"), line=LineNumber(root_item.lineno)))
    if not _has_discriminator_kind(root_item):
        found.append(Violation(rule=RuleBroken(f"{row.name}: root must carry Field(discriminator=\"kind\")"), line=LineNumber(root_item.lineno)))
    return found


def _flatten_crossing(annotation: ast.expr) -> list[str] | None:
    if isinstance(annotation, ast.Name):
        return [annotation.id]
    if (
        isinstance(annotation, ast.Subscript)
        and isinstance(annotation.value, ast.Name)
        and annotation.value.id == "Json"
        and isinstance(annotation.slice, ast.Name)
    ):
        return [annotation.slice.id]
    if isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
        left = _flatten_crossing(annotation.left)
        right = _flatten_crossing(annotation.right)
        if left is None or right is None:
            return None
        return left + right
    return None


def _annotated_ordered(expr: ast.expr) -> tuple[list[str] | None, bool]:
    if not (isinstance(expr, ast.Subscript) and isinstance(expr.value, ast.Name) and expr.value.id == "Annotated"):
        return None, False
    inner = expr.slice
    if not isinstance(inner, ast.Tuple) or len(inner.elts) < 2:
        return None, False
    flat = _flatten_crossing(inner.elts[0])
    left_to_right = any(
        isinstance(meta, ast.Call)
        and isinstance(meta.func, ast.Name)
        and meta.func.id == "Field"
        and any(
            kw.arg == "union_mode" and isinstance(kw.value, ast.Constant) and kw.value.value == "left_to_right"
            for kw in meta.keywords
        )
        for meta in inner.elts[1:]
    )
    return flat, left_to_right


def _check_ordered_crossing(node: ast.ClassDef, row: OrderedUnionRow, table: ModelTable, tree: ast.Module) -> list[Violation]:
    found: list[Violation] = []
    union_row = next((r for r in table.rows if not isinstance(r, DerivationRow) and r.name == row.over), None)
    if not isinstance(union_row, UnionRow):
        return found
    if not any("RootModel" in b for b in _base_names(node)) or not _class_has_flag(node, "frozen"):
        found.append(Violation(rule=RuleBroken(f"{row.name}: crossing shape is class {row.name}(RootModel[<ordered alias>], frozen=True)"), line=LineNumber(node.lineno)))
    expr = _class_fields(node).get("root")
    if expr is None:
        for base in node.bases:
            if isinstance(base, ast.Subscript) and isinstance(base.value, ast.Name) and base.value.id == "RootModel":
                target = base.slice
                if isinstance(target, ast.Name):
                    expr = next(
                        (
                            item.value
                            for item in tree.body
                            if isinstance(item, ast.Assign)
                            and any(isinstance(t, ast.Name) and t.id == target.id for t in item.targets)
                        ),
                        None,
                    )
                else:
                    expr = target
    if expr is None:
        found.append(Violation(rule=RuleBroken(f"{row.name}: the ordered alias is missing; declare Annotated[{' | '.join(union_row.variants)}, Field(union_mode=\"left_to_right\")]"), line=LineNumber(node.lineno)))
        return found
    flat, left_to_right = _annotated_ordered(expr)
    if flat is None or flat != list(union_row.variants):
        found.append(Violation(rule=RuleBroken(f"{row.name}: the crossing must attempt exactly {' | '.join(union_row.variants)} in the modeled order, failure variant last"), line=LineNumber(node.lineno)))
    if not left_to_right:
        found.append(Violation(rule=RuleBroken(f"{row.name}: ordered selection is declared, never caught: Field(union_mode=\"left_to_right\")"), line=LineNumber(node.lineno)))
    return found


def _check_consistency_model(node: ast.ClassDef, row: ConsistencyModelRow) -> list[Violation]:
    found: list[Violation] = []
    if _class_has_flag(node, "frozen"):
        found.append(Violation(rule=RuleBroken(f"{row.name} is the consistency model; it is the one unfrozen node, and freezing it while holding the live edge is a different construct wearing its name"), line=LineNumber(node.lineno)))
    actual = _class_fields(node)
    allowed = dict(row.clients) | dict(row.fields)
    for fname in sorted(set(actual) - set(allowed)):
        found.append(Violation(rule=RuleBroken(f"{row.name}: field `{fname}` is not in the model table; model it before building it"), line=LineNumber(node.lineno)))
    for fname, type_name in allowed.items():
        annotation = actual.get(fname)
        if annotation is not None and not _annotation_names_exactly(annotation, type_name):
            found.append(Violation(rule=RuleBroken(f"{row.name}: field `{fname}` must be {type_name}, as modeled"), line=LineNumber(annotation.lineno)))
    reached = {
        attr.attr
        for item in node.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        for attr in ast.walk(item)
        if isinstance(attr, ast.Attribute)
        and isinstance(attr.value, ast.Name)
        and attr.value.id == "self"
    }
    for client_name in sorted(set(row.clients) - reached):
        found.append(Violation(rule=RuleBroken(f"{row.name}: client `{client_name}` is held but no verb reaches it; a handle nothing emits through is the vacuous break"), line=LineNumber(node.lineno)))
    return found


def _collect_annotation_names(annotation: ast.expr) -> set[str]:
    return {n.id for n in ast.walk(annotation) if isinstance(n, ast.Name)}


def _is_stub_body(body: list[ast.stmt]) -> bool:
    effective = body[:]
    if effective and isinstance(effective[0], ast.Expr) and isinstance(effective[0].value, ast.Constant) and isinstance(effective[0].value.value, str):
        effective = effective[1:]
    if len(effective) != 1:
        return False
    stmt = effective[0]
    if isinstance(stmt, ast.Raise):
        return True
    if isinstance(stmt, ast.Pass):
        return True
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is ...:
        return True
    return False


def _collect_body_names(body: list[ast.stmt]) -> set[str]:
    names: set[str] = set()
    for stmt in body:
        for node in ast.walk(stmt):
            if isinstance(node, ast.Name):
                names.add(node.id)
    return names


def _is_capture_form(node: ast.Try) -> bool:
    """The licensed capture: one call assigned; each named, narrow handler reassigns
    the caught signal to the same name; nothing else. The raise becomes a value, only."""
    if node.orelse or node.finalbody:
        return False
    if len(node.body) != 1 or not isinstance(node.body[0], ast.Assign):
        return False
    opening = node.body[0]
    if len(opening.targets) != 1 or not isinstance(opening.targets[0], ast.Name):
        return False
    target = opening.targets[0].id
    value = opening.value.value if isinstance(opening.value, ast.Await) else opening.value
    if not isinstance(value, ast.Call):
        return False
    for handler in node.handlers:
        if handler.type is None or handler.name is None:
            return False
        named = {n.id for n in ast.walk(handler.type) if isinstance(n, ast.Name)}
        if named & {"Exception", "BaseException", "ValidationError"}:
            return False
        if len(handler.body) != 1 or not isinstance(handler.body[0], ast.Assign):
            return False
        reassign = handler.body[0]
        if len(reassign.targets) != 1 or not isinstance(reassign.targets[0], ast.Name) or reassign.targets[0].id != target:
            return False
        if not (isinstance(reassign.value, ast.Name) and reassign.value.id == handler.name):
            return False
    return True


def _check_methods(node: ast.ClassDef, row: Row, table: ModelTable) -> list[Violation]:
    found: list[Violation] = []
    if isinstance(row, ServiceRow):
        return found
    if isinstance(row, ConsistencyModelRow):
        verb_rows = {r.name: r for r in table.rows if isinstance(r, VerbRow) and r.on == node.name}
        verb_names = set(verb_rows)
        row_value_names = {
            r.name
            for r in table.rows
            if isinstance(r, (ScalarRow, CollectionRow, FrozenModelRow, UnionRow, DiscriminatedUnionRow, OrderedUnionRow, BoundaryRow, ExternalRow))
        }
        defined: set[str] = set()
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if item.name.startswith("__") and item.name.endswith("__"):
                continue
            if _decorator_names(item) & _VALIDATOR_DECORATORS:
                continue
            defined.add(item.name)
            if item.name not in verb_names:
                found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: verb not in the model table; model it before building it"), line=LineNumber(item.lineno)))
                continue
            verb = verb_rows[item.name]
            # a. Stub denial
            if _is_stub_body(item.body):
                found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: stub body; a verb expands its declared chain, it is never a placeholder"), line=LineNumber(item.lineno)))
            for stmt in ast.walk(item):
                if isinstance(stmt, ast.Try) and not _is_capture_form(stmt):
                    found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: try/except beyond the capture form; the capture is one call assigned and each declared signal reassigned as the arrived value, and everything else propagates"), line=LineNumber(stmt.lineno)))
            # b. Signature conformance
            if item.returns is None:
                found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: missing return annotation, as modeled"), line=LineNumber(item.lineno)))
            else:
                ann_names = _collect_annotation_names(item.returns)
                if verb.returns is not None:
                    if verb.returns not in ann_names:
                        found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: return annotation must include {verb.returns}, as modeled"), line=LineNumber(item.lineno)))
                elif verb.yields is not None:
                    if verb.yields not in ann_names:
                        found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: return annotation must include {verb.yields}, as modeled"), line=LineNumber(item.lineno)))
                    if not (ann_names & {"AsyncIterator", "Iterator"}):
                        found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: yielding verb must declare AsyncIterator or Iterator in return annotation, as modeled"), line=LineNumber(item.lineno)))
                else:
                    if not _is_none_constant(item.returns):
                        found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: verb declares no returns or yields; return annotation must be None, as modeled"), line=LineNumber(item.lineno)))
            params = item.args.args[1:]  # skip self
            if verb.accepts is not None:
                param_ann_names: set[str] = set()
                for param in params:
                    if param.annotation is not None:
                        param_ann_names |= _collect_annotation_names(param.annotation)
                if verb.accepts not in param_ann_names:
                    found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: parameter annotation must include {verb.accepts}, as modeled"), line=LineNumber(item.lineno)))
            else:
                if params:
                    found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: verb declares no accepts; method must have no parameters besides self, as modeled"), line=LineNumber(item.lineno)))
            # c. Chain presence
            body_names = _collect_body_names(item.body)
            for chain_name in verb.constructs:
                if chain_name not in body_names:
                    found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: declared chain constructs {chain_name}, which the body never touches"), line=LineNumber(item.lineno)))
            for chain_name in verb.emits:
                if chain_name not in body_names:
                    found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: declared chain emits {chain_name}, which the body never touches"), line=LineNumber(item.lineno)))
            # d. Chain completeness: a statement the chain cannot explain is a break
            chain_allowed = set(verb.constructs) | set(verb.emits)
            for declared in (verb.accepts, verb.returns, verb.yields):
                if declared is not None:
                    chain_allowed.add(declared)
            for stray in sorted((body_names & row_value_names) - chain_allowed):
                found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: body touches {stray}, which the declared chain cannot explain"), line=LineNumber(item.lineno)))
        for missing in sorted(verb_names - defined):
            found.append(Violation(rule=RuleBroken(f"{node.name}: modeled verb `{missing}` is missing from the surface"), line=LineNumber(node.lineno)))
        return found
    derivation_names = {
        r.name for r in table.rows if isinstance(r, DerivationRow) and r.on == node.name
    }
    for item in node.body:
        if not isinstance(item, ast.FunctionDef):
            continue
        decorators = _decorator_names(item)
        if decorators & _VALIDATOR_DECORATORS:
            continue
        if not (decorators & _DERIVATION_DECORATORS):
            found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: behavior on a frozen value is a derivation (@cached_property / @computed_field / @property), nothing else"), line=LineNumber(item.lineno)))
            continue
        if item.name not in derivation_names:
            found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: derivation not in the model table; model it before building it"), line=LineNumber(item.lineno)))
    return found


def _table_audit(tree: ast.Module, table: ModelTable, table_dir: Path, file_path: Path) -> list[Violation]:
    found: list[Violation] = []
    rows_here: dict[str, Row] = {}
    for r in table.rows:
        if isinstance(r, (DerivationRow, VerbRow)):
            continue
        if (table_dir / r.file).resolve() == file_path.resolve():
            rows_here[r.name] = r
    scalar_spaces = {
        r.value_space: set(r.members or ())
        for r in table.rows
        if isinstance(r, ScalarRow) and r.value_space is not None
    }
    union_axes = {r.axis: set(r.members) for r in table.rows if isinstance(r, UnionRow)}
    route_or_main_file = any(isinstance(r, (RouteRow, MainRow)) for r in rows_here.values())
    crossing_file = any(isinstance(r, (BoundaryRow, OrderedUnionRow)) for r in rows_here.values())
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            mode = _validator_mode(item)
            if mode == "after":
                found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: there is no asserting validator; a validator that raises is a check riding inside construction. Reparameterize the relation or factor the concept"), line=LineNumber(item.lineno)))
            elif mode == "before" and not crossing_file:
                found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: a before-validator is legal only where a boundary or ordered crossing claims the file"), line=LineNumber(item.lineno)))
    for item in tree.body:
        if isinstance(item, ast.FunctionDef) and not route_or_main_file:
            found.append(Violation(rule=RuleBroken(f"module-level def `{item.name}`: behavior lives on models as derivations, or in route/main files the table claims"), line=LineNumber(item.lineno)))
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        bases = _base_names(node)
        if any(b in _ENUM_BASES for b in bases):
            expected_members = scalar_spaces.get(node.name) or union_axes.get(node.name)
            if expected_members is None:
                found.append(Violation(rule=RuleBroken(f"enum {node.name}: not a modeled value space or union axis; model it before building it"), line=LineNumber(node.lineno)))
            elif _enum_member_names(node) != expected_members:
                found.append(Violation(rule=RuleBroken(f"enum {node.name}: members must be exactly the modeled set: {', '.join(sorted(expected_members))}"), line=LineNumber(node.lineno)))
            continue
        row = rows_here.get(node.name)
        if row is None:
            found.append(Violation(rule=RuleBroken(f"class {node.name}: not in the model table for this file; model it before building it"), line=LineNumber(node.lineno)))
            continue
        if isinstance(row, ScalarRow):
            found.extend(_check_scalar(node, row))
        elif isinstance(row, CollectionRow):
            found.extend(_check_collection(node, row))
        elif isinstance(row, FrozenModelRow):
            found.extend(_check_frozen_product(node, row.name, row.fields, row.kind))
        elif isinstance(row, BoundaryRow):
            found.extend(_check_frozen_product(node, row.name, row.fields, None))
        elif isinstance(row, ConfigRow):
            found.extend(_check_fields_exact(node, row.name, row.fields, None))
        elif isinstance(row, DiscriminatedUnionRow):
            found.extend(_check_envelope(node, row, table))
        elif isinstance(row, OrderedUnionRow):
            found.extend(_check_ordered_crossing(node, row, table, tree))
        elif isinstance(row, ConsistencyModelRow):
            found.extend(_check_consistency_model(node, row))
        elif isinstance(row, UnionRow):
            found.append(Violation(rule=RuleBroken(f"{row.name}: an in-graph union is a type alias, never a class; the class form is the discriminated_union envelope, and it stands only at crossings"), line=LineNumber(node.lineno)))
        found.extend(_check_methods(node, row, table))
    return found


# --------------------------------------------------------------------------
# Table discovery and scope
# --------------------------------------------------------------------------


def _in_scope(file_path: str) -> bool:
    scope = os.environ.get("TCA_GATE_PATH_SUBSTR", "")
    return (
        scope in file_path
        and "/.claude/" not in file_path
        and "/tests/" not in file_path
    )


def _find_table(file_path: Path) -> tuple[ModelTable, Path] | str | None:
    located: Path | None = None
    for directory in file_path.resolve().parents:
        candidate = directory / "spec" / "model.json"
        if candidate.exists():
            if located is not None:
                return f"two catalogs found: {located} and {candidate}; there is exactly one spec/model.json, at the repo root"
            located = candidate
    if located is None:
        return None
    try:
        table = ModelTable.model_validate_json(located.read_text())
    except ValidationError as error:
        return f"the model table at {located} fails construction; fix the catalog before building:\n{error}"
    root = located.parent.parent
    problems = _verify_externals(table, root)
    if problems:
        return f"the model table at {located} fails construction:\n" + "\n".join(problems)
    return table, root


def _audit_python(source: str, file_path: Path) -> tuple[list[Violation], str | None]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [], None
    located = _find_table(file_path)
    if located is None:
        return [
            Violation(
                rule=RuleBroken("no catalog at spec/model.json; the model comes first: write the one root catalog, run --order, then build rows in the printed order"),
                line=LineNumber(1),
            )
        ], None
    if isinstance(located, str):
        return [Violation(rule=RuleBroken(located), line=LineNumber(1))], None
    table, table_dir = located
    consistency_model = next((r.name for r in table.rows if isinstance(r, ConsistencyModelRow)), None)
    found = _legacy_audit(tree, consistency_model)
    found.extend(_table_audit(tree, table, table_dir, file_path))
    return found, consistency_model


# --------------------------------------------------------------------------
# Entry points
# --------------------------------------------------------------------------


def _context_dir(table_path: Path) -> Path:
    parent = table_path.resolve().parent
    return parent.parent if parent.name == "spec" else parent


def _verify_externals(table: ModelTable, table_dir: Path) -> list[str]:
    problems: list[str] = []
    for row in table.rows:
        if isinstance(row, ExternalRow):
            target = table_dir / row.file
            if not target.exists() or f"class {row.name}" not in target.read_text():
                problems.append(
                    f"external {row.name}: {row.file} does not define it; an external row records what already exists, never what is wished for"
                )
    return problems


def _deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))


class ViolationEntry(BaseModel, frozen=True, extra="forbid"):
    """A violation observed in the tree: sentenced and noted, never solved here."""

    file: str = Field(min_length=1)
    found: str = Field(min_length=1)
    breaks: Literal["escaped", "duplicated", "vacuous", "fused"]
    note: str = Field(min_length=20, max_length=400)


class ViolationLog(BaseModel, frozen=True, extra="forbid"):
    """spec/violation.json: the spec agent's standing ledger of observed violations."""

    violations: tuple[ViolationEntry, ...] = ()

    @model_validator(mode="after")
    def _entries_unique(self) -> "ViolationLog":
        keys = [(v.file, v.found) for v in self.violations]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate violation entry (file, found); one entry per violation")
        return self


def _check_files(paths: list[str]) -> int:
    total = 0
    for path in paths:
        file_path = Path(path)
        if file_path.name == "violation.json":
            try:
                _ = ViolationLog.model_validate_json(file_path.read_text())
            except ValidationError as error:
                print(f"{path}: violation ledger failed construction\n{error}")
                total += 1
            continue
        if file_path.name == "model.json":
            try:
                table = ModelTable.model_validate_json(file_path.read_text())
            except ValidationError as error:
                print(f"{path}: model table failed construction\n{error}")
                total += 1
                continue
            for problem in _verify_externals(table, _context_dir(file_path)):
                print(f"{path}: {problem}")
                total += 1
            continue
        violations, _ = _audit_python(file_path.read_text(), file_path.resolve())
        for violation in violations:
            print(f"{path}:{violation.line.root}: {violation.rule.root}")
        total += len(violations)
    print(f"tca gate: {total} violation(s) across {len(paths)} file(s)")
    return 1 if total else 0


def _print_order(table_path: str) -> int:
    table = ModelTable.model_validate_json(Path(table_path).read_text())
    ledger_path = Path(table_path).parent / "violation.json"
    if ledger_path.exists():
        ledger = ViolationLog.model_validate_json(ledger_path.read_text())
        root = _context_dir(Path(table_path))
        stale = [v.file for v in ledger.violations if not (root / v.file).exists()]
        if stale:
            print("\n".join(f"ledger entry for {f}: file no longer exists; the violation left the tree, so the entry leaves the ledger" for f in stale))
            return 1
    problems = _verify_externals(table, _context_dir(Path(table_path)))
    if problems:
        print("\n".join(problems))
        return 1
    for position, row in enumerate(table.build_order(), start=1):
        print(f"{position}. {row.construct} {row.name} -> {row.file}")
    return 0


def main() -> None:
    argv = sys.argv[1:]
    if argv and argv[0] == "--check":
        sys.exit(_check_files(argv[1:]))
    if argv and argv[0] == "--order":
        try:
            sys.exit(_print_order(argv[1]))
        except (ValidationError, ValueError) as error:
            print(str(error))
            sys.exit(1)
    event = _HookEvent.model_validate_json(sys.stdin.read())
    raw_path = event.tool_input.file_path
    if not raw_path.endswith(".py") or not _in_scope(raw_path):
        return
    source = _resulting_source(event.tool_input)
    if source is None or not source.strip():
        return
    violations, _ = _audit_python(source, Path(raw_path))
    if violations:
        listed = "\n".join(f"- {v.rule.root} (line {v.line.root})" for v in violations)
        _deny(
            "TCA gate denied this write.\n"
            + listed
            + "\n\nThe table models, the gate proves, the file conforms. Fix the model in model.json or fix the file to match it; a respelling of a denied form is the same denied form."
        )


if __name__ == "__main__":
    main()
