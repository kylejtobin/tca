"""The smell check against its conformance fixtures: every construction the skill allows passes,
and every disguise of one it forbids is refused under exactly the labels it earns. The fixtures are
kept as text, since most are deliberately invalid code, and written out as modules to be scanned."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

CHECK = Path(__file__).parents[5] / ".agents" / "skills" / "smell-check" / "smell-check"
FIXTURES = Path(__file__).parent / "conformance"
ADVERSARIAL = sorted((FIXTURES / "invalid").rglob("*.py.txt"))


def modules(text: Path, into: Path) -> Path:
    for source in [text] if text.is_file() else sorted(text.rglob("*.py.txt")):
        target = into / source.relative_to(FIXTURES).with_suffix("")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return into / text.relative_to(FIXTURES).with_suffix("" if text.is_file() else text.suffix)


def labels(path: Path) -> tuple[int, set[str]]:
    scan = subprocess.run(  # noqa: S603
        (sys.executable, str(CHECK), str(path)), capture_output=True, text=True, check=False
    )
    return scan.returncode, {line.split()[0] for line in scan.stdout.splitlines()}


def test_every_allowed_construction_passes(tmp_path: Path) -> None:
    assert labels(modules(FIXTURES / "valid", tmp_path)) == (0, set())


@pytest.mark.parametrize(
    "fixture", ADVERSARIAL, ids=lambda f: f.relative_to(FIXTURES / "invalid").parts[0]
)
def test_every_disguise_is_refused_under_its_labels(fixture: Path, tmp_path: Path) -> None:
    expected = set(fixture.read_text().splitlines()[0].removeprefix("# expect: ").split())
    assert labels(modules(fixture, tmp_path)) == (1, expected)


def test_there_is_a_disguise_for_every_label(tmp_path: Path) -> None:
    refused = {label for fixture in ADVERSARIAL for label in labels(modules(fixture, tmp_path))[1]}
    declared = {
        line.split("|")[1].strip(" `")
        for line in (CHECK.parent / "SKILL.md").read_text().splitlines()
        if line.startswith("| `")
    }
    assert declared == refused
