"""AST conformance checks for source files claimed by the ontology catalog.

This is the gate's intentionally procedural shell. ``model.py`` constructs the
declarative catalog; this module reads Python syntax and reports where source
does not match that catalog or where legacy structural smells appear before a
catalog can explain them.

This file is the exception, not the example. Domain code must not copy its
procedural density, class-keyword shortcuts, or comment load. The gate is an
imperative shell whose job is to police the declarative doctrine, so comments
earn their place when they point from syntax back to the construct card or
explain why AST shape is enough to refuse a write.

Two passes are exported:

* ``legacy_audit`` is catalog-light smell detection for inherited Python shapes
  TCA refuses everywhere it sees them.
* ``table_audit`` compares one parsed module against the rows whose ``file``
  points at that module.
"""

import ast
from pathlib import Path

from tca_gate.model import (
    BindingRow, CollectionRow, CompositionRootRow, ConceptModelRow, ConfigRow,
    ConsistencyModelRow, ContractModelRow, DerivationRow, ExistingRow, ForeignModelRow,
    KindPin, LineNumber, OntologyCatalog, OrderedUnionRow, Row, RouteRow, RuleBroken,
    SemanticScalarRow, UnionRow, ValueObjectRow, VerbRow, Violation, FieldSpec, field_type,
)


# These names are syntactic cues, not runtime imports. The gate judges source
# shape from the AST it is about to allow, so every helper below stays lexical.
_PRIMITIVES = {"str", "int", "float", "bool", "bytes", "Decimal", "date", "complex", "bytearray"}


_ENUM_BASES = {"Enum", "StrEnum", "IntEnum", "IntFlag", "Flag"}


_CONTAINERS = {"list", "tuple", "set", "frozenset", "dict"}


_MUTABLE_CONTAINERS = {"list", "set", "dict"}


_DERIVATION_DECORATORS = {"cached_property", "computed_field", "property"}


_VALIDATOR_DECORATORS = {"model_validator", "field_validator", "classmethod"}


def _base_names(node: ast.ClassDef) -> list[str]:
    """Read base names from syntax, not imports.

    The hook judges the source it is about to allow before that source becomes
    importable. A base-name check is intentionally lexical.
    """

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
    """Treat Pydantic class kwargs and ConfigDict as one rendered flag.

    Domain construct cards choose their required form. The gate itself accepts
    both spellings because it is reading generated and legacy source, not
    demonstrating the domain style.
    """

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


def legacy_audit(tree: ast.Module, consistency_model_name: str | None) -> list[Violation]:
    """Run catalog-independent structural smell checks.

    This pass catches the inherited Python forms that TCA refuses regardless of
    the row grammar: nullable fields, mutable containers, bare primitives,
    standalone enums, raw string Literals, and stray arbitrary types. The
    consistency model name is the one allowed owner of arbitrary live clients.

    Each violation message names the construct card that owns the replacement:
    semantic scalar for bare primitives and closed vocabularies, collection for
    mutable containers, union for meaningful absence, and consistency model for
    live clients.
    """

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
                Violation(rule=RuleBroken(f"arbitrary_types_allowed on {node.name}, which the ontology catalog does not name as the consistency model"), line=LineNumber(node.lineno))
            )
        is_root_model = any("RootModel" in b for b in bases)
        is_base_model = any(b in {"BaseModel", "BaseSettings"} for b in bases)
        if not (is_base_model and not is_root_model):
            continue
        for item in node.body:
            if not (isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name) and item.target.id != "model_config"):
                continue
            # tca-construct-union: meaningful absence is a state or fact, never
            # a nullable slot fused into another model.
            if _annotation_is_optional(item.annotation):
                found.append(Violation(rule=RuleBroken(f"absence fused into field `{item.target.id}` (`T | None`); factor the states into a union over a named axis"), line=LineNumber(item.lineno)))
            # tca-construct-collection: mutable sequences and mappings are not
            # proven domain values. Collections and associations construct whole.
            elif _annotation_is_mutable_container(item.annotation):
                found.append(Violation(rule=RuleBroken(f"mutable container field `{item.target.id}`; a sequence is `tuple[T, ...]` or a Collection, a mapping is an association (entry model + collection + query model)"), line=LineNumber(item.lineno)))
            # tca-construct-semantic-scalar: a primitive field is a domain value
            # whose name, constraint, or openness has not been modeled.
            elif _annotation_is_primitive(item.annotation):
                found.append(Violation(rule=RuleBroken(f"bare primitive field `{item.target.id}`; use a semantic scalar"), line=LineNumber(item.lineno)))
            # tca-construct-semantic-scalar: a standalone enum is a value space
            # without the scalar that owns it.
            elif _annotation_names_enum(item.annotation, enum_names) and node.name != consistency_model_name:
                found.append(Violation(rule=RuleBroken(f"standalone enum as field `{item.target.id}`; declare its value space as a semantic scalar"), line=LineNumber(item.lineno)))
            # tca-construct-union and tca-construct-semantic-scalar: raw string
            # Literal members are vocabulary with no owning construct.
            elif _annotation_is_raw_literal(item.annotation):
                found.append(Violation(rule=RuleBroken(f"raw string Literal field `{item.target.id}`; pin a StrEnum member, never a bare string"), line=LineNumber(item.lineno)))
    return found


def _check_scalar(node: ast.ClassDef, row: SemanticScalarRow) -> list[Violation]:
    """Enforce tca-construct-semantic-scalar source shape."""

    found: list[Violation] = []
    if not any("RootModel" in b for b in _base_names(node)):
        found.append(Violation(rule=RuleBroken(f"{row.name} is a modeled semantic scalar; the shape is class {row.name}(RootModel[...], frozen=True)"), line=LineNumber(node.lineno)))
        return found
    if not _class_has_flag(node, "frozen"):
        found.append(Violation(rule=RuleBroken(f"{row.name}: semantic scalar must be frozen=True"), line=LineNumber(node.lineno)))
    expected = row.primitive if row.primitive is not None else row.value_space
    root = _class_fields(node).get("root")
    if root is None or not _annotation_names_exactly(root, str(expected)):
        found.append(Violation(rule=RuleBroken(f"{row.name}: root must be annotated {expected}, as modeled"), line=LineNumber(node.lineno)))
    if row.constraint is not None:
        root_assign = next(
            (item for item in node.body if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name) and item.target.id == "root"),
            None,
        )
        value = root_assign.value if root_assign is not None else None
        is_field = isinstance(value, ast.Call) and (
            (isinstance(value.func, ast.Name) and value.func.id == "Field")
            or (isinstance(value.func, ast.Attribute) and value.func.attr == "Field")
        )
        if not is_field:
            found.append(Violation(rule=RuleBroken(f"{row.name}: root must carry Field({row.constraint.root}), as modeled; a scalar that declares a constraint proves it on the field"), line=LineNumber(node.lineno)))
    return found


def _check_collection(node: ast.ClassDef, row: CollectionRow) -> list[Violation]:
    """Enforce tca-construct-collection source shape."""

    found: list[Violation] = []
    if not any("RootModel" in b for b in _base_names(node)) or not _class_has_flag(node, "frozen"):
        found.append(Violation(rule=RuleBroken(f"{row.name} is modeled collection; the shape is class {row.name}(RootModel[tuple[{row.element}, ...]], frozen=True)"), line=LineNumber(node.lineno)))
    root = _class_fields(node).get("root")
    if root is None or not _annotation_is_element_tuple(root, row.element):
        found.append(Violation(rule=RuleBroken(f"{row.name}: root must be tuple[{row.element}, ...], as modeled"), line=LineNumber(node.lineno)))
    return found


def _check_fields_exact(node: ast.ClassDef, row_name: str, declared: dict[str, str | FieldSpec], kind: KindPin | None) -> list[Violation]:
    """Enforce field ownership declared by a construct row.

    Extra fields are unmodeled meaning entering source. Missing fields are
    modeled meaning not rendered. Wrong annotations break the catalog edge.
    """

    found: list[Violation] = []
    actual = _class_fields(node)
    expected_names = set(declared) | ({"kind"} if kind else set[str]())
    for fname in sorted(set(actual) - expected_names):
        found.append(Violation(rule=RuleBroken(f"{row_name}: field `{fname}` is not in the ontology catalog; model it before building it"), line=LineNumber(node.lineno)))
    for fname in sorted(expected_names - set(actual)):
        found.append(Violation(rule=RuleBroken(f"{row_name}: modeled field `{fname}` is missing"), line=LineNumber(node.lineno)))
    for fname, spec in declared.items():
        type_name = field_type(spec)
        annotation = actual.get(fname)
        if annotation is not None and not _annotation_names_exactly(annotation, type_name):
            found.append(Violation(rule=RuleBroken(f"{row_name}: field `{fname}` must be {type_name}, as modeled"), line=LineNumber(annotation.lineno)))
    if kind is not None:
        annotation = actual.get("kind")
        if annotation is not None and not _annotation_is_kind_pin(annotation, kind):
            found.append(Violation(rule=RuleBroken(f"{row_name}: kind must be Literal[{kind.axis}.{kind.member.upper()}]"), line=LineNumber(annotation.lineno)))
    return found


def _check_frozen_product(node: ast.ClassDef, row_name: str, declared: dict[str, str | FieldSpec], kind: KindPin | None) -> list[Violation]:
    """Enforce the frozen product shape shared by model constructs.

    Value objects, concept models, foreign models, and contract models differ
    in meaning and row origin, but the gate checks the same frozen, closed field
    product shape for each.
    """

    found: list[Violation] = []
    if not _class_has_flag(node, "frozen"):
        found.append(Violation(rule=RuleBroken(f"{row_name}: must be frozen=True; the one unfrozen node is the consistency model the ontology names"), line=LineNumber(node.lineno)))
    if not _class_has_flag(node, "extra"):
        found.append(Violation(rule=RuleBroken(f"{row_name}: must close shape with extra=\"forbid\""), line=LineNumber(node.lineno)))
    found.extend(_check_fields_exact(node, row_name, declared, kind))
    return found


def _flatten_crossing(annotation: ast.expr) -> list[str] | None:
    """Flatten a union expression into variant names, preserving order."""

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


def _annotated_discriminated(expr: ast.expr) -> tuple[list[str] | None, bool]:
    """Read the tca-construct-union alias shape from syntax."""

    if not (isinstance(expr, ast.Subscript) and isinstance(expr.value, ast.Name) and expr.value.id == "Annotated"):
        return None, False
    inner = expr.slice
    if not isinstance(inner, ast.Tuple) or len(inner.elts) < 2:
        return None, False
    flat = _flatten_crossing(inner.elts[0])
    discriminated = any(
        isinstance(meta, ast.Call)
        and isinstance(meta.func, ast.Name)
        and meta.func.id == "Field"
        and any(
            kw.arg == "discriminator" and isinstance(kw.value, ast.Constant) and kw.value.value == "kind"
            for kw in meta.keywords
        )
        for meta in inner.elts[1:]
    )
    return flat, discriminated


def _annotated_ordered(expr: ast.expr) -> tuple[list[str] | None, bool]:
    """Read the tca-construct-ordered-union alias shape from syntax."""

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


def _assignments(tree: ast.Module) -> dict[str, ast.expr]:
    """Return module-level assignments by target name."""

    return {
        target.id: item.value
        for item in tree.body
        if isinstance(item, ast.Assign)
        for target in item.targets
        if isinstance(target, ast.Name)
    }


def _assignment_lines(tree: ast.Module) -> dict[str, LineNumber]:
    """Return source lines for module-level assignment targets."""

    return {
        target.id: LineNumber(item.lineno)
        for item in tree.body
        if isinstance(item, ast.Assign)
        for target in item.targets
        if isinstance(target, ast.Name)
    }


def _type_adapter_targets(tree: ast.Module) -> set[str]:
    """Return ``AdapterName:TargetName`` pairs for TypeAdapter assignments."""

    targets: set[str] = set()
    for item in tree.body:
        if not isinstance(item, ast.Assign):
            continue
        if len(item.targets) != 1 or not isinstance(item.targets[0], ast.Name):
            continue
        value = item.value
        if not isinstance(value, ast.Call):
            continue
        func = value.func
        if not (isinstance(func, ast.Name) and func.id == "TypeAdapter"):
            continue
        if len(value.args) == 1 and isinstance(value.args[0], ast.Name):
            targets.add(f"{item.targets[0].id}:{value.args[0].id}")
    return targets


def _check_consistency_model(node: ast.ClassDef, row: ConsistencyModelRow) -> list[Violation]:
    """Enforce tca-construct-consistency-model field ownership.

    The live node may hold clients and mutable proven state, but every held
    client must be reached by a verb. A handle that no transition can use is a
    vacuous structure.
    """

    found: list[Violation] = []
    if _class_has_flag(node, "frozen"):
        found.append(Violation(rule=RuleBroken(f"{row.name} is the consistency model; it is the one unfrozen node, and freezing it while holding the live edge is a different construct wearing its name"), line=LineNumber(node.lineno)))
    actual = _class_fields(node)
    allowed = dict(row.clients) | dict(row.fields)
    for fname in sorted(set(actual) - set(allowed)):
        found.append(Violation(rule=RuleBroken(f"{row.name}: field `{fname}` is not in the ontology catalog; model it before building it"), line=LineNumber(node.lineno)))
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


def _is_construction_value(expr: ast.expr | None, value_names: set[str]) -> bool:
    """A statement's value is a construction when it calls a value-type by name
    (`Position(...)`) or lifts one (`X.model_validate`, adapter `validate_python`).
    A constituent constructed inside another call is not a separate statement."""
    inner = expr
    while isinstance(inner, ast.Await):
        inner = inner.value
    if isinstance(inner, ast.Yield):
        inner = inner.value
        while isinstance(inner, ast.Await):
            inner = inner.value
    if not isinstance(inner, ast.Call):
        return False
    func = inner.func
    if isinstance(func, ast.Name):
        return func.id in value_names
    if isinstance(func, ast.Attribute):
        return func.attr in {"model_validate", "model_validate_json", "validate_python", "validate_json"}
    return False


def _check_methods(node: ast.ClassDef, row: Row, table: OntologyCatalog) -> list[Violation]:
    """Check behavior declared inside a modeled class.

    Frozen models may only expose modeled derivations. The consistency model may
    expose modeled verbs, and each verb body must stay explainable by the verb
    row's declared chain. This is where tca-construct-derivation and
    tca-construct-verb become executable checks.
    """

    found: list[Violation] = []
    if isinstance(row, BindingRow):
        return found
    if isinstance(row, ConsistencyModelRow):
        verb_rows = {r.name: r for r in table.rows if isinstance(r, VerbRow) and r.on == node.name}
        verb_names = set(verb_rows)
        row_value_names = {
            r.name
            for r in table.rows
            if isinstance(r, (SemanticScalarRow, ValueObjectRow, CollectionRow, ConceptModelRow, UnionRow, OrderedUnionRow, ForeignModelRow, ContractModelRow, ExistingRow))
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
                found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: verb not in the ontology catalog; model it before building it"), line=LineNumber(item.lineno)))
                continue
            verb = verb_rows[item.name]
            # A verb row is already the work to perform. A placeholder body is
            # not a temporary implementation; it is a missing expansion.
            if _is_stub_body(item.body):
                found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: stub body; a verb expands its declared chain, it is never a placeholder"), line=LineNumber(item.lineno)))
            for stmt in ast.walk(item):
                # tca-construct-ordered-union and tca-construct-verb: expected
                # transport failure is captured in the one licensed form, then
                # constructed as data. Any broader handler is procedure.
                if isinstance(stmt, ast.Try) and not _is_capture_form(stmt):
                    found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: try/except beyond the capture form; the capture is one call assigned and each declared signal reassigned as the arrived value, and everything else propagates"), line=LineNumber(stmt.lineno)))
                # tca-construct-verb: verbs pass constructed values through the
                # graph. Projection belongs at route replies or client bindings.
                if isinstance(stmt, ast.Attribute) and stmt.attr in {"root", "model_dump", "model_dump_json"}:
                    found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: `{stmt.attr}` in a verb body; the verb passes the proven value itself, and serialization happens at the client binding or the route reply, never here"), line=LineNumber(stmt.lineno)))
            # The method surface is owned by the verb row: accepted value,
            # return/yield shape, and the absence of extra parameters.
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
            # Presence check: every declared chain participant must appear in
            # the body, otherwise the row promised work the source never does.
            body_names = _collect_body_names(item.body)
            for chain_name in ((verb.constructs,) if verb.constructs is not None else ()):
                if chain_name not in body_names:
                    found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: declared chain constructs {chain_name}, which the body never touches"), line=LineNumber(item.lineno)))
            for chain_name in verb.emits:
                if chain_name not in body_names:
                    found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: declared chain emits {chain_name}, which the body never touches"), line=LineNumber(item.lineno)))
            # Completeness check: a body that touches a value type the row never
            # declared has smuggled modeling back into source.
            chain_allowed: set[str] = set(verb.emits)
            if verb.constructs is not None:
                chain_allowed.add(verb.constructs)
            for declared in (verb.accepts, verb.returns, verb.yields):
                if declared is not None:
                    chain_allowed.add(declared)
            for stray in sorted((body_names & row_value_names) - chain_allowed):
                found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: body touches {stray}, which the declared chain cannot explain"), line=LineNumber(item.lineno)))
            # Verb construction is the state transition. More than one
            # top-level construction statement means the graph was sequenced by
            # procedure instead of by one constructed fact.
            constructions = sum(
                1
                for sub in ast.walk(item)
                if isinstance(sub, (ast.Assign, ast.AnnAssign, ast.Expr, ast.Return))
                and _is_construction_value(sub.value, row_value_names)
            )
            if constructions > 1:
                found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: more than one construction statement; a verb performs at most one construction, and constituents construct inside that one call"), line=LineNumber(item.lineno)))
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
        # tca-construct-derivation: behavior on a frozen value is a modeled
        # implied fact. A free method is escaped meaning.
        if not (decorators & _DERIVATION_DECORATORS):
            found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: behavior on a frozen value is a derivation (@cached_property / @computed_field / @property), nothing else"), line=LineNumber(item.lineno)))
            continue
        if item.name not in derivation_names:
            found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: derivation not in the ontology catalog; model it before building it"), line=LineNumber(item.lineno)))
    return found


def _is_wrap_form(func: ast.FunctionDef) -> bool:
    """The ordered union's last resort: one return placing the bare payload under its
    field name. Shape only; an index, rename, route, or compute is an alias, a
    path, or a model not yet written."""
    body = func.body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    if len(body) != 1 or not isinstance(body[0], ast.Return) or body[0].value is None:
        return False
    value = body[0].value
    if not isinstance(value, ast.Dict):
        return False
    params = [a.arg for a in func.args.args]
    payload = params[-1] if params else None
    return all(
        isinstance(k, ast.Constant) and isinstance(v, ast.Name) and v.id == payload
        for k, v in zip(value.keys, value.values)
    )


def table_audit(tree: ast.Module, table: OntologyCatalog, table_dir: Path, file_path: Path) -> list[Violation]:
    """Audit one Python module against the ontology rows that claim it.

    This is the row-to-card map in executable form: union aliases, ordered-union
    constructors, validators, route/composition-root functions, enum value
    spaces, class shapes, consistency verbs, and frozen derivations are each
    checked against the construct row that gave them permission to exist.
    """

    found: list[Violation] = []
    rows_here: dict[str, Row] = {}
    for r in table.rows:
        if isinstance(r, (DerivationRow, VerbRow)):
            continue
        if (table_dir / r.file).resolve() == file_path.resolve():
            rows_here[r.name] = r
    # Alias and enum checks need whole-module assignments, not class bodies.
    scalar_spaces = {
        r.value_space: set(r.members or ())
        for r in table.rows
        if isinstance(r, SemanticScalarRow) and r.value_space is not None
    }
    union_axes = {r.axis: set(r.members) for r in table.rows if isinstance(r, UnionRow)}
    assignments = _assignments(tree)
    assignment_lines = _assignment_lines(tree)
    type_adapter_targets = _type_adapter_targets(tree)
    route_or_main_file = any(isinstance(r, (RouteRow, CompositionRootRow)) for r in rows_here.values())
    crossing_file = any(isinstance(r, OrderedUnionRow) for r in rows_here.values())
    for row in rows_here.values():
        if isinstance(row, UnionRow):
            # tca-construct-union: the choice is an Annotated alias with a kind
            # discriminator, never an inferred class or raw string router.
            expr = assignments.get(row.name)
            line = assignment_lines.get(row.name, LineNumber(1))
            if expr is None:
                found.append(Violation(rule=RuleBroken(f"{row.name}: union alias is missing; declare Annotated[{' | '.join(row.variants)}, Field(discriminator=\"kind\")]"), line=line))
            else:
                flat, discriminated = _annotated_discriminated(expr)
                if flat is None or set(flat) != set(row.variants):
                    found.append(Violation(rule=RuleBroken(f"{row.name}: union alias must contain exactly {' | '.join(row.variants)}, as modeled"), line=line))
                if not discriminated:
                    found.append(Violation(rule=RuleBroken(f"{row.name}: union alias must carry Field(discriminator=\"kind\")"), line=line))
        if isinstance(row, OrderedUnionRow):
            # tca-construct-ordered-union: ordered construction is explicit in
            # the alias and TypeAdapter constructor, never an except/default.
            expr = assignments.get(row.name)
            line = assignment_lines.get(row.name, LineNumber(1))
            if expr is None:
                found.append(Violation(rule=RuleBroken(f"{row.name}: ordered union alias is missing; declare Annotated[{' | '.join(row.variants)}, Field(union_mode=\"left_to_right\")]"), line=line))
            else:
                flat, left_to_right = _annotated_ordered(expr)
                if flat is None or flat != list(row.variants):
                    found.append(Violation(rule=RuleBroken(f"{row.name}: ordered union must attempt exactly {' | '.join(row.variants)} in the modeled order, failure variant last"), line=line))
                if not left_to_right:
                    found.append(Violation(rule=RuleBroken(f"{row.name}: ordered selection is declared, never caught: Field(union_mode=\"left_to_right\")"), line=line))
            adapter_name = f"{row.name}Constructor"
            if f"{adapter_name}:{row.name}" not in type_adapter_targets:
                found.append(Violation(rule=RuleBroken(f"{row.name}: ordered union constructor is missing; declare {adapter_name} = TypeAdapter({row.name})"), line=line))
    # Validators are checked globally because a validator can hide procedural
    # work inside an otherwise correctly shaped class.
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            mode = _validator_mode(item)
            if mode == "after":
                # tca-construct-concept-model and tca-construct-value-object:
                # an after-validator is an assertion after construction. The
                # relation must be modeled before the value exists.
                found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: there is no asserting validator; a validator that raises is a check riding inside construction. Reparameterize the relation or factor the concept"), line=LineNumber(item.lineno)))
            elif mode == "before":
                # tca-construct-ordered-union: the only before-validator left is
                # the last-resort wrapper that puts identity-free payload under
                # its modeled field so construction can attempt the variants.
                if not crossing_file:
                    found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: a before-validator is legal only where an ordered union claims the file"), line=LineNumber(item.lineno)))
                elif not _is_wrap_form(item):
                    found.append(Violation(rule=RuleBroken(f"{node.name}.{item.name}: a before-validator beyond the wrap form; the last resort is one return placing the bare payload under its field, and an index, rename, route, or compute is an alias, a path, or a model not yet written"), line=LineNumber(item.lineno)))
    # Module-level functions are legal only where the ontology has named a
    # route or composition root. Elsewhere, behavior belongs on a model.
    for item in tree.body:
        if isinstance(item, ast.FunctionDef) and not route_or_main_file:
            # tca-construct-route and tca-construct-composition-root are the only
            # construct cards that license module-level functions.
            found.append(Violation(rule=RuleBroken(f"module-level def `{item.name}`: behavior lives on models as derivations, or in route/composition-root files the ontology claims"), line=LineNumber(item.lineno)))
    # Finally check each class against the row that claims its file. Unknown
    # classes are not tolerated in claimed files because the ontology is the
    # authority for what the file may contain.
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        bases = _base_names(node)
        if any(b in _ENUM_BASES for b in bases):
            # tca-construct-semantic-scalar owns closed scalar value spaces;
            # tca-construct-union owns choice axes. No other enum is meaningful.
            expected_members = scalar_spaces.get(node.name) or union_axes.get(node.name)
            if expected_members is None:
                found.append(Violation(rule=RuleBroken(f"enum {node.name}: not a modeled value space or union axis; model it before building it"), line=LineNumber(node.lineno)))
            elif _enum_member_names(node) != expected_members:
                found.append(Violation(rule=RuleBroken(f"enum {node.name}: members must be exactly the modeled set: {', '.join(sorted(expected_members))}"), line=LineNumber(node.lineno)))
            continue
        row = rows_here.get(node.name)
        if row is None:
            found.append(Violation(rule=RuleBroken(f"class {node.name}: not in the ontology catalog for this file; model it before building it"), line=LineNumber(node.lineno)))
            continue
        if isinstance(row, SemanticScalarRow):
            found.extend(_check_scalar(node, row))
        elif isinstance(row, ValueObjectRow):
            found.extend(_check_frozen_product(node, row.name, row.fields, None))
        elif isinstance(row, CollectionRow):
            found.extend(_check_collection(node, row))
        elif isinstance(row, ConceptModelRow):
            found.extend(_check_frozen_product(node, row.name, row.fields, row.kind))
        elif isinstance(row, ForeignModelRow):
            found.extend(_check_frozen_product(node, row.name, row.fields, None))
        elif isinstance(row, ContractModelRow):
            found.extend(_check_frozen_product(node, row.name, row.fields, None))
        elif isinstance(row, ConfigRow):
            found.extend(_check_fields_exact(node, row.name, row.fields, None))
        elif isinstance(row, OrderedUnionRow):
            found.append(Violation(rule=RuleBroken(f"{row.name}: ordered union is an alias with a TypeAdapter constructor, never a class"), line=LineNumber(node.lineno)))
        elif isinstance(row, ConsistencyModelRow):
            found.extend(_check_consistency_model(node, row))
        elif isinstance(row, UnionRow):
            found.append(Violation(rule=RuleBroken(f"{row.name}: a union is a type alias, never a class; identity-carrying data constructs through the discriminator on the alias"), line=LineNumber(node.lineno)))
        found.extend(_check_methods(node, row, table))
    return found
