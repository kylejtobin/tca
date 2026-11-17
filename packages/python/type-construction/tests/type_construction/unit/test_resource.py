"""The shared ``Resource`` contract is provider-independent; integrations specialize and bind it.

Governing requirements: docs/architecture/DESIGN.md sections 5.2 (``Resource`` declares an
integration resource's settings; live clients retain native types), 5.4 (core contracts require
no provider-specific fields or client types; provider dependencies and exports belong within the
integration boundary) and 7 (resource ownership is scoped to a runtime; each realization is a
separate placement). The core is exercised with a test-owned specialization whose native object
is a plain Python value, so nothing here depends on NATS.
"""

import subprocess
import sys
from typing import Any

import pytest
from faststream import FastStream
from pydantic import ConfigDict, ValidationError
from pydantic_settings import SettingsConfigDict

from type_construction import Model, Resource, Settings

# Blocks the NATS integration's dependencies before importing the core exports, as an
# installation without the ``nats`` extra would behave.
CORE_IMPORT_WITHOUT_NATS = """
import sys
class Blocked:
    NAMES = ("nats", "nkeys", "aiohttp", "faststream.nats", "type_construction.nats")
    def find_spec(self, name, path=None, target=None):
        if name in self.NAMES or name.startswith(tuple(f"{n}." for n in self.NAMES)):
            raise ModuleNotFoundError(f"blocked: {name}")
        return None
sys.meta_path.insert(0, Blocked())
import type_construction
from type_construction import Model, Resource, Root, Settings
from type_construction.diagnostics import Problem, problems
from type_construction.resources import Resource as Declared
print(sorted(type_construction.__all__))
loaded = [m for m in sys.modules if m.split(".")[0] in ("nats", "nkeys", "aiohttp")]
print(Declared is Resource, loaded)
try:
    import type_construction.nats
except ModuleNotFoundError as error:
    print("integration unavailable:", str(error).split(":")[0])
"""


class Registry:
    """A stand-in runtime object a test integration registers its native objects with."""

    def __init__(self) -> None:
        self.realized: list[object] = []


class Counter(Model):
    """The native object of the test integration: identity matters, configuration does not."""

    model_config = ConfigDict(frozen=False)

    start: int


class CounterResource(Resource[Counter]):
    """A test integration's specialization: typed configuration plus its binding."""

    start: int = 0

    def bind(self, owner: FastStream) -> Counter:
        counter = Counter(start=self.start)
        owner.context.set_global("counters", [*owner.context.get("counters", []), counter])
        return counter


class WorkerSettings(Settings):
    model_config = SettingsConfigDict(env_prefix="WORKER_")

    counter: CounterResource


def construct[S: Settings](declaration: type[S], /, **values: Any) -> S:
    return declaration(**values)


def test_the_shared_contract_cannot_be_realized_without_an_integration() -> None:
    with pytest.raises(TypeError, match="abstract"):
        Resource()  # type: ignore[abstract]


def test_an_integration_specialization_binds_to_a_runtime_and_returns_its_native_object(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WORKER_COUNTER__START", "7")
    owner = FastStream()

    resource = construct(WorkerSettings).counter
    native = resource.bind(owner)

    assert resource == CounterResource(start=7)
    assert isinstance(native, Counter) and native.start == 7
    assert owner.context.get("counters") == [native]


def test_each_binding_realizes_a_separate_placement() -> None:
    resource = CounterResource(start=1)
    owner = FastStream()
    other = FastStream()

    first = resource.bind(owner)
    second = resource.bind(owner)
    elsewhere = resource.bind(other)

    assert first is not second and first is not elsewhere
    assert first == second == elsewhere, "equal configuration, distinct native objects"
    assert owner.context.get("counters") == [first, second]
    assert other.context.get("counters") == [elsewhere]


def test_a_resource_is_an_immutable_fact_without_its_native_object() -> None:
    resource = CounterResource(start=3)
    native = resource.bind(FastStream())
    native.start = 99

    with pytest.raises(ValidationError) as excinfo:
        resource.start = 4

    assert excinfo.value.errors()[0]["type"] == "frozen_instance"
    assert resource.model_dump() == {"start": 3}, "the live object is never part of the model"
    assert hash(resource) == hash(CounterResource(start=3))


def test_core_exports_import_without_the_nats_integration_dependencies() -> None:
    result = subprocess.run(  # noqa: S603 - the interpreter and script are fixed test inputs
        [sys.executable, "-I", "-c", CORE_IMPORT_WITHOUT_NATS],
        env={},
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "['Model', 'Resource', 'Root', 'Settings']",
        "True []",
        "integration unavailable: blocked",
    ]
