"""TCA purity gate, tier one: a deterministic structural audit (PreToolUse Write|Edit).

Structure is decidable, so a parser decides it, not a model. This tier catches the
mechanical violations with certainty and zero latency: bare primitives, a match over a
union, arbitrary_types_allowed off the active model, a standalone enum used as a field type. The
findings are typed and the verdict is a union, so the gate is built the way it enforces.

This file is a boundary membrane (foreign Python text in, a typed verdict out), so its
own ast-walking is the sanctioned procedural crossing, not domain TCA; it lives under
.claude and is excluded from the domain it guards. The semantic residue a parser cannot
judge (is a name vacuous, should this union be a scalar, did this discharge the
obligation) is the tca-review agent's job in the graph, anchored by these findings.

Modes: hook (stdin PreToolUse event, emits a deny decision) and --check FILE... (audits
files directly for the construction graph's review nodes, exits non-zero on any finding).
"""

import ast
import json
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field, RootModel


class LineNumber(RootModel[int], frozen=True):
    root: int = Field(ge=1)


class RuleBroken(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class Violation(BaseModel, frozen=True, extra="forbid"):
    rule: RuleBroken
    line: LineNumber


class Conforming(BaseModel, frozen=True, extra="forbid"):
    pass


class Rejected(BaseModel, frozen=True, extra="forbid"):
    violations: tuple[Violation, ...]


Verdict = Conforming | Rejected


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


_PRIMITIVES = {"str", "int", "float", "bool", "bytes", "Decimal", "complex", "bytearray"}
_ENUM_BASES = {"Enum", "StrEnum", "IntEnum", "IntFlag", "Flag"}
_CONTAINERS = {"list", "tuple", "set", "frozenset", "dict"}


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


def _annotation_names_enum(annotation: ast.expr, enum_names: set[str]) -> bool:
    # A StrEnum is the value space of a scalar (RootModel[Suit]); it is only a break when
    # used bare as a frozen model's field type, the scalar wrapper skipped.
    if isinstance(annotation, ast.Name):
        return annotation.id in enum_names
    if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name) and annotation.value.id in _CONTAINERS:
        slice_node = annotation.slice
        elements = slice_node.elts if isinstance(slice_node, ast.Tuple) else [slice_node]
        return any(isinstance(e, ast.Name) and e.id in enum_names for e in elements)
    return False


def _configdict_has_arbitrary(value: ast.expr | None) -> bool:
    if not isinstance(value, ast.Call):
        return False
    func = value.func
    name = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else ""
    if name != "ConfigDict":
        return False
    return any(
        kw.arg == "arbitrary_types_allowed" and isinstance(kw.value, ast.Constant) and kw.value.value is True
        for kw in value.keywords
    )


def _audit(source: str) -> tuple[Violation, ...]:
    found: list[Violation] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return tuple(found)
    enum_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and any(b in _ENUM_BASES for b in _base_names(node))
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Match):
            found.append(
                Violation(
                    rule=RuleBroken("match over a union; read the selected variant's derivation"),
                    line=LineNumber(node.lineno),
                )
            )
        if not isinstance(node, ast.ClassDef):
            continue
        bases = _base_names(node)
        for keyword in node.keywords:
            if keyword.arg == "arbitrary_types_allowed" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                found.append(
                    Violation(rule=RuleBroken("arbitrary_types_allowed off the active model"), line=LineNumber(node.lineno))
                )
        is_root_model = any("RootModel" in b for b in bases)
        is_base_model = any(b in {"BaseModel", "BaseSettings"} for b in bases)
        for item in node.body:
            if isinstance(item, (ast.Assign, ast.AnnAssign)) and _configdict_has_arbitrary(item.value):
                found.append(
                    Violation(rule=RuleBroken("arbitrary_types_allowed off the active model"), line=LineNumber(item.lineno))
                )
            if is_base_model and not is_root_model and isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name) and item.target.id != "model_config":
                if _annotation_is_primitive(item.annotation):
                    found.append(
                        Violation(
                            rule=RuleBroken("bare primitive field `" + item.target.id + "`; use a semantic scalar"),
                            line=LineNumber(item.lineno),
                        )
                    )
                elif _annotation_names_enum(item.annotation, enum_names):
                    found.append(
                        Violation(
                            rule=RuleBroken("standalone enum as field `" + item.target.id + "`; declare its value space as a RootModel scalar"),
                            line=LineNumber(item.lineno),
                        )
                    )
    return tuple(found)


def _in_scope(file_path: str) -> bool:
    scope = os.environ.get("TCA_GATE_PATH_SUBSTR", "/tca/")
    return (
        file_path.endswith(".py")
        and scope in file_path
        and "/.claude/" not in file_path
        and not file_path.endswith("closure_linter.py")
        and "/tests/" not in file_path
    )


def _check_files(paths: list[str]) -> int:
    total = 0
    for path in paths:
        violations = _audit(Path(path).read_text())
        for violation in violations:
            print(path + ":" + str(violation.line.root) + ": " + violation.rule.root)
        total += len(violations)
    print("tca purity gate: " + str(total) + " violation(s) across " + str(len(paths)) + " file(s)")
    return 1 if total else 0


def main() -> None:
    argv = sys.argv[1:]
    if argv and argv[0] == "--check":
        sys.exit(_check_files(argv[1:]))
    event = _HookEvent.model_validate_json(sys.stdin.read())
    if not _in_scope(event.tool_input.file_path):
        return
    source = _resulting_source(event.tool_input)
    if source is None or not source.strip():
        return
    violations = _audit(source)
    verdict: Verdict = Rejected(violations=violations) if violations else Conforming()
    if isinstance(verdict, Rejected):
        listed = "\n".join("- " + v.rule.root + " (line " + str(v.line.root) + ")" for v in verdict.violations)
        reason = (
            "TCA purity gate denied this write.\n"
            + listed
            + "\n\nReconstruct from the catalog (docs/type-construction-architecture.md). "
            + "Construction is the proof, on your own write too."
        )
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))


if __name__ == "__main__":
    main()
