# 0033. Tests are written for procedure only

Status: accepted

## Context

The world module is classes with no behavior of its own. A page is classes. Pydantic guarantees construction, refusal, serialization and schema.

## Rejected

Writing a failing test before each class. A class has no behavior to fail; constructing it is its test.

## Decision

No test file for the world or for a page. A class is tested by constructing it, which a program does when it runs. Tests, when written, cover procedure: a library kind's `perform`, the engine's body. Until then the product's acceptance rows, run against the demo program through the command line and HTTP, are the checks. The feature files pin Pydantic's behavior against a Pydantic release, not our code.

## Evidence

Every behavior in the feature files is a Pydantic call and its result; none exercises code in this repository.

## Consequences

`just check`'s pytest step runs no tests until a library kind or the engine body exists. Refuted by a defect in the world module a test would have caught; none has occurred, and the module has no branch to be wrong in.
