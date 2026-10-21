# 0001. A Pydantic behavior is run before it is written down

Status: accepted

## Context

The first schema in `next/handoff.md` declared `class Ordered[T](RootModel[T])` with `root: Annotated[T, Field(union_mode="left_to_right")]`. On Pydantic 2.13.5 the class definition raised `RuntimeError: Unable to apply constraint 'union_mode' to schema of type 'any'`. The schema had been labeled "verbatim" without being executed.

## Rejected

Writing a schema, a decision or a skill sentence from recall of Pydantic's documentation.

## Decision

Every claimed Pydantic behavior is executed on the pinned version before it enters a module, a decision record, the skill or the product document. The run's input, output and error type are recorded with the claim.

## Evidence

The `Ordered` definition failed at class creation. Four later claims written with a "not yet run" label included `Unreachable[P]`, which, when run, accepted an instance of the wrong parametrization (0014).

## Consequences

A claim without a recorded run is not a decision. A label such as "not yet run" does not substitute for the run.
