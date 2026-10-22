"""Logfire's OpenTelemetry integration over the engine's spans: one route answered in a process
Logfire configured, with every span kept in memory. Logfire is optional: the engine imports
``opentelemetry-api`` alone, and this module is skipped where Logfire is not installed."""

import inspect
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from type_construction import engine

from .test_occurrences import ORDER

pytest.importorskip("logfire")

SCRIPT = Path(__file__).with_name("logfired.py")
"""The process that answers one route under Logfire and prints its spans."""

PRICES = '{"tea": "2.50", "mug": "4", "pot": "10"}'
"""The catalog's line: a business payload that must reach no span."""


def test_the_engine_imports_nothing_from_logfire() -> None:
    assert "logfire" not in inspect.getsource(engine)


def test_a_route_under_logfire_is_one_trace_of_the_engines_spans(tmp_path: Path) -> None:
    env = {
        **os.environ,
        "PYTHONPATH": str(SCRIPT.parents[1]),
        "CATALOG__PRICES": PRICES,
        "FRAUD__SAYS": '{"status": "clear"}',
    }
    ran = subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT)],
        input=ORDER,
        env=env,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    found = json.loads(ran.stdout)
    assert found["provider"] == "logfire._internal.tracer.ProxyTracerProvider"
    assert found["reply"] == '{"cart":"10.00","gifts":"4","pair":"14.50","solo":"10"}'
    spans = found["spans"]
    (route,) = [s for s in spans if s["name"] == "Checkout"]
    actions = [s for s in spans if s["name"] != "Checkout"]
    assert len(spans) == 8
    assert route["parent"] is None
    assert {s["trace"] for s in spans} == {route["trace"]}
    assert all(s["parent"] == route["span"] for s in actions)
    assert route["attributes"]["tca.request"] == "PlaceOrder"
    assert route["attributes"]["tca.outcome"] == "answered"
    assert route["attributes"]["tca.passes"] == 4
    assert sorted((e["name"], e["attributes"]["tca.heard"]) for e in route["events"]) == sorted(
        ("admitted", s["attributes"]["tca.heard"]) for s in actions
    )
    assert all(s["events"] == [] for s in actions)
    assert sorted(s["attributes"]["tca.site"] for s in actions) == [
        "Screen",
        "request.cart.lines.[0].Quote",
        "request.cart.lines.[1].Quote",
        "request.gifts.lines.[0].Quote",
        "request.pair.lines.[0].Quote",
        "request.pair.lines.[1].Quote",
        "request.solo.lines.[0].Quote",
    ]
    for s in actions:
        site = s["attributes"]["tca.site"]
        assert s["attributes"]["tca.pass"] == 1
        assert s["attributes"]["tca.heard"] == f"{site}.heard"
        assert s["attributes"]["tca.outcome"] == "heard"
        assert s["attributes"]["tca.record"] == ("Clear" if site == "Screen" else "Price")
        assert s["attributes"]["tca.party"] == ("Fraud" if site == "Screen" else "Catalog")
        assert s["status"] == "UNSET"
    exported = " ".join(str(v) for s in spans for v in s["attributes"].values())
    for secret in ("2.50", "10.00", "tea", "mug", "pot", "clear", PRICES, "TEN"):
        assert secret not in exported
