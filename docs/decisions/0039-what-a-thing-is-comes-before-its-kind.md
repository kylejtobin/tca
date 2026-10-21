# 0039. What a thing is, its valid states and its owner are stated before its kind

Status: accepted

## Context

`Ordered`, the fieldless records, `Unreachable` and the engine's producer classes each had a Pydantic feature behind them and were still wrong, because none was a thing in the business: one was an order of attempts, several were tags, one was the failure track, several were the engine's memory.

## Decision

Before a class is written, three answers are written: what it is in the business, which states it can be in, who owns it. The kind follows from the answers. A class with no answer to the first is a step or a mechanism wearing a type and is not written.

## Evidence

Each class in Context was removed by asking the first question; none was removed by a check.

## Consequences

A class whose docstring cannot say what it is in the business is a defect. Refuted by nothing.
