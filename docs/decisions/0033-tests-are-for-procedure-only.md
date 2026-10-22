# 0033. Tests are the framework's, run over a program; a page has none

Status: accepted

## Context

The world module is kinds whose behavior is Pydantic's. The engine and the library kinds are procedure. A page is classes. What must be shown is that the procedure does to a program what the records say.

## Rejected

Writing a failing test before each class on a page. A class has no behavior to fail; constructing it is its test. Testing the engine against stand-in classes written inside the test: a program the discipline would refuse proves nothing about one it would accept.

## Decision

Tests are written for the framework's procedure, the engine and a library kind's `perform`, and they run over a program the test module is: the engine reads a program as the classes its module defines, so a test module declares the few classes its behaviors need, named for what they are to the framework, `Element`, `Elements(Request)`, `Heard(Record)`, `Asked(Action)`, `Concluded(Fact)`, `Answered(Reply)`, `Operation(Route)`, `Parties(Config)`, with a stand-in party whose `perform` returns `hear(self, self.party.says.root)`. A program with the faults the proof refuses is a second small module beside it, named for its faults. No module and no class is named for a business, and nothing in `tests/` is a product. A kind's own construction and refusal are tested by constructing instances and asserting the `ValidationError` type. No test file exists for a page. `just check` runs `pytest` over `packages/python`. The feature files beside each package are the scenarios the tests bind.

## Evidence

Twenty-five tests pass under `uv run pytest -q packages/python`, in `just check`: the test program is proven and its classes are the ones its module defines; its proof is what joins from the request, read once per process; scope is read as the element a class descends from; a route's request, an action's records and a computed field's products are read from their parameters; each element is valued in its own run and collected in order; the relation that holds decides the outcome; no element collects the empty tuple; the bounds decide what a relation can never do, exactly over integers; complementary relations cannot both hold and overlapping ones can; the solver decides strictness; the faults program is refused with every fault at once, including a cycle beside a root fault; a stalled run names the relation that did not hold; an empty selection refuses; connections open once and close in reverse, and `opened` closes what it opened; an action or a connection without a library kind cannot be constructed; a client in a private attribute leaves the connection frozen; a failing action propagates in a group; a reply's computed field whose scalar refuses propagates the refusal out of `answer`; and an answer is one span per route and one per performed action.

## Consequences

A behavior a record claims about the engine has a test over the program, or it is not claimed. A test that needs a class the page rules refuse is a defect in the test. Refuted by nothing.
