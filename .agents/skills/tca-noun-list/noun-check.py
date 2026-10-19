"""Check a Python TCA package against its noun list, or draft the list from the code.

    noun-check.py <python-dev-tca SKILL.md> <src root> <nouns.json>   check
    noun-check.py <python-dev-tca SKILL.md> <src root> --draft        print a draft table

The list has four columns per row: name and kind are chosen; file and layer are
derived from the kind's construct page. The map from kind to file and layer is
read from the skill's "Its files, in dependency order" table, never retyped.
Faults are reported in the list gate's words and the exit code is nonzero when
any is found.
"""

import ast
import json
import re
import sys
from pathlib import Path

LAYER = {"semantic scalar": "Scalar", "ordered union": "Scalar", "value object": "Value",
         "concept model": "Thing", "action": "Thing"}
FILE_LAYER = {"type.py": "Scalar", "value.py": "Value", "model.py": "Value"}  # members' layer for collection/union
EVERY_LAYER = {"collection", "union", "ordered union"}  # "each occurs at every layer"
PREFER = ["semantic scalar", "union", "collection", "value object", "concept model", "foreign model",
          "transformation", "effect interpreter", "provider", "config", "composition root", "contract model",
          "format type", "action", "ordered union"]


def skill_map(skill: Path) -> dict[str, list[re.Pattern[str]]]:
    """kind -> file patterns, from the skill's files table."""
    block = skill.read_text().split("## Its files, in dependency order", 1)[1].split("```")[1]
    out: dict[str, list[re.Pattern[str]]] = {}
    for line in block.strip().splitlines():
        parts = line.split()
        if not parts or not parts[0].isdigit():
            continue
        path, pages = parts[1], [p for p in parts[2:] if p.endswith(".md")]
        pattern = re.sub(r"<[a-z]+>", "[^/]+", re.escape(path).replace("<package>/", ""))
        for page in pages:
            out.setdefault(page[:-3].replace("-", " "), []).append(re.compile(pattern + "$"))
    return out


def file_matches(kind: str, file: str, kinds: dict[str, list[re.Pattern[str]]]) -> bool:
    pats = [p for ps in kinds.values() for p in ps] if kind in EVERY_LAYER else kinds.get(kind, [])
    return any(p.search(file) for p in pats)


def layer_of(kind: str, file: str) -> str:
    if kind in LAYER:
        return LAYER[kind]
    if kind in ("collection", "union"):
        return FILE_LAYER.get(Path(file).name, "Thing" if "/domain/" in "/" + file else "Value")
    return "crossing"


def shape_kinds(node: ast.ClassDef, file: str) -> set[str]:
    """The kinds a class's shape admits; empty when the shape does not say."""
    bases = [ast.unparse(b) for b in node.bases]
    names = {n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    base = Path(file).name
    if any(b == "StrEnum" for b in bases):
        return {"semantic scalar", "ordered union"}
    for b in node.bases:
        if isinstance(b, ast.Subscript) and ast.unparse(b.value) == "RootModel":
            inner = b.slice
            if isinstance(inner, ast.Subscript) and ast.unparse(inner.value) in ("tuple", "Tuple"):
                return {"collection"}
            if isinstance(inner, ast.BinOp):
                return {"union", "ordered union"}
            return {"semantic scalar"}
    if any(b == "BaseSettings" for b in bases):
        return {"config"}
    if "interpret" in names:
        return {"effect interpreter"}
    if "client" in names:
        return {"provider"}
    if any(b == "BaseModel" for b in bases):
        if "/domain/" in "/" + file:
            return {"value object"} if base == "value.py" else {"contract model"} if base == "api.py" else {"concept model", "action"}
        if "/integration/" in "/" + file:
            return {"foreign model"} if base == "model.py" else {"transformation"}
        if "/parser/" in "/" + file:
            return {"format type"}
    return set()


def scan(src: Path) -> dict[str, tuple[str, set[str]]]:
    """name -> (file, kinds its shape admits), for every top-level class and composition-root callback."""
    found: dict[str, tuple[str, set[str]]] = {}
    for py in sorted(src.rglob("*.py")):
        rel = py.relative_to(src).as_posix()
        if "/__pycache__/" in "/" + rel:
            continue
        root = Path(rel).name in ("main.py", "__init__.py") and rel.count("/") <= 1
        for node in ast.parse(py.read_text()).body:
            if isinstance(node, ast.ClassDef):
                found[node.name] = (rel, shape_kinds(node, rel))
            elif root and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                found[node.name] = (rel, {"composition root"})
    return found


def draft(found: dict[str, tuple[str, set[str]]]) -> dict:
    rows = []
    for name, (file, kinds) in found.items():
        kind = next((k for k in PREFER if k in kinds), "?")
        rows.append({"name": name, "kind": kind, "file": file, "layer": layer_of(kind, file)})
    return {"rows": rows}


def check(table: dict, found: dict[str, tuple[str, set[str]]], kinds: dict[str, list[re.Pattern[str]]]) -> list[str]:
    rows = table["rows"]
    faults = []
    names = [r["name"] for r in rows]
    for n in sorted({n for n in names if names.count(n) > 1}):
        faults.append(f"redundant: {n} is listed more than once")
    listed = {r["name"]: r for r in rows}
    for name in sorted(found.keys() - listed.keys()):
        faults.append(f"missing from the list: {name} in {found[name][0]}")
    for name, row in listed.items():
        if name not in found:
            faults.append(f"missing from the code: {name}, listed in {row['file']}")
            continue
        file, shapes = found[name]
        if file != row["file"]:
            faults.append(f"misplaced: {name} listed in {row['file']}, found in {file}")
        if not file_matches(row["kind"], row["file"], kinds):
            faults.append(f"wrongly placed: {name} is a {row['kind']}, which does not live in {row['file']}")
        if row["layer"] != layer_of(row["kind"], row["file"]):
            faults.append(f"wrongly layered: {name} is a {row['kind']} in {row['file']}, so its layer is {layer_of(row['kind'], row['file'])}, not {row['layer']}")
        if shapes and row["kind"] not in shapes:
            faults.append(f"wrongly structured: {name} is listed as a {row['kind']} but is shaped as a {' or '.join(sorted(shapes))}")
    return faults


def main(argv: list[str]) -> int:
    skill, src = Path(argv[1]), Path(argv[2])
    kinds = skill_map(skill)
    found = scan(src)
    if argv[3] == "--draft":
        print(json.dumps(draft(found), indent=2))
        return 0
    faults = check(json.loads(Path(argv[3]).read_text()), found, kinds)
    print("\n".join(faults) if faults else f"the list and the code agree: {len(found)} nouns")
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
