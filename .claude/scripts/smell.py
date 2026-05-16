#!/usr/bin/env python3
"""TCA structural smell detector.

The script is itself a TCA program. Invariants are frozen Pydantic models
implementing the `Invariant` Protocol. File state is an active model whose
derivations cache via `@cached_property`. Smells are composed value objects.
AST dispatch is `match`/`case` against the `ast` module's sum type.

PostToolUse hook. Reads JSON on stdin, parses the edited file, yields smells.
Exit 2 blocks with stderr feedback. Exit 0 passes.
"""
from __future__ import annotations

import ast
import json
import sys
from functools import cached_property
from pathlib import Path
from typing import Annotated, Iterable, Iterator, Protocol, Sequence

from pydantic import BaseModel, ConfigDict, Field, RootModel


# ─── Scalars (type layer) ───────────────────────────────────────────────────


class LineNumber(RootModel[int], frozen=True):
    root: int = Field(ge=1)


# ─── AST predicates (pure functions over a foreign sum type) ─────────────────


def decorator_name(dec: ast.expr) -> str | None:
    match dec:
        case ast.Name(id=name):
            return name
        case ast.Attribute(attr=name):
            return name
        case ast.Call(func=ast.Name(id=name)):
            return name
        case ast.Call(func=ast.Attribute(attr=name)):
            return name
    return None


def returns_explicit_none(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """True only for `-> None` annotations. Un-annotated methods return False."""
    match fn.returns:
        case ast.Constant(value=None):
            return True
    return False


def literal_string_member_count(annotation: ast.expr) -> int:
    """String members in `Literal[...]`. Zero if not a homogeneous string literal."""
    match annotation:
        case ast.Subscript(value=ast.Name(id="Literal"), slice=ast.Tuple(elts=elts)):
            strs = [e for e in elts if _is_string_constant(e)]
            return len(strs) if len(strs) == len(elts) else 0
        case ast.Subscript(value=ast.Name(id="Literal"), slice=ast.Constant(value=str())):
            return 1
    return 0


def _is_string_constant(node: ast.expr) -> bool:
    match node:
        case ast.Constant(value=str()):
            return True
    return False


def tuple_element_types(annotation: ast.expr) -> tuple[str, ...]:
    """Element type names in `tuple[A, B, C]`. Empty if not a homogeneous Name tuple."""
    match annotation:
        case ast.Subscript(value=ast.Name(id="tuple"), slice=ast.Tuple(elts=elts)):
            names = [n.id for n in elts if isinstance(n, ast.Name)]
            return tuple(names) if len(names) == len(elts) else ()
    return ()


def is_basemodel_base(node: ast.expr) -> bool:
    match node:
        case ast.Name(id="BaseModel" | "RootModel"):
            return True
    return False


def is_frozen_true_kwarg(kw: ast.keyword) -> bool:
    match kw:
        case ast.keyword(arg="frozen", value=ast.Constant(value=True)):
            return True
    return False


# ─── Method decl ────────────────────────────────────────────────────────────


class MethodDecl(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    owner_class: str
    node: ast.FunctionDef | ast.AsyncFunctionDef

    @cached_property
    def name(self) -> str:
        return self.node.name

    @cached_property
    def line(self) -> LineNumber:
        return LineNumber(self.node.lineno)

    @cached_property
    def decorator_names(self) -> frozenset[str]:
        return frozenset(n for n in (decorator_name(d) for d in self.node.decorator_list) if n is not None)

    @cached_property
    def is_derivation(self) -> bool:
        return bool(self.decorator_names & {"cached_property", "computed_field"})

    @cached_property
    def has_computed_field_and_property(self) -> bool:
        decs = self.decorator_names
        return "computed_field" in decs and "property" in decs and "cached_property" not in decs

    @cached_property
    def is_static_or_class_method(self) -> bool:
        return bool(self.decorator_names & {"staticmethod", "classmethod"})

    @cached_property
    def is_private(self) -> bool:
        return self.name.startswith("_") and not self.name.startswith("__")

    @cached_property
    def returns_explicit_none(self) -> bool:
        return returns_explicit_none(self.node)

    @cached_property
    def mutable_accumulations(self) -> tuple[LineNumber, ...]:
        return tuple(LineNumber(ln) for ln in _find_mutable_accumulations(self.node.body))


def _find_mutable_accumulations(body: Sequence[ast.stmt]) -> Iterator[int]:
    """Single-pass ordered walk. Tracks names bound to fresh empty mutables in
    the same scope, yields the line of each subsequent mutation of those names.
    Does not flag `self.x` mutations or any name not locally bound to `[]`/`{}`."""
    mutable_names: dict[str, int] = {}

    def walk(node: ast.AST) -> Iterator[int]:
        match node:
            case ast.Assign(targets=[ast.Name(id=name)], value=ast.List(elts=[])):
                mutable_names[name] = node.lineno
            case ast.Assign(targets=[ast.Name(id=name)], value=ast.Dict(keys=[])):
                mutable_names[name] = node.lineno
            case ast.Call(
                func=ast.Attribute(value=ast.Name(id=name), attr="append" | "extend" | "update")
            ) if name in mutable_names:
                yield node.lineno
        for child in ast.iter_child_nodes(node):
            yield from walk(child)

    for stmt in body:
        yield from walk(stmt)


# ─── Class decl ─────────────────────────────────────────────────────────────


class ClassDecl(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    node: ast.ClassDef

    @cached_property
    def name(self) -> str:
        return self.node.name

    @cached_property
    def is_frozen_basemodel(self) -> bool:
        if not any(is_basemodel_base(b) for b in self.node.bases):
            return False
        return any(is_frozen_true_kwarg(kw) for kw in self.node.keywords)

    @cached_property
    def methods(self) -> tuple[MethodDecl, ...]:
        return tuple(_iter_methods(self.node))

    @cached_property
    def annotated_fields(self) -> tuple[ast.AnnAssign, ...]:
        return tuple(_iter_annotated_fields(self.node))

    @cached_property
    def try_blocks(self) -> tuple[LineNumber, ...]:
        return tuple(LineNumber(t.lineno) for t in _iter_try_blocks(self.node))

    @cached_property
    def homogeneous_tuple_field_counts(self) -> dict[str, int]:
        """Count of fields annotated `tuple[T, T, ...]` (homogeneous Name tuples), per T."""
        counts: dict[str, int] = {}
        for field in self.annotated_fields:
            if field.annotation is None:
                continue
            elements = tuple_element_types(field.annotation)
            if len(elements) >= 1 and len(set(elements)) == 1:
                counts[elements[0]] = counts.get(elements[0], 0) + 1
        return counts


def _iter_methods(class_node: ast.ClassDef) -> Iterator[MethodDecl]:
    for item in class_node.body:
        match item:
            case ast.FunctionDef() | ast.AsyncFunctionDef():
                yield MethodDecl(owner_class=class_node.name, node=item)


def _iter_annotated_fields(class_node: ast.ClassDef) -> Iterator[ast.AnnAssign]:
    for item in class_node.body:
        match item:
            case ast.AnnAssign():
                yield item


def _iter_try_blocks(class_node: ast.ClassDef) -> Iterator[ast.Try]:
    for item in class_node.body:
        match item:
            case ast.Try():
                yield item


# ─── File context (active model for one file's analysis) ────────────────────


class FileContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    path: Path
    source: str

    @cached_property
    def basename(self) -> str:
        return self.path.name

    @cached_property
    def in_domain(self) -> bool:
        return "/domain/" in self.path.as_posix()

    @cached_property
    def in_tests(self) -> bool:
        posix = self.path.as_posix()
        return (
            "/tests/" in posix
            or "/test/" in posix
            or self.basename.startswith("test_")
            or self.basename.endswith("_test.py")
            or self.basename == "conftest.py"
        )

    @cached_property
    def tree(self) -> ast.Module:
        return ast.parse(self.source)

    @cached_property
    def classes(self) -> tuple[ClassDecl, ...]:
        return tuple(_iter_class_defs(self.tree))

    @cached_property
    def imports(self) -> tuple[ast.ImportFrom, ...]:
        return tuple(_iter_import_froms(self.tree))

    @cached_property
    def package_root(self) -> Path | None:
        """Topmost directory above which `__init__.py` no longer exists."""
        if not (self.path.parent / "__init__.py").exists():
            return None
        current = self.path.parent
        while (current.parent / "__init__.py").exists():
            current = current.parent
        return current.parent

    @cached_property
    def dotted_module(self) -> str | None:
        root = self.package_root
        if root is None:
            return None
        relative = self.path.relative_to(root).with_suffix("")
        return ".".join(relative.parts)

    @cached_property
    def json_loads_then_validate_lines(self) -> tuple[LineNumber, ...]:
        return tuple(LineNumber(ln) for ln in _find_json_loads_then_validate(self.tree))

    def resolve_import(self, node: ast.ImportFrom) -> str | None:
        """Resolve a relative ImportFrom to its absolute dotted module path."""
        if node.level == 0:
            return node.module
        base = self.dotted_module
        if base is None:
            return None
        parts = base.split(".")
        if len(parts) < node.level:
            return None
        parts = parts[: -node.level]
        if node.module:
            parts.append(node.module)
        return ".".join(parts) if parts else None


def _iter_class_defs(tree: ast.Module) -> Iterator[ClassDecl]:
    for node in tree.body:
        match node:
            case ast.ClassDef():
                yield ClassDecl(node=node)


def _iter_import_froms(tree: ast.Module) -> Iterator[ast.ImportFrom]:
    for node in tree.body:
        match node:
            case ast.ImportFrom():
                yield node


def _find_json_loads_then_validate(tree: ast.Module) -> Iterator[int]:
    """Match `Model.model_validate(json.loads(...))` in a single expression."""
    for node in ast.walk(tree):
        match node:
            case ast.Call(
                func=ast.Attribute(attr="model_validate"),
                args=[ast.Call(func=ast.Attribute(value=ast.Name(id="json"), attr="loads")), *_],
            ):
                yield node.lineno


# ─── Smell (composed value object) ──────────────────────────────────────────


class SourceLocation(BaseModel, frozen=True):
    line: LineNumber
    class_name: str | None = None
    method_name: str | None = None

    @cached_property
    def qualified(self) -> str:
        match (self.class_name, self.method_name):
            case (None, _):
                return f"line {self.line.root}"
            case (cls, None):
                return f"{cls} (line {self.line.root})"
            case (cls, method):
                return f"{cls}.{method} (line {self.line.root})"


class Smell(BaseModel, frozen=True):
    invariant_name: Annotated[str, Field(min_length=1)]
    message: Annotated[str, Field(min_length=1)]
    location: SourceLocation

    @cached_property
    def rendered(self) -> str:
        return f"{self.invariant_name}: {self.message} ({self.location.qualified})"


# ─── Invariant Protocol ─────────────────────────────────────────────────────


class Invariant(Protocol):
    applies_in_tests: bool

    def check(self, ctx: FileContext) -> Iterable[Smell]: ...


def _smell(
    invariant: Invariant,
    message: str,
    line: int,
    *,
    class_name: str | None = None,
    method_name: str | None = None,
) -> Smell:
    return Smell(
        invariant_name=type(invariant).__name__,
        message=message,
        location=SourceLocation(line=LineNumber(line), class_name=class_name, method_name=method_name),
    )


# ─── Invariants (frozen models, one per rule) ───────────────────────────────


DOMAIN_TECH_NAMES = frozenset({
    "store.py", "repository.py", "handler.py", "controller.py",
    "crud.py", "manager.py", "processor.py", "router.py",
})

DOMAIN_DUMP_NAMES = frozenset({"utils.py", "helpers.py", "common.py", "misc.py"})


class DomainTechFilename(BaseModel, frozen=True):
    applies_in_tests: bool = False

    def check(self, ctx: FileContext) -> Iterable[Smell]:
        if not ctx.in_domain or ctx.basename not in DOMAIN_TECH_NAMES:
            return
        yield _smell(self, f"domain file named for technology pattern: {ctx.basename}", 1)


class DomainDumpFilename(BaseModel, frozen=True):
    applies_in_tests: bool = False

    def check(self, ctx: FileContext) -> Iterable[Smell]:
        if not ctx.in_domain or ctx.basename not in DOMAIN_DUMP_NAMES:
            return
        yield _smell(self, f"domain file with dumping-ground name: {ctx.basename}", 1)


class TypePyImportingProject(BaseModel, frozen=True):
    applies_in_tests: bool = False

    def check(self, ctx: FileContext) -> Iterable[Smell]:
        if ctx.basename != "type.py":
            return
        for imp in ctx.imports:
            if imp.level > 0:
                yield _smell(self, "type.py importing from project. Scalars are the bottom layer.", imp.lineno)


class ValuePyImportingNonType(BaseModel, frozen=True):
    applies_in_tests: bool = False

    def check(self, ctx: FileContext) -> Iterable[Smell]:
        if ctx.basename != "value.py":
            return
        for imp in ctx.imports:
            module = imp.module or ""
            if imp.level > 0 and module != "type" and not module.startswith("type."):
                yield _smell(self, "value.py importing from non-type.py. value.py composes only scalars.", imp.lineno)


class InvertedDomainImport(BaseModel, frozen=True):
    applies_in_tests: bool = False

    def check(self, ctx: FileContext) -> Iterable[Smell]:
        if not ctx.in_domain:
            return
        for imp in ctx.imports:
            resolved = ctx.resolve_import(imp)
            if resolved is None:
                continue
            segments = resolved.split(".")
            for index, segment in enumerate(segments):
                if segment in ("service", "api") and not _is_domain_owned_api(segments, index):
                    yield _smell(
                        self,
                        f"inverted dependency: domain imports from {resolved}. Domain imports nothing from above.",
                        imp.lineno,
                    )
                    break


def _is_domain_owned_api(segments: list[str], index: int) -> bool:
    """`domain/<context>/api.py` is approved — domain-owned contracts."""
    return index > 0 and segments[index - 1] == "domain" and segments[index] == "api"


class JsonLoadsThenValidate(BaseModel, frozen=True):
    applies_in_tests: bool = True

    def check(self, ctx: FileContext) -> Iterable[Smell]:
        for line in ctx.json_loads_then_validate_lines:
            yield _smell(self, "json.loads then model_validate. Use model_validate_json(raw_bytes).", line.root)


class ComputedFieldWithProperty(BaseModel, frozen=True):
    applies_in_tests: bool = False

    def check(self, ctx: FileContext) -> Iterable[Smell]:
        for cls in ctx.classes:
            if not cls.is_frozen_basemodel:
                continue
            for method in cls.methods:
                if method.has_computed_field_and_property:
                    yield _smell(
                        self,
                        "@computed_field + @property recomputes every access. Use @cached_property.",
                        method.line.root,
                        class_name=cls.name,
                        method_name=method.name,
                    )


class MutableInDerivation(BaseModel, frozen=True):
    applies_in_tests: bool = False

    def check(self, ctx: FileContext) -> Iterable[Smell]:
        for cls in ctx.classes:
            if not cls.is_frozen_basemodel:
                continue
            for method in cls.methods:
                if not method.is_derivation:
                    continue
                for line in method.mutable_accumulations:
                    yield _smell(
                        self,
                        "mutable accumulation in derivation. Use a comprehension.",
                        line.root,
                        class_name=cls.name,
                        method_name=method.name,
                    )


class PrivateMethodOnDomainModel(BaseModel, frozen=True):
    applies_in_tests: bool = False

    def check(self, ctx: FileContext) -> Iterable[Smell]:
        if not ctx.in_domain:
            return
        for cls in ctx.classes:
            for method in cls.methods:
                if method.is_private:
                    yield _smell(
                        self,
                        "private method on domain model: hidden procedure. Compose a type that makes this unnecessary.",
                        method.line.root,
                        class_name=cls.name,
                        method_name=method.name,
                    )


class VoidMethodOnDomainModel(BaseModel, frozen=True):
    applies_in_tests: bool = False

    def check(self, ctx: FileContext) -> Iterable[Smell]:
        if not ctx.in_domain:
            return
        for cls in ctx.classes:
            for method in cls.methods:
                if method.returns_explicit_none and not method.name.startswith("__"):
                    yield _smell(
                        self,
                        "domain model method returns None: frozen models are pure. No side effects.",
                        method.line.root,
                        class_name=cls.name,
                        method_name=method.name,
                    )


class StaticOrClassMethodOnDomainModel(BaseModel, frozen=True):
    applies_in_tests: bool = False

    def check(self, ctx: FileContext) -> Iterable[Smell]:
        if not ctx.in_domain:
            return
        for cls in ctx.classes:
            for method in cls.methods:
                if method.is_static_or_class_method:
                    yield _smell(
                        self,
                        "@staticmethod/@classmethod on domain model: escaped logic. Derivations use self.",
                        method.line.root,
                        class_name=cls.name,
                        method_name=method.name,
                    )


class TryExceptInDomainModel(BaseModel, frozen=True):
    applies_in_tests: bool = False

    def check(self, ctx: FileContext) -> Iterable[Smell]:
        if not ctx.in_domain:
            return
        for cls in ctx.classes:
            for line in cls.try_blocks:
                yield _smell(
                    self,
                    "try/except in domain model: construction fails or succeeds, models don't catch.",
                    line.root,
                    class_name=cls.name,
                )


class MultiValueStringLiteral(BaseModel, frozen=True):
    applies_in_tests: bool = False

    def check(self, ctx: FileContext) -> Iterable[Smell]:
        if not ctx.in_domain:
            return
        for cls in ctx.classes:
            for field in cls.annotated_fields:
                if field.annotation is None:
                    continue
                count = literal_string_member_count(field.annotation)
                if count >= 2:
                    yield _smell(
                        self,
                        f"multi-value Literal[str] ({count} values): forge a StrEnum in type.py. Single-value Literal['kind'] for DU discriminators is allowed.",
                        field.lineno,
                        class_name=cls.name,
                    )


class ParallelTupleFields(BaseModel, frozen=True):
    applies_in_tests: bool = False

    def check(self, ctx: FileContext) -> Iterable[Smell]:
        if not ctx.in_domain:
            return
        for cls in ctx.classes:
            for type_name, count in cls.homogeneous_tuple_field_counts.items():
                if count >= 3:
                    yield _smell(
                        self,
                        f"3+ tuple fields sharing inner type {type_name}: parallel data belongs in a composed value type.",
                        cls.node.lineno,
                        class_name=cls.name,
                    )


INVARIANTS: tuple[Invariant, ...] = (
    DomainTechFilename(),
    DomainDumpFilename(),
    TypePyImportingProject(),
    ValuePyImportingNonType(),
    InvertedDomainImport(),
    JsonLoadsThenValidate(),
    ComputedFieldWithProperty(),
    MutableInDerivation(),
    PrivateMethodOnDomainModel(),
    VoidMethodOnDomainModel(),
    StaticOrClassMethodOnDomainModel(),
    TryExceptInDomainModel(),
    MultiValueStringLiteral(),
    ParallelTupleFields(),
)


# ─── Composition ────────────────────────────────────────────────────────────


def collect_smells(ctx: FileContext) -> tuple[Smell, ...]:
    skip_tests = ctx.in_tests
    return tuple(
        smell
        for invariant in INVARIANTS
        if invariant.applies_in_tests or not skip_tests
        for smell in invariant.check(ctx)
    )


def _exit_pass() -> None:
    sys.exit(0)


def _exit_with_smells(smells: tuple[Smell, ...]) -> None:
    sys.stderr.write("STRUCTURAL SMELLS:\n")
    for smell in smells:
        sys.stderr.write(f"  - {smell.rendered}\n")
    sys.exit(2)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        _exit_pass()
        return

    raw_path = data.get("tool_input", {}).get("file_path", "")
    if not raw_path.endswith(".py"):
        _exit_pass()
        return

    path = Path(raw_path)
    if not path.is_file() or "/.claude/scripts/" in path.as_posix():
        _exit_pass()
        return

    try:
        source = path.read_text()
    except OSError:
        _exit_pass()
        return

    try:
        ctx = FileContext(path=path, source=source)
        _ = ctx.tree
    except SyntaxError:
        _exit_pass()
        return

    smells = collect_smells(ctx)
    if smells:
        _exit_with_smells(smells)
    _exit_pass()


if __name__ == "__main__":
    main()
