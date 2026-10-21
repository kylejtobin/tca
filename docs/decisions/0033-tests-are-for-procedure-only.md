# 0033. Tests are the framework's, run over a program; a page has none

Status: accepted

## Context

The world module is kinds whose behavior is Pydantic's. The engine and the library kinds are procedure. A page is classes. What must be shown is that the procedure does to a program what the records say.

## Rejected

Writing a failing test before each class on a page. A class has no behavior to fail; constructing it is its test. Testing the engine against stand-in classes written inside the test: a program the discipline would refuse proves nothing about one it would accept.

## Decision

Tests are written for the framework's procedure, the engine and a library kind's `perform`, and they run over a program that conforms to the page rules, held beside the tests: `packages/python/type-construction-engine/tests/type_construction_engine/shop.py`, with parties that answer from the environment. A broken program is that program's source with one edit, loaded as a module of its own, because the engine reads a program as the classes its module defines. A kind's own construction and refusal are tested by constructing instances and asserting the `ValidationError` type. No test file exists for a page. `just check` runs `pytest` over `packages/python`. The feature files beside each package are the scenarios the tests bind.

## Evidence

Thirteen tests over the shop pass under `uv run pytest -q packages/python`, in `just check`: the record union is heard and answered either way, the proof places each kind in its scope, an order with a derived total, a threshold relation and a selection answers `{"total":"120.000","charges":["ch_1","ch_1"],"cheapest":"7.50"}`, the overlap and the impossible relations are refused at startup, and each derivation, relation and selection kind constructs or refuses with the error type its record states.

## Consequences

A behavior a record claims about the engine has a test over the program, or it is not claimed. A test that needs a class the page rules refuse is a defect in the test. Refuted by nothing.
