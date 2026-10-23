"""The trust boundary of a run: every instance in it either arrived at an edge the caller, the
deployment or ``hear`` validated, or was constructed by ``model_validate`` from instances
already there; a computed value is what its bound operands compute; and nothing in production
source skips validation."""

import inspect
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import BaseModel, RootModel

import type_construction.cli
import type_construction.engine
import type_construction.world
from type_construction.engine import Constructed, Run, Scope, Site, config, is_elements, proven, ran
from type_construction.world import Computation, Measure, Relation

from . import occurrences as program
from .occurrences import PERFORMED, Checkout, PlaceOrder
from .test_occurrences import ORDER

PRODUCTION = [
    Path(inspect.getfile(module)).parent
    for module in (type_construction.world, type_construction.engine, type_construction.cli)
]
"""The source directories the engine's path runs through."""

BYPASSES = ("model_construct(", "model_copy(", "__setattr__(", "__pydantic_validator__")
"""Pydantic's ways around validation, as they are written."""


@pytest.fixture
def parties(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The catalog's prices and a clear screening in the environment; no ``.env``."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CATALOG__PRICES", '{"tea": "2.50", "mug": "4", "pot": "10"}')
    monkeypatch.setenv("FRAUD__SAYS", '{"status": "clear"}')
    PERFORMED.clear()


def scopes(scope: Scope) -> list[Scope]:
    """A scope and every scope under it."""
    return [scope, *(found for child in scope.children for found in scopes(child))]


def owned(root: Scope) -> list[tuple[Scope, Site, BaseModel]]:
    """Every instance a run holds, with its scope and declared site: what arrived or was heard,
    and what each construction made."""
    found: list[tuple[Scope, Site, BaseModel]] = []
    for s in scopes(root):
        for (origin, member), instance in s.arrived.items():
            site = member if origin is None else (*origin.site, "heard", *member)
            found.append((s, site, instance))
        for construction, made in s.made.items():
            if isinstance(made, Constructed):
                found.append((s, construction.site, made.instance))
    return found


def root_of(operand: object) -> Decimal:
    """The decimal root of one operand: a derivation's, or a scalar's."""
    if isinstance(operand, Measure):
        return operand.root
    assert isinstance(operand, RootModel)
    root: object = operand.model_dump()
    assert isinstance(root, (Decimal, int))
    return Decimal(root)


def computations(instance: BaseModel) -> list[tuple[str, Computation]]:
    """Each computed field of an instance with its declared computation."""
    return [
        (name, found)
        for name, info in type(instance).model_fields.items()
        for found in info.metadata
        if isinstance(found, Computation)
    ]


def recomputed(instance: BaseModel, computation: Computation) -> Decimal | int:
    """The computation applied again to the operands the instance holds."""
    roots: list[Decimal] = []
    for name in computation.operands:
        operand: object = getattr(instance, name)
        if is_elements(operand):
            roots.extend(root_of(o) for o in operand)
        else:
            roots.append(root_of(operand))
    return computation.computed(tuple(roots))


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_every_instance_in_a_run_arrived_at_an_edge_or_was_constructed_by_validation() -> (
    None
):
    request = PlaceOrder.model_validate_json(ORDER)
    proof = proven(program)
    run = await ran(Checkout, request, config(program)(), proof)
    assert isinstance(run, Run)
    constants = {c.__name__ for c in proof.constants}
    arrived: list[Site] = []
    constructed: list[Site] = []
    for scope, site, instance in owned(run.root):
        if site[0] in ("request", "deployment") or "heard" in site or site[0] in constants:
            arrived.append(site)
            continue
        assert any(c.site == site for c in scope.made), f"{site} is neither arrived nor constructed"
        assert type(instance).__name__ == site[-1]
        constructed.append(site)
    assert len(constructed) + len(arrived) == len(owned(run.root))
    assert ("request",) in arrived
    assert ("deployment",) in arrived
    assert any(site[-1] == "heard" for site in arrived)
    assert ("Checkout",) in constructed
    assert all(site[0] not in ("request", "deployment") for site in constructed)


@pytest.mark.asyncio
@pytest.mark.usefixtures("parties")
async def test_every_computed_value_in_a_run_is_what_its_bound_operands_compute() -> None:
    request = PlaceOrder.model_validate_json(ORDER)
    run = await ran(Checkout, request, config(program)(), proven(program))
    assert isinstance(run, Run)
    computed = [
        (site, instance)
        for _, site, instance in owned(run.root)
        if isinstance(instance, (Measure, Relation))
    ]
    assert len(computed) == 9
    assert all(computations(instance) for _, instance in computed)
    for _, instance in computed:
        for name, computation in computations(instance):
            assert getattr(instance, name) == recomputed(instance, computation)
    totals = [i for _, i in computed if isinstance(i, program.LineTotal)]
    assert len(totals) == 6
    lines = [
        line
        for carrier in (request.cart, request.gifts, request.pair, request.solo)
        for line in carrier.lines
    ]
    assert [t.right for t in totals] == [line.quantity for line in lines]
    assert all(t.right is line.quantity for t, line in zip(totals, lines, strict=True))


def test_no_production_source_skips_validation() -> None:
    found = [
        (path.relative_to(path.parents[3]), bypass)
        for root in PRODUCTION
        for path in root.rglob("*.py")
        for bypass in BYPASSES
        if bypass in path.read_text()
    ]
    assert found == []
    engine = Path(inspect.getfile(type_construction.engine)).read_text()
    assert engine.count("cls.model_validate(given)") == 1
    assert engine.count("adapter.validate_json(text, strict=True)") == 1
    assert engine.count("adapter.validate_python(data, strict=True)") == 1
    assert engine.count("await action.perform()") == 1
    assert "hear(action, await action.perform())" in engine
