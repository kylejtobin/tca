"""The skill's canonical examples, as written on its pages: each file assembled from the blocks that
name it, in dependency order, then constructed with valid and invalid values."""

import ast
import importlib
import re
import subprocess
import sys
from collections.abc import Iterator
from graphlib import TopologicalSorter
from pathlib import Path
from types import ModuleType

import pytest
from pydantic import ValidationError

SKILLS = Path(__file__).parents[5] / ".agents" / "skills"
PAGES = SKILLS / "python-dev-tca"
CHECK = SKILLS / "smell-check" / "smell-check"


def assemble(into: Path) -> None:
    files: dict[str, list[str]] = {}
    for page in sorted(PAGES.glob("*.md")):
        for block in re.findall(r"```python\n(.*?)```", page.read_text(), flags=re.S):
            head, _, body = block.partition("\n")
            if head.startswith("# ") and head.endswith(".py"):
                files.setdefault(head.removeprefix("# "), []).append(body)
    for path, bodies in files.items():
        nodes = [node for body in bodies for node in ast.parse(body).body]
        imports = [ast.unparse(n) for n in nodes if isinstance(n, ast.Import | ast.ImportFrom)]
        classes = {n.name: n for n in nodes if isinstance(n, ast.ClassDef)}
        rest = [
            ast.unparse(n)
            for n in nodes
            if not isinstance(n, ast.Import | ast.ImportFrom | ast.ClassDef)
        ]
        held = {
            name: {
                n.id
                for part in (*node.bases, *(f for f in node.body if isinstance(f, ast.AnnAssign)))
                for n in ast.walk(part)
                if isinstance(n, ast.Name) and n.id in classes and n.id != name
            }
            for name, node in classes.items()
        }
        ordered = [ast.unparse(classes[name]) for name in TopologicalSorter(held).static_order()]
        target = into / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "\n".join(dict.fromkeys(imports)) + "\n\n\n" + "\n\n\n".join((*ordered, *rest)) + "\n"
        )
        for parent in target.relative_to(into).parents:
            (into / parent / "__init__.py").touch()


@pytest.fixture(scope="module")
def shop(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    root = tmp_path_factory.mktemp("shop")
    assemble(root)
    sys.path.insert(0, str(root))
    yield root
    sys.path.remove(str(root))
    for name in [m for m in sys.modules if m.split(".")[0] in {"domain", "integration", "parser"}]:
        del sys.modules[name]


def module(name: str) -> ModuleType:
    return importlib.import_module(name)


def test_the_canonical_examples_pass_the_smell_check(shop: Path) -> None:
    scan = subprocess.run(  # noqa: S603
        (sys.executable, str(CHECK), str(shop)), capture_output=True, text=True, check=False
    )
    assert (scan.returncode, scan.stdout) == (0, "")


def test_aisle_matches_hold_each_product_once(shop: Path) -> None:
    value, kind = module("domain.shop.value"), module("domain.shop.type")
    near, far = (
        value.AisleMatch(sku=kind.Sku(sku), similarity=kind.Similarity(score))
        for sku, score in (("tea", 0.9), ("mug", 0.85))
    )
    assert value.AisleMatches((near, far)).root == (near, far)
    with pytest.raises(ValidationError, match=kind.Invariant.EACH_PRODUCT_ONCE):
        value.AisleMatches((near, near))
    with pytest.raises(ValidationError):
        value.AisleMatches(())


def test_aisles_hold_each_aisle_once(shop: Path) -> None:
    value, kind = module("domain.shop.value"), module("domain.shop.type")
    matches = value.AisleMatches(
        (value.AisleMatch(sku=kind.Sku("tea"), similarity=kind.Similarity(0.9)),)
    )
    pantry, kitchen = (
        value.Aisle(category=kind.Category(c), matches=matches) for c in ("pantry", "kitchen")
    )
    assert value.Aisles((pantry, kitchen)).root == (pantry, kitchen)
    with pytest.raises(ValidationError, match=kind.Invariant.EACH_AISLE_ONCE):
        value.Aisles((pantry, pantry))
    assert value.NoAisles(()).root == ()
    with pytest.raises(ValidationError):
        value.NoAisles((pantry,))


@pytest.mark.parametrize(
    ("stated", "unlisted", "listed", "invariant"),
    [
        ("StatedReason", "UnlistedReason", "DeclineReason", "UNLISTED_REASON"),
        ("StatedError", "UnlistedError", "ProviderError", "UNLISTED_ERROR"),
    ],
)
def test_an_unlisted_value_is_one_the_shop_has_no_word_for(
    shop: Path, stated: str, unlisted: str, listed: str, invariant: str
) -> None:
    kind = module("domain.shop.type")
    known = next(iter(getattr(kind, listed)))
    assert getattr(kind, stated).model_validate_json(f'"{known.value}"').root is known
    later = getattr(kind, stated).model_validate_json('"introduced_later"').root
    assert later == getattr(kind, unlisted)("introduced_later")
    with pytest.raises(ValidationError, match=getattr(kind.Invariant, invariant)):
        getattr(kind, unlisted)(known.value)
    with pytest.raises(ValidationError):
        getattr(kind, stated).model_validate_json('""')


def test_a_receipt_is_read_and_written_in_its_own_format(shop: Path) -> None:
    payments, receipts, kind = (
        module("integration.payments.model"),
        module("parser.receipt"),
        module("domain.shop.type"),
    )
    written = '{"id":"ch_1","receipt":"A1|1200|usd"}'
    read = payments.ChargeApproved.model_validate_json(written)
    assert read.receipt == receipts.Receipt(
        ref=receipts.ReceiptRef("A1"), amount=kind.Amount(1200), currency=kind.Currency.USD
    )
    assert read.model_dump_json(by_alias=True) == written
    for ref in ("A1", "order 7 / é", "x" * 200):
        typed = receipts.Receipt(
            ref=receipts.ReceiptRef(ref), amount=kind.Amount(0), currency=kind.Currency.EUR
        )
        held = payments.ChargeApproved(id=kind.ChargeId("ch_1"), receipt=typed)
        assert held.receipt is typed
        assert (
            payments.ChargeApproved.model_validate_json(held.model_dump_json(by_alias=True)) == held
        )
    for wrong in (
        '{"id":"ch_1","receipt":"A1|twelve|usd"}',
        '{"id":"ch_1","receipt":"A1|1200"}',
        '{"id":"ch_1","receipt":"A1|1200|gbp"}',
        '{"id":"ch_1","receipt":"A1|-5|usd"}',
        '{"id":"ch_1","receipt":12}',
        '{"id":"ch_1","receipt":null}',
        '{"id":"ch_1"}',
    ):
        with pytest.raises(ValidationError):
            payments.ChargeApproved.model_validate_json(wrong)
    for unwritable in ("A|1", "A\n1", ""):
        with pytest.raises(ValidationError):
            receipts.ReceiptRef(unwritable)
