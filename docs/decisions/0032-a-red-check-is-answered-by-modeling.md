# 0032. A red check is answered by modeling, not by narrowing

Status: accepted

## Context

The schema walk in the CLI was written over `dict[str, object]`. Each basedpyright error was answered with an `isinstance` or an `assert` on the node that was red.

## Rejected

Fixing the red line. Ten `REFLECTION` hits and three unknown-type errors later, the walk was asking every node what it was.

## Decision

When a check is red, the question is what the data is, not how to make the line pass. The ten checks said the input was untyped; the answer was to parse the schema into classes once, after which no node is asked what it is.

## Evidence

`Member` union and node classes: 0 basedpyright errors, `REFLECTION` from ten to two, the two on `ModuleType` and on the dict in `tree`.

## Consequences

A second `isinstance` on the same data is the signal to stop and model. Refuted by nothing.
