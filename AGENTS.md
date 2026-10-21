# AGENTS.md

This repository is Type Construction Architecture: a developer writes an application as subclasses of ten Pydantic classes, and an engine constructs them. Constructing a type is the computation. Refusal is the only control flow. The product is the modeling experience; the engine exists to make it true and never appear.

You own this model. The measure of every decision is whether a developer says less, says it once, and says only their world.

## How to think

- Before any line, say what the thing is in the business, which states it can be in, and who owns it. The kind follows from the answers. A class with no answer to the first question is a step or a mechanism wearing a type; do not write it.
- A rule is a type that cannot construct the wrong value: a constrained `Scalar`, or two scalars with disjoint constraints and a union of the facts that hold them. A check that confirms a value and returns the same type has thrown the knowledge away.
- A choice is a union whose members each say fully what they are. A collection is a tuple. A failure is a refusal. An absence is a class. Each of these is a Pydantic construct the checker reads; an `if`, a loop, a `try`, a `None` or a validator is the same thing written as procedure.
- Before adding a kind or a mechanism, name the discipline that already solved it and the Pydantic feature that already is it. When a line refuses, keep the kind and move its shape to what Pydantic constructs.
- Every change is more type safe than what it replaces: the checker sees more, the proof refuses more, the page says less. Otherwise write that no more type safe strategy exists and what would refute that.
- A red check is answered by modeling, not by narrowing. The second `isinstance` on the same data is the signal to stop and ask what the data is.
- Procedure lives in two places and nowhere else: the engine, which reads annotations and constructs in their order, and a library kind's `perform`, where Python calls a client.

## How to work

- Run every Pydantic behavior on the pinned version before writing it into code, a record or a skill. A claim without a run is not a decision.
- Record a decision before reporting the code it decides: `docs/decisions/`, with Context, Rejected, Decision, Evidence and Consequences. A record states the current decision only; a replaced approach moves into Rejected. "Later", "next session" and "the loop will decide" are not decisions. The scenarios that pin a behavior live beside the package in `tests/features/`.
- Run checks only as `just` declares them and report no other result. Passing is not proof: a design that meets a rule's syntax and defeats its purpose is wrong.
- Lead every report with what is not done and why. A report whose first line is a pass is a defect in the report.
- Write in software engineering language: classes, fields, calls, values and error types, each claim checkable. No metaphor.
- Do the scope asked and nothing beyond it. One request, one scope; anything more waits to be asked for.
- Run `git`, `just`, `uv` and `docker` as the bare command, never behind `cd`, `&&` or a pipe; the sandbox rules match the command as typed.
- Commit with `.gitmessage` filled; name the records a change implements or amends when it touches `packages/python`.

## Where things are

- `.agents/skills/tca-python-dev`: the developer's reference, what to write and what the engine does with it.
- `.agents/skills/smell-check`: the six line patterns that mark procedure on a page; `just check` runs it on every program.
- `.agents/skills/tca-python-package`, `tca-infra`, `naming-guidelines`: packages, build, names.
- `docs/product.md`: who this is for, the promise, the acceptance checks.
- `docs/decisions/`: every decision with its evidence. `TODO.md`: what is not built, in order.
