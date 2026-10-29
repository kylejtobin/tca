"""Require identical package test instructions; run without application dependencies."""

from pathlib import Path


def check(root: Path) -> list[str]:
    canonical = (root / ".agents/skills/tca-testing/TEST_DIR_AGENTS.md").read_bytes()
    failures = []
    packages = sorted((root / "packages/python").glob("*/pyproject.toml"))
    if not packages:
        failures.append("No Python package manifests found")
    for manifest in packages:
        instructions = manifest.parent / "tests/AGENTS.md"
        if not instructions.is_file() or instructions.read_bytes() != canonical:
            failures.append(str(instructions.relative_to(root)))
    return failures


if __name__ == "__main__":
    failures = check(Path(__file__).resolve().parents[1])
    if failures:
        raise SystemExit("Missing or divergent test instructions: " + ", ".join(failures))
    print("Package test instructions match the canonical standard.")
