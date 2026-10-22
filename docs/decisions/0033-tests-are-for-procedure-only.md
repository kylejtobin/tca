# 0033. Tests are the framework's, run over a program; a page has none

Status: accepted

## Context

The world module is kinds whose behavior is Pydantic's. The engine and the library kinds are procedure. A page is classes. What must be shown is that the procedure does to a program what the records say.

## Rejected

Writing a failing test before each class on a page. A class has no behavior to fail; constructing it is its test. Testing the engine against stand-in classes written inside the test: a program the discipline would refuse proves nothing about one it would accept.

## Decision

Tests are written for the framework's procedure, the engine, the command line and a library kind's `perform`, and they run over a program the test module is: the engine reads a program as the classes its module defines, so a test module declares the few classes its behaviors need, named for what they are to the framework, `Element`, `Elements(Request)`, `Heard(Record)`, `Asked(Action)`, `Concluded(Fact)`, `Answered(Reply)`, `Operation(Route)`, `Parties(Config)`, with a stand-in party whose `perform` returns `hear(self, self.party.says.root)`. A program with every fault the proof refuses is a second module beside it, `faults.py`; a program whose one outcome a party's answer refutes is a third, `stalls.py`; parties that record their opening and closing are in `lifecycle.py`, which is not a program. The command line's tests are the same shape over a request of every shape the shell renders. No module and no class is named for a business, and nothing in `tests/` is a product. A kind's own construction and refusal are tested by constructing instances and asserting the `ValidationError` type. No test file exists for a page. `just check` runs `pytest` over `packages/python`. The feature files beside each package are the scenarios the tests bind.

## Evidence

Thirty-five tests pass under `uv run pytest -q`, in `just check`. Over the engine's program: the proof places every class by its fields, as a path of element classes, with nothing waiting; the program's classes are the ones its module defines; a route's request, an action's records and a computed field's words are read from their parameters; a record union is heard as the member the text constructs; the classes a route builds are those its reply leads to; each element is valued in its own scope and each part in its own, and the reply is `{"total":"5.00"}` in four passes; the relation that holds decides the outcome and the effect on that branch is performed; a fresh scalar is constructed for each holder; no element collects the empty tuple; a relation that cannot hold or cannot refuse is read from the intervals; an interval is read from the bounds, the default or the operation; a scalar over `int` has no value between two integers; two facts told apart by complementary relations are proven exclusive; the proof refuses every fault at once, fourteen types; a stalled run names the relation that did not hold with the ordering observed, and the selection with nothing to choose and not the complement that was decided; a selection's shape is its tuple annotation; a relation's ordering is computed, admitted by its `Literal` and never given; `opened` closes what it opened; a failing action propagates in a group; connections open once and close in reverse; an action or a connection without a library kind cannot be constructed; an answer is one span per route and one per performed action; a client in a private attribute leaves the connection frozen; a reply's word that refuses refuses when the reply is serialized. Over the command line's program: the program is proven before anything is listed; a route's help shows each option read from the request; the parsed options rebuild the tree; a missing option and a value outside a constraint exit 1 naming the field; an unknown route exits 2; a valid request prints `{"name":"tea","words":["yes","yes"]}`; the deployment's variables are listed from the config; the proof is computed once and passed to the run.

## Consequences

A behavior a record claims about the engine has a test over a program, or it is not claimed. A test that needs a class the page rules refuse is a defect in the test. Refuted by nothing.
