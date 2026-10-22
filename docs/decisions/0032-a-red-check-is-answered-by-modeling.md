# 0032. A red check is answered by modeling, not by narrowing

Status: accepted

## Context

The schema walk in the CLI was written over `dict[str, object]`. Each basedpyright error was answered with an `isinstance` or an `assert` on the node that was red.

## Rejected

Fixing the red line. Ten `REFLECTION` hits and three unknown-type errors later, the walk was asking every node what it was. Parsing the schema into node classes, which answered the checker and kept a second representation of the request.

## Decision

When a check is red, the question is what the data is, not how to make the line pass. The ten checks said the input was untyped; the answer was to stop reading an untyped document and read the classes: the CLI's options, tree and variables are the engine's `holds` and `collects` over `model_fields`, where every value is a class.

## Evidence

The CLI over the engine's reads: 0 basedpyright errors in strict mode, no document, no node class, and no `isinstance` on data; the three `isinstance` calls that remain are on annotations, asking whether an annotation is a class, which is the read itself.

## Consequences

A second `isinstance` on the same data is the signal to stop and model. Refuted by nothing.
