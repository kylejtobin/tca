"""Transport edge for the gate command and hook integration.

This module owns everything that is not doctrine: argv dispatch, stdin hook
events, source reconstruction from tool payloads, catalog discovery, and the
JSON denial shape Cursor/Claude consumes. It intentionally keeps the AST audit
behind a lazy import so ``--order`` can prove a catalog without loading the
conformance engine.
"""

import ast
import json
import sys
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

from tca_gate.model import (
    ConsistencyModelRow, ExistingRow, LineNumber, OntologyCatalog, RuleBroken,
    Violation, ViolationLog,
)

# The scaffold layout, named once. A build target root (``src`` or ``demo``) holds
# two well-known children: ``spec/`` for the catalogs the gate discovers, and the
# ``app`` package for the source those catalogs describe. Row ``file`` paths are
# package-relative and resolve under ``<target>/app``, so the catalog and the
# topology never carry an ``app/`` prefix; this constant is where that convention
# lives.
SPEC = "spec"
PACKAGE = "app"


class _Edit(BaseModel, extra="ignore"):
    """One edit payload shape from tool events.

    Cursor and Claude have used both ``*_string`` and ``*_text`` keys across
    edit tools; the gate accepts either spelling and ignores unrelated fields.
    """

    old_string: str | None = None
    new_string: str | None = None
    old_text: str | None = None
    new_text: str | None = None


class _ToolInput(BaseModel, extra="ignore"):
    """The subset of tool input needed to reconstruct the proposed source."""

    file_path: str = ""
    content: str | None = None
    file_content: str | None = None
    file_text: str | None = None
    old_string: str | None = None
    new_string: str | None = None
    edits: list[_Edit] | None = None


class _HookEvent(BaseModel, extra="ignore"):
    """A PreToolUse event envelope.

    Only ``tool_input`` matters to the gate; unknown event metadata is ignored
    so the hook remains stable across host payload changes.
    """

    tool_name: str = ""
    tool_input: _ToolInput = Field(default_factory=_ToolInput)


def _resulting_source(tool_input: _ToolInput) -> str | None:
    """Return the source that would exist after the pending write/edit.

    Whole-file writes win first. Multi-edit payloads are replayed in order
    against the current file content. Single edit payloads use the same
    one-replacement semantics as the editing tool. ``None`` means the event did
    not contain enough source information for the hook to judge.
    """

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


def _in_scope(file_path: str) -> bool:
    """A write is governed only where the ontology already claims the file: a built
    row in the up-tree target catalog names it. Files the ontology does not claim,
    the framework's own and legacy code alike, are left alone, so the gate never
    condemns a tree it is being adopted into. The no-unmodeled guarantee lives in the
    row-driven build and operator review, not in a passive write veto."""
    if "/.claude/" in file_path or "/tests/" in file_path:
        return False
    path = Path(file_path).resolve()
    located = _find_table(path)
    if not isinstance(located, tuple):
        return False
    table, root = located
    return path in {(root / row.file).resolve() for row in table.rows if not isinstance(row, ExistingRow)}


def _find_table(file_path: Path) -> tuple[OntologyCatalog, Path] | str | None:
    """Find and construct the one ontology catalog governing ``file_path``.

    The catalog is co-located with its target: a ``spec/ontology.json`` in the
    target root (``src/spec`` or ``demo/spec``), beside the ``app`` package that
    holds the source. The nearest one up-tree governs. Row ``file`` paths are
    package-relative, so this returns ``(catalog, package_root)`` where
    ``package_root`` is ``<target>/app``, the directory those paths resolve
    under. Return ``None`` when no catalog is present, or a human-readable error
    string when discovery or construction fails.
    """

    located: Path | None = None
    for directory in file_path.resolve().parents:
        candidate = directory / SPEC / "ontology.json"
        if candidate.exists():
            if located is not None:
                return f"two ontology catalogs in one file's ancestry: {located} and {candidate}; a file is governed by exactly one spec/ontology.json, the one in its target root, never a nested pair"
            located = candidate
    if located is None:
        return None
    try:
        table = OntologyCatalog.model_validate_json(located.read_text())
    except ValidationError as error:
        return f"the ontology catalog at {located} fails construction; fix the catalog before building:\n{error}"
    package_root = located.parent.parent / PACKAGE
    problems = _verify_existing(table, package_root)
    if problems:
        return f"the ontology catalog at {located} fails construction:\n" + "\n".join(problems)
    return table, package_root


def _audit_python(source: str, file_path: Path) -> tuple[list[Violation], str | None]:
    """Parse source and run both smell and catalog-conformance audits."""

    # Lazy import keeps the --order path model-only. Ontology work should not pay
    # for the AST audit machinery used by source checks.
    from tca_gate.audit import legacy_audit, table_audit

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [], None
    located = _find_table(file_path)
    if located is None:
        return [
            Violation(
                rule=RuleBroken("no catalog at the target's spec/ontology.json; the ontology comes first: write the target's ontology catalog, run --order, then build rows in the printed order"),
                line=LineNumber(1),
            )
        ], None
    if isinstance(located, str):
        return [Violation(rule=RuleBroken(located), line=LineNumber(1))], None
    table, table_dir = located
    consistency_model = next((r.name for r in table.rows if isinstance(r, ConsistencyModelRow)), None)
    found = legacy_audit(tree, consistency_model)
    found.extend(table_audit(tree, table, table_dir, file_path))
    return found, consistency_model


def _package_root(table_path: Path) -> Path:
    """Return the ``app`` package root a catalog's row files resolve under.

    The catalog lives at ``<target>/spec/ontology.json``; the source lives in the
    sibling ``<target>/app`` package, so a package-relative row or ledger ``file``
    resolves against ``<target>/app``.
    """

    spec_dir = table_path.resolve().parent
    target_root = spec_dir.parent if spec_dir.name == SPEC else spec_dir
    return target_root / PACKAGE


def _verify_existing(table: OntologyCatalog, table_dir: Path) -> list[str]:
    """Verify that every existing row names a class already present on disk."""

    problems: list[str] = []
    for row in table.rows:
        if isinstance(row, ExistingRow):
            target = table_dir / row.file
            if not target.exists() or f"class {row.name}" not in target.read_text():
                problems.append(
                    f"existing {row.name}: {row.file} does not define it; an existing row records what already exists, never what is wished for"
                )
    return problems


def _deny(reason: str) -> None:
    """Emit the PreToolUse denial payload expected by the host."""

    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))


def _check_files(paths: list[str]) -> int:
    """Run standalone checks for catalogs, ledgers, and Python files."""

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
        if file_path.name == "ontology.json":
            try:
                table = OntologyCatalog.model_validate_json(file_path.read_text())
            except ValidationError as error:
                print(f"{path}: ontology catalog failed construction\n{error}")
                total += 1
                continue
            for problem in _verify_existing(table, _package_root(file_path)):
                print(f"{path}: {problem}")
                total += 1
            continue
        violations, _ = _audit_python(file_path.read_text(), file_path.resolve())
        for violation in violations:
            print(f"{path}:{violation.line.root}: {violation.rule.root}")
        total += len(violations)
    print(f"tca gate: {total} violation(s) across {len(paths)} file(s)")
    return 1 if total else 0


def _smell_files(paths: list[str]) -> int:
    """Catalog-free structural smell scan: legacy_audit alone, no ontology required,
    for planning a refactor over un-modeled code. Reports the structural smells
    (bare primitives, T | None, mutable containers, standalone enums, raw Literals,
    stray arbitrary_types_allowed); the catalog-conformance checks are not run here,
    because they need a catalog to compare against."""
    from tca_gate.audit import legacy_audit

    total = 0
    for path in paths:
        try:
            tree = ast.parse(Path(path).read_text())
        except SyntaxError as error:
            print(f"{path}: does not parse ({error.msg})")
            total += 1
            continue
        violations = legacy_audit(tree, None)
        for violation in violations:
            print(f"{path}:{violation.line.root}: {violation.rule.root}")
        total += len(violations)
    print(f"tca gate: {total} smell(s) across {len(paths)} file(s)")
    return 1 if total else 0


def _print_order(table_path: str) -> int:
    """Validate the ontology and print the row build order."""

    table = OntologyCatalog.model_validate_json(Path(table_path).read_text())
    ledger_path = Path(table_path).parent / "violation.json"
    if ledger_path.exists():
        ledger = ViolationLog.model_validate_json(ledger_path.read_text())
        package_root = _package_root(Path(table_path))
        stale = [v.file for v in ledger.violations if not (package_root / v.file).exists()]
        if stale:
            print("\n".join(f"ledger entry for {f}: file no longer exists; the violation left the tree, so the entry leaves the ledger" for f in stale))
            return 1
    problems = _verify_existing(table, _package_root(Path(table_path)))
    if problems:
        print("\n".join(problems))
        return 1
    for position, row in enumerate(table.build_order(), start=1):
        print(f"{position}. {row.construct} {row.name} -> {row.file}")
    return 0


def main() -> None:
    """Dispatch command modes or process a hook event from stdin."""

    argv = sys.argv[1:]
    if argv and argv[0] == "--check":
        sys.exit(_check_files(argv[1:]))
    if argv and argv[0] == "--order":
        try:
            sys.exit(_print_order(argv[1]))
        except (ValidationError, ValueError) as error:
            print(str(error))
            sys.exit(1)
    if argv and argv[0] == "--smell":
        sys.exit(_smell_files(argv[1:]))
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
            + "\n\nThe ontology models, the gate proves, the file conforms. Fix the target ontology catalog or fix the file to match it; a respelling of a denied form is the same denied form."
        )
